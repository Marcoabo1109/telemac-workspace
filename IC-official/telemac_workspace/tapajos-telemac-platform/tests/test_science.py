import numpy as np
import pandas as pd
import pytest
from scripts.tapajos_analysis import lag_correlation
from scripts.convert_to_telemac import series_to_qsl
from scripts.mesh_generator import generate
from scripts.postprocess import metrics
from backend.api.slf_io import read
from pathlib import Path


def test_known_lag_with_gap():
    rng = np.random.default_rng(3)
    v = rng.normal(size=140)
    dates = pd.date_range("2000-01-01", periods=len(v))
    a = pd.Series(v, index=dates)
    b = pd.Series(v, index=dates + pd.Timedelta(days=4))
    b.iloc[20:25] = np.nan
    r = lag_correlation(a, b)
    assert r["best"]["lag_days"] == 4
    assert r["best"]["correlation"] == pytest.approx(1)
    with pytest.raises(ValueError):
        lag_correlation(a * 0, b * 0)


def test_stage_datum_and_gap(tmp_path):
    p = tmp_path / "stage.csv"
    p.write_text("date,value\n2020-01-01,100\n2020-01-02,150\n")
    with pytest.raises(ValueError):
        series_to_qsl(p, kind="SL", unit="cm")
    out = series_to_qsl(p, kind="SL", unit="cm", datum_offset=10)
    assert "0 11" in out
    assert "86400 11.5" in out


def test_mesh_polygon_area_and_cli(tmp_path):
    from shapely.geometry import Polygon
    from scripts.mesh_generator import project

    g = {
        "type": "Polygon",
        "coordinates": [
            [[-56, -4.4], [-55.99, -4.4], [-55.99, -4.39], [-56, -4.39], [-56, -4.4]]
        ],
    }
    meta = generate(g, tmp_path, 200, 400, 200)
    m = read(tmp_path / "mesh.slf")
    poly, _ = project(g)
    area = sum(Polygon(np.column_stack([m.x[t], m.y[t]])).area for t in m.ikle)
    assert area == pytest.approx(poly.area, rel=0.001)
    assert meta["calibrated"] is False
    assert (m.ipobo > 0).sum() > 3
    with pytest.raises(ValueError):
        generate(
            {"type": "LineString", "coordinates": [[-56, -4.4], [-55, -4]]}, tmp_path
        )


def test_diagnostics():
    m = read(Path(__file__).resolve().parents[1] / "data/culm/ini_culm.slf")
    d = metrics(m)
    assert np.isfinite(d["froude"]).all()
    assert np.min(d["bed_shear_pa"]) >= 0
    assert np.allclose(metrics(m, 4, 1 / 30)["bed_shear_pa"], d["bed_shear_pa"])
