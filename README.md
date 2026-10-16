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
