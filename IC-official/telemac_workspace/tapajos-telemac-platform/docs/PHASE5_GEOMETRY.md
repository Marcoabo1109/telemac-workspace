# Fase 5 — geometria e batimetria observadas

## Aquisição inicial

Foram localizadas e baixadas as cartas náuticas oficiais CHM 4382B e 4383, que
cobrem respectivamente o trecho até Itaituba e o trecho Itaituba–São Luís do
Tapajós. A proveniência, hashes e inspeção técnica estão em
`data/tapajos/bathymetry/chm/README.md`.

As cartas oferecem linha de costa, ilhas, sondagens e referências de navegação,
mas são rasters cartográficos. Não constituem um modelo batimétrico contínuo e
seus pixels não podem ser convertidos automaticamente em profundidade.

## Fluxo de trabalho proposto

1. confirmar datum horizontal, referência vertical/redução de sondagem e edição
   de cada carta;
2. recortar o domínio Itaituba–Miritituba e digitalizar margens/ilhas com
   rastreabilidade para a carta de origem;
3. digitalizar sondagens e curvas somente após definir a correção pela régua e a
   referência vertical;
4. buscar perfis transversais e levantamentos hidrográficos mais recentes junto
   à ANA/SGB, CHM, DNIT e estudos portuários licenciados;
5. construir uma nuvem de pontos com `x`, `y`, profundidade/cota, data, fonte,
   datum e incerteza;
6. interpolar apenas dentro da cobertura suportada, testar sensibilidade e
   reservar seções independentes para validação.

## Critério para concluir a fase

A Fase 5 só pode ser declarada pronta quando o domínio tiver margens verificadas,
batimetria/seções com referência vertical conhecida e metadados de precisão. As
cartas náuticas isoladamente avançam a aquisição, mas não removem os bloqueios
`surveyed-bank-polygon`, `surveyed-bathymetry` e `vertical-datum-tie`.
