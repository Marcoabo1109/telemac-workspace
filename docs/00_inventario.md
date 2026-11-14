# Inventário do checkout

A navegação da raiz e a proveniência encontram-se em README.md e consolidation/manifest.json. A plataforma está em tapajos-telemac-platform e a versão histórica em IC-official. A primeira contém backend/api para CAS, CLI e Selafin, frontend/src para a interface, scripts para preparo e execução, data/culm e data/tapajos para entradas, reports para saídas e notebooks para exploração. A pasta poc na raiz recebe a nova cadeia.

|Módulo|Uso identificado|Arquivo e parâmetros|
|---|---|---|
|T2D|Execução documentada|tapajos-telemac-platform/data/culm/t2d_culm.cas, GEOMETRY FILE, PRESCRIBED FLOWRATES, LAW OF BOTTOM FRICTION|
|Traçador T2D|Caso Tapajós|tapajos-telemac-platform/reports/tapajos_initial/case.cas, NUMBER OF TRACERS|
|GAIA/Nestor|Editor e exemplos|tapajos-telemac-platform/docs/NESTOR.md, COUPLING WITH, GAIA STEERING FILE, NESTOR ACTION FILE|
|Sisyphe / DREDGESIM|Sem executável identificado na configuração escolhida|tapajos-telemac-platform/vendor/telemac/sources; substitutos disponíveis GAIA/Nestor|
|WAQTEL|Fonte distribuída, sem uso demonstrado nesta cadeia|tapajos-telemac-platform/vendor/telemac/sources/waqtel/waqtel.dico|
|Plataforma Tapajós|Preparo e pós-processamento|tapajos-telemac-platform/backend/api/telemac_runner.py e scripts/postprocess.py|

O Dockerfile em tapajos-telemac-platform/docker fixa v8p5r0 e compila com compile_telemac.py -j 2. O ambiente interno define HOMETEL=/opt/telemac, PYTHONPATH=/opt/telemac/scripts/python3, SYSTELCFG=/opt/telemac/configs/systel-platform.cfg (cópia de docker/systel.cfg) e USETELCFG=gnu. O wrapper docker/run-telemac chama telemac2d.py com Python 3.11. O HOMETEL do host apontava para um diretório ausente. A imagem local tapajos-telemac:source foi usada.

## Arquivos de modelagem e código por árvore

- .vscode 
- IC-official .cas: 117, .cli: 46, .slf: 298, .geo: 1, .f: 26, .py: 96, .sh: 4, .ipynb: 5
- bin .sh: 1
- consolidation .py: 1
- entrega_base_sintetica 
- gouttedo .cas: 9, .cli: 2, .slf: 8, .f: 2, .py: 3
- tapajos-telemac-platform .cas: 735, .cli: 305, .slf: 1169, .geo: 33, .f: 2089, .f90: 621, .py: 627, .sh: 13, .ipynb: 74
- telemac-examples-ref .cas: 137, .cli: 70, .slf: 254, .f: 140, .py: 84
- telemac2d_custom .py: 2
