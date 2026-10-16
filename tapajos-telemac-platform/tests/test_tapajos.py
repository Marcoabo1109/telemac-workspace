import json
from pathlib import Path
import numpy as np
from fastapi.testclient import TestClient
from backend.main import app
from backend.api import slf_io, cli_io, qsl_io, cas_parser

ROOT = Path(__file__).resolve().parents[1]


def test_tapajos_case_has_two_open_boundaries_and_positive_depth():
    p = ROOT / "models/tapajos_trecho1"
    m = slf_io.read(p / "mesh.slf")
    rows = cli_io.parse((p / "mesh.cli").read_text())
    codes = [r[0] for r in rows]
    starts = [
        codes[i] for i in range(len(codes)) if codes[i] != 2 and codes[i - 1] == 2
    ]
    assert starts == [
        4,
        5,
    ]  # CLI order; liquid IDs follow FRONT2 southwestern start, not this order
    assert {r[11] for r in rows} == set(np.flatnonzero(m.ipobo) + 1)
    assert all(m.ipobo[r[11] - 1] == r[12] for r in rows)
    q = qsl_io.parse((p / "tapajos.qsl").read_text())
    assert q["columns"] == ["T", "Q(2)", "SL(1)"]
    assert np.min(3.71 - m.values[0, 0]) > 3.5
    assert m.precision == 8
    params = cas_parser.parse((p / "tapajos.cas").read_text())
    assert "PREVIOUS COMPUTATION FILE" not in params
    assert params["MATRIX-VECTOR PRODUCT"] == "1"


def test_tapajos_source_and_api_label_assumptions():
    d = json.loads(
        (ROOT / "data/tapajos/stations/itaituba_sgb_monthly_levels.json").read_text()
    )
    assert d["station_code"] == "17730000"
    assert d["rows"][8][2] == 371
    assert "not_daily" in d["kind"]
    c = TestClient(app)
    r = c.get("/api/example?case_id=tapajos")
    assert r.status_code == 200
    assert r.json()["assumptions"]["status"] == "exploratory_uncalibrated"
    assert c.get("/api/example?case_id=invalid").status_code == 404
    assert c.get("/api/example/mesh.slf?case_id=tapajos").status_code == 200
