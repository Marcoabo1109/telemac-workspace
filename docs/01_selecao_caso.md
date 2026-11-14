# Seleção do caso

Os três modelos fluviais documentam trechos. Nenhum dos três representa um curso inteiro da nascente à foz. Selecionamos o domínio integral distribuído do Culm, incluindo planície inundável, sem recortar sua malha. A conclusão sobre cobertura se limita aos exemplos examinados.

Fontes: tapajos-telemac-platform/vendor/telemac/examples/telemac2d/{culm,donau,riogrande}, especialmente doc/*.tex, geo_*.slf, *.cli e t2d_*.cas. Comprimentos medidos diretamente nos três lados de cada triângulo, incluindo lados compartilhados.

|Trecho|Nós / triângulos|Arestas mín./mediana/máx. (m)|Fundo|Contornos e atrito|Custo|
|---|---:|---:|---|---|---|
|Culm, Devon (11 km)|1130 / 2019|1,11 / 81,38 / 322,91|BOTTOM Selafin do exemplo, calha refinada e triângulos alongados, levantamento original não identificado|28,32 m³/s e 23,77 m iniciais, Strickler 30|23–86 s históricos no CAS para configurações diversas|
|Danúbio perto de Deggendorf (7,7 km)|47543 / 93209|0,63 / 7,31 / 32,46|BOTTOM e rugosidade Selafin; quatro pontes|218 m³/s, 309,205 m, domínios em roughness.tbl|896–3080 s históricos em série|
|Rio Grande (≈6 km)|4989 / 8268|2,51 / 7,50 / 13,48|BOTTOM Selafin esquemático, malha mais uniforme|15,43 m³/s, 7,62 m, Chézy 55; arquivo temporal e Fortran|≈0,76 vezes o custo do Culm original por elementos × passos, sem benchmark|

Nenhum desses três diretórios contém um CAS sedimentológico ou de dragagem pronto. O exemplo gaia/nestor distribuído em examples/nestor/nestor1_Dig fornece a estrutura de acoplamento. Culm tem restart e malha pequena para comparações pareadas. Precisamos adicionar traçador, granulometria exploratória, contorno sedimentológico e polígono de remoção. A granulometria e a cota de projeto dependem de dados e decisão do orientador.

A busca textual nos capítulos doc/*.tex de examples/telemac2d também localizou Wesel (Reno), Mersey (estuário), Malpasset (ruptura de barragem), confluence e riv_art. A documentação consultada não identificou modelo distribuído demonstravelmente contínuo da nascente à foz com as entradas necessárias para esta cadeia. O acoplamento disponível foi confirmado no cabeçalho do solver e nos casos de examples/nestor; a versão v8 já inclui GAIA.
