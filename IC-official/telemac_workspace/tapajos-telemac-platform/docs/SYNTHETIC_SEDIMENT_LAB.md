# Laboratório sintético de sedimentos, micropoluentes e dragagem

## Escopo acordado em 13/10/2026

Consolidação desta entrega: 14/10/2026.

Desenvolver e verificar os processos com exemplos sintéticos antes de processar
amostras e levantamentos do Tapajós. Os bloqueios de dados reais continuam válidos
para a aplicação ao rio, mas não impedem esses experimentos controlados.

Esta base contém três componentes distintos:

1. **TELEMAC-2D + GAIA + Nestor:** transporte sedimentar, erosão/deposição,
   evolução de fundo e operações de dragagem/despejo nos exemplos oficiais.
2. **TELEMAC-2D + WAQTEL MICROPOL:** transferência reversível de contaminante entre
   água, partículas e leito em bacia sintética em repouso.
3. **Tanque conservativo em Python:** elemento hipotético X, sorção cinética,
   erosão, deposição, remoção e ressuspensão com calendário de dragagem, balanços
   explícitos e comparação de custos/restrições ilustrativos.

**Ainda não existe acoplamento espacial conjunto GAIA–MICROPOL–metais nesta
entrega.** Não somar os sedimentos internos do MICROPOL aos do GAIA: isso
contabilizaria duas vezes o estoque. O tanque também não é uma pluma 2D.

## Entrada recomendada

Consulte `reports/synthetic_transport/recommended_cases.json` para a seleção de
casos aprovados e `reports/synthetic_transport/README.md` para os resultados.
Foram aprovados 79 testes de software, com um opcional ignorado. Os CAS passaram
por leitura dos dicionários oficiais e conferência dos arquivos de entrada.
As tentativas reprovadas permanecem identificadas nos relatórios e não integram
a seleção recomendada.

## Casos GAIA/Nestor

Entradas, fontes Fortran, referências oficiais, resultados próprios e logs estão
em `models/synthetic_sediment`. `manifest.json` registra hashes e alterações.
Arquivos `*_ref*`/`f2d_*` são referências distribuídas upstream, nunca resultados
produzidos por esta execução. `execution.json` registra os resultados novos.

| Caso | Processo e hipótese |
|---|---|
| mud_exchange | Lama coesiva: erosão e deposição ativas |
| mud_deposition | Mesmo caso, constante de Partheniades zerada |
| mud_erosion | Mesmo caso, velocidade de queda zerada |
| mud_passive | Erosão e deposição zeradas: referência de transporte passivo |
| sand_bedload | Areia de 0,32 mm, densidade 2.650 kg/m³, transporte por arraste; formulação de volumes finitos oficial |
| nestor_dig | Operação programada Dig_by_time, com destino configurado no exemplo |
| nestor_dump | Operações de despejo do exemplo oficial |
| nestor_dig_dump | Dragagem por critério e despejo do exemplo oficial |

Na lama: diâmetro nominal 60 µm, densidade 1.600 kg/m³, concentração do leito
100 kg/m³, tensão crítica de erosão 0,1 Pa, tensão crítica de deposição 1.000 Pa,
velocidade de queda 0,01 m/s e constante de Partheniades 0,001 kg/m²/s no caso
completo. Esses valores são do teste numérico, **não uma caracterização do
Tapajós**. A concentração inicial em suspensão é definida pela rotina Fortran.
Os CAS e fontes de cada caso são a especificação completa; os casos Nestor
possuem classes, frações, camadas e porosidade próprias.

O balanço GAIA inclui a contribuição `NESTOR MASS`; remoção/despejo intencional
não deve ser confundido com erro numérico. A auditoria também compara os campos
finais com referências oficiais e exige a seção de balanço sedimentar final;
um erro de um passo isolado não aprova o balanço acumulado. As variantes isoladas de lama não possuem uma
referência oficial própria: são verificadas por execução e balanço.

## Micropoluentes como base para metais

`models/synthetic_micropollutant` contém três casos derivados de
`waqtel/waq2d_micropol` da revisão oficial v8p5r0. Bacia de 10 × 10 m,
profundidade 1 m, 159 nós e 272 triângulos, sem escoamento:

- `micropol_deposition`: contaminante inicialmente adsorvido, desorção e deposição;
- `micropol_adsorption`: inicialmente dissolvido, sem deposição;
- `micropol_desorption`: inicialmente adsorvido, sem deposição.

Não foi atribuído o nome de um metal medido. O contaminante é um substituto
matemático conservativo, com constante de desintegração zero. Elementos metálicos
não desaparecem por uma lei de decaimento de poluente orgânico; futuras reações
entre espécies devem conservar o total do elemento.

A convenção física do exemplo é documentada em
`examples/waqtel/waq2d_micropol/doc/waq2d_micropol.tex` upstream. Os rótulos
herdados `mg/l` do SERAFIN não distinguem estoques de leito por área de
concentrações na água por volume. A auditoria integra os termos de leito por área
e os termos na água por volume; não interpreta esses valores como concentrações
medidas de metal. A profundidade constante de 1 m desse benchmark não testa
conversões em profundidades variáveis.

O passo original é 3.600 s, em 3.200 passos. Foram preservadas as execuções
originais e preparado refinamento em `models/synthetic_micropollutant_dt360`.
A configuração recomendada está em `models/synthetic_micropollutant_dt360_tight`: passo de 360 s e
`ACCURACY FOR DIFFUSION OF TRACERS = 1e-12`. A configuração refinada apenas no
passo apresentou piora de precisão, documentada nos resultados. A tolerância
apertada reduziu a deriva máxima do contaminante a 3,86 × 10⁻⁸ e o erro absoluto
de troca contra a solução analítica a 1,66 × 10⁻⁵. A auditoria registra deriva
de massa e erro contra solução analítica de troca reversível. Uma execução concluída não é automaticamente aprovada no balanço.

## Tanque com espécie X e dragagem

Configuração editável: `models/synthetic_transport/scenarios.json`.
Todos os parâmetros estão explícitos em SI. O volume é fixo; quando há vazão,
a entrada e a saída têm a mesma vazão.

- SSC em kg/m³; estoques de sedimento e metal em kg;
- metal dissolvido em kg/m³ e associado ao sólido em kg/kg;
- Kd em m³/kg, desorção em s⁻¹ e queda em m/s;
- erosão de Partheniades limitada ao estoque, com tensão imposta;
- deposição reduzida pela tensão em relação ao limiar;
- dragagem em kg/s, limitada ao estoque, com início e fim em segundos;
- parte ressuspensa volta à água com a composição do material removido;
- custos em unidades monetárias arbitrárias, não em preços pesquisados.

A troca cinética usa `k_ads = k_des × Kd × SSC`; em equilíbrio,
`metal_particulado / metal_dissolvido = Kd × SSC`. A solução dessa troca em cada
subpasso é exata para SSC constante. A composição com erosão/deposição/fluxos é
sequencial e requer estudo de passo temporal.

O balanço de cada material é:

`estoque_final + saída + remoção − estoque_inicial − entrada = residual`.

A espécie X não inclui especiação, redox, metilação, toxicidade ou reação
irreversível. O leito do tanque não muda a hidrodinâmica. O modelo tem uma classe
coesiva; exemplos GAIA/Nestor cobrem outras classes sem implicar mistura química
já implementada no tanque.

Os cenários incluem troca pura, deposição, erosão, fluxo aberto, dragagem e
esgotamento do leito. Passos de 20, 10 e 5 s verificam sensibilidade. Os testes
incluem soluções analíticas de troca, deposição e renovação de água, alinhamento
do calendário e conservação mesmo com remoção superior ao estoque disponível.

Os candidatos de dragagem são filtrados por massa mínima, pico dissolvido e
custo máximo; a comparação de Pareto usa custo e exposição integrada. Os limiares
são **valores de teste**, sem significado regulatório ou recomendação operacional.

## Reprodução

Na raiz da plataforma, no ambiente Python do projeto:

```bash
python -m pytest -q
python -m scripts.synthetic_transport_study
python -m scripts.audit_synthetic_benchmarks
```

Para preparar novas cópias, sem sobrescrever execuções existentes:

```bash
python -m scripts.sediment_benchmarks prepare --source /caminho/telemac --out models/nova_suite_gaia
python -m scripts.sediment_benchmarks prepare --source /caminho/telemac --group waqtel --time-step 360 --tracer-accuracy 1e-12 --out models/nova_suite_waqtel
```

O checkout fonte deve estar no commit
`d1bff193746fd76425d7715a6e4d20d42eb8877e` (v8p5r0). Preserva-se a licença upstream.
O executável deve ser o TELEMAC compilado dessa revisão. Para executar as cópias
preparadas com a imagem já construída:

```bash
docker run --rm \
  -e OMPI_ALLOW_RUN_AS_ROOT=1 -e OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 \
  -v "$PWD:/app" -w /app tapajos-platform-backend:latest \
  python3.11 -m scripts.sediment_benchmarks run \
  --out models/nova_suite_gaia --executable /app/docker/run-telemac
```

As variáveis MPI acima são para o usuário interno do container. A execução é pela
CLI revisada; não se liberou upload de código Fortran na API web. Use `--case`
para um caso específico. Entradas modificadas após a preparação são rejeitadas
pelo hash; resultados anteriores não são sobrescritos.

## Controle de saída do canal de areia

O caso original adaptativo completou 1.800 s e reproduziu a referência, mas não
imprimiu a seção sedimentar acumulada final. `models/synthetic_sand_final_budget`
repete o mesmo caso com `NUMBER OF TIME STEPS = 216891`, número observado na
execução original. A duração e a física são preservadas; o objetivo é sincronizar
a impressão final GAIA com o término do cálculo adaptativo. Essa tentativa
também não imprimiu o balanço acumulado e foi preservada como evidência negativa.
A variante `models/synthetic_sand_fixed` usa passo fixo de 0,005 s, 360.000 passos
e a mesma duração física de 1.800 s, mas foi rejeitada: o esquema de volumes
finitos dessa versão exige passo variável. Ela está preservada como tentativa
reprovada, não como exemplo pronto para uso.

A rotina de diagnóstico em `models/synthetic_sand_diagnostic` altera somente as
duas condições de impressão de `mass_balance.f` para incluir a iteração final
observada no caso original (216891). Isso evita a indicação de término atrasada
no caminho FV do acoplamento. O hash do código upstream, o hash do log original
e as duas substituições estão no manifesto. Não é uma correção geral para
outros casos adaptativos; o diagnóstico é específico deste benchmark. A auditoria
exige igualdade exata dos campos finais com a execução original, além do balanço
acumulado. O diagnóstico passou: residual acumulado de 4,58 × 10⁻¹⁶ kg
e igualdade exata de todas as séries de campos TELEMAC/GAIA com a execução
original. O erro relativo à massa inicial da camada ativa foi 9,60 × 10⁻²³.

Para reproduzir a preparação, após executar a referência original:

```bash
python -m scripts.prepare_sand_diagnostic --source /caminho/telemac --out models/novo_diagnostico_areia
```

O caso Nestor por critério completa 120.000 s, mas o último frame gráfico é
116.640 s devido à frequência original de saída. A auditoria compara esse frame
com a referência no mesmo instante; o término completo é confirmado no log.

## Continuação sem depender ainda de campo

1. Concluir os critérios de conservação e independência temporal dos casos que
   a auditoria mantiver como `review_required`; manter resultados negativos.
2. Criar canal sintético com escoamento e verificar serial/MPI, classes e malha.
3. Desenvolver um contrato único de estoques/fluxos GAIA–química e testar trocas
   em repouso e transporte antes de incluir Nestor; evitar dupla contagem.
4. Integrar a transferência de metal nas operações Nestor e auditar remoção,
   ressuspensão e destino por classe/camada, com profundidade variável.
5. Comparar cenários sintéticos com objetivos explícitos de pesquisa.
6. Por último, substituir hipóteses por geometria, amostras, séries e custos
   observados, revisar a adequação das equações, calibrar e validar em dados
   independentes. A transferência ao rio não se resume a trocar números.
