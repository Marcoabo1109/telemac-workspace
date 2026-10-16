# Resumo Técnico e Científico do Projeto  
## Modelagem Computacional da Dispersão de Metais Pesados em Rios Brasileiros  
### Aplicação ao Planejamento Sustentável de Dragagens — Rio Tapajós  
**ICMC-USP · LMACC · Iniciação Científica 2026**  
**Aluno:** Marco Antonio Bicalho de Oliveira  
**Orientador:** Prof. Roberto F. Ausas (SME/ICMC-USP)  
**Colaboradores:** Prof. Elias S. Helou · Prof. Fabricio S. Sousa · Dr. Jorge Abad (Rede Yaku)

---

## 1. Contexto e Motivação

O projeto investiga a **dispersão de metais pesados** em rios brasileiros por meio de simulações numéricas, com aplicação direta ao **planejamento sustentável de operações de dragagem** na hidrovia do Rio Tapajós (bacia Pará/Mato Grosso). A relevância nacional é dupla: as hidrovias são alternativa logística eficiente ao modal rodoviário, mas as operações de dragagem ressuspendem sedimentos com alta carga de contaminantes (Hg, Pb, Cd, entre outros) — impacto documentado em populações ribeirinhas do Tapajós (refs. Coelho-Souza 2011, Faial 2015).

---

## 2. Repositório de Arquivos do Projeto

| Arquivo | Tipo | Função |
|---|---|---|
| `lattice_boltzman.py` | Python (D2Q9 LBM) | Protótipo de simulação de fluxo 2D com obstáculo |
| `IC_rivers.pdf` | Proposta de IC | Documento oficial do projeto ICMC-USP 2026 |
| `Parametrizac_a_o_do_modelo_TELEMAC_2D.pdf` | Resumo técnico | Configuração do caso Culm → diretrizes Tapajós |
| `telemac2d_theory_guide_9_1.pdf` | Guia oficial | TELEMAC-2D v9.1 — equações, palavras-chave, módulos |
| `Hydrodynamics_of_free_surface_flows.pdf` | Livro (Hervouet) | Fundamentos do método dos elementos finitos p/ superfície livre |
| `pa.pdf` | Mapa DNIT 2025 | Mapas multimodais — estado do Pará (hidrovias + hidrografia) |
| `mt.pdf` | Mapa DNIT 2025 | Mapas multimodais — estado do Mato Grosso (nascentes do Tapajós) |

---

## 3. Modelo Matemático

### 3.1 Hidrodinâmica — TELEMAC-2D (Saint-Venant 2D)

O módulo **TELEMAC-2D** resolve as equações bidimensionais de águas rasas obtidas pela integração vertical das equações de Navier-Stokes:

**Conservação de massa:**
$$\frac{\partial h}{\partial t} + \nabla \cdot (h\mathbf{u}) = 0$$

**Conservação do momento (componentes x, y):**
$$\frac{\partial (h\mathbf{u})}{\partial t} + \nabla \cdot (h\mathbf{u} \otimes \mathbf{u}) + gh\nabla\eta = \nabla \cdot (h\nu_t \nabla\mathbf{u}) - \frac{\boldsymbol{\tau}_b}{\rho}$$

onde: $h$ = profundidade, $\mathbf{u} = (u,v)^T$ = velocidade média vertical, $\eta = h + z_b$ = cota da superfície livre, $\nu_t$ = viscosidade turbulenta, $\boldsymbol{\tau}_b$ = tensão de atrito no leito.

### 3.2 Transporte de Contaminantes

$$\frac{\partial(hC)}{\partial t} + \nabla \cdot (h\mathbf{u}C) = \nabla \cdot (hD\nabla C) + S_C$$

$C(x,t)$ = concentração do contaminante, $D$ = coeficiente de difusão turbulenta, $S_C$ = termo fonte.

### 3.3 Transporte de Sedimentos — Módulo GAIA

**Sedimentos em suspensão (equação de advecção-difusão):**
$$\frac{\partial(hC_s)}{\partial t} + \nabla \cdot (h\mathbf{u}C_s) = \nabla \cdot (hD_s\nabla C_s) + E - D$$

**Evolução morfológica do fundo (equação de Exner):**
$$(1 - \lambda_p)\frac{\partial z_b}{\partial t} + \nabla \cdot \mathbf{q}_s = 0$$

### 3.4 Sedimentos Coesivos e Metais Pesados

**Lei de erosão de Partheniades:**
$$E = M\left(\frac{\tau_b}{\tau_{ce}} - 1\right), \quad \tau_b > \tau_{ce}$$

**Lei de deposição de Krone:**
$$D = w_s C_s \left(1 - \frac{\tau_b}{\tau_{cd}}\right), \quad \tau_b < \tau_{cd}$$

**Relação metal–sedimento (proporcionalidade linear):**
$$C_m = K_m C_s$$

### 3.5 Lattice Boltzmann (D2Q9) — Código Exploratório

O arquivo `lattice_boltzman.py` implementa o método LBM com:
- Domínio 2D: $L_x = 400$, $L_y = 100$ (unidades lattice)
- Viscosidade $\nu = 0{,}01$, força externa $f = 4\times10^{-6}$
- Obstáculo circular + paredes sólidas (no-slip via bounce-back)
- Aceleração JIT via Numba (`@njit`)
- Ciclo: colisão → streaming → troca de buffers → macro
- Visualização ao vivo a cada 250 timesteps

---

## 4. Plataforma de Simulação: Open TELEMAC-MASCARET

### 4.1 Estrutura de Arquivos de um Caso

| Arquivo | Função |
|---|---|
| `*.cas` | Steering file — controle total da simulação (pares `KEYWORD = VALUE`) |
| `geo_*.slf` | Geometria e batimetria da malha (formato SERAFIN) |
| `geo_*.cli` | Condições de contorno por nó da malha |
| `ini_*.slf` | Condição inicial da simulação |
| `*.qsl` | Séries temporais de vazão Q(t) e nível SL(t) nas fronteiras |
| `r2d_*.slf` | Resultados da simulação |

### 4.2 Parâmetros Físicos (caso Culm → base para Tapajós)

| Palavra-chave | Valor exemplo | Significado |
|---|---|---|
| `LAW OF BOTTOM FRICTION` | 3 | Lei de Strickler (0=sem, 1=Haaland, 2=Chézy, 3=Strickler, 4=Manning, 5=Nikuradse, 7=Colebrook) |
| `FRICTION COEFFICIENT` | 30 | Coeficiente de Strickler $K_s$ [m$^{1/3}$/s] |
| `VELOCITY DIFFUSIVITY` | 2 | Difusividade/viscosidade horizontal $\nu$ |
| `TURBULENCE MODEL` | 1 | Modelo de fechamento turbulento |

Relação Strickler–Manning: $n = 1/K_s$.

### 4.3 Condições de Contorno

| Palavra-chave | Significado |
|---|---|
| `PRESCRIBED FLOWRATES` | Vazão prescrita na fronteira de montante $Q_{in}$ |
| `PRESCRIBED ELEVATIONS` | Cota prescrita na fronteira de jusante $\eta_{out}$ |
| `LIQUID BOUNDARIES FILE` | Arquivo `.qsl` com séries temporais |
| `BOUNDARY CONDITIONS FILE` | Arquivo `.cli` — tipo de fronteira por nó |
| `GEOMETRY FILE` | Arquivo `.slf` — malha e batimetria |

### 4.4 Parâmetros Numéricos

| Palavra-chave | Função |
|---|---|
| `TIME STEP` | $\Delta t$ — passo de tempo [s] |
| `NUMBER OF TIME STEPS` | Número total de iterações |
| `SOLVER ACCURACY` | Precisão do solver linear |
| `SOLVER` | Algoritmo (CG, GMRES, etc.) |
| `IMPLICITATION FOR DEPTH` | Esquema implícito para $h$ |
| `IMPLICITATION FOR VELOCITY` | Esquema implícito para $\mathbf{u}$ |

---

## 5. Domínio Geográfico: Rio Tapajós

### 5.1 Divisão em Três Trechos

O Rio Tapajós pode ser segmentado em três regiões funcionais para modelagem:

| Trecho | Região | Características | Fonte de dados |
|---|---|---|---|
| **Alto Tapajós** | Cabeceiras — MT (nascentes: Rio Juruena + Rio Teles Pires) | Alta declividade, granulometria grossa | ANA/HidroWeb, SRTM, ICESat-2 |
| **Médio Tapajós** | MT→PA — Itaituba | Planície de inundação, meandros, garimpos (Hg) | ANA, MapBiomas, batimetria SNBH |
| **Baixo Tapajós** | PA — Santarém (foz no Amazonas) | Estuarino-fluvial, maré, maior profundidade | ANTAQ, ANA, Copernicus |

### 5.2 Fontes de Dados

- **ANA/HidroWeb API**: séries históricas de vazão Q(t) e nível h(t) por estação fluviométrica
- **SNBH (Sistema Nacional de Banco de Dados Hidrológicos)**: batimetria e perfis transversais
- **IBGE/SRTM/ALOS-PALSAR**: topografia e DEM
- **Copernicus / Sentinel-2**: geometria das margens, uso do solo, sazonalidade
- **Global Waterway / HydroSHEDS**: geometria hidrológica de referência
- **VGEO (LabGeo/IBGE) e OpenStreetMap**: dados vetoriais georreferenciados

---

## 6. Roadmap Técnico do Projeto (7 Etapas)

```
Etapa 1 ─ Caso de referência (Culm) validado
Etapa 2 ─ Delimitação do trecho do Tapajós + estações ANA
Etapa 3 ─ Levantamento de dados reais (batimetria, Q(t), h(t), granulometria)
Etapa 4 ─ Construção da malha (GMSH / BlueKenue / TELEMAC mesher)
Etapa 5 ─ Parametrização hidrodinâmica (t2d_tapajos.cas)
Etapa 6 ─ Calibração: HTELEMAC(x,t) vs Hobservado(x,t) → ajuste Ks / n
Etapa 7 ─ Extensão: GAIA (sedimentos) + módulo de transporte de traçadores/metais
```

---

## 7. Infraestrutura Computacional

### 7.1 Ambientes de Desenvolvimento

| Ambiente | Especificação | Uso |
|---|---|---|
| **Mac M3** (local) | Apple Silicon, macOS | Desenvolvimento, testes rápidos |
| **Docker** | Container Linux (Ubuntu/Debian) | Reprodutibilidade, TELEMAC compilado |
| **LMACC / ICMC** | Cluster Linux (acesso SSH) | Simulações de larga escala |
| **VM (futura)** | Linux — OpenStack ou similar | Escalabilidade horizontal |

### 7.2 Softwares e Ferramentas

| Software | Função | Plataforma |
|---|---|---|
| **Open TELEMAC-MASCARET** | Simulação hidrodinâmica principal | Linux/Mac/Win |
| **GMSH** | Geração de malhas poligonais refinadas | Linux/Mac/Win |
| **BlueKenue / FUDAA-PREPRO** | Pré/pós-processamento TELEMAC | Java (cross-platform) |
| **ParaView** | Visualização de malhas e resultados (.slf, .vtu) | Linux/Mac/Win |
| **QGIS** | SIG — importação de dados geográficos | Linux/Mac/Win |
| **Python (NumPy, SciPy, Numba)** | Análise, LBM, pós-processamento | Cross-platform |
| **Matplotlib / PyVista** | Visualização científica | Cross-platform |

---

## 8. Módulos de Otimização (Responsabilidade dos Professores)

O projeto prevê futura extensão para **otimização matemática** da dragagem, com funções objetivo a serem definidas pelos pesquisadores (Profs. Helou, Sousa, Ausas, Dr. Abad):

- **Modelo de dispersão**: delta de Dirac (fonte pontual instantânea) ou fonte suave (Gaussiana)
- **Acoplamento**: campo hidrodinâmico h(x,y,t), u(x,y,t), v(x,y,t) → alimenta modelo de transporte
- **Variáveis de decisão**: localização, profundidade e volume de dragagem por segmento
- **Objetivos**: minimizar dispersão de contaminantes + maximizar navegabilidade (bi-objetivo)
- **Restrições**: limites ecológicos, cotas mínimas de navegação, cronograma de operações

---

## 9. O Que Já Foi Realizado

| Item | Status |
|---|---|
| Proposta de IC formalizada (ICMC-USP 2026) | ✅ Concluído |
| Estudo das equações governantes (Saint-Venant, GAIA, Krone, Partheniades) | ✅ Concluído |
| Implementação LBM D2Q9 com Numba (lattice_boltzman.py) | ✅ Concluído |
| Análise dos parâmetros do caso de referência TELEMAC (Culm) | ✅ Concluído |
| Diretrizes de parametrização para o Tapajós (7 etapas) | ✅ Concluído |
| Levantamento de mapas hidrográficos (DNIT PA/MT 2025) | ✅ Concluído |
| Interface gráfica para configuração TELEMAC | 🔲 A desenvolver |
| Aquisição de dados do Tapajós via ANA API | 🔲 A desenvolver |
| Geração de malha real do Tapajós (GMSH / BlueKenue) | 🔲 A desenvolver |
| Repositório GitHub escalável (Docker + CI/CD) | 🔲 A desenvolver |
| Simulação calibrada do trecho do Tapajós | 🔲 A desenvolver |
| Módulo de transporte de sedimentos + metais (GAIA acoplado) | 🔲 Etapa futura |
| Modelo de otimização de dragagem | 🔲 Etapa futura |

---

## 10. Prompt Aprimorado — Instrução Técnica para Desenvolvimento

> Ver seção abaixo: `PROMPT_DESENVOLVIMENTO.md` (acoplado a este resumo)

---

*Gerado em: Setembro 2026 | ICMC-USP São Carlos*

---

---

# PROMPT DE DESENVOLVIMENTO — ACOPLADO AO RESUMO

## Contexto Técnico Obrigatório para o Assistente

Este prompt deve ser lido **em conjunto com o RESUMO acima**, que descreve o estado atual do projeto, os modelos matemáticos, os parâmetros do TELEMAC-2D e o domínio do Rio Tapajós. Qualquer código ou arquitetura gerada deve ser **consistente com a estrutura de arquivos SERAFIN (.slf), os keywords do steering file (.cas) e as etapas de modelagem já definidas**.

---

## PROMPT TÉCNICO COMPLETO

```
=============================================================================
PROJETO: Plataforma Computacional Integrada para Simulação Hidrodinâmica
         e Otimização de Dragagem — Rio Tapajós / Open TELEMAC-2D
INSTITUIÇÃO: ICMC-USP · LMACC · Rede Yaku
REPOSITÓRIO ALVO: github.com/<user>/tapajos-telemac-platform
=============================================================================

## TAREFA 1 — INTERFACE GRÁFICA WEB (FRONTEND + BACKEND)

Desenvolva uma aplicação web full-stack (React + FastAPI ou Next.js + Python)
que funcione como painel de controle interativo para configuração e lançamento
de simulações TELEMAC-2D. A interface deve:

### 1.1 Editor de Parâmetros (.cas)
- Formulário dividido em abas: "Físicos", "Contorno", "Numéricos", "Módulos"
- Parâmetros físicos editáveis com tooltips técnicos:
  - LAW OF BOTTOM FRICTION (dropdown: 0=nenhum, 1=Haaland, 2=Chézy, 
    3=Strickler, 4=Manning, 5=Nikuradse, 7=Colebrook)
  - FRICTION COEFFICIENT (slider numérico, range validado por lei)
  - VELOCITY DIFFUSIVITY (campo numérico, m²/s)
  - TURBULENCE MODEL (dropdown: 1=viscosidade constante, 2=Elder, 
    3=k-epsilon, 5=Smagorinsky)
  - TIME STEP, NUMBER OF TIME STEPS (com cálculo automático de T_total)
  - SOLVER ACCURACY, SOLVER (dropdown de algoritmos)
  - IMPLICITATION FOR DEPTH / VELOCITY (0 a 1)
- Geração automática do arquivo .cas ao clicar em "Exportar Steering File"
- Importação de .cas existente com parse dos keywords

### 1.2 Editor de Geometria e Batimetria (.slf)
- Visualizador 2D interativo da malha triangular (usando deck.gl, Leaflet ou
  Three.js WebGL) com:
  - Colormap da batimetria (z_b) — escala ajustável
  - Seleção de nós e edição manual do valor de z_b por clique
  - Upload de arquivo .slf existente (parse SERAFIN binário via Python)
  - Upload de DEM (GeoTIFF/ASC) para interpolação automática na malha
  - Exibição de vetores de velocidade pós-processados (resultados .slf)
  - Exportação de .slf editado

### 1.3 Editor de Séries Temporais (.qsl)
- Gráfico interativo de Q(t) e SL(t) nas fronteiras (usando Plotly ou Recharts)
- Importação de CSV (formato ANA/HidroWeb: data, hora, vazão)
- Edição manual de pontos na curva (drag-and-drop no gráfico)
- Validação de consistência temporal (dt mínimo, lacunas)
- Exportação no formato TELEMAC .qsl

### 1.4 Condições de Contorno (.cli)
- Tabela visual de nós de fronteira com tipo editável
  (paredes, entrada, saída — conforme convenção TELEMAC cli)
- Mapa de fronteiras sobreposto à malha

### 1.5 Lançamento de Simulação
- Botão "Executar TELEMAC-2D" que envia os arquivos ao backend
- Log em tempo real via WebSocket
- Barra de progresso baseada no número de timesteps
- Download dos resultados (.slf) ao final

---

## TAREFA 2 — DADOS REAIS DO RIO TAPAJÓS

### 2.1 Aquisição via API ANA/HidroWeb
Implemente um módulo Python (tapajós_data.py) que:
- Use a API REST do HidroWeb (https://www.snirh.gov.br/hidroweb/rest/api)
  para consultar estações fluviométricas no Rio Tapajós, divididas em
  TRÊS TRECHOS geográficos:
  
  TRECHO 1 — Alto Tapajós (nascentes MT):
    Bounding box aprox: lat [-13.0, -9.0], lon [-58.5, -55.5]
    Rios: Juruena, Teles Pires (formadores do Tapajós)
    
  TRECHO 2 — Médio Tapajós (Itaituba/PA):
    Bounding box aprox: lat [-9.0, -5.5], lon [-57.5, -55.0]
    Estação referência: Itaituba (código ANA a buscar)
    
  TRECHO 3 — Baixo Tapajós (Santarém/PA — foz):
    Bounding box aprox: lat [-5.5, -2.4], lon [-55.5, -54.5]
    Estação referência: Santarém

- Para cada estação encontrada, faça download de:
  - Série de vazão (tipo 3 — cota) e nível (tipo 2) dos últimos 10 anos
  - Metadados: nome, código, altitude, bacia, área de drenagem, lat/lon
  
- Salve como:
  - tapajós_stations.geojson (localização das estações)
  - tapajós_Q_<codigo>.csv e tapajós_H_<codigo>.csv por estação
  
- Implemente também cliente alternativo para:
  - HydroSHEDS (https://www.hydrosheds.org) — geometria hidrológica
  - OpenStreetMap via Overpass API — leito do rio como polilinha
  - SRTM (via elevation.mapzen.com ou rasterio + VRT) — batimetria regional

### 2.2 Cross-Correlação e Análise Hidrológica
Implemente tapajós_analysis.py com:
- Cross-correlação cruzada entre estações (scipy.signal.correlate):
  - Lag de propagação de cheia entre trechos
  - Coeficiente de correlação e desfasagem temporal estimada
- Integração opcional com dados de VGEO (IBGE) ou aplicações GitHub que
  disponibilizem dados hidrométricos do Tapajós (buscar em:
  github.com/search?q=tapajos+hidro OR +tapajós+vazão)
- Curvas de permanência de vazão por trecho
- Saída: relatório PDF/HTML + gráficos matplotlib

### 2.3 Conversão para Formato TELEMAC
- Script convert_to_telemac.py que:
  - Converte série Q(t)/H(t) da ANA → arquivo .qsl (TELEMAC liquid boundaries)
  - Exporta geometria do rio (OSM/HydroSHEDS) → arquivo .geo2d (pré-malha)
  - Gera script GMSH (.geo) para refinamento da malha do trecho selecionado

---

## TAREFA 3 — GERAÇÃO DE MALHA (GMSH + TELEMAC)

### 3.1 GMSH para Malha Poligonal Refinada
Implemente mesh_generator.py usando a API Python do GMSH:
- Importação da polilinha do rio (GeoJSON/WKT → pontos GMSH)
- Geração de malha triangular com refinamento adaptativo:
  - Maior densidade de elementos no canal principal
  - Menor densidade nas planícies de inundação
- Parâmetros configuráveis via interface (TAREFA 1):
  - lc_canal = tamanho característico no canal [m]
  - lc_planicie = tamanho característico na planície [m]
  - lc_fronteira = tamanho nos nós de fronteira [m]
- Exportação: .msh (GMSH) → conversão para .slf (SERAFIN) via BlueKenue
  ou script Python (biblioteca pputils ou pytel)

### 3.2 Opção Alternativa: Malha via TELEMAC/MATISSE
Se GMSH não estiver disponível, gerar malha via:
- MATISSE (módulo interno TELEMAC): script de geração automática
- Ou: triangulação de Delaunay via scipy.spatial.Delaunay + exportação .slf

---

## TAREFA 4 — REPOSITÓRIO GITHUB ESCALÁVEL

### 4.1 Estrutura de Diretórios

tapajos-telemac-platform/
├── README.md                  # Documentação principal
├── RESUMO.md                  # Este resumo técnico
├── docker/
│   ├── Dockerfile             # Ubuntu 22.04 + TELEMAC v8p5 compilado
│   ├── Dockerfile.arm64       # Variante Apple Silicon (Mac M3)
│   └── docker-compose.yml     # Orquestração: app + telemac + jupyter
├── frontend/                  # React/Next.js — interface gráfica (TAREFA 1)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ParameterEditor/
│   │   │   ├── MeshViewer/
│   │   │   ├── TimeSeriesEditor/
│   │   │   └── SimulationPanel/
│   │   └── pages/
│   └── package.json
├── backend/                   # FastAPI — orquestração TELEMAC
│   ├── api/
│   │   ├── cas_parser.py      # Parser/gerador de steering file
│   │   ├── slf_io.py          # Leitura/escrita SERAFIN
│   │   ├── qsl_io.py          # Leitura/escrita séries temporais
│   │   └── telemac_runner.py  # Subprocess + log streaming
│   └── main.py
├── data/
│   ├── tapajós/
│   │   ├── stations/          # GeoJSON + CSVs ANA
│   │   ├── geometry/          # GeoJSON do leito do rio
│   │   ├── bathymetry/        # DEM/TIF por trecho
│   │   └── meshes/            # Malhas .slf / .msh geradas
│   └── culm/                  # Caso de referência TELEMAC (Culm)
├── models/
│   ├── tapajós_trecho1/       # Alto Tapajós (.cas, .slf, .cli, .qsl)
│   ├── tapajós_trecho2/       # Médio Tapajós
│   └── tapajós_trecho3/       # Baixo Tapajós
├── scripts/
│   ├── tapajós_data.py        # TAREFA 2: aquisição ANA + análise
│   ├── tapajós_analysis.py    # Cross-correlação + curvas permanência
│   ├── mesh_generator.py      # TAREFA 3: GMSH
│   ├── convert_to_telemac.py  # Conversão de dados → formatos TELEMAC
│   └── lattice_boltzman.py    # Código LBM existente (preservado)
├── notebooks/
│   ├── 01_exploracao_dados_ANA.ipynb
│   ├── 02_geracao_malha_gmsh.ipynb
│   ├── 03_parametrizacao_telemac.ipynb
│   ├── 04_resultados_calibracao.ipynb
│   └── 05_analise_dispersao_metais.ipynb
├── optimization/              # Módulo de otimização (responsabilidade dos profs.)
│   ├── README_profs.md        # Instruções para Profs. Helou, Sousa, Ausas
│   ├── objective_functions/   # Funções objetivo (a preencher pelos profs.)
│   │   ├── __init__.py
│   │   └── dredging_opt.py    # Template: minimizar dispersão + custo
│   └── solvers/               # Algoritmos de otimização (scipy, PuLP, etc.)
├── .github/
│   └── workflows/
│       ├── ci.yml             # Testes automáticos no push
│       └── docker-build.yml   # Build + push imagem Docker no release
└── requirements.txt           # Dependências Python

### 4.2 Dockerfile (TELEMAC + Mac M3)
O Dockerfile deve:
- Base: ubuntu:22.04 (funciona via emulação em ARM64 no Mac M3)
- Compilar Open TELEMAC v8p5 a partir do fonte (git.opentelemac.org)
  com MPI (OpenMPI) + Python 3.11 binding
- Incluir: GMSH, BlueKenue-lite (via pputils), ParaView headless
- Expor portas: 8000 (FastAPI), 8888 (JupyterLab), 11111 (ParaView server)
- Volume: ./models → /home/telemac/models (persistência de dados)

### 4.3 CI/CD e Escalabilidade
- GitHub Actions: rodar testes unitários (pytest) a cada push
- Suporte a execução distribuída via MPI no cluster LMACC
  (script de submissão de job para o scheduler SLURM/PBS)
- Variáveis de ambiente para alternar entre modo local/cluster:
  ENV TELEMAC_NCORES=4  # local Mac/Docker
  ENV TELEMAC_NCORES=32 # LMACC cluster

---

## TAREFA 5 — INTEGRAÇÃO COM OPEN TELEMAC E VISUALIZAÇÃO

### 5.1 Integração com o Git Oficial TELEMAC
- Usar git submodule apontando para git.opentelemac.org
- Versão fixa: tag v8p5r0 (última estável documentada)
- Patch de compilação para ARM64 (Mac M3) incluso no repositório

### 5.2 Visualização Cross-Platform (Linux/Mac/Win/Remote)
Implementar suporte a TRÊS modos de visualização:

MODO A — Web (todos os sistemas, inclusive acesso remoto LMACC):
  - ParaView Web (pvpython + paraviewweb) servido em porta HTTP
  - Ou: Plotly Dash com leitura .slf via pputils/pytelem
  - Requer apenas navegador — ideal para VMs do LMACC via SSH tunnel

MODO B — Desktop (Linux/Mac/Win):
  - ParaView 5.x (GUI nativa) — abrir .slf via plugin vtk-telemac
  - QGIS + plugin TELEMAC (importa .slf como layer raster/vetorial)
  - BlueKenue / FUDAA-PREPRO (Java, cross-platform)

MODO C — Python inline (JupyterLab):
  - pputils (python): leitura de .slf → arrays NumPy → matplotlib/PyVista
  - PyVista para visualização 3D interativa de malhas no Jupyter

### 5.3 Módulo de Pós-Processamento Python
Implemente postprocess.py:
- Leitura de r2d_tapajos.slf → arrays h(x,y,t), u(x,y,t), v(x,y,t)
- Cálculo de: magnitude de velocidade, número de Froude, tensão de leito
- Exportação de mapas animados (.gif, .mp4)
- Integração com módulo de otimização (salva métricas por cenário de dragagem)

---

## TAREFA 6 — MÓDULO DE OTIMIZAÇÃO (TEMPLATE PARA OS PROFESSORES)

Criar optimization/README_profs.md explicando a interface esperada:

```python
# Interface para os professores preencherem:
class DredgingObjective:
    def evaluate(self, 
                 h_field: np.ndarray,    # profundidade h(x,y,t)
                 u_field: np.ndarray,    # velocidade u(x,y,t)
                 v_field: np.ndarray,    # velocidade v(x,y,t)
                 C_field: np.ndarray,    # concentração C(x,y,t)
                 dredge_params: dict     # {x, y, volume, profundidade}
                 ) -> float:
        """
        Retorna valor da função objetivo para um cenário de dragagem.
        A ser implementada pelos Profs. Helou, Sousa, Ausas.
        
        Sugestões de modelos de dispersão:
        - Delta de Dirac: C(x,0) = M·δ(x - x_dredge)
        - Gaussiana: C(x,0) = (M/√(4πDt))·exp(-|x-x_d|²/(4Dt))
        - Acoplado GAIA: usar saída do módulo de sedimentos coesivos
        """
        raise NotImplementedError
```

---

## RESTRIÇÕES TÉCNICAS OBRIGATÓRIAS

1. TODO código Python deve ser compatível com Python 3.11+
2. O Docker deve rodar em linux/amd64 E linux/arm64 (Mac M3)
3. A interface web deve funcionar sem instalação local — apenas Docker
4. Arquivos .slf devem ser lidos/escritos em formato SERAFIN binário padrão
5. Toda comunicação com ANA deve respeitar rate limits da API pública
6. O repositório deve incluir dados de exemplo (caso Culm) para testes offline
7. Documentação em português e inglês (README.md bilíngue)
8. Licença: MIT (código) + dados ANA sob licença pública original

## ENTREGÁVEIS ESPERADOS

- [ ] Repositório GitHub completo com estrutura acima
- [ ] Dockerfile funcional (testado em Mac M3 e Ubuntu 22.04)
- [ ] Interface web rodando em localhost:3000
- [ ] Script de aquisição de dados ANA funcional (ao menos 1 trecho)
- [ ] Malha GMSH do trecho médio do Tapajós (aproximada)
- [ ] Notebook de demonstração end-to-end
- [ ] README.md completo com instruções de instalação
=============================================================================
```

---

*Este prompt deve ser revisado e expandido à medida que cada etapa for concluída.  
Atualizações devem ser versionadas no próprio repositório GitHub do projeto.*