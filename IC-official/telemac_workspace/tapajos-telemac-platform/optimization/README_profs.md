# Interface científica / Research interface

`DredgingObjective.evaluate` recebe arrays [tempo, nó] em SI: profundidade (m), velocidades (m/s), concentração (unidade explicitada pelo cenário) e parâmetros de dragagem. Retorna um escalar, após definição dos pesos e unidades pelos Profs. Helou, Sousa e Ausas.

As métricas de `scripts.postprocess` fornecem velocidade, Froude e tensão de leito para Manning/Strickler. A função objetivo e o transporte reativo NÃO estão implementados. Definir domínio, janelas temporais, concentração de fundo, fração dissolvida/particulada, volume, custo e restrições antes de otimizar.

Em 2D, uma fonte gaussiana de massa M precisa ser normalizada pela integral de h C dA. A expressão unidimensional do resumo não deve ser transcrita como uma fonte 2D. Uma delta deve ser discretizada conservando massa. Identificar E e deposição com símbolos diferentes da difusividade. O balanço de Exner com troca de suspensão deve incluir E/deposição e unidades coerentes (massa/volume).
