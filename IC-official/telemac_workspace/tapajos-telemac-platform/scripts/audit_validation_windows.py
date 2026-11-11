"""Audit held-out daily forcing windows without interpolation or datum conversion."""
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'q_acara_m3_s': ('17650002', 'discharge', 'm3/s'),
    'h_itaituba_cm': ('17730000', 'stage', 'cm'),
    'q_bubure_m3_s': ('17710000', 'discharge', 'm3/s'),
    'h_bubure_cm': ('17710000', 'stage', 'cm'),
}


def audit(root=ROOT):
    output = root / 'data/tapajos/acquisition/2026-11-10'
    output.mkdir(parents=True, exist_ok=True)
    series, provenance = {}, {}
    for name, (station, variable, unit) in SOURCES.items():
        paths = list((root / 'data/tapajos/stations/processed').glob(f'ana_{station}_{variable}_consisted_*.csv'))
        if len(paths) != 1:
            raise ValueError(f'Ambiguous source: {name}')
        path = paths[0]
        records = {}
        with path.open() as stream:
            for row in csv.DictReader(stream):
                day = dt.date.fromisoformat(row['date'])
                if day in records:
                    raise ValueError(f'Duplicate date: {path}, {day}')
                if row['unit'] != unit:
                    raise ValueError(f'Unexpected unit: {path}')
                value = float(row['value'])
                if not math.isfinite(value) or row['consistency'] != '2':
                    continue
                records[day] = value
        series[name] = records
        provenance[name] = {'path':str(path.relative_to(root)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'unit':unit}
    report = {'date':'2026-11-10','calibration_year':2007,'sources':provenance,'years':{},'status':'coverage_audited_not_physically_validated'}
    for year in (2005,2006,2007,2008):
        start,end=dt.date(year,1,1),dt.date(year+1,1,1)
        days=[start+dt.timedelta(days=i) for i in range((end-start).days)]
        missing={key:[d.isoformat() for d in days if d not in values] for key,values in series.items()}
        common=[d for d in days if all(d in values for values in series.values())]
        report['years'][str(year)]={'expected_days':len(days),'common_valid_days':len(common),'coverage_percent':round(100*len(common)/len(days),3),'missing_by_series':missing,'complete':len(common)==len(days),'role':'calibration_candidate' if year==2007 else 'validation_candidate'}
    selected=2008 if report['years']['2008']['complete'] else None
    report['reserved_validation_year']=selected
    report['limitations']=['Coverage does not validate station representativeness or observation accuracy.', 'Itaituba is a boundary condition, not an independent internal validation gauge.', 'Bubure and Acara require spatial and routing checks.', 'Vertical datum, surveyed bathymetry and surveyed banks remain unresolved.', 'No interpolation, vertical correction or model execution performed.']
    out=output/'validation_2008_daily.csv'
    if not selected:
        out.unlink(missing_ok=True)  # Remove an obsolete product from an earlier audit.
    if selected:
        with out.open('w',newline='') as stream:
            writer=csv.writer(stream);writer.writerow(['date',*series])
            day=dt.date(selected,1,1)
            while day.year==selected:
                writer.writerow([day.isoformat(),*[values[day] for values in series.values()]])
                day+=dt.timedelta(days=1)
        report['derived_output']={'path':str(out.relative_to(root)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
    (output/'validation_windows.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__ == '__main__':
    result=audit()
    print(json.dumps({k:{x:v[x] for x in ('expected_days','common_valid_days','complete')} for k,v in result['years'].items()},indent=2))
