"""Static report figures for the synthetic lab (no observed data)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT/'reports/synthetic_transport'
    r = json.loads((folder/'study.json').read_text())
    a = json.loads((folder/'solver_audit.json').read_text())
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, ax = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')
    trace = r['scenarios']['dredging'][-1]['history']
    times = np.array([v['time_s'] for v in trace])/60
    for key, label in [('dissolved_metal_kg', 'Dissolvido'), ('suspended_metal_kg', 'Nas partículas'), ('removed_metal_kg', 'Removido')]:
        ax[0, 0].plot(times, [v[key]*1e3 for v in trace], label=label)
    ax[0, 0].axvspan(10, 30, alpha=.08, color='black')
    ax[0, 0].set(title='Elemento X: água e remoção no tanque', xlabel='Tempo (min)', ylabel='Massa (g)')
    ax[0, 0].legend()
    names = ['Original: 1 h', '360 s, tolerância original', '360 s, tolerância 1e-12']
    groups = ['micropol', 'micropol_dt360', 'micropol_dt360_tight']
    vals = [next(x for x in a[g] if x['id']=='micropol_deposition')['pollutant_relative_drift'] for g in groups]
    ax[0, 1].barh(names, vals, color=['#a84b31', '#a84b31', '#147d73'])
    ax[0, 1].set_xscale('log'); ax[0, 1].axvline(1e-6, color='black', ls='--', label='Critério 1e-6')
    ax[0, 1].set(title='WAQTEL: deriva de inventário do contaminante', xlabel='Máxima deriva relativa'); ax[0, 1].legend()
    for key, label in [('sediment_kg', 'Sedimento'), ('metal_kg', 'Elemento X')]:
        vals = [max(abs(x[key]['relative_residual']) for x in runs) for runs in r['scenarios'].values()]
        ax[1, 0].plot(range(len(vals)), np.maximum(vals, 1e-18), 'o-', label=label)
    ax[1, 0].set_yscale('log'); ax[1, 0].set_xticks(range(6), ['Troca', 'Deposição', 'Erosão', 'Fluxo', 'Dragagem', 'Exaustão'], rotation=25)
    ax[1, 0].text(.02, .02, 'Residual zero mostrado em 1e-18', transform=ax[1, 0].transAxes, fontsize=8)
    ax[1, 0].set(title='Tanque: conservação nos seis experimentos', ylabel='Máximo residual relativo'); ax[1, 0].legend()
    for x in r['dredging_candidates']:
        ax[1, 1].scatter(x['sediment_kg']['removed'], x['illustrative_cost'], color='#147d73' if x['feasible_illustrative'] else '#a84b31')
        ax[1, 1].annotate(str(x['parameters']['dredge_kg_s'])+' kg/s', (x['sediment_kg']['removed'], x['illustrative_cost']), xytext=(5, -12), textcoords='offset points', fontsize=8)
    ax[1, 1].axhline(1000, ls='--', color='gray'); ax[1, 1].axvline(500, ls='--', color='gray')
    ax[1, 1].set(title='Comparação ilustrativa de dragagem', xlabel='Sedimento removido (kg)', ylabel='Custo (unidade monetária arbitrária)', xlim=(-200, 6500), ylim=(-120, 1400))
    from matplotlib.lines import Line2D
    ax[1, 1].legend(handles=[Line2D([], [], marker='o', ls='', color='#147d73', label='Atende aos critérios de teste'), Line2D([], [], marker='o', ls='', color='#a84b31', label='Não atende')], loc='upper left', fontsize=8)
    fig.suptitle('Laboratório sintético • sem calibração ou dados de campo', fontsize=15)
    fig.savefig(folder/'synthetic_lab.png', dpi=160)
    plt.close(fig)


if __name__ == '__main__': main()
