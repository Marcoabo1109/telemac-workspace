"""Figuras, métricas pareadas e balanços dos arquivos realmente calculados."""
import json
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mt
from matplotlib.animation import FuncAnimation, PillowWriter
from run import ROOT, RUN, P, read, steady_test

out = ROOT/"poc/results"
out.mkdir(exist_ok=True)
models = {k:read(RUN/(k+".slf")) for k in ("r2d_culm","control","tracer","bed","bed_dye","cut","cut_dye")}
m = models["r2d_culm"]
tri = mt.Triangulation(m.x,m.y,m.ikle)
xy = np.stack([m.x,m.y],1)[m.ikle]
length = np.linalg.norm(xy-np.roll(xy,1,axis=1),axis=2)
a,b = xy[:,1]-xy[:,0],xy[:,2]-xy[:,0]
double_area = abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])
weights = np.bincount(m.ikle.ravel(),weights=np.repeat(double_area/6,3))


def field(model,name,t=-1):
    if name=="speed":
        return np.hypot(model.field("VELOCITY U",t),model.field("VELOCITY V",t))
    if name=="tau":
        h = model.field("WATER DEPTH",t)
        return np.divide(1000*9.81*field(model,"speed",t)**2,P["strickler"]**2*np.cbrt(h),out=np.zeros_like(h),where=h>0)
    return model.field(name,t)


def compare(left,right,names):
    return {name:norm(field(models[left],name)-field(models[right],name)) for name in names}


def norm(v):
    return dict(max_abs=float(abs(v).max()),L2=float(np.sqrt(np.sum(weights*v*v))))


def maps(filename,layers):
    fig,axes = plt.subplots(1,len(layers),figsize=(3.3*len(layers),5),layout="constrained")
    for ax,(title,values) in zip(np.atleast_1d(axes),layers):
        if values is None:
            ax.triplot(tri,lw=.25)
        else:
            col=ax.tripcolor(tri,values,shading="gouraud")
            fig.colorbar(col,ax=ax,orientation="horizontal")
        ax.set(title=title,xlabel="x (m)",ylabel="y (m)",aspect="equal")
    fig.savefig(out/filename,dpi=145)
    plt.close(fig)


maps("geometria.png",[("Malha",None),("Cota do leito (m)",field(m,"BOTTOM"))])
maps("hidro.png",[(label,field(m,k)) for label,k in zip(["H (m)","u (m/s)","v (m/s)","Velocidade (m/s)"],["WATER DEPTH","VELOCITY U","VELOCITY V","speed"])])
maps("pluma.png",[(f"C em {t:.0f} s",field(models["tracer"],"DYE",i)) for i,t in enumerate(models["tracer"].times) if i in (1,5,10)])
maps("leito.png",[(label,field(models[k],"BOTTOM")-field(models[k],"BOTTOM",0)) for label,k in [("GAIA Δz (m)","bed"),("Dragagem Δz (m)","cut"),("Dragagem + C Δz (m)","cut_dye")]])
maps("impacto.png",[(label,field(models["cut_dye"],k)-field(models["bed_dye"],k)) for label,k in [("ΔH (m)","WATER DEPTH"),("Δ velocidade (m/s)","speed"),("ΔC","DYE")]])
y=np.linspace(m.y.min(),m.y.max(),5000)
fig,axes=plt.subplots(1,2,figsize=(9,4),layout="constrained")
lines=[]
model=models["cut_dye"]
for ax,x in zip(axes,[170,200]):
    profiles=[mt.LinearTriInterpolator(tri,field(model,"BOTTOM",i))(np.full_like(y,x),y) for i in range(len(model.times))]
    for i in (0,5,10):
        ax.plot(y,profiles[i],label=f"{model.times[i]:.0f} s")
    ax.set(xlim=(360,650),title=f"x = {x} m",xlabel="y (m)",ylabel="Cota do leito (m)")
    ax.legend()
    lines.append((ax.plot(y,profiles[0],"k--")[0],profiles))
fig.savefig(out/"perfis.png",dpi=150)
def update(i):
    for line,profiles in lines:
        line.set_ydata(profiles[i])
    fig.suptitle(f"Dragagem e transporte de fundo · {model.times[i]:.0f} s")
FuncAnimation(fig,update,frames=len(model.times)).save(out/"perfis.gif",writer=PillowWriter(fps=3))
plt.close(fig)
metrics=dict(steady=steady_test(),passivo=compare("tracer","control",["WATER DEPTH","VELOCITY U","VELOCITY V","tau"]),fundo={},dragagem=compare("cut_dye","bed_dye",["BOTTOM","WATER DEPTH","speed","DYE"]),gaia_passivo=compare("bed_dye","bed",["BOTTOM"]),balanco={})
for name in ("tracer","bed","bed_dye","cut","cut_dye"):
    model=models[name]
    metrics["fundo"][name]=norm(field(model,"BOTTOM")-field(model,"BOTTOM",0))
    if name!="tracer":
        log=(RUN/(name+".log")).read_text()
        metrics["balanco"][name]=float(re.findall(r"CUMULATED LOST MASS \(INI-FINAL\+FLUXES\)\s+=\s*([-.\dE+]+)",log)[-1])
model=models["bed"]
alt=double_area/length.max(axis=1)
metrics["courant_adv_max_amostrado"]=max(float((P["time_step_s"]*field(model,"speed",i)[m.ikle].max(axis=1)/alt).max()) for i in range(len(model.times)))
(out/"metricas.json").write_text(json.dumps(metrics,indent=2)+"\n")
metrics["volume_removido_m3"]=float(re.search(r"removed volume\s+\[m\*\*3\]\s+:\s*([\d.E+-]+)",(RUN/"cut.log").read_text()).group(1))
metrics["concentracao_final"]=[float(f(field(models["tracer"],"DYE"))) for f in (np.min,np.max)]
(out/"metricas.json").write_text(json.dumps(metrics,indent=2)+"\n")
# Verificação independente: plano analítico -> BOTTOM -> interpolação nos triângulos.
from bathymetry import BathymetryAnalytic
plane=BathymetryAnalytic(lambda x,y: 0.001*x+0.002*y)
plane.write_to_selafin(m,RUN/"analytic_check.slf")
z=read(RUN/"analytic_check.slf").field("BOTTOM")
fig,(left,right)=plt.subplots(1,2,figsize=(8,4),layout="constrained")
fig.colorbar(left.tripcolor(tri,z,shading="gouraud"),ax=left,label="Cota (m)")
left.set(xlabel="x (m)",ylabel="y (m)",title="Plano gravado no Selafin",aspect="equal")
profile=mt.LinearTriInterpolator(tri,z)(np.full_like(y,170),y)
right.plot(y,profile,label="Selafin")
right.plot(y,np.ma.array(plane.evaluate(170,y),mask=profile.mask),"--",label="Analítico")
right.set(xlabel="y (m)",ylabel="Cota (m)",title="Seção x = 170 m")
right.legend()
fig.savefig(out/"batimetriateste.png",dpi=145)
plt.close(fig)
