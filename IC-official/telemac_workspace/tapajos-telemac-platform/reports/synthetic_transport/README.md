# Resultados do laboratório sintético

Base de exemplos controlados, sem dados de amostragem e sem calibração do Tapajós.

## TELEMAC–GAIA/Nestor

Os erros abaixo são relativos à massa inicial da camada ativa; não são concentrações nem erros de previsão de campo.

| Grupo/caso | Balanço final acumulado | Estado |
|---|---:|---|
| gaia/mud_exchange | 1.407e-20 | checks_passed |
| gaia/mud_deposition | 4.397e-21 | checks_passed |
| gaia/mud_erosion | 8.794e-22 | checks_passed |
| gaia/mud_passive | 0.000e+00 | checks_passed |
| gaia/sand_bedload | não impresso | review_required |
| gaia/nestor_dig | 0.000e+00 | checks_passed |
| gaia/nestor_dump | 0.000e+00 | checks_passed |
| gaia/nestor_dig_dump | -7.340e-15 | checks_passed |
| sand_final_budget/sand_bedload | não impresso | review_required |
| sand_fixed/sand_fixed | não impresso | solver_failed |
| sand_diagnostic/sand_diagnostic | 9.601e-23 | checks_passed |

As referências oficiais são comparadas apenas quando a configuração numérica é correspondente. A tentativa de passo fixo foi rejeitada pelo solver FV e não é uma configuração recomendada. A rotina de diagnóstico da areia é comparada também com os resultados próprios originais, exigindo igualdade numérica exata. Os casos adaptativos de areia sem a seção final permanecem pendentes nesse critério, mesmo quando reproduzem a referência.

## TELEMAC–WAQTEL MICROPOL

| Configuração | Deposição: deriva relativa máxima | Troca: erro analítico máximo |
|---|---:|---:|
| micropol | 1.723e-03 | 8.252e-04 |
| micropol_dt360 | 7.581e-03 | 5.891e-03 |
| micropol_dt360_tight | 3.860e-08 | 1.657e-05 |

Critérios escolhidos para os testes: deriva relativa < 1e-6, concentrações não negativas dentro de 1e-8 e erro analítico absoluto < 1e-3. A configuração de passo 360 s e tolerância de difusão dos traçadores 1e-12 atende aos critérios. Esses limiares não são critérios ambientais.

## Tanque com elemento X e dragagem

- Sedimento: máximo residual relativo 3.656e-14.
- Elemento X: máximo residual relativo 6.183e-15.

Seis cenários × três passos temporais; soluções analíticas e esgotamento do estoque cobertos por testes. Custos, concentrações, Kd, tensões críticas e limites operacionais são hipotéticos.

## Evidências e uso

- `solver_audit.json`: resultados completos e comparação com referências.
- `input_validation.json`: leitura dos CAS pelos dicionários oficiais e hashes.
- `environment.json`: revisão do solver, imagem e suíte de testes.
- `study.json`: trajetórias e balanços do tanque.
- `synthetic_lab.png`: figura dos resultados.
- `../../docs/SYNTHETIC_SEDIMENT_LAB.md`: parâmetros, reprodução e limites.

**Limite de integração:** GAIA/Nestor e MICROPOL são exemplos independentes. O tanque não representa transporte espacial. Ainda é necessário implementar e verificar o compartilhamento de estoques entre GAIA, química e dragagem para um caso integrado; depois vêm dados reais, calibração e validação independente.
