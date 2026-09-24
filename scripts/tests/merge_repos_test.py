import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


SCRIPT = Path(os.environ.get(
    'MERGE_REPOS_SCRIPT',
    Path(__file__).resolve().parents[1] / 'merge-repos.py',
)).resolve()


class MergeReposTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        self.first = self.directory / 'ros2 input.repos'
        self.second = self.directory / 'space ros input.repos'
        self.output = self.directory / 'merged output.repos'
        self.base = {'repositories': {
            'z/base': {'type': 'git', 'url': 'https://example.invalid/base', 'version': 'main'},
            'm/shared': {'type': 'git', 'url': 'https://example.invalid/shared', 'version': 'old'},
        }}
        self.override = {'repositories': {
            'm/shared': {'type': 'git', 'url': 'https://example.invalid/replacement', 'version': 'new'},
            'a/added': {'type': 'git', 'url': 'https://example.invalid/added', 'version': 'v1'},
        }}
        self.expected = {'repositories': {
            'a/added': self.override['repositories']['a/added'],
            'm/shared': self.override['repositories']['m/shared'],
            'z/base': self.base['repositories']['z/base'],
        }}
        self.first.write_text(yaml.safe_dump(self.base, sort_keys=False), encoding='utf-8')
        self.second.write_text(yaml.safe_dump(self.override, sort_keys=False), encoding='utf-8')
        self.first_before = self.first.read_bytes()
        self.second_before = self.second.read_bytes()

    def run_merge(self, *arguments):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.first), str(self.second), *map(str, arguments)],
            cwd=self.directory, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.second.read_bytes(), self.second_before)

    def assert_merged(self, path):
        actual = yaml.safe_load(path.read_text(encoding='utf-8'))
        self.assertEqual(actual, self.expected)
        self.assertEqual(list(actual['repositories']), ['a/added', 'm/shared', 'z/base'])

    def test_omitted_output_overwrites_first_input(self):
        self.run_merge()
        self.assert_merged(self.first)
        self.assertFalse(self.output.exists())

    def test_short_output_preserves_inputs(self):
        self.run_merge('-o', self.output)
        self.assert_merged(self.output)
        self.assertEqual(self.first.read_bytes(), self.first_before)

    def test_long_output_preserves_inputs(self):
        self.run_merge('--output', self.output)
        self.assert_merged(self.output)
        self.assertEqual(self.first.read_bytes(), self.first_before)

    def test_explicit_output_can_overwrite_first_input(self):
        self.run_merge('-o', self.first)
        self.assert_merged(self.first)


if __name__ == '__main__':
    unittest.main()
