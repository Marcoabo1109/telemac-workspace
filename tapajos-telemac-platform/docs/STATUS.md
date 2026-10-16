# Estado dos entregáveis — 08/09/2026

## Entregue e verificado

| Entregável | Evidência |
|---|---|
| Plataforma React + FastAPI | Disponível em http://localhost:3000 via Docker Compose; API em :8000 |
| Editor de parâmetros | Abas físicas, contorno, numéricos e módulos; importação/exportação CAS, opções corrigidas pelo dicionário |
| Leitura/escrita SERAFIN | Testes com Culm, big/little endian, single/double precision, edição e corrupção de registros |
| Visualizador WebGL | Malha, seleção de nós, edição BOTTOM, escala, campos e instantes de resultados, vetores de velocidade |
| Séries temporais | QSL real de Culm, CSV de vazão, tabela e edição vertical no gráfico; exportação com validação |
| Condições de contorno | CLI de 13 colunas, edição de tipos e visualização de nós sobre a malha |
| Execução real | Jobs isolados; logs WebSocket; resultado disponível apenas após sucesso; teste HTTP e navegador concluídos |
| MPI em dois processos | Culm concluído com partel e gretel; ver `native-smoke-mpi.json` e diferenças serial/MPI registradas |
| Compilação TELEMAC ARM64 | Ubuntu 22.04 + Python 3.11 + MPI + v8p5r0 compilados nativamente; Culm executado com retorno correto |
| Aplicação ARM64 e amd64 | Ambas construídas; suíte de testes passou nas duas arquiteturas com Python 3.11 |
| Malha aproximada | Itaituba esquemática: 218 nós, 372 triângulos, EPSG:32721, fundo provisório zero; não representa levantamento real |
| Análise científica | Correlação por lag com pares válidos, permanência, conversão de unidade/datum, HTML e gráficos, métricas e animação |
| Notebook ponta a ponta | `03_parametrizacao_telemac.ipynb`: cinco células executadas com solver real, saídas salvas |
| Repositório local | Estrutura, documentação PT/EN, licenças separadas, hashes, testes, CI/CD e submódulo fixado em v8p5r0 |
| Otimização | Interface reservada aos professores com `NotImplementedError` intencional, unidades e hipóteses documentadas |

## Testes e resultados

- Suíte Python: 19 testes inicialmente aprovados em macOS/Python 3.14 e em containers Linux ARM64/amd64/Python 3.11. Revisão adicional da coluna CLI de atrito acrescentou um teste (20 no total, aprovados em macOS e no Ubuntu do solver).
- Frontend: `npm run build` concluído. Há aviso de tamanho do bundle Three.js/Recharts; não impede uso. Sem fontes/CDNs externas necessárias para o painel offline.
- Caso Culm: 20 passos × 2 s; frames 0, 10, 20, 30, 40 s; 1.130 nós; 2.019 triângulos. Ver `smoke-run.json` e `native-smoke.json`.
- `reports/culm_smoke`: resultado SERAFIN, VTK, campos/métricas e GIF. Teste de software, não calibração.
- Verificação visual: navegação no painel, execução, status completed e abertura de resultados observados no navegador.
- Testes de compatibilidade GMSH 4.8 (apt Linux) e 4.15 (macOS pip). O pacote pip GMSH não está disponível para Linux ARM64, portanto a receita usa a biblioteca nativa do sistema.

## Dependências externas e limites restantes

1. **ANA real:** não há token de acesso no ambiente. Os três XML locais são respostas de erro. O cliente atual usa Bearer, cache e limites de frequência; resolve parâmetros históricos a partir do OpenAPI oficial ou de `ANA_OPENAPI_FILE`. A aquisição ao vivo e a normalização do schema da conta ainda não estão validadas. Nenhum dado sintético é apresentado como observação ANA.
- Em 09/09/2026, adquirido eixo OSM pela API oficial e estatísticas mensais SGB. Detalhes em `models/tapajos_trecho1/README.md`. Overpass falhou, mas a API de mapa funcionou.
2. **Tapajós real:** faltam polígono de margens verificado, levantamento batimétrico, datum, séries observacionais e granulometria. Não foi gerado um caso supostamente calibrado nem uma análise ambiental de dragagem.
3. **GitHub:** destino identificado: repositório privado `Marcoabo1109/IC`, subdiretório `telemac_workspace/tapajos-telemac-platform`. Ver `GITHUB.md` para instruções.
4. **GAIA/metais:** acoplamento reativo e funções objetivo não foram implementados como ciência pronta; dependem dos pesquisadores. A execução web rejeita código Fortran e arquivos acoplados arbitrários; usar CLI revisado para casos avançados.
5. **Cluster:** templates SLURM/PBS disponíveis; submissão e desempenho não testados sem acesso LMACC. Jupyter é perfil opcional; imagem/ambiente notebook separado não foi iniciado, mas o notebook ponta a ponta foi executado no container do solver.
6. **Escala e interface:** SERAFIN 2D triangular em memória (upload até 64 MiB); sem autenticação multiusuário e sem fila persistente. Séries muito grandes são amostradas no gráfico, preservando os registros na exportação. CAS inglês; comentários não são preservados. DEM amostrado exige CRS e cobertura completa, sem correção automática de datum vertical.
7. **Precisão física:** o teste curto não é convergência de malha, calibração, validação de modelo ou autorização de dragagem. Ver `SCIENCE.md`.

## Retomar

```bash
cd /Users/marcoabo/telemac_workspace/tapajos-telemac-platform
docker compose -p tapajos-platform -f docker/docker-compose.yml -f docker/compose.telemac.yml up -d --build
```

Para encerrar apenas a plataforma criada: o mesmo comando Compose seguido de `stop` em lugar de `up -d --build`. O container original `nice_austin` não é parte desta composição.

## Atualização de 09/09/2026

- Coletados: eixo OSM do Tapajós em Itaituba e 12 registros de estatísticas mensais SGB, com fontes e unidades. Não são séries diárias adquiridas da ANA.
- Caso exploratório completo em `models/tapajos_trecho1`, com largura, fundo, vazão e datum assumidos conforme autorização do usuário.
- Integração real TELEMAC de 3.600 s, 31 frames, 228 nós/397 triângulos. Profundidade mínima 3,789 m, velocidade máxima 1,474 m/s, Froude máximo 0,234; traçador entre 0 e 1. Resultados em `reports/tapajos_initial`.
- Corrigida associação de fronteiras após inspecionar o log do solver: saída 1, entrada 2. Execução sem profundidades negativas e com transporte ativo. A primeira tentativa inconsistente foi rejeitada; seus artefatos temporários não integram o relatório publicado.
- 22 testes Python aprovados; frontend compilado. O aplicativo inicia no cenário Tapajós e mantém Culm disponível.
- Cenário sem calibração, convergência de malha ou química de metais; limites científicos preservados.
