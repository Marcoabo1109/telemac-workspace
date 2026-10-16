"""Enable a final GAIA budget print for a completed deterministic FV benchmark.

The upstream FV T2D path calls GAIA before updating TOTAL_ITER at the final step.
A benchmark-specific user routine only widens print predicates at the final
iteration observed in the baseline log. Hydrodynamics and sediment equations are
unchanged. This is not a general patch for unknown adaptive runs.
"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from scripts.sediment_benchmarks import ROOT, SHA, digest


def prepare(source, destination):
    source = Path(source); destination = Path(destination)
    if subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() != SHA:
        raise ValueError('Wrong source revision')
    if destination.exists(): raise FileExistsError('Preserve existing runs; choose a new destination')
    base = ROOT/'models/synthetic_sediment'
    manifest = json.loads((base/'manifest.json').read_text())
    case = next(c for c in manifest['cases'] if c['id']=='sand_bedload')
    original = base/'sand_bedload'
    evidence = json.loads((original/'execution.json').read_text())
    log = (original/'solver-output.txt').read_text()
    if evidence['returncode'] != 0 or 'My work is done' not in log:
        raise ValueError('A completed baseline is required')
    for item in evidence['results']:
        if digest(original/item['file']) != item['sha256']:
            raise ValueError('Baseline result hash changed')
    iterations = re.findall(r'ITERATION\s+(\d+)\s+TIME:', log)
    last = int(iterations[-1])
    case['id'] = 'sand_diagnostic'
    folder = destination/case['id']; folder.mkdir(parents=True)
    for rel, sha in case['input_sha256'].items():
        if digest(original/rel) != sha: raise ValueError('Baseline input hash changed')
        target = folder/rel; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original/rel, target)
    routine = (source/'sources/gaia/mass_balance.f').read_text()
    replacements = {'      IF(ENTET) THEN': f'      IF(ENTET.OR.LT.EQ.{last}) THEN',
                    '          IF(LT.EQ.NIT) THEN': f'          IF(LT.EQ.NIT.OR.LT.EQ.{last}) THEN'}
    for before, after in replacements.items():
        if routine.count(before) != 1: raise ValueError('Upstream print structure changed')
        routine = routine.replace(before, after)
    header = f'! Synthetic benchmark diagnostic: print final budget at LT={last}.\n! Only print predicates changed; baseline final iteration is recorded.\n'
    (folder/'user_fortran/mass_balance.f').write_text(header+routine)
    case['diagnostic'] = {'final_iteration': last, 'baseline_log_sha256': digest(original/'solver-output.txt'),
                          'source_routine_sha256': digest(source/'sources/gaia/mass_balance.f'),
                          'changes': replacements, 'purpose': 'final balance print only; verify outputs against baseline'}
    case['input_sha256'] = {str(p.relative_to(folder)): digest(p) for p in folder.rglob('*') if p.is_file()}
    manifest['cases'] = [case]
    (destination/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    shutil.copy2(base/'LICENSE.upstream.txt', destination/'LICENSE.upstream.txt')


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--source', type=Path, required=True); p.add_argument('--out', type=Path, default=ROOT/'models/synthetic_sand_diagnostic'); a = p.parse_args()
    prepare(a.source, a.out)
