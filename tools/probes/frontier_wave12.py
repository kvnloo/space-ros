"""Fork-only evidence workers. No upstream writes, simulation or flight validation.

SU2: collect pinned sources and nearfield references; not a solver execution.
PlasmaPy: execute the exact proposed Markdown examples against pinned source.
"""
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
OUT = Path('wave12-results').resolve()
PLASMA_SHA = '391579b61d153bfe4b92f59f39ab6e563a44f29d'
SU2_SHA = '9cd08dcdf7fc8aab2660497ac02c3f67285efbbe'


def source_audit():
    """Read explicitly allowlisted public code, retaining complete sources."""
    files = [
        'SU2_CFD/src/solvers/CEulerSolver.cpp',
        'SU2_CFD/src/integration/CIntegration.cpp',
        'Common/src/geometry/CPhysicalGeometry.cpp',
        'TestCases/euler/biparabolic/BIPARABOLIC.cfg',
        'config_template.cfg',
    ]
    receipts, excerpts = [], []
    for path in files:
        url = 'https://raw.githubusercontent.com/su2code/SU2/' + SU2_SHA + '/' + path
        with urlopen(Request(url, headers={'User-Agent': 'kvnloo-frontier-evidence'}), timeout=30) as response:
            raw = response.read(8 * 1024 * 1024 + 1)
        if len(raw) > 8 * 1024 * 1024:
            raise RuntimeError('Source exceeds read budget: ' + path)
        target = OUT / 'su2-source' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        lines = raw.decode('utf-8').splitlines()
        hits = [i for i, line in enumerate(lines) if re.search(r'nearfield|near_field', line, re.I)]
        receipts.append({'path': path, 'commit': SU2_SHA, 'url': url,
                         'git_blob_sha': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(),
                         'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
                         'reference_lines': [i + 1 for i in hits]})
        # Bounded context is an index into the saved complete files, not a code proof.
        selected = sorted({j for i in hits[:30] for j in range(max(0, i-8), min(len(lines), i+70))})
        excerpts.append('\n# ' + path + '\n' + '\n'.join(f'{i+1}: {lines[i]}' for i in selected))
    (OUT / 'su2-nearfield-excerpts.txt').write_text('\n'.join(excerpts))
    result = {'scope': 'Pinned complete-source retrieval only', 'sources': receipts,
              'not_run': ['CFD solver', 'mesh audit', 'convergence experiment'],
              'root_cause': 'UNPROVEN'}
    (OUT / 'su2-receipts.json').write_text(json.dumps(result, indent=2) + '\n')
    print('SU2_AUDIT ' + json.dumps(result), flush=True)


def plasma_examples():
    """Test proposed documentation without changing scientific implementations."""
    import astropy
    import astropy.units as u
    import numpy as np
    import plasmapy
    from plasmapy.particles import CustomParticle, Particle, ParticleList

    target = Path('plasmapy-target').resolve()
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=target, check=True,
                          capture_output=True, text=True).stdout.strip()
    if head != PLASMA_SHA:
        raise RuntimeError('Unexpected PlasmaPy checkout')
    if not Path(plasmapy.__file__).resolve().is_relative_to(target):
        raise RuntimeError('Imported PlasmaPy does not come from the pinned checkout')
    original = (target / 'AGENTS.md').read_text()
    guidance = (HERE / 'plasmapy_units_guidance.md').read_text()
    if original.count('## Documentation\n') != 1:
        raise RuntimeError('Expected exactly one insertion anchor')
    candidate = original.replace('## Documentation\n', guidance + '## Documentation\n')
    if len(candidate.splitlines()) > 200:
        raise RuntimeError('Candidate exceeds the requested guidance length')
    for relative in ['docs/contributing/coding_guide.rst', 'docs/particles/index.rst']:
        if not (target / relative).is_file():
            raise RuntimeError('Candidate contains an invalid documentation link: ' + relative)
    (OUT / 'AGENTS.candidate.md').write_text(candidate)
    patch = ''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                                       fromfile='a/AGENTS.md', tofile='b/AGENTS.md'))
    (OUT / 'plasmapy-agents.patch').write_text(patch)
    namespace = {}
    blocks = re.findall(r'```python\n(.*?)```', guidance, re.S)
    if len(blocks) != 3:
        raise RuntimeError('Expected exactly three executable documentation examples')
    for index, block in enumerate(blocks):
        exec(compile(block, f'plasmapy_units_guidance.md:block-{index+1}', 'exec'), namespace)

    class GuidanceTests(unittest.TestCase):
        def test_temperature_equivalence(self):
            np.testing.assert_allclose(namespace['temperature'].to_value(u.K), 11604.518121550082, rtol=1e-12)
        def test_energy_requires_explicit_equivalence(self):
            with self.assertRaises(u.UnitConversionError):
                (1*u.eV).to(u.K)
        def test_particle_examples(self):
            self.assertEqual(namespace['helium_ion'], Particle('He-4 +1'))
            self.assertIsInstance(namespace['species'], ParticleList)
            self.assertEqual(namespace['species'].symbols, ['p+', 'e-'])
            self.assertIsInstance(namespace['custom'], CustomParticle)
            self.assertEqual(namespace['custom'].mass, 1e-26*u.kg)
        def test_decorated_temperature_and_particle(self):
            value, particle = namespace['checked_inputs'](1*u.eV, 'p+')
            self.assertEqual(value.unit, u.K)
            np.testing.assert_allclose(value.value, namespace['temperature'].value)
            self.assertEqual(particle, Particle('p+'))
        def test_kelvin_and_ev_inputs_agree(self):
            first, _ = namespace['checked_inputs'](namespace['temperature'], 'p+')
            second, _ = namespace['checked_inputs'](1*u.eV, 'p+')
            self.assertEqual(first, second)
        def test_reject_incompatible_units(self):
            with self.assertRaises(u.UnitsError):
                namespace['checked_inputs'](1*u.m, 'p+')
        def test_reject_negative_temperature(self):
            with self.assertRaises(ValueError):
                namespace['checked_inputs'](-1*u.eV, 'p+')
        def test_array_temperature_and_particle_list(self):
            values, particles = namespace['checked_inputs'](np.array([1.,2.])*u.eV, ['p+', 'e-'])
            self.assertEqual(values.shape, (2,))
            np.testing.assert_allclose(values.value, namespace['temperature'].value*np.array([1.,2.]))
            self.assertIsInstance(particles, ParticleList)

    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GuidanceTests))
    summary = {'commit': head, 'python': sys.version, 'plasmapy_source': str(plasmapy.__file__),
               'astropy_version': astropy.__version__, 'numpy_version': np.__version__,
               'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
               'skips': len(result.skipped), 'markdown_lines': len(candidate.splitlines()),
               'scope': 'Documentation example execution; no scientific implementation changes',
               'not_run': ['full PlasmaPy suite', 'docs build', 'repository lint']}
    (OUT / 'plasmapy-results.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('PLASMAPY_EXAMPLES ' + json.dumps(summary), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
    subprocess.run(['git', 'apply', '--check', str(OUT/'plasmapy-agents.patch')], cwd=target, check=True)


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    if sys.argv[1:] == ['su2']:
        source_audit()
    elif sys.argv[1:] == ['plasmapy']:
        plasma_examples()
    else:
        raise SystemExit('usage: frontier_wave12.py su2|plasmapy')
