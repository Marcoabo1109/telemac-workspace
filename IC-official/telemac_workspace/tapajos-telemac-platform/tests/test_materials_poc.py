import json
from pathlib import Path
import numpy as np
from fastapi.testclient import TestClient
from backend.main import app
from backend.api import slf_io

ROOT=Path(__file__).resolve().parents[1]


def test_executed_materials_match_public_api():
    response=TestClient(app).get('/api/poc/materials')
    assert response.status_code==200
    data=response.json()
    result=slf_io.read(ROOT/'models/tapajos_materials/materials.slf')
    assert data['times']==result.times.tolist()
    assert len(data['times'])==61 and data['times'][-1]==3600
    c=np.array(data['concentrations'])
    assert c.shape==(61,3,len(data['x']))
    assert np.isfinite(c).all() and c.min()>=0 and c.max()<=1
    np.testing.assert_allclose(c[0,0],c[0,1])
    np.testing.assert_allclose(c[0,0],c[0,2])
    for i,name in enumerate(['CONSERVATIVE','POLLUTANT','SEDIMENT']):
        np.testing.assert_allclose(c[-1,i],result.field(name,-1),atol=5.1e-7)
    # Reactions must yield genuinely different executed fields, not relabeling.
    assert c[-1,1].sum()<c[-1,2].sum()<c[-1,0].sum()
    assert data['metadata']['solver_commit']=='d1bff193746fd76425d7715a6e4d20d42eb8877e'
    assert TestClient(app).get('/api/poc/materials/download').content==response.content


def test_solver_material_balances():
    import re
    log=(ROOT/'models/tapajos_materials/solver-output.txt').read_text()
    for name in ['CONSERVATIVE','POLLUTANT','SEDIMENT']:
        match=re.search(r'FINAL BALANCE OF '+name+r'.*?RELATIVE ERROR\s*:\s*([\d.E+-]+)',log,re.S)
        assert match is not None
        assert abs(float(match[1]))<1e-3
