"""Write a reviewable summary from recorded solver and component evidence."""
import json
from pathlib import Path
from scripts.sediment_benchmarks import ROOT


def main():
    out = ROOT/'reports/synthetic_transport'
    audit = json.loads((out/'solver_audit.json').read_text())
    tank = json.loads((out/'study.json').read_text())
    lines = ['# Resultados do laboratório sintético', '',
             'Base de exemplos controlados, sem dados de amostragem e sem calibração do Tapajós.', '',
             '## TELEMAC–GAIA/Nestor', '',
             'Os erros abaixo são relativos à massa inicial da camada ativa; não são concentrações nem erros de previsão de campo.', '',
             '| Grupo/caso | Balanço final acumulado | Estado |', '|---|---:|---|']
    for group in ('gaia', 'sand_final_budget', 'sand_fixed', 'sand_diagnostic'):
        for r in audit.get(group, []):
            error = r.get('sediment_relative_initial_active_layer_final')
            lines.append(f"| {group}/{r['id']} | {error:.3e} | {r['status']} |" if error is not None else f"| {group}/{r['id']} | não impresso | {r['status']} |")
    lines += ['', 'As referências oficiais são comparadas apenas quando a configuração numérica é correspondente. A tentativa de passo fixo foi rejeitada pelo solver FV e não é uma configuração recomendada. A rotina de diagnóstico da areia é comparada também com os resultados próprios originais, exigindo igualdade numérica exata. Os casos adaptativos de areia sem a seção final permanecem pendentes nesse critério, mesmo quando reproduzem a referência.', '',
              '## TELEMAC–WAQTEL MICROPOL', '',
              '| Configuração | Deposição: deriva relativa máxima | Troca: erro analítico máximo |', '|---|---:|---:|']
    for group in ('micropol', 'micropol_dt360', 'micropol_dt360_tight'):
        rows = audit[group]
        drift = next(r['pollutant_relative_drift'] for r in rows if r['id']=='micropol_deposition')
        error = max(r.get('max_abs_analytic_error', 0) for r in rows)
        lines.append(f'| {group} | {drift:.3e} | {error:.3e} |')
    lines += ['', 'Critérios escolhidos para os testes: deriva relativa < 1e-6, concentrações não negativas dentro de 1e-8 e erro analítico absoluto < 1e-3. A configuração de passo 360 s e tolerância de difusão dos traçadores 1e-12 atende aos critérios. Esses limiares não são critérios ambientais.', '',
              '## Tanque com elemento X e dragagem', '']
    for key, name in [('sediment_kg', 'Sedimento'), ('metal_kg', 'Elemento X')]:
        maximum = max(abs(x[key]['relative_residual']) for rows in tank['scenarios'].values() for x in rows)
        lines.append(f'- {name}: máximo residual relativo {maximum:.3e}.')
    lines += ['', 'Seis cenários × três passos temporais; soluções analíticas e esgotamento do estoque cobertos por testes. Custos, concentrações, Kd, tensões críticas e limites operacionais são hipotéticos.', '',
              '## Evidências e uso', '',
              '- `solver_audit.json`: resultados completos e comparação com referências.',
              '- `input_validation.json`: leitura dos CAS pelos dicionários oficiais e hashes.',
              '- `environment.json`: revisão do solver, imagem e suíte de testes.',
              '- `study.json`: trajetórias e balanços do tanque.',
              '- `synthetic_lab.png`: figura dos resultados.',
              '- `../../docs/SYNTHETIC_SEDIMENT_LAB.md`: parâmetros, reprodução e limites.', '',
              '**Limite de integração:** GAIA/Nestor e MICROPOL são exemplos independentes. O tanque não representa transporte espacial. Ainda é necessário implementar e verificar o compartilhamento de estoques entre GAIA, química e dragagem para um caso integrado; depois vêm dados reais, calibração e validação independente.', '']
    (out/'README.md').write_text('\n'.join(lines))


if __name__ == '__main__': main()
