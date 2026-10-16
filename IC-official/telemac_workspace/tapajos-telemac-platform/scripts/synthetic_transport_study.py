"""Synthetic examples, time sensitivity, and illustrative dredging constraints."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
from backend.api.synthetic_sediment import Tank, simulate

ROOT = Path(__file__).resolve().parents[1]


def study(config):
    base = Tank(**config['parameters'])
    duration = config['duration_s']
    scenarios = {}
    for name, overrides in config['scenarios'].items():
        runs = [simulate(replace(base, **overrides), duration, dt) for dt in config['time_steps_s']]
        for r in runs:
            if any(abs(r[k]['relative_residual']) > 1e-10 for k in ('sediment_kg', 'metal_kg')):
                raise ValueError('Mass budget failed: '+name)
        scenarios[name] = runs
    candidates = []
    limits = config['illustrative_constraints']
    for rate in config['dredge_rates_kg_s']:
        r = simulate(replace(base, dredge_kg_s=rate), duration, min(config['time_steps_s']))
        r.pop('history')
        r['feasible_illustrative'] = (r['sediment_kg']['removed'] >= limits['min_removed_kg'] and
                                     r['dissolved_peak_kg_m3'] <= limits['max_dissolved_kg_m3'] and
                                     r['illustrative_cost'] <= limits['max_cost'])
        candidates.append(r)
    eligible = [r for r in candidates if r['feasible_illustrative']]
    for r in candidates:
        r['pareto_illustrative'] = r['feasible_illustrative'] and not any(
            x['illustrative_cost'] <= r['illustrative_cost'] and x['dissolved_exposure_kg_s_m3'] <= r['dissolved_exposure_kg_s_m3'] and
            (x['illustrative_cost'] < r['illustrative_cost'] or x['dissolved_exposure_kg_s_m3'] < r['dissolved_exposure_kg_s_m3']) for x in eligible)
    sensitivity = {}
    for name, runs in scenarios.items():
        fine = min(runs, key=lambda r: r['dt_s'])
        sensitivity[name] = [{'dt_s': r['dt_s'], 'absolute_difference_from_finest': {
            key: abs(r['history'][-1][key]-fine['history'][-1][key])
            for key in ('suspended_kg', 'bed_kg', 'dissolved_metal_kg', 'suspended_metal_kg', 'bed_metal_kg')}} for r in runs]
    return {'status': 'synthetic_component_examples', 'configuration': config, 'scenarios': scenarios,
            'time_sensitivity': sensitivity, 'dredging_candidates': candidates,
            'limitations': ['No spatial TELEMAC-GAIA-metal coupling.', 'All values are assumptions, no measured metal species.',
                            'Costs use arbitrary monetary units; thresholds are test values, not legal criteria.',
                            'Positive split updates conserve mass but require step convergence.']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--config', type=Path, default=ROOT/'models/synthetic_transport/scenarios.json'); p.add_argument('--out', type=Path, default=ROOT/'reports/synthetic_transport/study.json'); a = p.parse_args()
    result = study(json.loads(a.config.read_text()))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2)+'\n')
    print(a.out)
