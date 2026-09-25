"""Bounded, read-only source trace for SU2#2865. No solver/build/root-cause claim."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = '9cd08dcdf7fc8aab2660497ac02c3f67285efbbe'
OUT = Path('wave12-results/su2-trace')
ROOTS = ('SU2_CFD/src/', 'SU2_CFD/include/', 'Common/src/', 'Common/include/')
PATTERN = r'NEARFIELD_BOUNDARY|BC_NearField|BC_Fluid_Interface|MatchNearField'


def run(*args):
    completed = subprocess.run(args, capture_output=True, text=True, timeout=180)
    if completed.returncode:
        print(completed.stderr, flush=True)
        raise RuntimeError(f'Command failed ({completed.returncode}): {args}')
    return completed.stdout


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    repo = OUT / 'checkout'
    run('git', 'init', str(repo))
    run('git', '-C', str(repo), 'remote', 'add', 'origin', 'https://github.com/su2code/SU2.git')
    run('git', '-C', str(repo), 'fetch', '--filter=blob:none', '--depth=1', 'origin', BASE)
    run('git', '-C', str(repo), 'sparse-checkout', 'set', 'SU2_CFD/src', 'SU2_CFD/include', 'Common/src', 'Common/include')
    run('git', '-C', str(repo), 'checkout', '--detach', 'FETCH_HEAD')
    if run('git', '-C', str(repo), 'rev-parse', 'HEAD').strip() != BASE:
        raise RuntimeError('Wrong source revision')
    paths = run('git', '-C', str(repo), 'ls-tree', '-r', '--name-only', BASE).splitlines()
    hits, receipts = [], []
    byte_count = 0
    for path in paths:
        if not path.startswith(ROOTS) or not path.endswith(('.cpp', '.hpp', '.inl', '.h')):
            continue
        raw = (repo / path).read_bytes()
        lines = raw.decode('utf-8').splitlines()
        matched = [i for i, line in enumerate(lines) if re.search(PATTERN, line)]
        if not matched:
            continue
        byte_count += len(raw)
        if byte_count > 12*1024*1024:
            raise RuntimeError('Matching-file evidence budget exceeded')
        target = OUT / 'source' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        expected = run('git', '-C', str(repo), 'rev-parse', BASE+':'+path).strip()
        if expected != blob:
            raise RuntimeError('Blob hash mismatch: '+path)
        receipts.append({'path': path, 'blob_sha': blob, 'sha256': hashlib.sha256(raw).hexdigest(),
                         'lines': [i+1 for i in matched]})
        for i in matched:
            hits.append({'path': path, 'line': i+1, 'text': lines[i],
                         'context': '\n'.join(f'{j+1}: {lines[j]}' for j in range(max(0,i-5),min(len(lines),i+55)))})
    (OUT / 'matches.json').write_text(json.dumps(hits, indent=2)+'\n')
    (OUT / 'receipts.json').write_text(json.dumps({'base':BASE,'scope':'Complete source matches, no build or solver execution',
                                                 'sources':receipts,'root_cause':'UNPROVEN'},indent=2)+'\n')
    for match in hits:
        print(f"{match['path']}:{match['line']}: {match['text']}")
    print('SOURCE_TRACE_SUMMARY '+json.dumps({'files':len(receipts),'matches':len(hits),'bytes':byte_count,'commit':BASE}))


if __name__ == '__main__':
    main()
