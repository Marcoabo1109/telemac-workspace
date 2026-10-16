# Fase 3 — dados hidrológicos reais

## Resultado em 01/10/2026

O procedimento do tutorial HidroWeb foi aplicado à pesquisa por município e
tipo de estação. O inventário oficial retornou 16 estações fluviométricas em
Itaituba. A seleção científica separa canal principal, tributários e registros
curtos; ela está registrada em
`data/tapajos/stations/processed/ana_inventory_itaituba_fluviometric_2026-10-01.csv`.
O XML integral do inventário também foi preservado em `raw/`.

Foram adquiridas e auditadas 13 séries diárias:

| Estação | Rio | Variável | Período retornado | Registros | Cobertura | Uso proposto |
|---|---|---:|---:|---:|---:|---|
| 17500000 Fortaleza | Tapajós | cota | 1982-07-23–2014-12-31 | 11.346 | 95,75% | referência regional de montante |
| 17500000 Fortaleza | Tapajós | vazão | 1982-07-23–2014-12-31 | 11.346 | 95,75% | referência regional de montante |
| 17650000 Jatobá | Tapajós | cota | 1972-12-20–2007-02-28 | 8.991 | 71,99% | verificação longitudinal |
| 17650002 Acará do Tapajós | Tapajós | cota | 1976-04-29–2011-01-31 | 9.218 | 72,61% | verificação longitudinal |
| 17650002 Acará do Tapajós | Tapajós | vazão | 1996-01-01–2011-01-31 | 5.420 | 98,37% | vazão primária de montante |
| 17675000 Jardim do Ouro | Jamanxim | cota | 1987-08-15–2023-12-31 | 9.292 | 69,93% | aporte lateral |
| 17675000 Jardim do Ouro | Jamanxim | vazão | 1987-08-15–2025-10-31 | 9.809 | 70,28% | aporte lateral |
| 17680000 Jamanxim | Jamanxim | cota | 1986-02-18–2023-12-31 | 7.319 | 52,92% | controle próximo à foz |
| 17680000 Jamanxim | Jamanxim | vazão | 1986-02-18–2025-10-31 | 7.408 | 51,09% | aporte lateral próximo à foz |
| 17710000 Buburé | Tapajós | cota | 1995-06-16–2023-12-31 | 9.387 | 90,03% | validação próxima de montante |
| 17710000 Buburé | Tapajós | vazão | 2004-10-21–2025-10-29 | 6.707 | 87,34% | validação próxima de montante |
| 17720000 Bela Vista | Tapajós | cota | 1991-01-01–2007-02-28 | 2.480 | 42,01% | apenas verificação auxiliar |
| 17730000 Itaituba | Tapajós | cota | 1974-01-01–2014-05-31 | 14.361 | 97,29% | controle de nível de jusante |

Cada aquisição preserva resposta XML, CSV canônico
`date,value,consistency,unit` e manifesto com hash, lacunas, extremos e contagem
por nível de consistência. Nenhuma lacuna foi preenchida.

## Par principal para o primeiro experimento observacional

- Montante: vazão de Acará do Tapajós `17650002`.
- Jusante/calibração: cota de Itaituba `17730000`.
- Janela comum máxima: 01/01/1996 a 31/01/2011.
- Dias com ambas as observações presentes: 5.268 de 5.510 (95,61%).
- Buburé `17710000` deve ser usado como controle intermediário na janela comum,
  não como substituto automático de Acará.
- Jardim do Ouro e Jamanxim devem quantificar o aporte lateral do rio Jamanxim
  quando o domínio representar esse trecho da rede.

O par Acará–Itaituba é promovido no catálogo porque a vazão de Acará é 100%
nível de consistência 2 e tem apenas 90 dias ausentes na janela retornada. As
vazões de Buburé, Jardim do Ouro e Jamanxim contêm mistura de níveis 1 e 2; os
manifestos registram essa composição e ela deve ser filtrada explicitamente na
definição das janelas de calibração.

## Estações não promovidas

- Chacorão e Garimpo do Batalha: séries muito curtas no canal principal.
- Porto Alegre, Garimpo Surubim e Fazenda Goiano: tributários e séries curtas.
- Itaituba `17730001`: registro iniciado em 2024; útil futuramente para
  monitoramento, não para calibração histórica.
- Itaituba `17730002`: pode estender a série até 1973, mas não deve ser unido a
  `17730000` sem provar a continuidade do zero das réguas.
- Jatobá e Itaituba: o inventário declara períodos de descarga líquida, mas o
  serviço histórico não retornou observações de vazão, nem consistidas nem
  brutas, nas consultas realizadas.

## Limites ainda ativos

- Cota em centímetros sobre o zero local da régua não é profundidade nem
  elevação geodésica.
- A vazão de Acará não deve ser imposta no contorno de Itaituba sem considerar
  propagação, armazenamento e afluências entre as duas seções.
- A calibração hidrodinâmica continua bloqueada por margens verificadas,
  batimetria/seções e vínculo vertical da régua.
- O endpoint legado foi usado como fonte pública de leitura e deve ser
  substituído pelo HidroWebService autorizado quando a integração autenticada
  estiver disponível.

## Auditoria

```bash
python -m scripts.data_catalog
python -m scripts.phase3_data --help
```

Um conjunto só deve entrar em cenário TELEMAC depois de selecionar uma janela
comum, decidir a política de lacunas e registrar qualquer transformação de cota
ou deslocamento temporal.
