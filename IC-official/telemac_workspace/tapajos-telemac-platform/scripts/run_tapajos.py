"""Submit the documented exploratory case to the local API and retain diagnostics."""

import argparse
import hashlib
import json
import re
from pathlib import Path
import time
import httpx as requests
import numpy as np
from backend.api import cas_parser, slf_io
from scripts.postprocess import metrics, export_vtk, animate

ROOT = Path(__file__).resolve().parents[1]


def run(base="http://localhost:8000", duration=None):
    case = ROOT / "models/tapajos_trecho1"
    params = cas_parser.parse((case / "tapajos.cas").read_text())
    if duration is not None:
        params["NUMBER OF TIME STEPS"] = str(int(duration / float(params["TIME STEP"])))
    files = [
        ("files", (n, (case / n).read_bytes()))
        for n in ["mesh.slf", "mesh.cli", "tapajos.qsl"]
    ]
    response = requests.post(
        base + "/api/jobs", data={"params": json.dumps(params)}, files=files, timeout=30
    )
    response.raise_for_status()
    job = response.json()["id"]
    print("Job:", job, flush=True)
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        r = requests.get(base + "/api/jobs/" + job, timeout=30)
        r.raise_for_status()
        state = r.json()
        if state["status"] in ("completed", "failed"):
            break
        time.sleep(1)
    else:
        raise TimeoutError("Solver still active after 600 s; inspect job " + job)
    if state["status"] != "completed":
        print(json.dumps(state, ensure_ascii=False)[-6000:])
        raise RuntimeError("Solver failed")
    response = requests.get(base + "/api/jobs/" + job + "/result", timeout=60)
    response.raise_for_status()
    out = ROOT / "reports/tapajos_initial"
    out.mkdir(parents=True, exist_ok=True)
    m = slf_io.read(response.content)
    d = metrics(m)
    assert np.isfinite(m.values).all()
    assert m.times[-1] == float(params["TIME STEP"]) * int(
        params["NUMBER OF TIME STEPS"]
    )
    names = [n.strip() for n, u in m.variables]
    h = m.values[:, names.index("WATER DEPTH")]
    tr = m.values[:, names.index("PASSIVE TRACER")]
    assert h.min() > 0, "Negative depth: reject exploratory run"
    assert tr.max() > 0.5 and tr.min() >= -0.01 and tr.max() <= 1.05, (
        "Tracer failed or exceeded bounds"
    )
    log = "\n".join(state.get("logs", [])).rstrip() + "\n"
    match = re.search(r"RELATIVE ERROR CUMULATED ON VOLUME:\s*([\d.E+-]+)", log)
    volume_error = float(match.group(1)) if match else None
    inlet_flux = re.findall(r"FLUX BOUNDARY\s+2:\s*([\d.E+-]+)", log)
    assert volume_error is not None and abs(volume_error) < 1e-3, (
        "Mass balance check failed"
    )
    assert inlet_flux and abs(float(inlet_flux[-1]) - 6000) < 6, (
        "Inlet boundary assignment failed"
    )
    (out / "r2d_tapajos.slf").write_bytes(response.content)
    tracer_match = re.search(
        r"FINAL BALANCE OF PASSIVE TRACER.*?RELATIVE ERROR\s*:\s*([\d.E+-]+)", log, re.S
    )
    tracer_error = float(tracer_match.group(1)) if tracer_match else None
    summary = {
        "relative_cumulative_volume_error": volume_error,
        "relative_final_tracer_mass_error": tracer_error,
        "status": state["status"],
        "job": job,
        "solver": "TELEMAC-2D v8p5r0 source build",
        "duration_s": float(m.times[-1]),
        "frames": len(m.times),
        "nodes": len(m.x),
        "triangles": len(m.ikle),
        "minimum_depth_m": float(h.min()),
        "maximum_speed_m_s": float(d["speed"].max()),
        "maximum_froude": float(d["froude"].max()),
        "tracer_min": float(tr.min()),
        "tracer_max": float(tr.max()),
        "result_sha256": hashlib.sha256(response.content).hexdigest(),
        "interpretation": "Uncalibrated startup scenario; assumed hydraulics and normalized conservative tracer, not measured metals.",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "case.cas").write_text(cas_parser.generate(params))
    (out / "solver-output.txt").write_text(log)
    np.savez_compressed(out / "fields.npz", **d)
    export_vtk(m, out / "results.vtk", -1)
    animate(m, out / "tracer.gif", "PASSIVE TRACER")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default="http://localhost:8000")
    p.add_argument("--duration", type=int)
    a = p.parse_args()
    run(a.base, a.duration)
