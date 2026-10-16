"""Integration check against the running local API, using real Culm files."""

import json, os
import time
from pathlib import Path
import httpx
from backend.api.slf_io import read

root = Path(__file__).resolve().parents[1]
with httpx.Client(
    base_url=os.getenv("TAPAJOS_API", "http://127.0.0.1:8000"), timeout=60
) as c:
    params = c.get("/api/example").json()["params"]
    params.update(
        {
            "NUMBER OF TIME STEPS": "20",
            "GRAPHIC PRINTOUT PERIOD": "5",
            "LISTING PRINTOUT PERIOD": "5",
        }
    )
    r = c.post(
        "/api/jobs",
        data={"params": json.dumps(params), "example": "culm"},
        files={"files": ("note.txt", b"HTTP integration smoke check")},
    )
    r.raise_for_status()
    jobid = r.json()["id"]
    print(jobid, flush=True)
    from websockets.sync.client import connect

    wsurl = (
        os.getenv("TAPAJOS_API", "http://127.0.0.1:8000")
        .replace("http:", "ws:")
        .replace("https:", "wss:")
        + "/api/jobs/"
        + jobid
        + "/ws"
    )
    with connect(wsurl) as ws:
        while True:
            message = json.loads(ws.recv(timeout=90))
            if message["status"] in ("completed", "failed"):
                break
    print("WebSocket logs verified", flush=True)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        j = c.get("/api/jobs/" + jobid).json()
        if j["status"] in ("completed", "failed"):
            break
        time.sleep(1)
    print(j["status"])
    print("\n".join(j["logs"][-8:]))
    assert j["status"] == "completed"
    b = c.get("/api/jobs/" + jobid + "/result")
    b.raise_for_status()
    m = read(b.content)
    assert list(m.times) == [0.0, 10.0, 20.0, 30.0, 40.0]
    report = root / "reports/culm_smoke"
    report.mkdir(parents=True, exist_ok=True)
    (report / "r2d_culm_smoke.slf").write_bytes(b.content)
    (root / "docs/smoke-run.json").write_text(
        json.dumps(
            {
                "id": jobid,
                "status": j["status"],
                "times": m.times.tolist(),
                "nodes": len(m.x),
                "triangles": len(m.ikle),
                "solver": "source-built TELEMAC v8p5r0 (Docker compose)",
                "test": "HTTP API + WebSocket + real solver + binary result",
            },
            indent=2,
        )
    )
