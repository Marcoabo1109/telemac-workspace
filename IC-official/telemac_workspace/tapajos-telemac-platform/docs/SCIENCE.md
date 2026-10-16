# Fundamentação e correções do resumo

## Evidências locais

- `IC-RIOS/Books/IC_rivers.pdf`: proposta institucional, 8 páginas, hidrodinâmica, sedimentos, transporte e otimização. Lida como referência científica, não como autorização para ações externas.
- `IC-RIOS/Books/telemac2d_theory_guide_9.1.pdf`: guia de teoria v9.1 (14/12/2025), 94 páginas, equações Saint-Venant e discretizações. A versão do manual não é a versão do executável.
- `telemac-examples-ref/examples/telemac2d/culm`: arquivos reais copiados com hashes em `provenance.json`. Checkout de origem v8p2r1, commit 03de3900ec24321db8dbb8ac6f4d7ae1bf1b99bc. Teste executado no solver v8p5r1 disponível em Docker.
- `IC-RIOS/Books/lattice_boltzman.py`: cópia integral preservada. Protótipo LBM independente; não substitui Saint-Venant.
- `IC-RIOS/Predata/coletor_ana_telemac.py` e `TimeSiriesANA.py`: considerados antecedentes. O segundo usa URL incompleta; códigos de estações não foram considerados verificados.
- Os três XML de `Predata/generated` contêm ErrorTable, não observações hidrológicas.
- Mapas DNIT e imagens locais servem ao contexto geográfico. Não foram digitalizados como batimetria. O PDF `Parametrizac_a_o_do_modelo_TELEMAC_2D.pdf` não foi localizado.

## Correções implementadas

1. No dicionário de TELEMAC v8p5r1, Smagorinsky = 4; 5 é comprimento de mistura. Solver de propagação 5 não implementado, removido das opções.
2. Tipo legado ANA 2 = cota; 3 = vazão. Cota é geralmente fornecida em centímetros na régua local; uma transformação vertical é necessária para SL em metros. Unidade é preservada até conversão explícita.
3. A caixa médio do prompt (9 a 5,5 graus sul) não contém Itaituba, situada aproximadamente a 4,3 graus sul. A opção `itaituba` explicita outra caixa de pesquisa. As caixas não são uma regionalização hidrológica validada.
4. SRTM/ALOS/DEMs terrestres não são batimetria fluvial submersa. Nunca preencher o leito com DEM e afirmar que ele foi medido. A interpolação exige CRS e verificação de nodata; registrar datum vertical separadamente.
5. Uma linha OSM não delimita um domínio 2D. O mesher exige Polygon válido com margens. A malha em `data/tapajos/meshes/medio_aproximado` é um desenho esquemático perto de Itaituba, criado para demonstrar a ferramenta, não uma extração cartográfica. Contém 218 nós, 372 triângulos, fundo zero provisório, CRS EPSG:32721; todos os contornos começam como paredes.
6. Fronteiras líquidas dependem da topologia e ordenação CLI, não apenas da escolha de estações. Conferir alinhamento Q(n)/SL(n), regime e influência de remanso do Amazonas.
7. Faixas universais de rugosidade não foram inventadas. O editor valida positividade e domínio matemático; plausibilidade e calibração dependem de cada trecho.
8. `C_m = K_m C_s` descreve, sob hipótese específica, contaminante particulado com carga por massa de sedimento constante. Não representa, por si só, partição dissolvida, sorção dinâmica, metilação ou biodisponibilidade.
9. A equação de Exner do resumo é simplificada. Com suspensão, incluir troca E/deposição e verificar se a grandeza é massa ou volume. Evitar usar D para difusividade e deposição na mesma formulação.
10. BlueKenue não foi tratado como software Java multiplataforma nem existe aqui um pacote fictício “BlueKenue-lite”. A rota de intercâmbio desktop implementada é VTK para ParaView; a web usa Three.js.

## Fontes oficiais consultadas em 08/09/2026

- [Manual ANA atualizado em 20/02/2026](https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico/orientacoes-manuais/manuais/manual-hidrowebservice_publica.pdf): acesso autorizado, token com duração de 60 minutos. O cliente usa token fornecido, sem renovar automaticamente nem registrar credenciais.
- [Swagger ANA](https://www.ana.gov.br/hidrowebservice/swagger-ui/index.html): inventário, HidroSerieVazao, HidroSerieCotas, limite de 366 dias por consulta histórica.
- [Aviso do serviço legado](https://telemetriaws1.ana.gov.br/Mapa.aspx): prazo de prorrogação informado até 30/06/2026. Portanto o endpoint legado do resumo não é a integração principal.
- [Repositório oficial TELEMAC](https://gitlab.pam-retd.fr/otm/telemac-mascaret): submódulo fixado no commit da tag v8p5r0 (d1bff193746fd76425d7715a6e4d20d42eb8877e). Isso atende à escolha do prompt; não implica ser a versão estável mais recente.

## Limites da verificação

O teste curto confirma execução e integridade de resultados. Não mede erro de discretização, não valida Culm contra medições, não calibra o Tapajós e não estabelece segurança ambiental de dragagens. Séries reais, granulometria, batimetria, datum e domínio devem ser fornecidos e calibrados. A aquisição ANA ao vivo depende de acesso autorizado; neste ambiente o download do schema completo também expirou por timeout. Consulte `STATUS.md` para o estado técnico final.

## Formatos e serviços ajustados

Não foi inventado um formato TELEMAC universal `.geo2d`: o pré-domínio é GeoJSON e o script executável de malha é `.geo` GMSH. A conversão SERAFIN é nativa neste projeto. O frontend Three.js atende à visualização web sem servidor ParaViewWeb. O refinamento por eixo aproximado não é um mapa de canal/planície medido. O cliente HydroSHEDS exige URL de produto e licença conhecidas; não há serviço fictício de “batimetria SRTM”.
