"""Execute bundled Culm with the configured native solver (including inside Docker)."""

import asyncio, json, os
from backend.api import telemac_runner as r, cas_parser, slf_io

p = r.ROOT / "data/culm"
params = cas_parser.parse((p / "t2d_culm.cas").read_text())
params.update(
    {
        "NUMBER OF TIME STEPS": "20",
        "GRAPHIC PRINTOUT PERIOD": "5",
        "LISTING PRINTOUT PERIOD": "5",
    }
)
files = {
    f.name: f.read_bytes()
    for f in p.iterdir()
    if f.suffix in (".slf", ".qsl", ".cli") and not f.name.startswith("f2d")
}
j = r.prepare(params, files)
asyncio.run(r.run(j))
print(j["status"])
print("\n".join(j["logs"][-20:]))
assert j["status"] == "completed"
m = slf_io.read(j["path"] / j["result"])
assert m.times[-1] == 40.0
(
    r.ROOT
    / (
        "docs/native-smoke-mpi.json"
        if int(os.getenv("TELEMAC_NCORES", "1")) > 1
        else "docs/native-smoke.json"
    )
).write_text(
    json.dumps(
        {
            "ncores": int(os.getenv("TELEMAC_NCORES", "1")),
            "status": j["status"],
            "job": j["id"],
            "nodes": len(m.x),
            "triangles": len(m.ikle),
            "times": m.times.tolist(),
            "test": "Ubuntu 22.04 ARM64 source-built v8p5r0 Python 3.11",
        },
        indent=2,
    )
)
