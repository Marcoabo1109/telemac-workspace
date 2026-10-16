# Tapajós em Itaituba — primeira simulação exploratória

Trecho de 3,47 km a partir do eixo público OSM `way/26158344`. A largura é um buffer **assumido** de 1.200 m; não corresponde a margens levantadas. Batimetria analítica com profundidades nominais de 4–8 m e declividade 0,00005. Malha GMSH: 228 nós / 397 triângulos, EPSG:32721, SERAFIND (64 bits).

## Dados e hipóteses

- **Coletado:** eixo OSM, com data, versão, URL, atribuição e hash da resposta original em `../../data/tapajos/geometry/osm_tapajos_axis.geojson`.
- **Coletado:** Tabela 3.2 da nota técnica SGB de 11/09/2025, estação Itaituba 17730000, em `../../data/tapajos/stations/itaituba_sgb_monthly_levels.json`.
- **Derivado:** mediana climatológica de setembro de 371 cm → 3,71 m. Valor constante do cenário, não medição atual.
- **Assumido:** vazão 6.000 m³/s, Strickler 30 m^(1/3)/s, difusividade de velocidade 2 m²/s, difusividade do traçador 5 m²/s, largura, fundo e offset vertical nulo. As cotas são relativas ao zero arbitrário do modelo, suposto coincidente com a régua; não são altitudes geodésicas.
- **Assumido:** traçador conservativo normalizado contínuo de concentração 1 na entrada e 0 inicialmente. Não equivale a concentração medida de metal. Reações, sorção e transporte de sedimentos não estão representados.

Todos os parâmetros e limitações constam em `assumptions.json`. A numeração líquida observada no solver é **saída 1 / entrada 2**; por isso o hidrograma usa `Q(2)` e `SL(1)`. `FRONT2` enumera a partir do ponto sudoeste, independentemente da primeira linha CLI. Revalidar os identificadores ao mudar a geometria. Usar produto matriz-vetor 1, sem exigir renumeração STBTEL.

## Executar

Na raiz da plataforma, iniciar `./scripts/start.sh` e executar:

```bash
python -m scripts.run_tapajos
```

A execução integra 1.800 passos de 2 s (1 hora), com 31 frames. Parte de água parada: o transiente de inicialização está incluído, sem alegação de regime permanente ou convergência. O script verifica término, tempo final, valores finitos, profundidades positivas e limites do traçador; salva SERAFIN, VTK, GIF, log e resumo em `reports/tapajos_initial`.

Para refazer a malha, baixar o recorte pela URL em `scripts/prepare_tapajos.py` e executar `python -m scripts.prepare_tapajos recorte.osm`. Preservar a resposta original para comparação do hash. O gerador exige revisão caso o recorte do eixo mude.

## Leitura dos resultados iniciais

Profundidade mínima 3,789 m; velocidade máxima 1,474 m/s; Froude máximo 0,234; traçador normalizado entre 0 e 1. O erro relativo acumulado de volume é aproximadamente −4,99 × 10⁻⁷. O balanço final do **traçador** apresenta erro relativo de **−0,00869 (cerca de −0,87%)** com o esquema inicial de advecção; é distinto do erro da água e deve ser reduzido/avaliado em estudos de convergência antes de análises quantitativas de massa de contaminante.
