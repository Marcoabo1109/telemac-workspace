"""Prepare pinned, synthetic TELEMAC/GAIA/Nestor benchmarks; run via trusted CLI.

Preparation is not solver validation. Upstream reference results remain separately
labelled and are never accepted as outputs of a new execution.
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
from pathlib import Path
from backend.api import cas_parser

ROOT = Path(__file__).resolve().parents[1]
SHA = 'd1bff193746fd76425d7715a6e4d20d42eb8877e'
CASES = {
    'micropol_deposition': ('waqtel/waq2d_micropol', 't2d_waq2d_micropol.cas', {}),
    'micropol_adsorption': ('waqtel/waq2d_micropol', 't2d_waq2d_micropol.cas', {'SEDIMENT SETTLING VELOCITY': '0.'}),
    'micropol_desorption': ('waqtel/waq2d_micropol', 't2d_waq2d_micropol.cas', {'SEDIMENT SETTLING VELOCITY': '0.'}),
    'mud_exchange': ('gaia/mud_conservation-t2d', 't2d_mud_cons.cas', {}),
    'mud_deposition': ('gaia/mud_conservation-t2d', 't2d_mud_cons.cas', {'LAYERS PARTHENIADES CONSTANT': '0.'}),
    'mud_erosion': ('gaia/mud_conservation-t2d', 't2d_mud_cons.cas', {'CLASSES SETTLING VELOCITIES': '0.'}),
    'mud_passive': ('gaia/mud_conservation-t2d', 't2d_mud_cons.cas', {'LAYERS PARTHENIADES CONSTANT': '0.', 'CLASSES SETTLING VELOCITIES': '0.'}),
    'sand_bedload': ('gaia/flume_bc-t2d', 't2d_flume_bc.cas', {}),
    'nestor_dig': ('nestor/nestor1_Dig', 't2d_nestor1_gai.cas', {}),
    'nestor_dump': ('nestor/nestor2_Dump', 't2d_nestor2_gai.cas', {}),
    'nestor_dig_dump': ('nestor/nestor3_critDigDump', 't2d_nestor3_gai.cas', {}),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(source, destination, group="gaia", time_step=None, tracer_accuracy=None):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    sha = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if sha != SHA:
        raise ValueError(f'Expected TELEMAC v8p5r0 {SHA}, got {sha}')
    if destination.exists():
        raise FileExistsError('Choose a new output directory; existing runs are preserved')
    destination.mkdir(parents=True)
    shutil.copy2(source/'LICENSE.txt', destination/'LICENSE.upstream.txt')
    records = []
    for name, (relative, steering, overrides) in CASES.items():
        if (relative.startswith('waqtel/')) != (group == 'waqtel'):
            continue
        original = source/'examples'/relative
        folder = destination/name
        folder.mkdir()
        # Preserve upstream source, inputs and references, excluding images/docs.
        for item in original.iterdir():
            if item.is_file():
                shutil.copy2(item, folder/item.name)
            elif item.name.startswith('user_fortran'):
                shutil.copytree(item, folder/item.name)
        hydro = cas_parser.parse((folder/steering).read_text())
        original_hydro = dict(hydro)
        module = 'waqtel' if 'WAQTEL STEERING FILE' in hydro else 'gaia'
        gaia_name = hydro[module.upper()+' STEERING FILE'].strip("'\"")
        if time_step is not None:
            if not math.isfinite(time_step) or time_step <= 0 or time_step > 72000 or 72000 % time_step or module != 'waqtel':
                raise ValueError('Time refinement is supported for WAQTEL with positive step')
            duration = float(hydro['TIME STEP'])*int(hydro['NUMBER OF TIME STEPS'])
            if duration % time_step:
                raise ValueError('Step must divide original duration')
            hydro['TIME STEP'] = str(time_step)
            hydro['NUMBER OF TIME STEPS'] = str(int(duration/time_step))
        if tracer_accuracy is not None:
            if not math.isfinite(tracer_accuracy) or tracer_accuracy <= 0:
                raise ValueError('Positive solver accuracy required')
            hydro['ACCURACY FOR DIFFUSION OF TRACERS'] = str(tracer_accuracy)
        if module == 'waqtel':
            hydro['GRAPHIC PRINTOUT PERIOD'] = str(int(72000/float(hydro['TIME STEP'])))
            if name == 'micropol_adsorption':
                hydro['INITIAL VALUES OF TRACERS'] = '1.;0.;1.;0.;0.'
            (folder/steering).write_text(cas_parser.generate(hydro))
        if overrides:
            gaia = cas_parser.parse((folder/gaia_name).read_text())
            gaia.update(overrides)
            (folder/gaia_name).write_text(cas_parser.generate(gaia))
        expected = []
        for cas in (hydro, cas_parser.parse((folder/gaia_name).read_text())):
            if 'RESULTS FILE' in cas:
                expected.append(cas['RESULTS FILE'].strip("'\""))
        if any((folder/p).exists() for p in expected):
            raise ValueError('Upstream directory contains a generated result; refuse ambiguous provenance')
        inputs = {str(p.relative_to(folder)): digest(p) for p in sorted(folder.rglob('*')) if p.is_file()}
        record = {'id': name, 'status': 'prepared_not_executed', 'source_example': relative,
                  'telemac_cas': steering, 'coupled_module': module, 'coupled_cas': gaia_name, 'overrides': overrides,
                  'hydro_overrides': {k: v for k, v in hydro.items() if original_hydro.get(k) != v},
                  'expected_results': expected, 'input_sha256': inputs,
                  'duration_s': float(hydro.get('DURATION', float(hydro.get('TIME STEP', 1))*float(hydro.get('NUMBER OF TIME STEPS', 0))))}
        records.append(record)
    manifest = {'status': 'prepared_not_executed', 'solver_commit': sha,
                'source': 'https://gitlab.pam-retd.fr/otm/telemac-mascaret',
                'data_kind': 'synthetic_upstream_benchmarks_not_Tapajos_measurements',
                'cases': records}
    (destination/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def inspect_balance(log):
    """Extract evidence only. Nestor budgets require explicit dredge/dump accounting."""
    number = r'([-+\d.]+(?:[EeDd][-+]?\d+)?)'
    patterns = {'water_relative': r'RELATIVE ERROR CUMULATED ON VOLUME:\s*'+number,
                'sediment_relative_initial_active_layer': r'RELATIVE ERROR TO INITIAL ACT LAYER MASS\s*=\s*'+number,
                'sediment_cumulated_lost_kg': r'CUMULATED LOST MASS\s*=\s*'+number}
    values = {key: [float(x.replace('D', 'E').replace('d', 'e')) for x in re.findall(pattern, log, re.I)]
              for key, pattern in patterns.items()}
    final = log.split('FINAL MASS-BALANCE OF SEDIMENTS:')[-1] if 'FINAL MASS-BALANCE OF SEDIMENTS:' in log else ''
    values['sediment_final_relative_reported'] = [float(x.replace('D', 'E').replace('d', 'e')) for x in re.findall(patterns['sediment_relative_initial_active_layer'], final, re.I)]
    return values


def run(destination, executable, selected=None):
    import numpy as np
    from backend.api import slf_io
    destination = Path(destination).resolve()
    manifest = json.loads((destination/'manifest.json').read_text())
    solver_source = os.environ.get('HOMETEL')
    if not solver_source:
        raise ValueError('Set HOMETEL to the compiled, pinned solver checkout')
    solver_sha = subprocess.check_output(['git', '-C', solver_source, 'rev-parse', 'HEAD'], text=True).strip()
    if solver_sha != manifest['solver_commit']:
        raise ValueError('Compiled solver checkout differs from prepared source revision')
    if selected and selected not in {r['id'] for r in manifest['cases']}:
        raise ValueError('Unknown case')
    for case in manifest['cases']:
        if selected and case['id'] != selected:
            continue
        folder = destination/case['id']
        evidence = folder/'execution.json'
        if evidence.exists() or any((folder/f).exists() for f in case['expected_results']):
            raise FileExistsError('Existing execution: prepare a new suite to repeat')
        for name, checksum in case['input_sha256'].items():
            if digest(folder/name) != checksum:
                raise ValueError('Input changed after preparation: '+name)
        with (folder/'solver-output.txt').open('w') as stream:
            process = subprocess.run([executable, case['telemac_cas'], '--ncsize=1'], cwd=folder,
                                     stdout=stream, stderr=subprocess.STDOUT)
        result = {'status': 'solver_failed', 'returncode': process.returncode, 'solver_commit': solver_sha,
                  'balance': inspect_balance((folder/'solver-output.txt').read_text(errors='replace'))}
        if process.returncode == 0:
            fields = []
            for name in case['expected_results']:
                output = slf_io.read(folder/name)
                hydro = cas_parser.parse((folder/case['telemac_cas']).read_text())
                cadence = int(hydro.get('GRAPHIC PRINTOUT PERIOD', 1))
                last_time = case['duration_s'] if 'DURATION' in hydro else (int(hydro['NUMBER OF TIME STEPS'])//cadence)*cadence*float(hydro['TIME STEP'])
                if not np.isfinite(output.values).all() or not np.isclose(output.times[-1], last_time):
                    raise ValueError('Nonfinite/incomplete solver result: '+name)
                fields.append({'file': name, 'sha256': digest(folder/name), 'final_time_s': float(output.times[-1])})
            result.update(status='executed_budget_review_required', results=fields)
        evidence.write_text(json.dumps(result, indent=2)+'\n')
        if process.returncode:
            raise RuntimeError('Solver failed; see '+str(folder/'solver-output.txt'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    a = sub.add_parser('prepare'); a.add_argument('--source', type=Path, required=True); a.add_argument('--group', choices=['gaia', 'waqtel'], default='gaia'); a.add_argument('--time-step', type=float); a.add_argument('--tracer-accuracy', type=float); a.add_argument('--out', type=Path, default=ROOT/'models/synthetic_sediment')
    a = sub.add_parser('run'); a.add_argument('--out', type=Path, default=ROOT/'models/synthetic_sediment'); a.add_argument('--executable', required=True); a.add_argument('--case', choices=CASES)
    a = p.parse_args()
    if a.action == 'prepare':
        print(json.dumps(prepare(a.source, a.out, a.group, a.time_step, a.tracer_accuracy), indent=2))
    else:
        run(a.out, a.executable, a.case)


if __name__ == '__main__':
    main()
