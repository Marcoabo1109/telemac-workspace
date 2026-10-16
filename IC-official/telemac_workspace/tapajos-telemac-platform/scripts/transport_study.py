"""Run the hypothetical sediment/metal screening model and step sensitivity."""
import json
from pathlib import Path
from backend.api.research_transport import Parameters, simulate, pareto_candidates


def main():
    out=Path(__file__).resolve().parents[1]/'reports/transport_screening'
    out.mkdir(parents=True,exist_ok=True)
    steps=[simulate(Parameters(dredge_kg_s=25), dt_s=dt) for dt in (120,60,30)]
    result={'status':'exploratory_not_calibrated','geometry':'assumed mixed volume; no spatial coupling to TELEMAC',
            'assumptions':'All Parameters values are hypothetical, not measured Tapajos sediment or metal properties.',
            'limitations':['No metal species or reactions beyond instantaneous linear partitioning.',
                           'No shear-dependent erosion, spatial plume, bed morphology feedback or ecological thresholds.',
                           'Pareto candidates do not establish a dredging recommendation or economic optimum.'],
            'step_sensitivity':steps, 'candidates':pareto_candidates()}
    (out/'study.json').write_text(json.dumps(result,indent=2)+'\n')
    print(out/'study.json')


if __name__=='__main__':main()
