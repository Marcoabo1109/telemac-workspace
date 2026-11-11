# Coleta e qualificação de dados — 10/11/2026

## Resultado desta rodada

Auditadas as quatro séries diárias consistidas: vazão Acará (17650002), cota Itaituba (17730000), vazão e cota Buburé (17710000). Foram conferidos unidade, unicidade das datas, valores finitos e consistência 2. Não houve interpolação nem alteração do datum.

| Ano | Dias comuns válidos | Papel proposto |
|---|---:|---|
| 2005 | 365/365 | Alternativa de validação |
| 2006 | 365/365 | Alternativa de validação |
| 2007 | 365/365 | Calibração, conforme plano existente |
| 2008 | 366/366 | Reservado como candidato à validação |

O arquivo `data/tapajos/acquisition/2026-11-10/validation_2008_daily.csv` contém as quatro séries alinhadas. `validation_windows.json` preserva hashes das fontes, lacunas e limitações. É um produto derivado das observações já coletadas, não uma nova coleta ANA. Cobertura completa não comprova precisão das observações nem representatividade espacial. Itaituba é condição de contorno; não deve validar o próprio nível imposto. É necessário obter observações internas independentes.

Reprodução: `python3 -m scripts.audit_validation_windows`.

## Documentação oficial coletada

Foram preservadas localmente as páginas do [PMH](https://www.gov.br/dnit/pt-br/assuntos/aquaviario/programa-de-monitoramento-hidroviario-pmh) e da [hidrovia Tapajós–Teles Pires](https://www.gov.br/dnit/pt-br/assuntos/aquaviario/intervencao-em-hidrovias/hidrovias-1/hidrovia-do-tapajos-teles-pires), além do [Plano de Trabalho ACT 001/2025 DAQ](https://www.gov.br/dnit/pt-br/acesso-a-informacao/convenios/acordos-de-cooperacao-tecnica/2025/acordo-de-cooperacao-tecnica-no-001-2025-daq/act0012025daqPT.pdf). URLs, data de acesso, tamanhos e SHA-256 estão em `sources.json`.

O plano, página 3, atribui as batimetrias prévias à supervisora contratada pelo DNIT. O processo identificado é **50600.027534/2024-78**. Isso fornece uma referência documental para localizar os levantamentos; não demonstra que estejam disponíveis para download ou que cubram Itaituba–Miritituba. O PDF não fornece pontos XYZ para preencher o fundo do modelo. Os documentos brutos ficam fora do Git enquanto os termos de redistribuição não forem estabelecidos.

## Datum e batimetria: pendências verificadas

A listagem pública de estações fluviométricas da Marinha foi localizada em https://www.marinha.mil.br/chm/estacoes-fluviometricas?page=1, mas a tentativa de download retornou HTTP 403. A ficha original de Itaituba não foi adquirida nesta rodada. A relação histórica descrita no EIA continua não verificada para 2007/2008; nenhum offset foi aplicado.

O relatório SGB de cotas de alerta em municípios da Amazônia Ocidental (https://rigeo.sgb.gov.br/handle/doc/22012) foi triado e descartado como evidência específica de Itaituba: o escopo listado corresponde a municípios do Amazonas. Não importar cotas de outras estações.

## Dados a obter em seguida

1. **CHM/ANA/SGB:** ficha F-43-4382B-001/82 e revisões, marcos de referência, nivelamentos, alterações do zero da régua 17730000, relação entre nível de redução e datum geodésico, épocas de validade e incerteza. Confirmar a associação entre a estação CHM e a série ANA.
2. **DNIT/DAQ e SR/PA:** localizar no processo acima e no PMH os levantamentos que efetivamente intersectam Itaituba–Miritituba. Solicitar XYZ/CSV/LAS e seções, polígonos de cobertura, datas, CRS, datum vertical, redução de sondagem, precisão, relatórios de controle e licença de uso. A existência do programa não substitui a entrega dos dados.
3. **Observações internas:** níveis e velocidades/ADCP em pontos dentro do domínio, com coordenadas e datum; manter 2008 reservado e não ajustar parâmetros com base nos erros desse período.
4. **Geometria:** após obter as referências, digitalizar sondagens e margens das cartas 4382B/4383 com rastreabilidade, sem converter pixels RGB em profundidades. A precisão deve vir do levantamento ou ser declarada desconhecida.

Nenhuma solicitação externa foi enviada. Calibração, batimetria levantada, margens verificadas e vínculo vertical permanecem bloqueados. A coleta sedimentológica e de metais não foi promovida com hipóteses sintéticas.
