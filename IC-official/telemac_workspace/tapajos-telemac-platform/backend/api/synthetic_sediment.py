"""Synthetic closed/open tank with cohesive sediment and a conserved element X.

Independent verification component, NOT a spatial GAIA-metal coupling.
SI throughout; no elemental decay. Kinetic sorption, erosion, deposition and
scheduled dredging have explicit paired transfers and external mass ledgers.
"""
from dataclasses import dataclass, asdict
import math


@dataclass(frozen=True)
class Tank:
    volume_m3: float = 1000.
    area_m2: float = 200.
    flow_m3_s: float = 0.
    initial_ssc_kg_m3: float = .05
    initial_bed_kg: float = 10000.
    initial_dissolved_kg_m3: float = 1e-6
    initial_suspended_metal_kg_kg: float = 2e-5
    initial_bed_metal_kg_kg: float = 2e-5
    inflow_ssc_kg_m3: float = 0.
    inflow_dissolved_kg_m3: float = 0.
    inflow_particle_metal_kg_kg: float = 0.
    settling_m_s: float = .001
    shear_pa: float = .05
    erosion_threshold_pa: float = .1
    deposition_threshold_pa: float = 1.
    partheniades_kg_m2_s: float = 1e-5
    kd_m3_kg: float = 10.
    desorption_s_1: float = .001
    dredge_kg_s: float = 0.
    dredge_start_s: float = 600.
    dredge_end_s: float = 1800.
    resuspension_fraction: float = .05
    mobilization_cost: float = 100.
    cost_per_kg_removed: float = .2

    def validate(self):
        if any(not math.isfinite(v) or v < 0 for v in asdict(self).values()):
            raise ValueError('All parameters must be finite and nonnegative')
        if min(self.volume_m3, self.area_m2, self.erosion_threshold_pa, self.deposition_threshold_pa) <= 0:
            raise ValueError('Geometry and critical stresses must be positive')
        if self.resuspension_fraction > 1 or self.dredge_end_s < self.dredge_start_s:
            raise ValueError('Invalid dredging window/fraction')


def partition(dissolved, particulate, suspended, volume, kd, desorption, dt):
    """Exact two-state kinetic exchange for a fixed suspended inventory.

    adsorption rate = k_des * Kd * SSC; equilibrium P/D = Kd * SSC.
    """
    adsorption = desorption*kd*suspended/volume
    rate = adsorption+desorption
    if rate == 0:
        return dissolved, particulate
    total = dissolved+particulate
    equilibrium = total*desorption/rate
    d = equilibrium+(dissolved-equilibrium)*math.exp(-rate*dt)
    return d, total-d


def simulate(p=Tank(), duration_s=3600., dt_s=10.):
    p.validate()
    if not all(math.isfinite(x) and x > 0 for x in (duration_s, dt_s)):
        raise ValueError('Duration and time step must be positive and finite')
    s = p.initial_ssc_kg_m3*p.volume_m3
    bed = p.initial_bed_kg
    d = p.initial_dissolved_kg_m3*p.volume_m3
    particulate = s*p.initial_suspended_metal_kg_kg
    bm = bed*p.initial_bed_metal_kg_kg
    initial_s, initial_m = s+bed, d+particulate+bm
    sin = sout = sremoved = minput = mout = mremoved = gross_dredged = 0.
    exposure = 0.; peak = d/p.volume_m3; t = 0.
    history = []

    def record():
        history.append({'time_s': t, 'suspended_kg': s, 'bed_kg': bed,
                        'dissolved_metal_kg': d, 'suspended_metal_kg': particulate,
                        'bed_metal_kg': bm, 'removed_sediment_kg': sremoved,
                        'removed_metal_kg': mremoved})
    record()
    while t < duration_s:
        # Align event boundaries exactly, regardless of requested step.
        limits = [duration_s-t, dt_s]
        limits += [x-t for x in (p.dredge_start_s, p.dredge_end_s) if x > t]
        dt = min(limits)
        before_d = d/p.volume_m3
        erosion_rate = p.area_m2*p.partheniades_kg_m2_s*max(p.shear_pa/p.erosion_threshold_pa-1, 0.)
        eroded = min(bed, erosion_rate*dt)
        eroded_m = bm*(eroded/bed) if bed else 0.
        bed -= eroded; bm -= eroded_m; s += eroded; particulate += eroded_m
        active = p.dredge_start_s <= t < p.dredge_end_s
        dredged = min(bed, p.dredge_kg_s*dt) if active else 0.
        dredged_m = bm*(dredged/bed) if bed else 0.
        bed -= dredged; bm -= dredged_m
        gross_dredged += dredged
        f = p.resuspension_fraction
        s += dredged*f; particulate += dredged_m*f
        sremoved += dredged*(1-f); mremoved += dredged_m*(1-f)
        # Exact continuously stirred tank update under constant inlet forcing.
        fraction = -math.expm1(-p.flow_m3_s/p.volume_m3*dt)
        for which, incoming_concentration in [('s', p.inflow_ssc_kg_m3), ('d', p.inflow_dissolved_kg_m3), ('p', p.inflow_ssc_kg_m3*p.inflow_particle_metal_kg_kg)]:
            old = {'s': s, 'd': d, 'p': particulate}[which]
            incoming = p.flow_m3_s*incoming_concentration*dt
            new = old*(1-fraction)+p.volume_m3*incoming_concentration*fraction
            outgoing = old+incoming-new
            if which == 's':
                s = new; sin += incoming; sout += outgoing
            else:
                minput += incoming; mout += outgoing
                if which == 'd': d = new
                else: particulate = new
        d, particulate = partition(d, particulate, s, p.volume_m3, p.kd_m3_kg, p.desorption_s_1, dt)
        probability = max(1-p.shear_pa/p.deposition_threshold_pa, 0.)
        fraction = -math.expm1(-p.settling_m_s*p.area_m2/p.volume_m3*probability*dt)
        deposited, deposited_m = s*fraction, particulate*fraction
        s -= deposited; bed += deposited; particulate -= deposited_m; bm += deposited_m
        after_d = d/p.volume_m3
        exposure += .5*(before_d+after_d)*dt; peak = max(peak, after_d)
        t += dt
        record()
    sediment = dict(initial=initial_s, inflow=sin, outflow=sout, removed=sremoved, final=s+bed)
    metal = dict(initial=initial_m, inflow=minput, outflow=mout, removed=mremoved, final=d+particulate+bm)
    for ledger in (sediment, metal):
        ledger['residual'] = ledger['final']+ledger['outflow']+ledger['removed']-ledger['initial']-ledger['inflow']
        ledger['relative_residual'] = ledger['residual']/max(ledger['initial']+ledger['inflow'], 1e-30)
    return {'status': 'synthetic_tank_not_spatial_gaia_coupling', 'species': 'hypothetical_conserved_element_X',
            'parameters': asdict(p), 'duration_s': duration_s, 'dt_s': dt_s,
            'sediment_kg': sediment, 'metal_kg': metal, 'history': history,
            'dissolved_peak_kg_m3': peak, 'dissolved_exposure_kg_s_m3': exposure,
            'gross_dredged_sediment_kg': gross_dredged,
            'illustrative_cost': (p.mobilization_cost if gross_dredged else 0.)+p.cost_per_kg_removed*sremoved}
