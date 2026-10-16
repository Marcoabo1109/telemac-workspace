"""Reproducibility inventory, reference run, and TELEMAC result comparison."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "culm"
REFERENCE_FILES = (
    "t2d_culm.cas",
    "geo_culm.slf",
    "geo_culm.cli",
    "ini_culm.slf",
    "t2d_culm.qsl",
)
DEFAULT_TOLERANCES = ROOT / "docs" / "reproducibility-tolerances.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def command_output(command: list[str]) -> str | None:
    if not shutil.which(command[0]):
        return None
    try:
        result = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = result.stdout.strip().splitlines()
    return lines[0] if lines else None


def git_value(path: Path, *arguments: str) -> str | None:
    try:
        result = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={path}",
                "-C",
                str(path),
                *arguments,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def reference_manifest() -> dict:
    files = []
    combined = hashlib.sha256()
    for name in REFERENCE_FILES:
        path = REFERENCE / name
        digest = sha256(path)
        files.append({"path": str(path.relative_to(ROOT)), "sha256": digest})
        combined.update(name.encode())
        combined.update(digest.encode())
    return {
        "id": "culm-20x2s-v1",
        "description": "Culm reference case shortened to 20 steps of 2 seconds",
        "steps": 20,
        "time_step_seconds": 2.0,
        "final_time_seconds": 40.0,
        "files": files,
        "combined_sha256": combined.hexdigest(),
    }


def collect_environment() -> dict:
    telemac_root = os.environ.get("HOMETEL")
    telemac_path = Path(telemac_root).resolve() if telemac_root else None
    executable = os.environ.get("TELEMAC_EXECUTABLE") or shutil.which("telemac2d.py")
    return {
        "schema_version": 1,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "host": {
            "hostname": platform.node(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
        },
        "project": {
            "git_commit": git_value(ROOT, "rev-parse", "HEAD"),
            "git_branch": git_value(ROOT, "branch", "--show-current"),
            "git_dirty": bool(
                git_value(
                    ROOT,
                    "status",
                    "--porcelain",
                    "--ignore-submodules=dirty",
                )
            ),
        },
        "runtime": {
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "node": command_output(["node", "--version"]),
            "npm": command_output(["npm", "--version"]),
            "gfortran": command_output(["gfortran", "--version"]),
            "mpiexec": command_output(["mpiexec", "--version"]),
            "packages": {
                name: package_version(name)
                for name in ("fastapi", "numpy", "scipy", "pandas", "gmsh")
            },
        },
        "telemac": {
            "root": str(telemac_path) if telemac_path else None,
            "git_commit": git_value(telemac_path, "rev-parse", "HEAD")
            if telemac_path
            else None,
            "executable": executable,
            "configuration": os.environ.get("USETELCFG"),
            "configuration_file": os.environ.get("SYSTELCFG"),
        },
        "reference_case": reference_manifest(),
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def canonical_variable(name: str) -> str:
    return name.strip().upper()


def result_summary(mesh) -> dict:
    summary = {}
    for index, (name, unit) in enumerate(mesh.variables):
        values = np.asarray(mesh.values[:, index, :], dtype=np.float64)
        summary[canonical_variable(name)] = {
            "unit": unit.strip(),
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
            "mean": float(np.mean(values)),
            "rms": float(np.sqrt(np.mean(values * values))),
        }
    return summary


def run_reference(output: Path, ncores: int) -> dict:
    if ncores < 1:
        raise ValueError("ncores must be at least one")
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    output.mkdir(parents=True)

    from backend.api import cas_parser, slf_io
    from backend.api import telemac_runner as runner

    params = cas_parser.parse((REFERENCE / "t2d_culm.cas").read_text())
    params.update(
        {
            "NUMBER OF TIME STEPS": "20",
            "GRAPHIC PRINTOUT PERIOD": "5",
            "LISTING PRINTOUT PERIOD": "5",
        }
    )
    files = {
        item.name: item.read_bytes()
        for item in REFERENCE.iterdir()
        if item.suffix in (".slf", ".qsl", ".cli")
        and not item.name.startswith("f2d")
    }
    previous_ncores = os.environ.get("TELEMAC_NCORES")
    previous_runs = runner.RUNS
    os.environ["TELEMAC_NCORES"] = str(ncores)
    runner.RUNS = output / "jobs"
    try:
        job = runner.prepare(params, files)
        asyncio.run(runner.run(job))
    finally:
        runner.RUNS = previous_runs
        if previous_ncores is None:
            os.environ.pop("TELEMAC_NCORES", None)
        else:
            os.environ["TELEMAC_NCORES"] = previous_ncores

    (output / "run.log").write_text("\n".join(job["logs"]) + "\n")
    if job["status"] != "completed":
        raise RuntimeError("reference run failed; inspect run.log")
    source_result = job["path"] / job["result"]
    result = output / "result.slf"
    shutil.copy2(source_result, result)
    mesh = slf_io.read(result)
    if not math.isclose(float(mesh.times[-1]), 40.0):
        raise RuntimeError(f"unexpected final time: {mesh.times[-1]}")
    report = {
        "schema_version": 1,
        "status": "completed",
        "ncores": ncores,
        "environment": collect_environment(),
        "reference_case": reference_manifest(),
        "result": {
            "path": "result.slf",
            "sha256": sha256(result),
            "nodes": len(mesh.x),
            "triangles": len(mesh.ikle),
            "times": [float(value) for value in mesh.times],
            "variables": result_summary(mesh),
        },
    }
    write_json(output / "report.json", report)
    return report


def load_tolerances(path: Path) -> dict:
    value = json.loads(path.read_text())
    if "default_max_abs" not in value or "variables" not in value:
        raise ValueError("invalid tolerance file")
    return value


def compare_results(first: Path, second: Path, tolerances_path: Path) -> dict:
    from backend.api import slf_io

    left = slf_io.read(first)
    right = slf_io.read(second)
    problems = []
    if left.ikle.shape != right.ikle.shape or not np.array_equal(left.ikle, right.ikle):
        problems.append("mesh connectivity differs")
    if left.x.shape != right.x.shape or not np.allclose(left.x, right.x, atol=1e-9):
        problems.append("mesh x coordinates differ")
    if left.y.shape != right.y.shape or not np.allclose(left.y, right.y, atol=1e-9):
        problems.append("mesh y coordinates differ")
    if left.times.shape != right.times.shape or not np.allclose(
        left.times, right.times, atol=1e-12
    ):
        problems.append("result times differ")

    left_names = [canonical_variable(name) for name, _ in left.variables]
    right_names = [canonical_variable(name) for name, _ in right.variables]
    if left_names != right_names:
        problems.append("variable lists differ")

    tolerances = load_tolerances(tolerances_path)
    comparisons = {}
    if not problems:
        for index, name in enumerate(left_names):
            difference = np.asarray(left.values[:, index, :], dtype=np.float64) - np.asarray(
                right.values[:, index, :], dtype=np.float64
            )
            max_abs = float(np.max(np.abs(difference)))
            rmse = float(np.sqrt(np.mean(difference * difference)))
            limit = float(
                tolerances["variables"].get(name, tolerances["default_max_abs"])
            )
            passed = max_abs <= limit
            comparisons[name] = {
                "max_abs_difference": max_abs,
                "rmse": rmse,
                "max_abs_tolerance": limit,
                "passed": passed,
            }
            if not passed:
                problems.append(f"{name} exceeds tolerance")
    return {
        "schema_version": 1,
        "status": "passed" if not problems else "failed",
        "first": {"path": str(first), "sha256": sha256(first)},
        "second": {"path": str(second), "sha256": sha256(second)},
        "tolerances": str(tolerances_path),
        "variables": comparisons,
        "problems": problems,
    }


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description=__doc__)
    subcommands = cli.add_subparsers(dest="command", required=True)
    inventory = subcommands.add_parser("inventory", help="record environment and case")
    inventory.add_argument("--output", type=Path, required=True)
    manifest = subcommands.add_parser("manifest", help="record the immutable case")
    manifest.add_argument("--output", type=Path, required=True)
    run = subcommands.add_parser("run", help="run the short Culm reference case")
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--ncores", type=int, default=1)
    compare = subcommands.add_parser("compare", help="compare two SERAFIN results")
    compare.add_argument("first", type=Path)
    compare.add_argument("second", type=Path)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--tolerances", type=Path, default=DEFAULT_TOLERANCES)
    return cli


def main() -> int:
    args = parser().parse_args()
    if args.command == "inventory":
        write_json(args.output, collect_environment())
        return 0
    if args.command == "manifest":
        write_json(args.output, reference_manifest())
        return 0
    if args.command == "run":
        run_reference(args.output, args.ncores)
        return 0
    comparison = compare_results(args.first, args.second, args.tolerances)
    write_json(args.output, comparison)
    return 0 if comparison["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
