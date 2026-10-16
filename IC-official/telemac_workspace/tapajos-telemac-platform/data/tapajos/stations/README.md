# Dados de Itaituba — Tapajós

`itaituba_sgb_monthly_levels.json`: 12 registros de estatísticas mensais, transcritos da Tabela 3.2 (p. 10) de nota técnica oficial SGB de 11/09/2025. Unidade: centímetros acima do zero da régua local. Inclui URL, hash do PDF consultado e ressalva sobre o período descrito na fonte.

Estação confirmada: **17730000**. Estes dados são estatísticas publicadas, não uma série diária adquirida da ANA. Não usar a cota como profundidade. A transformação ao datum do modelo ainda é uma hipótese.

O cenário inicial usa a mediana de setembro (371 cm) como referência climatológica; não representa uma medição em setembro de 2026.

## Inventário e seleção HidroWeb — 01/10/2026

O inventário oficial de Itaituba foi preservado em `raw/ana_inventory_*` e a
triagem das 16 estações fluviométricas está em `processed/ana_inventory_*`.
Foram importadas 13 séries pertinentes ao modelo, sempre com XML bruto, CSV
canônico e manifesto em diretórios separados.

Para o primeiro experimento com observações, usar como candidato principal a
vazão de Acará do Tapajós `17650002` e a cota de Itaituba `17730000`, na janela
comum 1996-01-01 a 2011-01-31. Fortaleza é referência regional; Buburé é controle
intermediário; Jardim do Ouro e Jamanxim representam aporte lateral. Ver a
justificativa completa em `docs/PHASE3_DATA.md`.

## Série diária ANA — Fase 3

A resposta oficial `HidroSerieHistorica` da estação **17730000** foi obtida em
18/09/2026 para cotas consistidas (`tipoDados=1`, `nivelConsistencia=2`). O XML
original está em `raw/`, o CSV canônico em `processed/` e o manifesto com hashes
e transformação em `manifests/`.

A série contém 14.361 observações entre 01/01/1974 e 31/05/2014, unidade cm e
nível de consistência 2. Há 400 dias ausentes em cinco intervalos; nenhuma lacuna
foi interpolada. A consulta solicitou dados até 2024, mas não retornou cotas
consistidas posteriores a maio de 2014. A estação não retornou vazões no serviço
consultado. O vínculo entre o zero da régua e o datum da malha continua ausente.
