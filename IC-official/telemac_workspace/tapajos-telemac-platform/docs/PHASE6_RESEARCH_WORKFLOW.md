# Continuação científica — 09/10/2026

**Mudança de sequência em 13/10/2026:** desenvolver primeiro a base sintética de sedimentos, metais e dragagem, conforme [laboratório sintético](SYNTHETIC_SEDIMENT_LAB.md). Os bloqueios de campo descritos abaixo continuam válidos para aplicar e validar o modelo no Tapajós; não impedem os benchmarks controlados.

## Resultado e limites

Há séries observadas suficientes para preparar períodos de estudo, mas a geometria e o vínculo vertical ainda impedem calibração física. Foram executados 12 ensaios TELEMAC de uma hora, com duas formulações do traçador, três malhas e três passos temporais na malha fina. A formulação conservativa passou no balanço; a independência espacial do traçador **não** foi atingida. Não há modelo calibrado nem recomendação de dragagem.

## 1. Dados e referência vertical

As 13 séries ANA já adquiridas permanecem em `data/tapajos/stations/processed`, com XML e manifestos de origem. Não foi necessário acesso autenticado adicional. O usuário dispõe apenas do tutorial HidroWeb. O cenário observado de 2007 contém 365 dias completos de vazão Acará e nível Itaituba; não preencher lacunas automaticamente nem apresentar hipóteses como observações.

As cartas CHM 4382B/4383 já baixadas são imagens RGB georreferenciadas. Seus pixels não representam profundidade numérica. A próxima aquisição é digitalizar sondagens com coordenadas, edição, unidade, incerteza e referência vertical, ou obter levantamento ADCP/eco­batímetro. Um mapa de profundidades por classes também não substitui uma nuvem de sondagens.

Foi consultado o [EIA ETC HBSA Tapajós](https://portos.terradedireitos.org.br/wp-content/uploads/2024/02/EIA-Hidrovias-do-Brasil.pdf), com inspeção visual das páginas 182 e 217. A página 182 informa `Z_Imbituba = Z_NR + 5,242 m`. A página 217 cita a ficha F-43-4382B-001/82, versão 1/2009, e informa NR 2,270 m acima do zero da régua. Disso decorrem:

- `nível_NR = régua_cm / 100 − 2,270`;
- `nível_Imbituba = régua_cm / 100 + 2,972`;
- `fundo_Imbituba = 5,242 − profundidade_positiva_abaixo_NR`.

Essas relações são uma **evidência histórica local**, com incerteza ainda desconhecida. Confirmar ficha original, marcos, época do zero da régua e edição das cartas antes de aplicá-las a 2007. O registro com hash do documento está em `data/tapajos/vertical_datum/itaituba_historical_reference.json`; a função de conversão exige confirmação explícita de compatibilidade temporal. O catálogo principal não foi promovido a “datum verificado”.

O EIA também apresenta correntometria pontual nas páginas 223–224. Profundidades de amostragem não são cotas de fundo. Sem data exata, CRS confirmado e cobertura do domínio, esses perfis não entram como alvos de calibração.

## 2. Verificação numérica executada

Geometria exploratória original, fundo linear por elemento e contornos preservados por subdivisão uniforme. Refinar não acrescenta informação batimétrica. Malhas: 228/852/3.291 nós e 397/1.588/6.352 triângulos. Passos: 2, 1 e 0,5 s; duração 3.600 s. Os testes são de partida, não demonstram equilíbrio permanente ou desempenho durante um ano hidrológico.

| Indicador | Resultado conservativo | Critério provisório |
|---|---:|---:|
| Maior erro relativo absoluto de balanço da água | 4,99 × 10⁻⁷ | 10⁻⁴ |
| Maior erro relativo absoluto de balanço do traçador | 8,65 × 10⁻⁶ | 10⁻³ |
| RMS espacial de superfície, L1→L2 | 0,00199 m | 0,02 m |
| RMS espacial do vetor velocidade, L1→L2 | 0,00331 m/s | 0,03 m/s |
| RMS espacial de traçador, L1→L2 | **0,03396** | **0,02 — falhou** |
| RMS temporal do traçador, 1→0,5 s | 0,000503 | 0,02 |

O traçador permaneceu entre 0 e 1, sem profundidades negativas nos frames gravados. Isso não verifica todos os passos internos. O balanço vem do relatório do solver; inventários nodais auxiliares são aproximações por áreas concentradas.

A referência por características apresentou erro de traçador −0,008688563 (−0,869%). Trocar somente advecção para PSI não resolveu. A combinação `TYPE OF ADVECTION = 1;5;5`, `TREATMENT OF FLUXES AT THE BOUNDARIES = 2` e `OPTION FOR THE DIFFUSION OF TRACERS = 2` produziu o balanço conservativo. O dicionário TELEMAC v8p5r0 explica que a opção 2 prioriza fluxos sobre valores prescritos de traçador e usa difusão ponderada pela profundidade. Essa mudança de formulação está explícita nos CAS; o cenário original permanece como referência.

Resultados completos: `reports/convergence/study.json` e `reports/convergence/conservative/study.json`, CAS, logs, SERAFIN e figuras. Comparações usam coordenadas da malha de entrada para evitar arredondamento UTM na saída SERAFIN de precisão simples. As tolerâncias são escolhas de pesquisa, não limites regulatórios. Não se calculou GCI nem se demonstrou regime assintótico; a velocidade não apresenta redução temporal monotônica de RMS.

Próximo ensaio: mais refinamento espacial/estudo de frente de concentração, seguido de verificação no domínio batimétrico observado e nas vazões baixa/alta. Não reduzir a tolerância para declarar aprovação.

## 3. Calibração e validação

Implementadas RMSE, MAE, viés, NSE e KGE (forma de 2009) para pares finitos previamente alinhados. Séries constantes retornam métricas indefinidas como `null`, sem pontuação artificial. Unidade e datum devem coincidir antes da comparação.

Plano de ajuste: usar 2007 para calibração, e um ano distinto (candidato 2008, sujeito à auditoria de cobertura) para validação. Separar aquecimento e períodos de cheia/vazante. Ajustar rugosidade e viscosidade dentro de faixas justificadas, sem compensar erro de datum com atrito. Comparar níveis e velocidades em observações internas independentes. O nível imposto em Itaituba não pode ser usado como evidência de validação; Acará e Buburé tampouco podem ser tratados como pontos dentro do pequeno domínio sem verificação espacial.

A função `require_calibration_evidence` bloqueia a etapa quando faltam batimetria, datum, observações independentes no domínio ou período reservado. **Nenhum parâmetro hidrodinâmico foi declarado calibrado.**

## 4. Sedimentos, metais e dragagem

Foi implementado e executado um protótipo de trecho completamente misturado, separado da hidrodinâmica 2D. Ele acompanha sedimento suspenso/leito e metal na água/leito, com entrada, saída, deposição, erosão prescrita, remoção e ressuspensão por dragagem. Usa partição linear instantânea `fração_particulada = Kd × SSC / (1 + Kd × SSC)` em unidades SI; metal particulado deposita com o sedimento. Remoção é limitada ao estoque disponível; todos os intercâmbios têm contrapartida no balanço.

**Todos os parâmetros sedimentológicos e químicos são assumidos**, incluindo Kd, concentração de entrada, estoque do leito, velocidade de queda e fração ressuspensa. Não representam mercúrio ou outro metal específico. Volume/área são hipóteses de um compartimento, sem acoplamento espacial ao TELEMAC. Não há erosão dependente de tensão, cinética geoquímica, reação redox, realimentação morfológica ou predição de pluma.

`reports/transport_screening/study.json` contém sensibilidade de passo 120/60/30 s e quatro taxas hipotéticas de dragagem. A classificação de Pareto contrapõe massa removida e exposição dissolvida integrada. Não existe ótimo econômico sem custo, restrições operacionais, volume-alvo e critérios ambientais definidos pelos pesquisadores. A interface de otimização reservada aos professores foi preservada.

Próxima implementação física: parametrizar classes granulométricas e propriedades do leito, executar GAIA com a hidrodinâmica validada, verificar conservação em canais de referência e depois introduzir espécie metálica/partição medidas. Somente então comparar alternativas de dragagem e objetivos aprovados.

## Reprodução

No diretório da plataforma e em ambiente Python com dependências instaladas:

```bash
python -m pytest -q
python -m scripts.transport_study
python -m scripts.numerical_study --out reports/convergence
python -m scripts.numerical_study --out reports/convergence/conservative --flux-priority
```

Os dois últimos comandos exigem TELEMAC funcional (`TELEMAC_EXECUTABLE`); casos com hash idêntico reutilizam resultados já presentes. O estudo não altera as condições do caso original. Foram aprovados 59 testes, com 1 teste opcional ignorado. Os ensaios TELEMAC foram executados no container `tapajos-platform-backend:latest`, com Python 3.11; a suíte unitária foi executada no Python 3.14 local.
