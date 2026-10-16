"""Validated inventory and scientific readiness gates for Tapajós data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from .field_data import analyse_daily_csv, phase3_report


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "data" / "tapajos" / "catalog.json"
STATUSES = {"available", "derived", "missing"}
FITNESS = {"context_only", "exploration_only", "required"}
CATEGORIES = {
    "geometry",
    "stage",
    "flow",
    "bathymetry",
    "boundary_series",
    "vertical_datum",
    "sediment",
    "metals",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path = CATALOG_PATH) -> dict:
    return json.loads(path.read_text())


def _error(errors: list[str], dataset_id: str, message: str) -> None:
    errors.append(f"{dataset_id}: {message}")


def _catalog_file(
    errors: list[str], dataset_id: str, relative: str | None, root: Path
) -> Path | None:
    if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        _error(errors, dataset_id, "safe local_path is required")
        return None
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        _error(errors, dataset_id, "local_path escapes project root")
        return None
    if not path.is_file():
        _error(errors, dataset_id, f"file not found: {relative}")
        return None
    return path


def validate(catalog: dict, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if catalog.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    datasets = catalog.get("datasets")
    gates = catalog.get("gates")
    if not isinstance(datasets, list) or not datasets:
        return errors + ["datasets must be a non-empty list"]
    if not isinstance(gates, list) or not gates:
        errors.append("gates must be a non-empty list")
        gates = []

    ids: set[str] = set()
    by_id: dict[str, dict] = {}
    for dataset in datasets:
        dataset_id = dataset.get("id", "<missing-id>")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", dataset_id):
            _error(errors, dataset_id, "invalid id")
        if dataset_id in ids:
            _error(errors, dataset_id, "duplicate id")
        ids.add(dataset_id)
        by_id[dataset_id] = dataset
        if not dataset.get("title"):
            _error(errors, dataset_id, "title is required")
        if dataset.get("category") not in CATEGORIES:
            _error(errors, dataset_id, "invalid category")
        status = dataset.get("status")
        if status not in STATUSES:
            _error(errors, dataset_id, "invalid status")
        if dataset.get("fitness") not in FITNESS:
            _error(errors, dataset_id, "invalid fitness")
        if not isinstance(dataset.get("variables"), list):
            _error(errors, dataset_id, "variables must be a list")
        if not dataset.get("limitations"):
            _error(errors, dataset_id, "at least one limitation is required")
        if status == "missing":
            if dataset.get("local_path") or dataset.get("sha256"):
                _error(errors, dataset_id, "missing dataset cannot have a local file")
            continue

        relative = dataset.get("local_path")
        path = _catalog_file(errors, dataset_id, relative, root)
        if not re.fullmatch(r"[0-9a-f]{64}", str(dataset.get("sha256", ""))):
            _error(errors, dataset_id, "valid sha256 is required")
        elif path and sha256(path) != dataset["sha256"]:
            _error(errors, dataset_id, "sha256 mismatch")

        for artifact in dataset.get("artifacts", []):
            artifact_id = f"{dataset_id}/{artifact.get('role', 'artifact')}"
            artifact_path = _catalog_file(
                errors, artifact_id, artifact.get("local_path"), root
            )
            artifact_hash = str(artifact.get("sha256", ""))
            if not re.fullmatch(r"[0-9a-f]{64}", artifact_hash):
                _error(errors, artifact_id, "valid sha256 is required")
            elif artifact_path and sha256(artifact_path) != artifact_hash:
                _error(errors, artifact_id, "sha256 mismatch")

        source = dataset.get("source")
        if not isinstance(source, dict):
            _error(errors, dataset_id, "source metadata is required")
        else:
            for field in ("institution", "url", "retrieved_on", "license"):
                if not source.get(field):
                    _error(errors, dataset_id, f"source.{field} is required")
        if dataset.get("category") in {"geometry", "bathymetry"}:
            spatial = dataset.get("spatial_reference")
            if not isinstance(spatial, dict) or not spatial.get("horizontal_crs"):
                _error(errors, dataset_id, "horizontal CRS is required")
        if dataset.get("category") in {"stage", "bathymetry", "boundary_series"}:
            spatial = dataset.get("spatial_reference")
            if not isinstance(spatial, dict) or not spatial.get("vertical_datum"):
                _error(errors, dataset_id, "vertical datum/reference is required")
        for variable in dataset.get("variables", []):
            if not variable.get("name") or not variable.get("unit"):
                _error(errors, dataset_id, "each variable requires name and unit")
        if (
            path
            and dataset.get("fitness") == "required"
            and dataset.get("category") in {"flow", "stage"}
        ):
            try:
                expected_unit = dataset.get("variables", [{}])[0].get("unit")
                measured = analyse_daily_csv(path, expected_unit)
                declared = dataset.get("quality")
                if not isinstance(declared, dict):
                    _error(errors, dataset_id, "quality metadata is required")
                else:
                    for field in (
                        "records",
                        "start",
                        "end",
                        "missing_days",
                        "completeness_percent",
                    ):
                        if declared.get(field) != measured[field]:
                            _error(errors, dataset_id, f"quality.{field} mismatch")
            except ValueError as exc:
                _error(errors, dataset_id, f"invalid daily series: {exc}")

    gate_ids: set[str] = set()
    for gate in gates:
        gate_id = gate.get("id", "<missing-gate-id>")
        if gate_id in gate_ids:
            errors.append(f"{gate_id}: duplicate gate id")
        gate_ids.add(gate_id)
        if not gate.get("title") or not gate.get("requirements"):
            errors.append(f"{gate_id}: title and requirements are required")
        for requirement in gate.get("requirements", []):
            dataset_id = requirement.get("dataset_id")
            if dataset_id not in by_id:
                errors.append(f"{gate_id}: unknown dataset {dataset_id}")
            accepted = requirement.get("accepted_statuses")
            if not accepted or any(status not in STATUSES for status in accepted):
                errors.append(f"{gate_id}: invalid accepted_statuses for {dataset_id}")
    return errors


def report(catalog: dict, root: Path = ROOT) -> dict:
    errors = validate(catalog, root)
    datasets = catalog.get("datasets", [])
    by_id = {dataset["id"]: dataset for dataset in datasets if "id" in dataset}
    counts = {status: 0 for status in sorted(STATUSES)}
    counts["total"] = len(datasets)
    for dataset in datasets:
        if dataset.get("status") in counts:
            counts[dataset["status"]] += 1
    gates = []
    for gate in catalog.get("gates", []):
        blocked = []
        for requirement in gate.get("requirements", []):
            dataset = by_id.get(requirement.get("dataset_id"))
            if not dataset or dataset.get("status") not in requirement.get(
                "accepted_statuses", []
            ):
                blocked.append(
                    {
                        "id": requirement.get("dataset_id"),
                        "title": dataset.get("title") if dataset else "Dataset desconhecido",
                        "status": dataset.get("status") if dataset else "unknown",
                    }
                )
        gates.append(
            {
                "id": gate.get("id"),
                "title": gate.get("title"),
                "status": "ready" if not blocked and not errors else "blocked",
                "blocked_by": blocked,
            }
        )
    return {
        "valid": not errors,
        "errors": errors,
        "counts": counts,
        "gates": gates,
    }


def validated_catalog(path: Path = CATALOG_PATH, root: Path = ROOT) -> dict:
    catalog = load(path)
    result = report(catalog, root)
    if not result["valid"]:
        raise ValueError("Invalid data catalog: " + "; ".join(result["errors"]))
    return {
        "catalog": catalog,
        "report": result,
        "phase3": phase3_report(catalog, root),
    }
