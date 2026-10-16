# Editor GAIA / Nestor

A aba **GAIA / Nestor** prepara configurações de dragagem e despejo. O editor mantém seu estado ao trocar de aba; **Salvar projeto do editor** baixa um JSON para reabrir depois. Esse estado é independente do CAS hidrodinâmico e não é substituído ao carregar Culm ou Tapajós.

1. Importe o CAS sedimentológico GAIA ou preencha seus campos. O botão de geometria copia o nome do caso hidrodinâmico atual; a fronteira sedimentológica deve ser definida separadamente.
2. Importe um arquivo de ações ou adicione operações. São suportados `Dig_by_time`, `Dump_by_time`, `Dig_by_criterion`, `Save_water_level` e `Backfill_to_level`.
3. Configure datas absolutas, volumes, taxas, profundidades, critérios e destinos. As datas precisam ser coerentes com a origem temporal do caso TELEMAC. As frações `GrainClass`, separadas por `;` no formulário, são exportadas como linhas repetidas na ordem das classes GAIA.
4. Importe ou edite os polígonos `NAME:NNN_nome` com pares X/Y. Os IDs das ações são associados pelos três dígitos iniciais, conforme o leitor oficial. As coordenadas devem usar o CRS da malha. Superfícies e restart são importados/editados como texto original.
5. Exporte as ações isoladas ou o pacote ZIP. O pacote contém `gaia.cas`, ações, polígonos, auxiliares necessários e um trecho de acoplamento `coupling_t2d.txt` para incorporar ao CAS TELEMAC-2D existente. Ele não contém a malha ou demais entradas sedimentológicas.

O catálogo permite editar as 152 palavras-chave de `gaia.dico`, com tipos, padrões e ajuda oficial. Os campos sedimentares iniciais são exemplos, não calibração. Palavras-chave adicionais importadas são preservadas no CAS; comentários e formatação original não são preservados. Os nomes Nestor no ZIP são normalizados automaticamente, independentemente dos nomes importados.

## Rastreabilidade

Fonte: submódulo oficial [TELEMAC-MASCARET](https://gitlab.pam-retd.fr/otm/telemac-mascaret/-/tree/d1bff193746fd76425d7715a6e4d20d42eb8877e), tag v8p5r0, commit `d1bff193746fd76425d7715a6e4d20d42eb8877e`.

Arquivos consultados: `sources/gaia/gaia.dico`, `sources/nestor/readdigactions.f`, `isactioncompletelydefined.f`, `set_action_defaults.f`, `readpolygons.f` e os quatro exemplos em `examples/nestor`.

A consulta remota ao GitLab falhou por resolução DNS nesta sessão; foi usado o checkout oficial já disponível. Não foi feita atualização da versão. `backend/data/gaia_v8p5r0.json` é a extração do dicionário, com origem, commit e SHA-256, usada quando o submódulo não está instalado (inclusive Docker). Mantém-se a atribuição e licença do código/dicionário TELEMAC original.

## Validação e limites

O editor verifica estrutura das ações, datas, números finitos, campos obrigatórios, regras por operação, soma e quantidade de frações sedimentares, existência de áreas e arquivos auxiliares exigidos. Os quatro exemplos oficiais passam pelo teste de importação/exportação. `DigPlanar=TRUE` é rejeitado pelo solver dessa versão; `Reset_bottom` é restrito à hidrodinâmica pura e não é oferecido no editor GAIA.

A validação não cobre integralmente o dicionário GAIA, geometria espacial dos polígonos, cobertura da malha, formato interno de superfície/restart ou dependências temporais WATERLVL. Revise esses dados no caso real. O pacote é de preparação: o executor web continua bloqueando acoplamentos arbitrários e não foi executada uma simulação GAIA/Nestor nesta entrega. Execute o caso completo pelo CLI TELEMAC e verifique balanço sedimentar e estabilidade.
