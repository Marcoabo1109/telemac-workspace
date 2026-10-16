"""Exploratory mixed reach: sediment/metal mass ledgers, not a GAIA substitute.

SI units: volume m3, discharge m3/s, sediment kg, metal kg, Kd m3/kg.
Instantaneous linear partitioning; constant water volume; no bed feedback.
"""
from dataclasses import dataclass, asdict
import math


@dataclass(frozen=True)
class Parameters:
    volume_m3: float = 27_640_000.
    area_m2: float = 4_170_000.
    discharge_m3_s: float = 6000.
    settling_m_s: float = 0.0001
    kd_m3_kg: float = 1.
    suspended_in_kg_m3: float = 0.02
    dissolved_in_kg_m3: float = 1e-9
    particulate_in_kg_kg: float = 1e-6
    bed_initial_kg: float = 1e8
    bed_metal_kg_kg: float = 1e-6
    erosion_kg_s: float = 0.
    dredge_kg_s: float = 0.
    resuspension_fraction: float = 0.05

    def validate(self):
        if any(not math.isfinite(v) or v < 0 for v in asdict(self).values()):
            raise ValueError('Parameters must be finite and nonnegative')
        if min(self.volume_m3, self.area_m2) <= 0 or self.resuspension_fraction > 1:
            raise ValueError('Positive geometry and resuspension in [0, 1] required')


def simulate(p=Parameters(), duration_s=86400., dt_s=60.):
    """Conservative positive split updates; exact mixed-volume outflow per step.

    Returns final inventories and cumulative external ledgers. All defaults are
    hypotheses, including concentration and metal partition coefficient.
    """
    p.validate()
    if not all(math.isfinite(x) and x > 0 for x in (duration_s, dt_s)):
        raise ValueError('Positive finite duration and step required')
    s=p.suspended_in_kg_m3*p.volume_m3
    m=p.volume_m3*p.dissolved_in_kg_m3+s*p.particulate_in_kg_kg
    bed=p.bed_initial_kg; bm=bed*p.bed_metal_kg_kg
    initial_s=s+bed; initial_m=m+bm
    incoming_s=incoming_m=out_s=out_m=removed_s=removed_m=exposure=0.
    peak=0.; t=0.
    while t < duration_s:
        dt=min(dt_s, duration_s-t)
        # Bed removal is capped by available mass; metal follows bed composition.
        mobilized=min(bed, (p.erosion_kg_s+p.dredge_kg_s)*dt)
        dredged= mobilized*p.dredge_kg_s/(p.erosion_kg_s+p.dredge_kg_s) if mobilized else 0.
        removed=dredged*(1-p.resuspension_fraction)
        ratio=bm/bed if bed else 0.
        bed-=mobilized; bm-=mobilized*ratio
        s+=mobilized-removed; m+=(mobilized-removed)*ratio
        removed_s+=removed; removed_m+=removed*ratio
        si=p.discharge_m3_s*p.suspended_in_kg_m3*dt
        mi=p.discharge_m3_s*(p.dissolved_in_kg_m3+p.suspended_in_kg_m3*p.particulate_in_kg_kg)*dt
        s+=si; m+=mi; incoming_s+=si; incoming_m+=mi
        fraction=-math.expm1(-p.discharge_m3_s*dt/p.volume_m3)
        out_s+=s*fraction; out_m+=m*fraction
        s*=1-fraction; m*=1-fraction
        particulate=m*(p.kd_m3_kg*s/p.volume_m3)/(1+p.kd_m3_kg*s/p.volume_m3)
        fraction=-math.expm1(-p.settling_m_s*p.area_m2*dt/p.volume_m3)
        settled=s*fraction; deposited=particulate*fraction
        s-=settled; bed+=settled; m-=deposited; bm+=deposited
        dissolved=m/(1+p.kd_m3_kg*s/p.volume_m3)/p.volume_m3
        peak=max(peak,dissolved); exposure+=dissolved*dt; t+=dt
    sediment_residual=s+bed+out_s+removed_s-initial_s-incoming_s
    metal_residual=m+bm+out_m+removed_m-initial_m-incoming_m
    return {'status':'hypothetical_well_mixed_reach_not_spatial_prediction',
            'parameters':asdict(p), 'duration_s':duration_s, 'dt_s':dt_s,
            'sediment_kg':{'suspended':s,'bed':bed,'initial_total':initial_s,'inflow':incoming_s,'outflow':out_s,'removed':removed_s,'balance_residual':sediment_residual},
            'metal_kg':{'water_total':m,'bed':bm,'initial_total':initial_m,'inflow':incoming_m,'outflow':out_m,'removed':removed_m,'balance_residual':metal_residual},
            'dissolved_peak_kg_m3':peak,'dissolved_exposure_kg_s_m3':exposure}


def pareto_candidates(rates=(0.,10.,25.,50.), **kwargs):
    """Exploratory tradeoff: maximize removed sediment, minimize dissolved exposure.

    No economic optimum: costs, targets and environmental constraints are absent.
    """
    rows=[simulate(Parameters(dredge_kg_s=float(rate)), **kwargs) for rate in rates]
    for row in rows:
        removed=row['sediment_kg']['removed']; exposure=row['dissolved_exposure_kg_s_m3']
        row['pareto']=not any(
            x['sediment_kg']['removed']>=removed and x['dissolved_exposure_kg_s_m3']<=exposure
            and (x['sediment_kg']['removed']>removed or x['dissolved_exposure_kg_s_m3']<exposure)
            for x in rows)
    return rows
