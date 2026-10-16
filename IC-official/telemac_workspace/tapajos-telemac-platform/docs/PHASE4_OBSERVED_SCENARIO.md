# Fase 4 — primeiro cenário com forçantes observadas

## Janela selecionada

Foi selecionado o ano civil de 2007 porque as quatro séries de controle possuem
365 observações diárias, sem interpolação:

- vazão de montante: Acará do Tapajós `17650002`;
- cota de jusante: Itaituba `17730000`;
- vazão de controle: Buburé `17710000`;
- cota de controle: Buburé `17710000`.

A vazão de Acará variou de 3.423,06 a 28.678,60 m³/s. A cota de Itaituba
variou de 188 a 833 cm sobre o zero local da régua. A correlação bruta máxima
entre vazão de Acará e cota de Itaituba ocorreu com defasagem de 22 dias
(`r = 0,8308`, 343 pares). Esse valor é apenas diagnóstico: tendência sazonal,
armazenamento e afluências intermediárias impedem interpretá-lo diretamente
como tempo de viagem.

## Artefatos

- `data/tapajos/scenarios/observed_2007/forcing_daily.csv`: séries alinhadas,
  tempo em segundos, unidades e indicadores de consistência.
- `forcing_local_gauge_datum.qsl.template`: template TELEMAC com vazão observada
  e cota em metros sobre o zero local da régua.
- `scenario.json`: período, estatísticas, hashes, bloqueios e proveniência.
- `reports/hydrology/observed_2007/hydrographs.png`: hidrogramas e cotagramas.
- `reports/hydrology/observed_2007/duration_lag.png`: permanência e defasagem.
- `control_summary.json`: resultados numéricos dos gráficos.

Reprodução:

```bash
python -m scripts.observed_scenario
```

## Estado científico

O pacote está marcado como `forcing_prepared_execution_blocked`. Ele não deve
ser executado ou apresentado como cenário calibrado porque:

1. o zero da régua de Itaituba não está ligado ao datum vertical da malha;
2. a batimetria e as margens atuais são esquemáticas;
3. a propagação de Acará até Itaituba e os aportes laterais ainda precisam ser
   estimados e calibrados.

## Próximas fases

### Fase 5 — geometria observada

Adquirir polígono de margens e seções/batimetria com CRS, datum vertical, data,
responsável e precisão. Não substituir o leito submerso por DEM terrestre.

### Fase 6 — calibração e validação

Após a Fase 5, aplicar o offset vertical documentado, testar sensibilidade de
rugosidade e condições de contorno, usar parte de 2007 para calibração e uma
janela independente completa de 2005, 2006 ou 2008 para validação. Registrar
NSE, KGE, RMSE, viés, erro de pico, tempo de pico e balanço de massa.

### Fase 7 — sedimentos e metais

Somente após a hidrodinâmica validada: adquirir granulometria, sedimento em
suspensão, concentração de metais por fase e parâmetros de partição/reação.
Então configurar GAIA e os traçadores, com análise de sensibilidade e incerteza.
