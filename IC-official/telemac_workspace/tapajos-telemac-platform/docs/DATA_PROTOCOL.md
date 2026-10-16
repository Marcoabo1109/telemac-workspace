# Protocolo de dados — Fase 2

O catálogo `data/tapajos/catalog.json` é a fonte única sobre disponibilidade, origem e aptidão científica dos dados do Tapajós. Um arquivo existir não significa que ele seja adequado para calibração. O catálogo distingue dados disponíveis, produtos derivados e requisitos ausentes.

## Princípios

1. Preservar o arquivo original sem edição.
2. Registrar instituição, URL, data de acesso, licença, unidade, cobertura temporal, CRS horizontal e referência vertical.
3. Calcular SHA-256 antes de qualquer transformação.
4. Transformações devem ser executáveis e produzir um novo arquivo; nunca substituir o original.
5. Hipótese, dado observado e produto derivado são categorias distintas.
6. Estatística mensal não é hidrograma; cota de régua não é profundidade nem elevação geodésica.
7. DEM terrestre não é batimetria submersa.
8. Credenciais, tokens e dados restritos não entram no Git.

## Entrada de um novo conjunto

Antes de adicionar um item como `available`:

- confirmar autorização/licença de uso;
- guardar o original em armazenamento apropriado;
- definir um nome estável e sem espaços;
- registrar o hash SHA-256;
- declarar variáveis e unidades;
- registrar período, frequência e lacunas;
- informar CRS e datum quando aplicável;
- documentar controle de qualidade e limitações;
- adicionar teste de leitura quando o formato for novo.

Arquivos pequenos e redistribuíveis podem ficar em `data/tapajos`. Arquivos grandes, sensíveis ou restritos ficam fora do Git; o catálogo registra um identificador e o local institucional, sem expor credenciais ou caminhos pessoais.

## Validação

```bash
python -m scripts.data_catalog
python -m scripts.data_catalog --report runs/data-catalog-report.json
```

O comando verifica esquema mínimo, IDs, arquivos, hashes, fontes, licença, unidades, CRS, referência vertical e dependências dos marcos. Retorno diferente de zero bloqueia a promoção dos dados.

## Marcos científicos

- **Demonstração exploratória:** disponível; usa geometria, fundo e contornos assumidos.
- **Calibração hidrodinâmica:** bloqueada até obter margens, batimetria, vazão, nível e vínculo de datum.
- **Transporte de sedimentos / GAIA:** exige ainda granulometria e sedimento em suspensão.
- **Avaliação de metais:** exige observações por fase e parâmetros de partição/reação defensáveis.

Os marcos são calculados pelo catálogo e exibidos na interface. Não devem ser liberados por edição visual isolada; é necessário registrar e validar os conjuntos exigidos.

## Ordem de aquisição

1. Confirmar estação, período comum e acesso às séries diárias ANA.
2. Obter vínculo geodésico da régua de Itaituba.
3. Obter polígono de margens e levantamento batimétrico/seções.
4. Definir períodos separados de calibração e validação.
5. Adquirir granulometria e sedimentos.
6. Somente depois, estruturar dados de metais e cenários GAIA/Nestor.

## Fase 3 iniciada

A série diária consistida de cotas da estação Itaituba `17730000` foi promovida
em 18/09/2026 após preservação do XML, conversão para CSV canônico, cálculo de
hashes e auditoria de lacunas. Consulte `docs/PHASE3_DATA.md`. A promoção deste
conjunto não remove os bloqueios independentes de vazão, datum, margens e
batimetria.
