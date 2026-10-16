# PoC visual — três materiais no Tapajós

Este caso **executado em TELEMAC-2D** integra advecção/difusão de três escalares no mesmo escoamento. Não é animação de partículas fictícias nem aplicação posterior de filtros à imagem. O visualizador apresenta os valores calculados em SERAFIN.

## Fontes e hipóteses

- Código oficial: https://gitlab.pam-retd.fr/otm/telemac-mascaret.git, v8p5r0, commit `d1bff193746fd76425d7715a6e4d20d42eb8877e`. O gerador verifica a revisão antes de executar.
- Rio real: Tapajós, trecho de 3,47 km próximo de Itaituba, Pará. Eixo público OpenStreetMap (ODbL; © contribuidores OpenStreetMap), URL e hash em `provenance.json`.
- Referência de nível: estatística mensal pública SGB, convertida para um datum local **assumido**. As séries diárias ANA disponíveis no projeto não são impostas neste ensaio curto.
- Largura 1.200 m, fundo esquemático 4–8 m, vazão 6.000 m³/s, Strickler 30 e difusividade 5 m²/s são hipóteses. Não há batimetria observada suficiente nem calibração. Convergência espacial do traçador permanece pendente.

## Materiais e equações

Pulso gaussiano inicial idêntico, σ = 180 m, concentração normalizada C/C₀; concentração nula na entrada durante o ensaio. Não é uma concentração medida em mg/L.

1. **CONSERVATIVE:** advecção e difusão, sem reação.
2. **POLLUTANT:** fonte `−ln(2)/1800 × C`; meia-vida hipotética 30 min.
3. **SEDIMENT:** fonte `−ws/h × C`, ws = 0,001 m/s; deposição simplificada. A massa retirada da suspensão é registrada como sumidouro, mas não é armazenada em leito móvel. Não há erosão, ressuspensão, granulometria múltipla ou acoplamento GAIA.

O código em `user_fortran/difsou.f` deriva da rotina oficial DIFSOU v8p5r0, com histórico original preservado, e acrescenta fontes e sua contribuição ao balanço. Está sujeito à licença TELEMAC upstream (GPL; consultar LICENSE do repositório oficial), distinta de qualquer licença dos códigos próprios da plataforma. `user_condin_trac.f` inicializa o pulso. Esta extensão revisada é executada apenas pela CLI; a API genérica continua rejeitando código Fortran arbitrário enviado pela web.

## Resultado executado em 09/10/2026

852 nós, 1.588 triângulos, dt = 1 s, 3.600 passos, saída a cada 60 s. Escoamento parte do repouso; inclui transiente de partida.

| Material | Inventário final do solver [C/C₀ × m³] | Erro relativo de balanço |
|---|---:|---:|
| Traçador | 466.479,1 | 1,701584 × 10⁻⁵ |
| Poluente | 116.336,0 | 1,228289 × 10⁻⁵ |
| Sedimento suspenso | 277.864,2 | 1,509587 × 10⁻⁵ |

Concentrações entre 0 e 0,988365 nos frames gravados; erro relativo de volume −1,562230 × 10⁻⁷. Esses resultados verificam execução e balanços, não validam o rio real. O gráfico da interface usa integração nodal aproximada por áreas concentradas; o balanço formal é o do solver em `solver-output.txt`. Saída do trecho também reduz inventário, independentemente de reação.

## Executar e abrir

Na raiz da plataforma, com Docker ativo:

```bash
# Primeira instalação: compilar o solver a partir do Git oficial (pode demorar).
docker build -f docker/Dockerfile -t tapajos-platform-backend:latest .
# Regenerar os resultados (a interface já inclui o caso executado).
docker compose -p tapajos-poc -f docker/compose.poc.yml run --rm backend python3.11 -m scripts.materials_poc
# Disponibilizar a interface.
docker compose -p tapajos-poc -f docker/compose.poc.yml up -d --build
```

Abrir http://localhost:3001, aba **Dispersão · PoC** (inicial). Reproduzir/pausar, arrastar a linha temporal, comparar três mapas ou selecionar um material, consultar concentração com o cursor, acompanhar inventário e baixar JSON. Todos os mapas usam escala fixa 0–1. As cores dos pontos/títulos identificam as curvas de inventário; a escala dos mapas representa concentração.

Portas configuráveis por `POC_PORT` e `POC_API_PORT`; padrões 3001 e 8001 evitam conflito com o túnel SSH existente. Para encerrar somente este PoC: `docker compose -p tapajos-poc -f docker/compose.poc.yml stop`.

`materials.slf`, `solver-output.txt`, `case.cas`, malha, fronteiras, fontes Fortran e metadados são preservados. `data/tapajos/poc/materials.json` é exportado do SERAFIN com seis casas decimais para a interface. Não editar o JSON para modificar a física: alterar o caso, executar o solver e exportar novamente.
