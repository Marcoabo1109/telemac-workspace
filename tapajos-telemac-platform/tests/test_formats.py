from pathlib import Path
import numpy as np
import pytest
from backend.api import cas_parser as cas, slf_io as slf, qsl_io as qsl, cli_io as cli
from backend.api.telemac_runner import prepare, safe_name

P = Path(__file__).resolve().parents[1] / "data/culm"


def test_real_culm_and_quotes():
    p = cas.parse((P / "t2d_culm.cas").read_text())
    assert p["SOLVER"] == "1"
    assert len(p) > 30
    assert cas.parse(cas.generate(p)) == p
    assert (
        cas.parse("TITLE = 'a: b / c' / comment\nTIME STEP=2. NUMBER OF TIME STEPS:10")[
            "TITLE"
        ]
        == "'a: b / c'"
    )
    assert cas.parse("TITLE='a '' quote'\nTIME STEP=2")["TIME STEP"] == "2"


def test_validation():
    for p in [
        {"TIME STEP": 0},
        {"SOLVER": 5},
        {"NUMBER OF TIME STEPS": 1.2},
        {"IMPLICITATION FOR DEPTH": 2},
        {"FRICTION COEFFICIENT": -1},
        {"VELOCITY DIFFUSIVITY": "nan"},
    ]:
        with pytest.raises(ValueError):
            cas.validate(p)


@pytest.mark.parametrize("endian", [">", "<"])
@pytest.mark.parametrize("precision", [4, 8])
def test_serafin_roundtrip(endian, precision):
    m = slf.read(P / "geo_culm.slf")
    m.endian = endian
    m.precision = precision
    n = slf.read(slf.write(m))
    assert len(n.x) == 1130
    assert len(n.ikle) == 2019
    assert np.array_equal(m.ikle, n.ikle)
    assert np.allclose(m.values, n.values)
    m.values[0, 0, 0] = 12.75
    assert slf.read(slf.write(m)).values[0, 0, 0] == 12.75


def test_corruption_rejected():
    blob = (P / "geo_culm.slf").read_bytes()
    with pytest.raises(ValueError):
        slf.read(blob[:-3])
    with pytest.raises(ValueError):
        slf.read(blob[:84] + b"BAD!" + blob[88:])


def test_qsl_real_and_invalid():
    s = qsl.parse((P / "t2d_culm.qsl").read_text())
    assert s["columns"] == ["T", "Q(1)", "SL(2)"]
    assert qsl.parse(qsl.generate(**s)) == s
    for rows in [[[0, 1], [0, 2]], [[1, 1], [0, 2]], [[0, 1], [1, float("nan")]]]:
        with pytest.raises(ValueError):
            qsl.generate(["T", "Q(1)"], rows)
    with pytest.raises(ValueError):
        qsl.validate(["T", "Q(1)"], [[0, 1], [100, 1]], max_gap=10)


def test_cli_real():
    rows = cli.parse((P / "geo_culm.cli").read_text())
    assert cli.parse(cli.generate(rows)) == rows


def test_job_rejects_unsafe_and_missing():
    for name in ["../foo", "/tmp/x", "x;whoami", "a/b"]:
        with pytest.raises(ValueError):
            safe_name(name)
    with pytest.raises(ValueError):
        prepare({"FORTRAN FILE": "hack.f"}, {})
    with pytest.raises(ValueError):
        prepare({"GEOMETRY FILE": "missing.slf"}, {})


def test_cli_friction_and_tracer_column_types():
    row = "2 2 2 0 0 0 0.125 2 0 0 0 1 1"
    parsed = cli.parse(row)
    assert parsed[0][6] == 0.125
    with pytest.raises(ValueError):
        cli.parse("2 2 2 0 0 0 0 2.5 0 0 0 1 1")
