import numpy as np
import pytest
from backend.api.research_transport import Parameters, simulate, pareto_candidates
from backend.api.calibration_metrics import metrics, gauge_to_imbituba, require_calibration_evidence
from backend.api import slf_io, cli_io
from scripts.numerical_study import ROOT, refine, nodal_areas, balance


def test_refinement_preserves_domain_and_linear_bed():
    m=slf_io.read(ROOT/'models/tapajos_trecho1/mesh.slf')
    rows=cli_io.parse((ROOT/'models/tapajos_trecho1/mesh.cli').read_text())
    m.values[0,0]=.01*m.x+.02*m.y
    refined, boundary=refine(m,rows)
    assert len(refined.ikle)==4*len(m.ikle)
    assert nodal_areas(refined).sum()==pytest.approx(nodal_areas(m).sum())
    np.testing.assert_allclose(refined.values[0,0], .01*refined.x+.02*refined.y)
    assert len(boundary)==2*len(rows)
    assert len(set(r[11] for r in boundary))==len(boundary)


@pytest.mark.parametrize('p',[Parameters(),Parameters(discharge_m3_s=0),Parameters(dredge_kg_s=1e7,erosion_kg_s=10)])
def test_mass_and_positivity(p):
    r=simulate(p,duration_s=3600)
    for key in ['sediment_kg','metal_kg']:
        ledger=r[key]
        assert abs(ledger['balance_residual']) < 1e-12*(ledger['initial_total']+ledger['inflow'])
        assert all(v>=0 for k,v in ledger.items() if k!='balance_residual')


def test_closed_settling_analytical():
    p=Parameters(discharge_m3_s=0)
    result=simulate(p,3600,60)
    expected=p.suspended_in_kg_m3*p.volume_m3*np.exp(-p.settling_m_s*p.area_m2/p.volume_m3*3600)
    assert result['sediment_kg']['suspended']==pytest.approx(expected)


def test_scores_and_datum_guard():
    assert metrics([1,2,3],[1,2,3])['nse']==1
    assert metrics([1,2,3],[2,3,4])['bias']==1
    assert metrics([2,2,2],[2,2,2])['nse'] is None
    with pytest.raises(ValueError):gauge_to_imbituba([539])
    assert gauge_to_imbituba([539],epoch_verified=True)[0]==pytest.approx(8.362)
    with pytest.raises(ValueError):
        require_calibration_evidence(bathymetry_verified=False,datum_verified=False,independent_in_domain_observations=False,held_out_period=True)


def test_hypothetical_pareto_and_invalid_inputs():
    assert any(x['pareto'] for x in pareto_candidates(duration_s=600))
    with pytest.raises(ValueError):simulate(Parameters(resuspension_fraction=2))
