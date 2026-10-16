"""Paired observational metrics. Scores alone do not establish calibration."""
import numpy as np


def metrics(observed, simulated):
    o=np.asarray(observed,dtype=float); s=np.asarray(simulated,dtype=float)
    if o.ndim != 1 or o.shape != s.shape or len(o) < 3:
        raise ValueError('At least three aligned pairs required')
    if not np.isfinite(o).all() or not np.isfinite(s).all():
        raise ValueError('Resolve missing pairs explicitly; no automatic filling')
    residual=s-o; variance=np.sum((o-o.mean())**2)
    correlation=float(np.corrcoef(o,s)[0,1]) if o.std()>0 and s.std()>0 else None
    kge=None
    if correlation is not None and o.mean()!=0:
        kge=float(1-np.sqrt((correlation-1)**2+(s.std()/o.std()-1)**2+(s.mean()/o.mean()-1)**2))
    return {'n':len(o),'rmse':float(np.sqrt(np.mean(residual**2))),
            'bias':float(residual.mean()),'mae':float(np.abs(residual).mean()),
            'nse':float(1-np.sum(residual**2)/variance) if variance>0 else None,
            'kge_2009':kge,'correlation':correlation}


def gauge_to_imbituba(gauge_cm, *, epoch_verified=False):
    """Historical EIA relation, forbidden for production until epochs are checked."""
    if not epoch_verified:
        raise ValueError('Confirm gauge/chart epochs and benchmark linkage first')
    values=np.asarray(gauge_cm,dtype=float)
    if not np.isfinite(values).all():
        raise ValueError('Finite gauge values required')
    return values/100+2.972


def require_calibration_evidence(*, bathymetry_verified, datum_verified,
                                 independent_in_domain_observations, held_out_period):
    evidence=locals()
    missing=[k for k,v in evidence.items() if not v]
    if missing:
        raise ValueError('Physical calibration blocked: '+', '.join(missing))
