"""TELEMAC grid/time refinement on a fixed exploratory geometry, never calibration."""
import argparse
import asyncio
import copy
import hashlib
import json
import re
from pathlib import Path
import numpy as np
from backend.api import slf_io, cli_io, cas_parser, telemac_runner as runner

ROOT=Path(__file__).resolve().parents[1]


def refine(mesh, rows):
    """Split every triangle into four; exactly retain piecewise-linear bed/domain."""
    m=copy.deepcopy(mesh); xy=list(zip(m.x,m.y)); z=list(m.values[0,0]); mid={}
    def midpoint(a,b):
        key=tuple(sorted((int(a),int(b))))
        if key not in mid:
            mid[key]=len(xy);xy.append(tuple((np.array(xy[a])+xy[b])/2));z.append((z[a]+z[b])/2)
        return mid[key]
    tri=[]
    for a,b,c in m.ikle:
        ab,bc,ca=midpoint(a,b),midpoint(b,c),midpoint(c,a)
        tri.extend([[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]])
    refined=[]
    for i,r in enumerate(rows):
        nxt=rows[(i+1)%len(rows)]; refined.append(list(r))
        new=list(r) if r[:3]==nxt[:3] else [2,2,2,0.,0.,0.,0.,2,0.,0.,0.,0,0]
        new[11]=midpoint(r[11]-1,nxt[11]-1)+1;refined.append(new)
    m.x,m.y=np.array(xy).T;m.ikle=np.array(tri);m.ipobo=np.zeros(len(xy),int)
    for i,r in enumerate(refined):r[12]=i+1;m.ipobo[r[11]-1]=i+1
    m.values=np.array(z)[None,None,:];m.precision=8;m.title=m.title[:72]+b'SERAFIND'
    return m,refined


def nodal_areas(m):
    t=m.ikle;x=m.x[t];y=m.y[t]
    area=np.abs((x[:,1]-x[:,0])*(y[:,2]-y[:,0])-(x[:,2]-x[:,0])*(y[:,1]-y[:,0]))/2
    w=np.zeros(len(m.x))
    for i in range(3):np.add.at(w,t[:,i],area/3)
    return w


def compare(a,b):
    """Weighted final-field RMS on finer mesh using actual triangular interpolation."""
    import matplotlib.tri as mt
    w=nodal_areas(b); ta=mt.Triangulation(a.x,a.y,a.ikle);out={}
    for name in ['WATER DEPTH','FREE SURFACE','VELOCITY U','VELOCITY V','PASSIVE TRACER']:
        av=a.field(name,-1); bv=b.field(name,-1)
        v=mt.LinearTriInterpolator(ta,av)(b.x,b.y)
        if np.ma.getmaskarray(v).any():raise ValueError('Comparison outside common domain')
        delta=np.asarray(v)-bv
        out[name]={'rms':float(np.sqrt(np.sum(w*delta**2)/w.sum())),'max_abs':float(np.abs(delta).max())}
    out['velocity_vector_rms_m_s']=float(np.hypot(out['VELOCITY U']['rms'],out['VELOCITY V']['rms']))
    return out


def balance(log):
    patterns={'water_relative':r'RELATIVE ERROR CUMULATED ON VOLUME:\s*([\d.E+-]+)',
        'tracer_relative':r'FINAL BALANCE OF PASSIVE TRACER.*?RELATIVE ERROR\s*:\s*([\d.E+-]+)'}
    values={}
    for k,p in patterns.items():
        match=re.search(p,log,re.S)
        if not match:raise ValueError('Missing solver balance: '+k)
        values[k]=float(match.group(1).replace('D','E'))
    return values


async def study(out, levels=2, duration=3600, flux_priority=False):
    if levels < 1 or duration <= 0 or duration % 120:
        raise ValueError('Use levels >= 1 and duration a positive multiple of 120 s')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    base=ROOT/'models/tapajos_trecho1';mesh=slf_io.read(base/'mesh.slf');rows=cli_io.parse((base/'mesh.cli').read_text())
    meshes=[(mesh,rows)]
    for _ in range(levels):meshes.append(refine(*meshes[-1]))
    specs=[('characteristics_L0_dt2',0,2.,1)]+[(f'psi_L{i}_dt2',i,2.,5) for i in range(levels+1)]+[(f'psi_L{levels}_dt{dt:g}',levels,dt,5) for dt in (1.,.5)]
    outputs={};summaries=[]
    for name,level,dt,scheme in specs:
        folder=out/name;folder.mkdir(exist_ok=True)
        m,cli=meshes[level];params=cas_parser.parse((base/'tapajos.cas').read_text())
        params.update({'TIME STEP':str(dt),'NUMBER OF TIME STEPS':str(int(duration/dt)), 'GRAPHIC PRINTOUT PERIOD':str(int(120/dt)), 'LISTING PRINTOUT PERIOD':str(int(600/dt)), 'TYPE OF ADVECTION':f'1;5;{scheme}'})
        if flux_priority and scheme==5:
            params['TREATMENT OF FLUXES AT THE BOUNDARIES']='2'
            params['OPTION FOR THE DIFFUSION OF TRACERS']='2'
        files={'mesh.slf':slf_io.write(m),'mesh.cli':cli_io.generate(cli).encode(),'tapajos.qsl':(base/'tapajos.qsl').read_bytes()}
        signature=hashlib.sha256(cas_parser.generate(params).encode()+b''.join(files.values())).hexdigest()
        if (folder/'summary.json').exists() and json.loads((folder/'summary.json').read_text()).get('input_sha256')==signature:
            record=json.loads((folder/'summary.json').read_text());result=slf_io.read(folder/'result.slf')
        else:
            job=runner.prepare(params,files);await runner.run(job)
            log='\n'.join(job['logs']).rstrip()+'\n';(folder/'solver-output.txt').write_text(log)
            if job['status']!='completed':raise RuntimeError(name+' failed: '+log[-2500:])
            result=slf_io.read(job['path']/job['result'])
            if not np.isfinite(result.values).all() or result.times[-1]!=duration:raise ValueError('Invalid result')
            bal=balance(log);h=result.field('WATER DEPTH',-1);c=result.field('PASSIVE TRACER',-1)
            record={'name':name,'level':level,'dt_s':dt,'tracer_scheme':scheme,'nodes':len(m.x),'triangles':len(m.ikle),'duration_s':duration,'input_sha256':signature,'job':job['id'],'balance':bal,'min_depth_all_frames_m':float(min(result.field('WATER DEPTH',i).min() for i in range(len(result.times)))),'tracer_range_all_frames':[float(result.values[:,5].min()),float(result.values[:,5].max())],'final_water_volume_m3':float(nodal_areas(result)@h),'final_tracer_inventory_normalized_m3':float(nodal_areas(result)@(h*c))}
            (folder/'result.slf').write_bytes(slf_io.write(result));(folder/'case.cas').write_text(cas_parser.generate(params));(folder/'summary.json').write_text(json.dumps(record,indent=2)+'\n')
        # Output SERAFIN can quantize UTM coordinates; compare on exact input mesh.
        result.x=m.x.copy();result.y=m.y.copy()
        outputs[name]=result;summaries.append(record);print(json.dumps(record),flush=True)
    spatial=[{'coarse':f'psi_L{i}_dt2','fine':f'psi_L{i+1}_dt2','difference':compare(outputs[f'psi_L{i}_dt2'],outputs[f'psi_L{i+1}_dt2'])} for i in range(levels)]
    temporal=[{'coarse':f'psi_L{levels}_dt{a}','fine':f'psi_L{levels}_dt{b}','difference':compare(outputs[f'psi_L{levels}_dt{a}'],outputs[f'psi_L{levels}_dt{b}'])} for a,b in [('2','1'),('1','0.5')]]
    def passes(c):
        d=c['difference'];return d['FREE SURFACE']['rms']<.02 and d['velocity_vector_rms_m_s']<.03 and d['PASSIVE TRACER']['rms']<.02
    report={'status':'numerical_experiment_not_physical_validation','flux_priority':flux_priority,'comparison_coordinates':'exact input mesh coordinates, avoiding SERAFIN output float32 rounding','domain':'fixed schematic geometry and piecewise-linear bed; midpoint refinement does not add bathymetric knowledge','comparisons_at':f'final {duration} s fields; area-weighted RMS','criteria':{'free_surface_rms_m':.02,'velocity_vector_rms_m_s':.03,'tracer_rms':.02,'water_balance_abs':1e-4,'tracer_balance_abs':1e-3,'kind':'provisional research tolerances, not regulatory limits'},'cases':summaries,'spatial':spatial,'temporal':temporal,'finest_pair_spatial_pass':passes(spatial[-1]),'finest_pair_temporal_pass':passes(temporal[-1]),'all_psi_balances_pass':all(abs(r['balance']['water_relative'])<1e-4 and abs(r['balance']['tracer_relative'])<1e-3 for r in summaries if r['tracer_scheme']==5)}
    (out/'study.json').write_text(json.dumps(report,indent=2)+'\n')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for a,comparisons,title in zip(ax,[spatial,temporal],['Refinamento espacial','Refinamento temporal']):
        for field in ['FREE SURFACE','PASSIVE TRACER']:
            a.plot(range(len(comparisons)),[v['difference'][field]['rms'] for v in comparisons],'-o',label=field)
        a.set_xticks(range(len(comparisons)),[v['coarse']+' → '+v['fine'] for v in comparisons],rotation=15,fontsize=7);a.set_yscale('log');a.set_title(title);a.set_ylabel('RMS: superfície [m]; traçador [1]');a.legend(fontsize=8);a.grid(alpha=.2)
    fig.savefig(out/'convergence.png',dpi=150);plt.close(fig)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',default='reports/convergence');p.add_argument('--levels',type=int,default=2);p.add_argument('--duration',type=int,default=3600);p.add_argument('--flux-priority',action='store_true');a=p.parse_args();asyncio.run(study(a.out,a.levels,a.duration,a.flux_priority))
