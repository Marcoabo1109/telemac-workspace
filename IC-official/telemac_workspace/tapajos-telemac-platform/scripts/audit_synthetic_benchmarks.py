"""Audit completed synthetic cases; missing evidence is never a pass."""
import json
from pathlib import Path
import numpy as np
from backend.api import slf_io
from scripts.sediment_benchmarks import inspect_balance, ROOT

REFERENCES = {
    'mud_exchange': [('gai_mud_cons-t2d.slf', 'gai_ref_mud_cons-t2d.slf', 1e-7), ('r2d_mud_cons-t2d.slf', 'f2d_mud_cons-t2d.slf', 1e-7)],
    'sand_bedload': [('gai_flume_bc.slf', 'gai_ref_flume_bc.slf', 1e-6)],
    'sand_diagnostic': [('gai_flume_bc.slf', 'gai_ref_flume_bc.slf', 1e-6), ('gai_flume_bc.slf', '../../synthetic_sediment/sand_bedload/gai_flume_bc.slf', 0.), ('r2d_flume_bc.slf', '../../synthetic_sediment/sand_bedload/r2d_flume_bc.slf', 0.)],
    'nestor_dig': [('gai_nestor1.slf', 'gai_ref_nestor1.slf', 1e-6), ('r2d_nestor1.slf', 't2d_ref_nestor1.slf', 1e-6)],
    'nestor_dump': [('gai_nestor2.slf', 'gai_ref_nestor2.slf', 1e-6), ('r2d_nestor2.slf', 't2d_ref_nestor2.slf', 1e-6)],
    'nestor_dig_dump': [('gai_nestor3.slf', 'gai_ref_nestor3.slf', 1e-3), ('r2d_nestor3.slf', 't2d_ref_nestor3_gai.slf', 1e-3)],
}


def weights(m):
    x, y = m.x[m.ikle], m.y[m.ikle]
    a = np.abs((x[:, 1]-x[:, 0])*(y[:, 2]-y[:, 0])-(x[:, 2]-x[:, 0])*(y[:, 1]-y[:, 0]))/6
    w = np.zeros(len(m.x))
    for i in range(3): np.add.at(w, m.ikle[:, i], a)
    return w


def compare(actual, reference, tolerance):
    a, b = slf_io.read(actual), slf_io.read(reference)
    if a.variables != b.variables or not np.array_equal(a.ikle, b.ikle) or not np.allclose(a.x, b.x) or not np.allclose(a.y, b.y):
        raise ValueError('Reference layout differs')
    if not np.isclose(a.times[-1], b.times[-1]):
        raise ValueError('Reference time differs')
    errors = np.max(np.abs(a.values[-1]-b.values[-1]), axis=1)
    exact_series = bool(np.array_equal(a.times, b.times) and np.array_equal(a.values, b.values)) if tolerance == 0 else None
    return {'reference': reference.name, 'tolerance_absolute': tolerance, 'exact_full_series': exact_series,
            'max_abs_by_variable': {v[0]: float(e) for v, e in zip(a.variables, errors)},
            'passed': bool(np.all(errors <= tolerance) and (exact_series is not False))}


def audit_gaia(folder):
    output = []
    for c in json.loads((folder/'manifest.json').read_text())['cases']:
        case = folder/c['id']
        if not (case/'execution.json').exists():
            output.append({'id': c['id'], 'status': 'not_executed'}); continue
        execution = json.loads((case/'execution.json').read_text())
        if execution['returncode']:
            output.append({'id': c['id'], 'status': 'solver_failed'}); continue
        evidence = inspect_balance((case/'solver-output.txt').read_text(errors='replace'))
        water = evidence['water_relative']; sediment = evidence['sediment_final_relative_reported']
        budget_ok = bool(water and sediment and abs(water[-1]) <= 1e-6 and max(abs(x) for x in sediment) <= 1e-6)
        refs = [compare(case/a, case/b, tol) for a, b, tol in REFERENCES.get(c['id'], [])]
        hydro = slf_io.read(case/c['expected_results'][0])
        min_depth = float(min(hydro.field('WATER DEPTH', i).min() for i in range(len(hydro.times))))
        sediment_names = [name for name, unit in hydro.variables if name.startswith(('COH SEDIMENT', 'NCO SEDIMENT'))]
        min_concentration = min((float(hydro.field(name, i).min()) for name in sediment_names for i in range(len(hydro.times))), default=None)
        positivity_ok = min_depth >= -1e-8 and (min_concentration is None or min_concentration >= -1e-8)
        output.append({'id': c['id'], 'budget_passed': budget_ok,
                       'water_relative_final': water[-1] if water else None,
                       'sediment_relative_initial_active_layer_final': sediment[-1] if sediment else None,
                       'cumulated_lost_kg_final': evidence['sediment_cumulated_lost_kg'][-1] if evidence['sediment_cumulated_lost_kg'] else None,
                       'references': refs, 'min_depth_recorded_m': min_depth, 'min_suspended_concentration_recorded': min_concentration,
                       'positivity_recorded_frames_passed': positivity_ok, 'status': 'checks_passed' if budget_ok and positivity_ok and all(r['passed'] for r in refs) else 'review_required'})
    return output


def audit_micropol(folder):
    rows = []
    for c in json.loads((folder/'manifest.json').read_text())['cases']:
        p = folder/c['id']; execution = p/'execution.json'
        if not execution.exists():
            rows.append({'id': c['id'], 'status': 'not_executed'}); continue
        m = slf_io.read(p/'r2d_waq2d_micropol.slf'); w = weights(m)
        inventories = []
        for i, t in enumerate(m.times):
            h = m.field('WATER DEPTH', i)
            # Bed variables are AREAL inventories, despite inherited mg/l labels.
            sediment = w@(h*m.field('SUSPENDED LOAD', i)+m.field('BED SEDIMENTS', i))
            pollutant = w@(h*(m.field('MICRO POLLUTANT', i)+m.field('ABS. SUSP. LOAD.', i))+m.field('ABSORB. BED SED.', i))
            inventories.append([float(t), float(sediment), float(pollutant)])
        inventory = np.array(inventories)
        drift = np.max(np.abs(inventory[:, 1:]-inventory[0, 1:])/np.maximum(np.abs(inventory[0, 1:]), 1e-30), axis=0)
        minimum = float(m.values[:, 5:].min())
        r = {'id': c['id'], 'inventories': inventories, 'sediment_relative_drift': float(drift[0]),
             'pollutant_relative_drift': float(drift[1]), 'minimum_scalar': minimum,
             'quantity_convention': 'Official benchmark quantity; no measured metal concentration. Bed terms integrated by area, water terms by volume.'}
        analytic_ok = True
        if c['id'] in ('micropol_adsorption', 'micropol_desorption'):
            # Official defaults: Kd=1, SSC=1, k_des=2.5e-7 s^-1.
            initial_d = 1. if c['id'] == 'micropol_adsorption' else 0.
            analytic = .5+(initial_d-.5)*np.exp(-5e-7*m.times)
            observed = np.array([np.mean(m.field('MICRO POLLUTANT', i)) for i in range(len(m.times))])
            r['max_abs_analytic_error'] = float(np.max(np.abs(observed-analytic)))
            analytic_ok = r['max_abs_analytic_error'] < 1e-3
        r['status'] = 'checks_passed' if np.max(drift) < 1e-6 and minimum >= -1e-8 and analytic_ok else 'review_required'
        rows.append(r)
    return rows


def main():
    result = {'criteria': {'relative_budget': 1e-6, 'micropol_analytic_absolute': 1e-3},
              'gaia': audit_gaia(ROOT/'models/synthetic_sediment'),
              'sand_final_budget': audit_gaia(ROOT/'models/synthetic_sand_final_budget'),
              'sand_fixed': audit_gaia(ROOT/'models/synthetic_sand_fixed'),
              'sand_diagnostic': audit_gaia(ROOT/'models/synthetic_sand_diagnostic'),
              'micropol': audit_micropol(ROOT/'models/synthetic_micropollutant'),
              'micropol_dt360': audit_micropol(ROOT/'models/synthetic_micropollutant_dt360'),
              'micropol_dt360_tight': audit_micropol(ROOT/'models/synthetic_micropollutant_dt360_tight'),
              'scope': 'Synthetic benchmarks; not field calibration, full convergence, or integrated GAIA-metal chemistry.'}
    out = ROOT/'reports/synthetic_transport/solver_audit.json'
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: [(r['id'], r['status']) for r in result[k]] for k in ('gaia', 'sand_final_budget', 'sand_fixed', 'sand_diagnostic', 'micropol', 'micropol_dt360', 'micropol_dt360_tight')}, indent=2))


if __name__ == '__main__': main()
