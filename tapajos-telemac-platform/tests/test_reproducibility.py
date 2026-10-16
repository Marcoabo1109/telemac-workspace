import json
from pathlib import Path

import numpy as np

from backend.api import slf_io
from scripts import reproducibility as rep


def test_reference_manifest_is_stable():
    manifest = rep.reference_manifest()
    assert manifest["id"] == "culm-20x2s-v1"
    assert manifest["steps"] == 20
    assert manifest["final_time_seconds"] == 40.0
    assert len(manifest["files"]) == 5
    assert all(len(item["sha256"]) == 64 for item in manifest["files"])
    assert (
        manifest["combined_sha256"]
        == "a0591cbdbb20b7ed9493b980ec3d4dd94e7ae55c58135266b4adf34add42eaed"
    )
    recorded = json.loads((rep.ROOT / "docs/reproducibility-case.json").read_text())
    assert manifest == recorded


def test_environment_inventory_has_required_sections():
    inventory = rep.collect_environment()
    assert inventory["schema_version"] == 1
    assert inventory["host"]["machine"]
    assert inventory["runtime"]["python"]
    assert inventory["project"]["git_commit"]
    assert inventory["reference_case"]["combined_sha256"]


def test_compare_results_detects_difference(tmp_path):
    source = rep.ROOT / "data" / "culm" / "geo_culm.slf"
    first = slf_io.read(source)
    second = slf_io.read(source)
    second.values = np.array(second.values, copy=True)
    second.values[0, 0, 0] += 0.5
    left = tmp_path / "left.slf"
    right = tmp_path / "right.slf"
    left.write_bytes(slf_io.write(first))
    right.write_bytes(slf_io.write(second))
    tolerances = tmp_path / "tolerances.json"
    tolerances.write_text(
        json.dumps({"default_max_abs": 0.1, "variables": {}})
    )
    report = rep.compare_results(left, right, tolerances)
    assert report["status"] == "failed"
    assert any("exceeds tolerance" in problem for problem in report["problems"])


def test_compare_results_accepts_identical_files(tmp_path):
    source = rep.ROOT / "data" / "culm" / "geo_culm.slf"
    tolerances = tmp_path / "tolerances.json"
    tolerances.write_text(json.dumps({"default_max_abs": 0.0, "variables": {}}))
    report = rep.compare_results(source, source, tolerances)
    assert report["status"] == "passed"
    assert report["problems"] == []
