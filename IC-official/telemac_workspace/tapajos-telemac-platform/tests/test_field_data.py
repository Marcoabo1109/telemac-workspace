import json

import pytest

from backend.api.field_data import analyse_daily_csv
from scripts.phase3_data import ingest_ana_xml


def test_daily_series_reports_gaps(tmp_path):
    path = tmp_path / "series.csv"
    path.write_text(
        "date,value,consistency,unit\n"
        "2024-01-01,100,2,cm\n"
        "2024-01-03,110,2,cm\n"
    )
    report = analyse_daily_csv(path, "cm")
    assert report["records"] == 2
    assert report["missing_days"] == 1
    assert report["gaps"] == [
        {"start": "2024-01-02", "end": "2024-01-02", "days": 1}
    ]


def test_daily_series_rejects_duplicates(tmp_path):
    path = tmp_path / "series.csv"
    path.write_text(
        "date,value,consistency,unit\n"
        "2024-01-01,100,1,cm\n"
        "2024-01-01,101,2,cm\n"
    )
    with pytest.raises(ValueError, match="duplicate"):
        analyse_daily_csv(path, "cm")


def test_phase3_ingest_preserves_raw_and_manifest(tmp_path):
    source = tmp_path / "source.xml"
    source.write_text(
        "<Data><Serie><DataHora>2024-01-01</DataHora>"
        "<NivelConsistencia>2</NivelConsistencia>"
        "<Cota01>10</Cota01><Cota03>12</Cota03>"
        "</Serie></Data>"
    )
    result = ingest_ana_xml(
        source,
        tmp_path / "out",
        kind="H",
        station="17730000",
        source_url="https://example.invalid/official-fixture",
        retrieved_on="2026-09-18",
    )
    manifest = json.loads(open(result["manifest_path"]).read())
    assert manifest["quality"]["records"] == 2
    assert manifest["quality"]["missing_days"] == 1
    assert manifest["transformation"]["gap_policy"].startswith("No interpolation")
