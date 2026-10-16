import math
from dataclasses import replace
import json
from pathlib import Path
import pytest
from backend.api.synthetic_sediment import Tank, simulate
from scripts.sediment_benchmarks import inspect_balance
from scripts.synthetic_transport_study import study


def test_kinetic_partition_analytic():
    p = Tank(settling_m_s=0, partheniades_kg_m2_s=0)
    r = simulate(p, 100, 13)
    total = p.volume_m3*(p.initial_dissolved_kg_m3+p.initial_ssc_kg_m3*p.initial_suspended_metal_kg_kg)
    equilibrium = total/(1+p.kd_m3_kg*p.initial_ssc_kg_m3)
    expected = equilibrium+(p.initial_dissolved_kg_m3*p.volume_m3-equilibrium)*math.exp(-p.desorption_s_1*(1+p.kd_m3_kg*p.initial_ssc_kg_m3)*100)
    assert r['history'][-1]['dissolved_metal_kg'] == pytest.approx(expected, rel=1e-12)


def test_settling_and_particle_metal_exact():
    p = Tank(partheniades_kg_m2_s=0, desorption_s_1=0)
    r = simulate(p, 301, 17)
    fraction = math.exp(-p.settling_m_s*p.area_m2/p.volume_m3*(1-p.shear_pa/p.deposition_threshold_pa)*301)
    expected = p.initial_ssc_kg_m3*p.volume_m3*fraction
    assert r['history'][-1]['suspended_kg'] == pytest.approx(expected)
    assert r['history'][-1]['suspended_metal_kg'] == pytest.approx(expected*p.initial_suspended_metal_kg_kg)


def test_flow_exact_including_ledger():
    p = Tank(flow_m3_s=2, settling_m_s=0, partheniades_kg_m2_s=0, desorption_s_1=0, inflow_ssc_kg_m3=.02)
    r = simulate(p, 101, 19)
    expected = p.volume_m3*(p.inflow_ssc_kg_m3+(p.initial_ssc_kg_m3-p.inflow_ssc_kg_m3)*math.exp(-p.flow_m3_s/p.volume_m3*101))
    assert r['history'][-1]['suspended_kg'] == pytest.approx(expected)
    assert abs(r['sediment_kg']['relative_residual']) < 1e-12


def test_dredging_window_and_stock_limit():
    p = Tank(settling_m_s=0, desorption_s_1=0, partheniades_kg_m2_s=0, dredge_kg_s=2, dredge_start_s=17, dredge_end_s=43)
    r = simulate(p, 80, 30)
    assert r['sediment_kg']['removed'] == pytest.approx(2*26*(1-p.resuspension_fraction))
    empty = simulate(replace(p, dredge_kg_s=1e9), 80, 30)
    assert empty['sediment_kg']['removed'] == pytest.approx(p.initial_bed_kg*(1-p.resuspension_fraction))
    assert empty['history'][-1]['bed_kg'] == 0


@pytest.mark.parametrize('p', [Tank(), Tank(shear_pa=2), Tank(dredge_kg_s=1000), Tank(flow_m3_s=3, dredge_kg_s=1)])
def test_complete_ledgers_and_positivity(p):
    r = simulate(p, 3600, 17)
    for key in ('sediment_kg', 'metal_kg'):
        assert abs(r[key]['relative_residual']) < 1e-12
    assert all(value >= -1e-14 for row in r['history'] for value in row.values())


def test_timestep_refinement_reduces_error():
    p = Tank(dredge_kg_s=2)
    reference = simulate(p, 3600, .5)['history'][-1]['dissolved_metal_kg']
    errors = [abs(simulate(p, 3600, dt)['history'][-1]['dissolved_metal_kg']-reference) for dt in (20, 10, 5)]
    assert errors[2] < errors[1] < errors[0]


@pytest.mark.parametrize('p', [Tank(kd_m3_kg=-1), Tank(volume_m3=0), Tank(resuspension_fraction=2), Tank(dredge_end_s=1), Tank(shear_pa=float('nan'))])
def test_reject_invalid(p):
    with pytest.raises(ValueError): simulate(p)


def test_log_evidence_never_invents_missing_budget():
    assert inspect_balance('solver failed')['water_relative'] == []
    r = inspect_balance('RELATIVE ERROR CUMULATED ON VOLUME: -1.2D-08\nRELATIVE ERROR TO INITIAL ACT LAYER MASS = 3.0E-9\nCUMULATED LOST MASS = -0.5')
    assert r['water_relative'] == [-1.2e-8]
    assert r['sediment_cumulated_lost_kg'] == [-.5]


def test_synthetic_study_constraints():
    path = Path(__file__).resolve().parents[1]/'models/synthetic_transport/scenarios.json'
    r = study(json.loads(path.read_text()))
    assert len(r['scenarios']) == 6
    assert not r['dredging_candidates'][0]['feasible_illustrative']
    assert any(x['feasible_illustrative'] for x in r['dredging_candidates'])


def test_mobilization_cost_even_if_all_material_is_resuspended():
    p = Tank(dredge_kg_s=1, resuspension_fraction=1)
    r = simulate(p, 700, 10)
    assert r['sediment_kg']['removed'] == 0
    assert r['gross_dredged_sediment_kg'] == 100
    assert r['illustrative_cost'] == p.mobilization_cost


def test_step_balance_is_not_a_final_cumulative_balance():
    step = 'RELATIVE ERROR TO INITIAL ACT LAYER MASS = 1e-15'
    assert inspect_balance(step)['sediment_final_relative_reported'] == []
    assert inspect_balance(step+'\nFINAL MASS-BALANCE OF SEDIMENTS:\n'+step)['sediment_final_relative_reported'] == [1e-15]
