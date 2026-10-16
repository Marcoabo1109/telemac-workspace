from pathlib import Path
import asyncio
import io
import json
import zipfile
import tempfile
import numpy as np
from fastapi import (
    FastAPI,
    UploadFile,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Request,
)
from fastapi.responses import Response, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .api import (
    cas_parser,
    slf_io,
    qsl_io,
    cli_io,
    data_catalog,
    nestor,
    telemac_runner as runner,
)

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Tapajós • Laboratório de rios", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def invalid(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def blob(file):
    data = await file.read(64 * 1024 * 1024 + 1)
    if len(data) > 64 * 1024 * 1024:
        raise HTTPException(413, "Limite: 64 MiB por arquivo")
    return data


def download(data, name):
    return Response(
        data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@app.get("/api/health")
def health():
    try:
        runner.command(ROOT / "runs" / "probe")
        ready = True
    except Exception:
        ready = False
    return {
        "status": "ok",
        "runner_configured": ready,
        "ana_credentials": bool(__import__("os").environ.get("ANA_TOKEN")),
    }


@app.get("/api/schema")
def schema():
    return dict(defaults=cas_parser.DEFAULTS, choices=cas_parser.CHOICES)


@app.get("/api/data/catalog")
def catalog():
    return data_catalog.validated_catalog()


def example_directory(case_id):
    if case_id == "culm":
        return ROOT / "data/culm", "t2d_culm.cas"
    if case_id == "tapajos":
        return ROOT / "models/tapajos_trecho1", "tapajos.cas"
    raise HTTPException(404, "Caso desconhecido")


@app.get("/api/example")
def example(case_id: str = "culm"):
    p, steering = example_directory(case_id)
    params = cas_parser.parse((p / steering).read_text())

    def filename(key):
        return cas_parser.scalar(params[key])

    return dict(
        params=params,
        mesh=slf_io.read(p / filename("GEOMETRY FILE")).summary(),
        qsl=qsl_io.parse((p / filename("LIQUID BOUNDARIES FILE")).read_text()),
        cli=cli_io.parse((p / filename("BOUNDARY CONDITIONS FILE")).read_text()),
        assumptions=json.loads((p / "assumptions.json").read_text())
        if case_id == "tapajos"
        else None,
    )


@app.get("/api/example/{name}")
def example_file(name: str, case_id: str = "culm"):
    runner.safe_name(name)
    p, _ = example_directory(case_id)
    path = p / name
    if not path.is_file():
        raise HTTPException(404)
    return FileResponse(path, filename=name)


@app.post("/api/cas/import")
async def cas_import(file: UploadFile):
    return cas_parser.parse((await blob(file)).decode("utf-8-sig"))


@app.post("/api/cas/export")
async def cas_export(request: Request):
    return download(cas_parser.generate(await request.json()), "case.cas")


@app.post("/api/qsl/import")
async def qsl_import(file: UploadFile):
    return qsl_io.parse((await blob(file)).decode("utf-8-sig"))


@app.post("/api/qsl/export")
async def qsl_export(request: Request):
    return download(qsl_io.generate(**(await request.json())), "boundaries.qsl")


@app.post("/api/cli/import")
async def cli_import(file: UploadFile):
    return cli_io.parse((await blob(file)).decode())


@app.post("/api/cli/export")
async def cli_export(request: Request):
    return download(cli_io.generate(await request.json()), "boundary.cli")


@app.post("/api/mesh/import")
async def mesh_import(file: UploadFile, frame: int = 0):
    return slf_io.read(await blob(file)).summary(frame)


@app.post("/api/mesh/export")
async def mesh_export(request: Request):
    form = await request.form()
    m = slf_io.read(await blob(form["file"]))
    edits = json.loads(form.get("edits", "{}"))
    names = [n.strip().upper() for n, u in m.variables]
    ix = next((i for i, n in enumerate(names) if n in ("BOTTOM", "FOND")), None)
    if ix is None:
        raise ValueError("Arquivo não contém BOTTOM/FOND")
    for node, z in edits.items():
        node = int(node)
        z = float(z)
        if not 0 <= node < len(m.x) or not np.isfinite(z):
            raise ValueError("Edição de nó inválida")
        m.values[:, ix, node] = z
    return download(slf_io.write(m), "mesh_edited.slf")


@app.post("/api/mesh/dem")
async def mesh_dem(request: Request):
    import rasterio
    from rasterio.warp import transform

    form = await request.form()
    m = slf_io.read(await blob(form["file"]))
    crs = str(form.get("mesh_crs", ""))
    if not crs:
        raise ValueError("Informe o CRS da malha; SERAFIN não armazena EPSG")
    with rasterio.io.MemoryFile(await blob(form["dem"])) as mem:
        with mem.open() as dem:
            if not dem.crs:
                raise ValueError("Raster sem CRS")
            x, y = transform(crs, dem.crs, m.x, m.y)
            vals = list(dem.sample(zip(x, y), masked=True))
            edits = {
                str(i): float(v[0])
                for i, v in enumerate(vals)
                if not np.ma.is_masked(v[0]) and np.isfinite(v[0])
            }
    if len(edits) != len(m.x):
        raise ValueError("DEM não cobre todos os nós ou contém nodata")
    return {
        "edits": edits,
        "warning": "Topografia emersa não é batimetria submersa; valide datum vertical.",
    }


@app.post("/api/mesh/generate")
async def mesh_generate(request: Request):
    from scripts.mesh_generator import generate

    config = await request.json()
    with tempfile.TemporaryDirectory() as d:
        generate(
            config["geometry"],
            Path(d),
            lc_canal=float(config.get("lc_canal", 200)),
            lc_planicie=float(config.get("lc_planicie", 800)),
            lc_fronteira=float(config.get("lc_fronteira", 200)),
        )
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as z:
            for p in Path(d).iterdir():
                z.write(p, p.name)
        return download(stream.getvalue(), "mesh.zip")


@app.post("/api/jobs")
async def jobs(request: Request):
    form = await request.form()
    params = json.loads(str(form["params"]))
    files = {}
    if form.get("example"):
        directory, _ = example_directory(str(form["example"]))
        files = {
            p.name: p.read_bytes()
            for p in directory.iterdir()
            if p.suffix in (".slf", ".cli", ".qsl") and not p.name.startswith("f2d_")
        }
    for name, f in form.multi_items():
        if name == "files":
            files[runner.safe_name(f.filename)] = await blob(f)
    if any(j["status"] in ("queued", "running") for j in runner.JOBS.values()):
        raise HTTPException(409, "Aguarde a execução ativa")
    job = runner.prepare(params, files)
    asyncio.create_task(runner.run(job))
    return {"id": job["id"]}


@app.get("/api/jobs/{jobid}")
def job_status(jobid: str):
    job = runner.JOBS.get(jobid)
    if not job:
        raise HTTPException(404)
    return {k: job[k] for k in ("id", "status", "progress", "logs")}


@app.get("/api/jobs/{jobid}/result")
def job_result(jobid: str):
    job = runner.JOBS.get(jobid)
    if not job or job["status"] != "completed":
        raise HTTPException(404)
    return FileResponse(job["path"] / job["result"], filename=job["result"])


@app.websocket("/api/jobs/{jobid}/ws")
async def logs(ws: WebSocket, jobid: str):
    await ws.accept()
    seen = 0
    try:
        while jobid in runner.JOBS:
            j = runner.JOBS[jobid]
            await ws.send_json(
                dict(status=j["status"], progress=j["progress"], logs=j["logs"][seen:])
            )
            seen = len(j["logs"])
            if j["status"] in ("completed", "failed"):
                break
            await asyncio.sleep(0.5)
        await ws.close()
    except WebSocketDisconnect:
        pass

# GAIA/Nestor preparation endpoints; execution remains subject to runner policy.


@app.get('/api/nestor/schema')
def nestor_schema():
    return dict(fields=nestor.FIELDS, required=nestor.REQUIRED, labels=nestor.LABELS,
                numeric=sorted(nestor.NUMERIC), references=nestor.REFERENCES,
                gaia=nestor.gaia_schema(), source=nestor.SOURCE, commit=nestor.COMMIT)


@app.post('/api/nestor/import')
async def nestor_import(file: UploadFile):
    return nestor.parse_actions((await blob(file)).decode('utf-8-sig'))


@app.post('/api/nestor/export')
async def nestor_export(request: Request):
    return download(nestor.generate_actions(await request.json()), 'nestor_actions.dat')


@app.post('/api/nestor/bundle')
async def nestor_bundle(request: Request):
    return download(nestor.bundle(await request.json()), 'gaia_nestor.zip')


@app.get("/api/poc/materials")
@app.get("/api/poc/materials/download")
def materials_poc():
    path = ROOT / "data/tapajos/poc/materials.json"
    if not path.is_file():
        raise HTTPException(503, "Execute scripts.materials_poc para gerar os resultados")
    return FileResponse(path, media_type="application/json", filename="tapajos-materials-poc.json")
