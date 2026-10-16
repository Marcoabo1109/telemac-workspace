"""Trusted CLI: generate and run the three-material TELEMAC Tapajos PoC."""
import json
import hashlib
import subprocess
from pathlib import Path
import numpy as np
from backend.api import slf_io, cli_io, cas_parser
from scripts.numerical_study import refine, nodal_areas

ROOT=Path(__file__).resolve().parents[1]
OFFICIAL_SHA='d1bff193746fd76425d7715a6e4d20d42eb8877e'


def prepare(source):
    base=ROOT/'models/tapajos_trecho1'; out=ROOT/'models/tapajos_materials'
    (out/'user_fortran').mkdir(parents=True,exist_ok=True)
    source=Path(source)
    (out/'LICENSE.upstream.txt').write_bytes((source/'LICENSE.txt').read_bytes())
    sha=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    if sha!=OFFICIAL_SHA:raise ValueError('Expected pinned official TELEMAC revision')
    mesh, rows=refine(slf_io.read(base/'mesh.slf'),cli_io.parse((base/'mesh.cli').read_text()))
    (out/'mesh.slf').write_bytes(slf_io.write(mesh));(out/'mesh.cli').write_text(cli_io.generate(rows))
    original=json.loads((base/'assumptions.json').read_text())
    original_mesh=slf_io.read(base/'mesh.slf')
    a=np.array(original['derived']['inlet_nodes'])-1;b=np.array(original['derived']['outlet_nodes'])-1
    cx=.75*original_mesh.x[a].mean()+.25*original_mesh.x[b].mean()
    cy=.75*original_mesh.y[a].mean()+.25*original_mesh.y[b].mean()
    (out/'user_fortran/user_condin_trac.f').write_text(f'''      SUBROUTINE USER_CONDIN_TRAC
      USE BIEF
      USE DECLARATIONS_TELEMAC2D
      IMPLICIT NONE
      INTEGER I,J
      DOUBLE PRECISION C
      DO I=1,NPOIN
        C=EXP(-((X(I)-{cx:.8f}D0)**2
     &        +(Y(I)-{cy:.8f}D0)**2)/(2.D0*180.D0**2))
        DO J=1,3
          T%ADR(J)%P%R(I)=C
        ENDDO
      ENDDO
      END
''')
    # Preserve upstream routine and insert audited source terms before return.
    upstream=(source/'sources/telemac2d/difsou.f').read_text()
    anchor='!     TOTAL CONTRIBUTION OF TEXP AND TIMP'
    addition='''!     POC: first-order pollutant loss and suspended sediment settling.
!     Normalized concentration; ws=0.001 m/s; half-life=1800 s.
      DO I=1,NPOIN
        TEXP%ADR(2)%P%R(I)=-LOG(2.D0)/1800.D0*TN%ADR(2)%P%R(I)
        TEXP%ADR(3)%P%R(I)=-0.001D0/MAX(HPROP%R(I),0.1D0)
     &                       *TN%ADR(3)%P%R(I)
        DO ITRAC=2,3
          MASSOU(ITRAC)=MASSOU(ITRAC)+DT*H%R(I)
     &        *TEXP%ADR(ITRAC)%P%R(I)*VOLU2D%R(I)
        ENDDO
      ENDDO
      IF(NCSIZE.GT.0) THEN
        MASSOU(2)=P_SUM(MASSOU(2))
        MASSOU(3)=P_SUM(MASSOU(3))
      ENDIF
!
'''
    assert upstream.count(anchor)==1
    (out/'user_fortran/difsou.f').write_text(upstream.replace(anchor,addition+anchor).rstrip()+"\n")
    p=cas_parser.parse((base/'tapajos.cas').read_text())
    p.update({'TITLE':"'TAPAJOS THREE MATERIALS POC'",'RESULTS FILE':"'materials.slf'",'FORTRAN FILE':"'user_fortran'",'TIME STEP':'1','NUMBER OF TIME STEPS':'3600','GRAPHIC PRINTOUT PERIOD':'60','LISTING PRINTOUT PERIOD':'600','NUMBER OF TRACERS':'3','NAMES OF TRACERS':"'CONSERVATIVE    ';'POLLUTANT       ';'SEDIMENT        '",'INITIAL VALUES OF TRACERS':'0;0;0','PRESCRIBED TRACERS VALUES':'0;0;0;0;0;0','TYPE OF ADVECTION':'1;5;5;5;5','COEFFICIENT FOR DIFFUSION OF TRACERS':'5;5;5','TREATMENT OF FLUXES AT THE BOUNDARIES':'2','OPTION FOR THE DIFFUSION OF TRACERS':'2;2;2'})
    (out/'case.cas').write_text(cas_parser.generate(p).replace("NAMES OF TRACERS = ", "NAMES OF TRACERS =\n"));(out/'tapajos.qsl').write_bytes((base/'tapajos.qsl').read_bytes())
    return out,mesh,{'solver_git':'https://gitlab.pam-retd.fr/otm/telemac-mascaret.git','solver_commit':sha,'solver_version':'v8p5r0','river':'Tapajós · Itaituba, Pará','crs':'EPSG:32721','release_xy_m':[float(cx),float(cy)],'release_sigma_m':180,'duration_s':3600,'dt_s':1,'nodes':len(mesh.x),'triangles':len(mesh.ikle),'data':original['collected'],'assumptions':{'flow_m3_s':6000,'width_m':1200,'bed':'schematic 4–8 m depth','datum':'local assumed; not tied to observed gauge','initial_hydrodynamics':'still water; startup transient','diffusivity_m2_s':5,'concentrations':'C/C0 normalized; initial Gaussian pulse identical for all materials','pollutant_half_life_s':1800,'sediment_settling_m_s':0.001},'limitations':['Uncalibrated exploratory geometry; spatial convergence of tracer not achieved.','Sediment is a suspended scalar with settling sink, without erosion or bed feedback; not GAIA.','Pollutant is hypothetical first-order decay, without species-specific chemistry.','ANA observed daily series are available in the project but are not imposed in this short assumed-flow scenario.']}


def export(out,mesh,meta):
    r=slf_io.read(out/'materials.slf')
    if not np.isfinite(r.values).all() or r.times[-1]!=3600:raise ValueError('Incomplete/nonfinite solver output')
    fields=[r.field(n,i) for i in range(len(r.times)) for n in ['CONSERVATIVE','POLLUTANT','SEDIMENT']]
    lo=min(x.min() for x in fields); hi=max(x.max() for x in fields)
    if lo < -1e-5 or hi>1.001:raise ValueError(f'Invalid concentration range {lo}, {hi}')
    weights=nodal_areas(mesh)
    inventories=[[float(weights@(r.field('WATER DEPTH',i)*r.field(n,i))) for n in ['CONSERVATIVE','POLLUTANT','SEDIMENT']] for i in range(len(r.times))]
    meta['range']=[float(lo),float(hi)];meta['result_sha256']=hashlib.sha256((out/'materials.slf').read_bytes()).hexdigest()
    payload={'metadata':meta,'x':mesh.x.tolist(),'y':mesh.y.tolist(),'triangles':mesh.ikle.tolist(),'times':r.times.tolist(),'materials':[{'id':'CONSERVATIVE','name':'Traçador conservativo','description':'Advecção e difusão, sem reação.'},{'id':'POLLUTANT','name':'Poluente degradável','description':'Meia-vida assumida: 30 minutos.'},{'id':'SEDIMENT','name':'Sedimento fino','description':'Deposição simplificada; velocidade de queda: 1 mm/s.'}],'concentrations':[[np.round(r.field(n,i),6).tolist() for n in ['CONSERVATIVE','POLLUTANT','SEDIMENT']] for i in range(len(r.times))],'inventory_normalized_m3':inventories}
    target=ROOT/'data/tapajos/poc';target.mkdir(exist_ok=True)
    (target/'materials.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
    (out/'provenance.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'frames':len(r.times),'range':meta['range'],'output':str(target)}))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',default='/opt/telemac');a=p.parse_args()
    out,mesh,meta=prepare(a.source)
    with (out/'solver-output.txt').open('w') as log:
        subprocess.run(['/app/docker/run-telemac','case.cas','--ncsize=1'],cwd=out,stdout=log,stderr=subprocess.STDOUT,check=True)
    logpath=out/'solver-output.txt'
    logpath.write_text("\n".join(line.rstrip() for line in logpath.read_text().splitlines()).rstrip()+"\n")
    export(out,mesh,meta)
