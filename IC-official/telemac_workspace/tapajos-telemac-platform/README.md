# Tapajós · Plataforma TELEMAC

**Novo (14/10/2026):** [laboratório sintético de sedimentos, micropoluentes e dragagem](docs/SYNTHETIC_SEDIMENT_LAB.md), com casos executados GAIA/Nestor, WAQTEL e balanços conservativos. Dados reais e calibração ficam para a etapa posterior.

Plataforma local de pesquisa para preparar arquivos TELEMAC-2D, explorar malhas SERAFIN, editar fronteiras e séries, executar casos e analisar resultados. React + FastAPI + Python 3.11+. Fundamentada nos arquivos de IC-RIOS e telemac_workspace; os originais foram preservados.

**Estado:** implementação inicial funcional com exemplo offline Culm. Não é uma simulação calibrada do Tapajós. Consulte [estado dos entregáveis](docs/STATUS.md) e [fundamentação e correções](docs/SCIENCE.md).

## Acesso local

Atalho para iniciar: `./scripts/start.sh`; para parar somente esta plataforma: `./scripts/stop.sh`.

Interface: http://localhost:3000. API/documentação: http://localhost:8000/docs.

A entrega final usa o solver compilado em Docker Compose (Ubuntu 22.04, ARM64, v8p5r0). No teste inicial foi usado o container TELEMAC já existente `nice_austin`, imagem `simvia/opentelemac:v8p5r1` (amd64 em emulação no Mac ARM64). Não alteramos a instalação nem os casos originais.

```bash
cd /Users/marcoabo/telemac_workspace/tapajos-telemac-platform
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
npm ci --prefix frontend
TELEMAC_CONTAINER=nice_austin .venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000
# Em outro terminal
npm run dev --prefix frontend
```

O adaptador de container requer que o workspace esteja montado em `/workspace`, como na instalação local. Em outro computador, use o solver nativo ou o build Docker abaixo. `TELEMAC_HOST_ROOT` altera a raiz local correspondente a `/workspace`. Nunca monte o socket Docker em um serviço público.

## Apenas Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

Este comando serve os editores com Python 3.11 e GMSH. Para incluir o solver compilado, use:

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.telemac.yml up --build
```

A receita do solver usa Ubuntu 22.04, Python 3.11, OpenMPI, METIS e tag v8p5r0. A imagem de editores usa Debian bookworm; em Linux ARM64 o GMSH vem de apt, pois o pacote pip não oferece wheel nessa arquitetura. Não se aplicam patches Fortran especulativos: flags GNU portáveis em `docker/systel.cfg`. Confira os testes efetivamente concluídos em `docs/STATUS.md`.

```bash
# Builds explícitos das duas arquiteturas
docker buildx build --platform linux/amd64,linux/arm64 -f docker/Dockerfile.app .
# Notebook opcional (token de acesso exibido pelo Jupyter)
docker compose -f docker/docker-compose.yml --profile notebooks up jupyter
```

## Fluxo de demonstração

1. Carregue Culm na interface.
2. Explore os parâmetros; duração = TIME STEP × NUMBER OF TIME STEPS. Tooltips indicam unidades.
3. Em Malha, use scroll/arraste para navegar. Clique num nó para editar BOTTOM; exporte SERAFIN mantendo variáveis e instantes. Para resultados, selecione campo e instante, e ative vetores.
4. Em Séries, carregue QSL/CSV, escolha Q/SL e edite pontos na tabela ou arrastando a curva. Q e SL possuem unidades distintas. O CSV web aceita `data,hora,vazao`; para cota use conversor explícito de unidade/datum.
5. Em Fronteiras, edite parede / vazão prescrita / nível prescrito. A associação numérica de fronteiras líquidas precisa ser revisada.
6. Em Simulação, configure o teste curto e execute. O backend cria `runs/<uuid>`, preserva entradas, salva log e oferece o resultado após retorno zero e leitura SERAFIN bem-sucedida.
7. Para outro caso, importe .cas e todos os arquivos referenciados. A importação limpa a geometria e as séries do caso anterior.

A aplicação é para uso local confiável ou túnel SSH. Não possui contas, autenticação multiusuário, persistência do histórico de jobs no banco nem fila distribuída. Não exponha diretamente as portas na Internet. Limite de upload por arquivo: 64 MiB; somente SERAFIN 2D triangular, single/double precision, big/little endian. Malhas/resultados são carregados em memória. O editor CAS preserva palavras-chave desconhecidas; não preserva comentários originais nem valida o dicionário inteiro. Execução web rejeita Fortran e acoplamento arbitrário; casos GAIA completos devem ser revisados pela equipe.

## Dados ANA

A API atual autenticada exige autorização da ANA e token, fornecido em
`ANA_TOKEN`. Não inclua token no Git, em notebooks ou mensagens. O projeto
também preserva respostas válidas obtidas do serviço histórico público, sempre
com XML original, CSV canônico, manifesto e ressalva de proveniência.

O inventário científico da Fase 2 está em `data/tapajos/catalog.json`. Ele separa dados disponíveis, produtos derivados e requisitos ausentes, confere hashes e calcula os marcos exibidos na interface. Consulte [`docs/DATA_PROTOCOL.md`](docs/DATA_PROTOCOL.md) e valide antes de promover qualquer conjunto:

```bash
python -m scripts.data_catalog
```

A Fase 3 incorporou 13 séries diárias pertinentes. O par principal é a vazão
consistida de Acará do Tapajós `17650002` e a cota consistida de Itaituba
`17730000`, com 5.268 dias simultâneos entre 1996-01-01 e 2011-01-31. A Fase 4
preparou a janela completa de 2007, os gráficos de controle e um template QSL.
Como o zero da régua ainda não está ligado ao datum da malha, esse template não
é apresentado como simulação calibrada. Consulte
[`docs/PHASE3_DATA.md`](docs/PHASE3_DATA.md) e
[`docs/PHASE4_OBSERVED_SCENARIO.md`](docs/PHASE4_OBSERVED_SCENARIO.md).

```bash
python -m scripts.phase3_data --help
python -m scripts.observed_scenario
```

```bash
python -m scripts.tapajos_data --help
# Converter um XML histórico válido sem rede
python -m scripts.tapajos_data --xml arquivo.xml --kind Q --out data/tapajos/stations
# Inventário previamente baixado e seleção geográfica
python -m scripts.tapajos_data --inventory-json inventario.json --reach itaituba --out data/tapajos/stations
```

Para consultas ao vivo, `--query-params` recebe filtros do inventário como JSON conforme o Swagger atual. O cliente consulta séries em lotes de até 366 dias, cacheia respostas, respeita intervalo e Retry-After e rejeita respostas de erro. Os nomes dos parâmetros históricos são resolvidos pelo OpenAPI oficial; forneça ANA_OPENAPI_FILE para usar um schema baixado. O schema mensal precisa ser verificado contra a conta/API em uso antes de afirmar integração validada. O código falha explicitamente se a resposta não contiver medições reconhecidas. O prazo do token é controlado pelo usuário; 401/403 requer novo token. Não envia solicitações de acesso por e-mail automaticamente.

```bash
python -m scripts.convert_to_telemac vazao.csv --kind Q --unit m3/s --boundary 1 --out montante.qsl
python -m scripts.convert_to_telemac nivel.csv --kind SL --unit cm --datum-offset 12.34 --boundary 2 --out jusante.qsl
python -m scripts.tapajos_analysis montante.csv jusante.csv --out reports/hydrology
```

O CSV canônico tem `date,value` (datas ISO). O offset acima é ilustrativo: use o levantamento da régua. Não há preenchimento implícito de lacunas; ajuste o limite de lacuna conscientemente. A correlação usa datas alinhadas e Pearson em cada lag, com número mínimo de pares, evitando preencher faltas com zero. Lag positivo significa jusante atrasada; sazonalidade pode induzir correlação espúria.

## Geometria e malha

```bash
python -m scripts.tapajos_data --overpass --reach itaituba --out data/tapajos/geometry
python -m scripts.mesh_generator dominio.geojson --out data/tapajos/meshes/meu_trecho --lc-canal 200 --lc-planicie 800 --lc-fronteira 200
```

Overpass retorna linhas de rios OSM, não margens. O mesher exige Polygon WGS84 válido e projeta para UTM. Refinamento usa aproximação do eixo principal; não é talvegue medido. Inclui `.msh`, `.geo_unrolled`, `.slf`, `.cli` e metadados. O fallback Delaunay rejeita domínios cuja cobertura não seja preservada. A geometria esquemática de Itaituba incluída é apenas demonstração, com fundo provisório zero. HydroSHEDS e DEMs podem ser preparados com `scripts.geodata`; nenhum DEM é considerado batimetria submersa automaticamente.

## Pós-processamento e cluster

```bash
python -m scripts.postprocess resultado.slf --law 3 --coefficient 30 --out reports/scenario --animate gif
# MP4 requer ffmpeg
sbatch --export=ALL,TELEMAC_ENV=/caminho/ambiente.sh,CAS_FILE=/caminho/caso.cas scripts/submit_slurm.sh
```

Gera velocidade, Froude e tensão de leito para Strickler/Manning, `.npz`, métricas JSON, VTK para ParaView e animação. Arquivos VTK abrem em ParaView sem depender de plugin SERAFIN. Notebooks mostram a visualização inline. Os scripts SLURM/PBS precisam de conta, ambiente e recursos definidos pelo LMACC; não foram submetidos a um cluster.

## Desenvolvimento e rastreabilidade

```bash
.venv/bin/python -m pytest -q
npm run build --prefix frontend
git submodule update --init --depth 1
```

O protocolo da Fase 1 registra automaticamente ambiente, commits e hashes do caso curto Culm, executa a referência serial/MPI sem sobrescrever evidências versionadas e compara resultados entre Mac e VM. Consulte [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

O submódulo `vendor/telemac` aponta ao commit da tag v8p5r0; a instalação local de teste é v8p5r1 e os dados Culm vieram de v8p2r1. Não confundir as três versões. GitHub Actions inclui testes Python, build web e publicação de imagens em release. A publicação GitHub depende do repositório de destino do usuário; nenhum remoto foi inventado.

Código novo: MIT. Dados/exemplos TELEMAC mantêm a licença em `data/culm/LICENCE.txt`; dados ANA e OSM mantêm suas licenças e atribuições. Livros e PDFs originais não foram redistribuídos. Veja `docs/provenance.json` para hashes das cópias.

## English

Research platform for TELEMAC-2D with React/FastAPI, binary SERAFIN I/O, steering/boundary editors, isolated simulation jobs, GMSH meshing and scientific post-processing. The original local files are preserved. Start with `docker compose -f docker/docker-compose.yml up --build`; add `-f docker/compose.telemac.yml` to build the solver. Open localhost:3000; API docs are on localhost:8000/docs.

The bundled Culm case supports offline testing. A successful short run is not validation of the Tapajós model. The approximate Itaituba mesh is schematic, with placeholder bathymetry and all-wall boundaries. Real ANA acquisition requires an authorized token and current API schema verification. Stage units and vertical datum must be specified before TELEMAC conversion. Terrestrial DEMs do not measure submerged river beds. GAIA/reactive metal transport and dredging objectives remain research tasks. Check `docs/STATUS.md` for verified deliverables and remaining limitations. The web service is intended for a trusted local user or SSH tunnel; it is not a public multiuser platform.

Run `pytest -q` and `npm run build --prefix frontend` for checks. New code is MIT; bundled TELEMAC examples retain their original license. Source provenance, scientific corrections, container recipes, SLURM/PBS templates and demonstration notebooks are included.

## Primeiro cenário do Tapajós — 09/09/2026

O painel agora abre o cenário exploratório de Itaituba; o botão **Carregar Culm** mantém o caso de referência. Foram coletados o eixo do rio via OpenStreetMap, 12 registros de estatísticas mensais de nível publicados pelo SGB e 14.361 cotas diárias consistidas da ANA (estação 17730000). Vazão diária, datum e batimetria levantada ainda não foram adquiridos.

A primeira simulação usa 3,47 km de eixo, largura assumida 1.200 m, fundo analítico de 4–8 m, vazão assumida 6.000 m³/s e nível climatológico de setembro 3,71 m em datum local assumido. Inclui traçador conservativo normalizado; não representa concentração observada de metais. Consulte [hipóteses e reprodução](models/tapajos_trecho1/README.md), [parâmetros rastreáveis](models/tapajos_trecho1/assumptions.json) e [resultados](reports/tapajos_initial/summary.json).

```bash
python -m scripts.run_tapajos
```

## Editor GAIA / Nestor

A aba **GAIA / Nestor** oferece importação de ações, formulários por operação de dragagem/despejo, edição do catálogo oficial GAIA, polígonos, referência e restart. Exporte ações `.dat`, salve o projeto do editor em JSON ou baixe o pacote de configuração GAIA + Nestor. A execução acoplada usa o CLI TELEMAC; o executor web permanece restrito. Veja [instruções e rastreabilidade](docs/NESTOR.md).
