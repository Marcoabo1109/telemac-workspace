import copy

from backend.api import data_catalog


def test_catalog_is_valid_and_truthful():
    catalog = data_catalog.load()
    result = data_catalog.report(catalog)
    assert result["valid"] is True
    assert result["counts"] == {
        "available": 4,
        "derived": 4,
        "missing": 7,
        "total": 15,
    }
    gates = {gate["id"]: gate for gate in result["gates"]}
    assert gates["exploratory-demo"]["status"] == "ready"
    assert gates["hydrodynamic-calibration"]["status"] == "blocked"
    assert gates["sediment-transport"]["status"] == "blocked"
    assert gates["metals-assessment"]["status"] == "blocked"
    stage = next(item for item in catalog["datasets"] if item["id"] == "daily-stage")
    assert stage["status"] == "available"
    assert stage["quality"]["records"] == 14361
    discharge = next(
        item for item in catalog["datasets"] if item["id"] == "daily-discharge"
    )
    assert discharge["status"] == "available"
    assert discharge["station"]["code"] == "17650002"
    assert discharge["quality"]["records"] == 5420


def test_catalog_detects_hash_mismatch():
    catalog = copy.deepcopy(data_catalog.load())
    catalog["datasets"][0]["sha256"] = "0" * 64
    errors = data_catalog.validate(catalog)
    assert any("sha256 mismatch" in error for error in errors)


def test_missing_dataset_cannot_claim_file():
    catalog = copy.deepcopy(data_catalog.load())
    missing = next(item for item in catalog["datasets"] if item["status"] == "missing")
    missing["local_path"] = "invented.csv"
    errors = data_catalog.validate(catalog)
    assert any("missing dataset cannot have a local file" in error for error in errors)
