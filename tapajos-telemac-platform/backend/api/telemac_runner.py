"""Isolated local jobs. No shell or user-defined executables/Fortran accepted."""

import asyncio
import os
from pathlib import Path
import re
import shutil
import uuid
from . import cas_parser, slf_io, qsl_io, cli_io

ROOT = Path(__file__).resolve().parents[2]
RUNS = Path(os.environ.get("TAPAJOS_RUNS", ROOT / "runs")).resolve()
JOBS = {}


def safe_name(name):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", name) or ".." in name:
        raise ValueError("Nome de arquivo inválido")
    return name


def prepare(params, files):
    params = dict(params)
    cas_parser.validate(params)
    for k in params:
        if any(
            s in k
            for s in ("FORTRAN", "DICTIONARY", "STEERING FILE", "COUPLING", "USER CRAY")
        ):
            raise ValueError(
                f"{k}: execução web não aceita código ou acoplamento arbitrário; use CLI revisado"
            )
    required = ["GEOMETRY FILE", "BOUNDARY CONDITIONS FILE"]
    if cas_parser.scalar(params.get("COMPUTATION CONTINUED", "NO")).upper() in (
        "YES",
        "TRUE",
        "OUI",
    ):
        required += ["PREVIOUS COMPUTATION FILE"]
    for k, v in params.items():
        if "FILE" in k:
            name = safe_name(cas_parser.scalar(v))
            params[k] = f"'{name}'"
            if k not in ("RESULTS FILE",):
                if name not in files:
                    raise ValueError(f"Arquivo ausente: {name}")
    for k in required:
        if k not in params:
            raise ValueError(f"Palavra-chave obrigatória: {k}")
    result = safe_name(cas_parser.scalar(params.get("RESULTS FILE", "results.slf")))
    if result in files:
        raise ValueError("Resultado não pode sobrescrever arquivo de entrada")
    params["RESULTS FILE"] = f"'{result}'"
    mesh = slf_io.read(files[cas_parser.scalar(params["GEOMETRY FILE"])])
    rows = cli_io.parse(
        files[cas_parser.scalar(params["BOUNDARY CONDITIONS FILE"])].decode()
    )
    if any(r[11] > len(mesh.x) for r in rows):
        raise ValueError("CLI referencia nó fora da malha")
    if {r[11] for r in rows} != {i + 1 for i, v in enumerate(mesh.ipobo) if v > 0}:
        raise ValueError("CLI não corresponde aos nós de fronteira da malha")
    if "LIQUID BOUNDARIES FILE" in params:
        q = qsl_io.parse(
            files[cas_parser.scalar(params["LIQUID BOUNDARIES FILE"])].decode()
        )
        duration = float(params["TIME STEP"]) * int(params["NUMBER OF TIME STEPS"])
        if q["rows"][0][0] > 0 or q["rows"][-1][0] < duration:
            raise ValueError("Série não cobre a duração da simulação")
    jobid = uuid.uuid4().hex
    path = RUNS / jobid
    path.mkdir(parents=True)
    for name, blob in files.items():
        safe_name(name)
        (path / name).write_bytes(blob)
    (path / "case.cas").write_text(cas_parser.generate(params))
    job = dict(
        id=jobid,
        status="queued",
        progress=0,
        logs=[],
        result=result,
        path=path,
        total=int(params["NUMBER OF TIME STEPS"]),
    )
    JOBS[jobid] = job
    return job


def command(path):
    n = int(os.environ.get("TELEMAC_NCORES", "1"))
    if not 1 <= n <= 256:
        raise ValueError("TELEMAC_NCORES inválido")
    container = os.environ.get("TELEMAC_CONTAINER")
    if container:
        hostroot = Path(os.environ.get("TELEMAC_HOST_ROOT", ROOT.parent)).resolve()
        rel = path.relative_to(hostroot)
        return [
            "docker",
            "exec",
            "-w",
            "/workspace/" + str(rel),
            container,
            "bash",
            "-lc",
            "source /opt/open_telemac/configs/pysource-simvia.sh && telemac2d.py case.cas --ncsize="
            + str(n),
        ]
    executable = os.environ.get("TELEMAC_EXECUTABLE", "telemac2d.py")
    if not shutil.which(executable):
        raise RuntimeError(
            "TELEMAC não configurado: defina TELEMAC_EXECUTABLE ou TELEMAC_CONTAINER"
        )
    return [executable, "case.cas", f"--ncsize={n}"]


async def run(job):
    try:
        job["status"] = "running"
        proc = await asyncio.create_subprocess_exec(
            *command(job["path"]),
            cwd=job["path"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            limit=2**20,
        )
        job["process"] = proc
        with (job["path"] / "run.log").open("w") as log:
            async for raw in proc.stdout:
                line = raw.decode(errors="replace").rstrip()
                log.write(line + "\n")
                log.flush()
                job["logs"].append(line)
                match = re.search(r"ITERATION\s*:?\s*(\d+)", line, re.I)
                if match:
                    job["progress"] = min(99, 100 * int(match[1]) / job["total"])
        code = await proc.wait()
        job["returncode"] = code
        if code == 0 and (job["path"] / job["result"]).is_file():
            slf_io.read(job["path"] / job["result"])
            job["status"] = "completed"
            job["progress"] = 100
        else:
            job["status"] = "failed"
    except Exception as exc:
        job["status"] = "failed"
        job["logs"].append(str(exc))
    finally:
        job.pop("process", None)
