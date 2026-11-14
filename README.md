# TELEMAC Workspace — pesquisa e modelagem de rios

Repositório público consolidado do workspace de pesquisa com TELEMAC, incluindo a plataforma Tapajós, exemplos, dados, resultados e entregas. Snapshot preparado em 16/10/2026. Os diretórios originais foram preservados para manter referências relativas e distinguir versões de trabalho.

## Navegação

| Diretório | Conteúdo |
| --- | --- |
| [tapajos-telemac-platform](tapajos-telemac-platform/README.md) | Plataforma React/FastAPI, scripts, modelos, dados, relatórios, testes e fonte TELEMAC em `vendor/telemac`. |
| [IC-official](IC-official/README.md) | Versão de pesquisa anteriormente vinculada ao repositório `Marcoabo1109/IC`, com cenários e entregas adicionais. Mantida separada para não sobrescrever versões diferentes. |
| [telemac-examples-ref](telemac-examples-ref/README.txt) | Exemplos de referência disponíveis localmente e seus resultados. |
| [gouttedo](gouttedo/Readme.txt) | Casos Gouttedo/Thompson, malhas, Fortran e resultados. |
| [telemac2d_custom](telemac2d_custom) | Adaptadores Python locais do TELEMAC-2D. |
| [bin](bin) | Script auxiliar de execução. |
| [entrega_base_sintetica](entrega_base_sintetica) | Pacote de entrega da base sintética GAIA/metais/dragagem. |
| [consolidation](consolidation/README.md) | Inventário, proveniência, exclusões e restauração dos arquivos grandes. |

## Obter o conteúdo completo

```bash
git clone https://github.com/Marcoabo1109/telemac-workspace.git
cd telemac-workspace
python3 consolidation/restore_large_files.py
```

O script recompõe e descomprime os arquivos grandes, conferindo o SHA-256 original. Não é necessário Git LFS nem baixar submódulos: o código TELEMAC disponível no workspace está incorporado. Execute a restauração antes de utilizar casos que dependam desses arquivos.

Para iniciar a plataforma, consulte o README da versão desejada. Dependências Python/Node e solver precisam ser instalados conforme suas instruções. Caminhos absolutos da máquina de origem presentes em scripts e documentação podem precisar de adaptação.

## Escopo científico e reprodução

Os cenários exploratórios e sintéticos não equivalem a modelos calibrados do Tapajós nem validam previsões sobre metais. Consulte os documentos científicos e de estado de cada versão antes de interpretar resultados. Esta publicação conserva os arquivos; não representa uma nova execução ou validação de todas as simulações.

## Licenças e créditos

As licenças existentes de cada componente foram preservadas. A plataforma possui sua própria licença e o TELEMAC mantém suas licenças e créditos de origem. Este agrupamento não altera a titularidade nem aplica uma licença única a dados e componentes de terceiros.

## Atualização de dados — 10/11/2026

[Relatório da coleta e auditoria](IC-official/telemac_workspace/tapajos-telemac-platform/docs/DATA_ACQUISITION_2026-11-10.md): candidato de validação de 2008 com 366 dias completos, inventário das fontes consultadas e pendências de batimetria/datum. Documentos brutos externos permanecem locais; o repositório inclui referências e hashes.

## PoC do rio Culm

O caso usa a malha integral distribuída do trecho do Culm. Os dados, o inventário e os critérios de seleção estão em docs/00_inventario.md e docs/01_selecao_caso.md. Requer Docker com acesso ao diretório do clone, Python 3.14 para o pós-processamento e LaTeX com latexmk para o relatório. A configuração GNU/OpenMPI do solver usa Python 3.11 dentro da imagem. Execute na raiz:

```bash
python3.14 -m venv .venv-poc
source .venv-poc/bin/activate
pip install -r poc/requirements.txt
docker build -f tapajos-telemac-platform/docker/Dockerfile -t tapajos-telemac:source tapajos-telemac-platform
export PYTHONPATH="$PWD:$PWD/tapajos-telemac-platform"
python -m unittest discover -s tests
python poc/run.py steady
python poc/run.py tracer
python poc/run.py bed
python poc/run.py cut
python poc/analyse.py
(cd report && latexmk -pdf main.tex)
```

O notebook notebooks/PoC_telemac.ipynb executa a mesma sequência. Use o kernel do ambiente instalado. Cada cenário grava CAS, listagem e Selafin em poc/work. A última saída de r2d_culm.slf é o estado de continuação. As figuras e métricas ficam em poc/results. O JSON poc/parameters.json controla as comparações e tolerâncias. O CAS poc/steady.cas fixa a configuração hidrodinâmica do caso-base.

Se Docker informar que não consegue abrir o socket, inicie o daemon. Em Linux, dê ao UID 1000 do contêiner acesso de escrita a poc/work. Se o solver não encontrar um arquivo, confira a etapa anterior e o primeiro erro em poc/work/*.log. A ausência de T1 na seleção de saídas omite o campo do traçador. O CLI sedimentológico precisa de código livre nas fronteiras abertas. A falta da seção de referência do Nestor interrompe sua saída de diagnóstico.

Para executar o notebook sem interface gráfica no ambiente instalado:

```bash
jupyter nbconvert --to notebook --execute notebooks/PoC_telemac.ipynb --ExecutePreprocessor.timeout=300 --output=/tmp/PoC_executada.ipynb
```
