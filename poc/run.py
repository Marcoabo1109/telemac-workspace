"""Executar da raiz: PYTHONPATH=tapajos-telemac-platform python poc/run.py steady|tracer|bed|cut"""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import numpy as np
from backend.api.slf_io import read, write

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tapajos-telemac-platform/data/culm"
RUN = ROOT / "poc/work"
P = json.loads((ROOT/"poc/parameters.json").read_text())


def solve(name, cas):
    (RUN/f"{name}.cas").write_text(cas)
    with (RUN/f"{name}.log").open("w") as log:
        subprocess.run(["docker","run","--rm","--user","1000:1000","-v",f"{RUN}:/case","-w","/case",
                        P["image"],"/app/docker/run-telemac",f"{name}.cas"], stdout=log, stderr=subprocess.STDOUT,check=True)


def steady_test():
    m = read(RUN/"r2d_culm.slf")
    dt = m.times[-1]-m.times[-2]
    rate = [abs(m.field(key,-1)-m.field(key,-2)).max()/dt for key in ("WATER DEPTH","VELOCITY U","VELOCITY V")]
    flux = [float(v) for v in re.findall(r"FLUX BOUNDARY\s+\d+:\s*([-+\d.E]+)",(RUN/"steady.log").read_text())[-2:]]
    if len(flux)!=2 or abs(sum(flux))/flux[0]>P["steady_flux_fraction"] or rate[0]>P["steady_depth_rate"] or max(rate[1:])>P["steady_velocity_rate"]:
        raise ValueError("Estado estacionário reprovado")
    return dict(time_s=m.times[-1],rates=rate,flux_m3_s=flux)


def scenario(name, previous, tracer=False, bed=False, cut=False):
    cas = (ROOT/"poc/steady.cas").read_text().replace("r2d_culm.slf",name+".slf").replace("ini_culm.slf",previous)
    cas = cas.replace("= 27000",f'= {P["steps"]}').replace(": 1000",f': {P["print_period"]}').replace("=  250",f'= {P["print_period"]}')
    if tracer:
        cas = cas.replace("geo_culm.cli","tracer.cli").replace("U,V,S,B,H","U,V,S,B,H,T1")
        cas += f"""
NUMBER OF TRACERS = 1
NAMES OF TRACERS = 'DYE'
INITIAL VALUES OF TRACERS = 0.
PRESCRIBED TRACERS VALUES = 1.;0.
SCHEME FOR ADVECTION OF TRACERS = 14
COEFFICIENT FOR DIFFUSION OF TRACERS = {P['dispersion_m2_s']}
"""
        rows = [s.split() for s in (BASE/"geo_culm.cli").read_text().splitlines()]
        for row in rows:
            if row[1:3] == ["5","5"]:
                row[7] = "5"
        (RUN/"tracer.cli").write_text("".join(" ".join(r)+"\n" for r in rows))
    if bed:
        rows = [s.split() for s in (BASE/"geo_culm.cli").read_text().splitlines()]
        for row in rows:
            if row[:3] != ["2","2","2"]:
                row[7] = "4"
        (RUN/"mor.cli").write_text("".join(" ".join(r)+"\n" for r in rows))
        cas += f"COUPLING WITH = 'GAIA'\nGAIA STEERING FILE = {name}_gai.cas\n"
        (RUN/f"{name}_gai.cas").write_text(f"""GEOMETRY FILE = geo_culm.slf
BOUNDARY CONDITIONS FILE = mor.cli
RESULTS FILE = {name}_gai.slf
VARIABLES FOR GRAPHIC PRINTOUTS = 'B,E,TOB,QSBL'
MASS-BALANCE = YES
CLASSES TYPE OF SEDIMENT = 'NCO'
CLASSES SEDIMENT DENSITY = 2650.
CLASSES SEDIMENT DIAMETERS = {P['diameter_m']}
BED LOAD FOR ALL SANDS = YES
SUSPENSION FOR ALL SANDS = NO
BED-LOAD TRANSPORT FORMULA FOR ALL SANDS = 1
MPM COEFFICIENT = 8.
CLASSES SHIELDS PARAMETERS = 0.047
SKIN FRICTION CORRECTION = 1
LAYERS NON COHESIVE BED POROSITY = 0.4
""")
    solve(name,cas)


if __name__ == "__main__":
    stage = sys.argv[1]
    RUN.mkdir(exist_ok=True)
    for filename in ["geo_culm.slf","geo_culm.cli","ini_culm.slf"]:
        shutil.copyfile(BASE/filename,RUN/filename)
    if stage=="steady":
        solve("steady",(ROOT/"poc/steady.cas").read_text())
        print(steady_test())
    elif stage=="tracer":
        steady_test()
        scenario("control","r2d_culm.slf")
        scenario("tracer","r2d_culm.slf",True)
    elif stage=="bed":
        scenario("bed","control.slf",bed=True)
        scenario("bed_dye","tracer.slf",True,True)
