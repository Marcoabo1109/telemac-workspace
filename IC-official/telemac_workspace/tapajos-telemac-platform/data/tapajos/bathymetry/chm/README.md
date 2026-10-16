# Cartas náuticas oficiais — apoio à Fase 5

Arquivos baixados localmente em 01/10/2026 do Centro de Hidrografia da Marinha
(CHM). Os binários não são versionados: devem ser obtidos novamente das fontes
oficiais e sua licença deve ser revisada antes de redistribuição.

| Carta | Trecho | Arquivo oficial | SHA-256 do ZIP local |
|---|---|---|---|
| 4382B | Das Ilhas do Prado a Itaituba | `4382bgeotiff.zip` | `581c78a41ad5af7b6fd0b0d50ebbba8627cfe63635a4bb827da404a3124ff1b2` |
| 4383 | De Itaituba a São Luís do Tapajós | `4383geotiff_0.zip` | `b0168faf1a0db9f445c13c8900e94e130afb88e40ffbe812ea3a5d49051a1964` |

Fontes:

- https://www.marinha.mil.br/chm/dados-do-segnav/cartas-raster
- https://www.marinha.mil.br/chm/sites/www.marinha.mil.br.chm/files/geotiff/4382bgeotiff.zip
- https://www.marinha.mil.br/chm/sites/www.marinha.mil.br.chm/files/geotiff/4383geotiff_0.zip

## Inspeção inicial

- 4382B: GeoTIFF RGB de carta raster, software CARIS++ 4.2.0, arquivo datado de
  17/11/2021; imagem principal 15.937 × 12.494 pixels.
- 4383: GeoTIFF RGB de carta raster, software CARIS++ 6.5.35, arquivo datado de
  26/02/2024; imagem 27.697 × 20.128 pixels, projeção Mercator/WGS 84 declarada.

Esses GeoTIFFs são imagens georreferenciadas de cartas náuticas. Os valores RGB
**não são profundidades** e não podem preencher diretamente o campo `BOTTOM`.
As sondagens, contornos, referências de redução e avisos aos navegantes precisam
ser interpretados/digitalizados e comparados com levantamentos mais recentes.

O site do CHM informa licença Creative Commons Atribuição-SemDerivações 3.0 para
o conteúdo da página e orienta contato prévio para adoção comercial das cartas.
O uso nesta pesquisa deve preservar atribuição e registrar claramente qualquer
produto derivado de interpretação.
