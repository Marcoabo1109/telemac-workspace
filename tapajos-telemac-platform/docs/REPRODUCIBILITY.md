# Reprodutibilidade — Fase 1

Este protocolo separa validação de software de validação científica. O caso Culm curto confirma instalação, formatos, execução serial/MPI e compatibilidade entre máquinas; ele não calibra nem valida o Tapajós.

## Fonte oficial e versões

- O repositório privado `Marcoabo1109/IC` é a fonte oficial. Antes de trabalhar, use `git pull --recurse-submodules` e confirme `git status` limpo.
- O submódulo TELEMAC é fixado na tag v8p5r0, commit `d1bff193746fd76425d7715a6e4d20d42eb8877e`.
- O inventário registra commit do projeto, commit TELEMAC, sistema, arquitetura, Python, Node, compilador, MPI e pacotes científicos. A limpeza do projeto ignora somente arquivos materializados por Git LFS dentro do submódulo; o commit TELEMAC continua obrigatório e explícito.
- Resultados de referência ficam em `runs/reproducibility/`, que não é versionado. Relatórios aprovados podem ser copiados conscientemente para `docs/environments/`.

## Caso de referência imutável

O identificador `culm-20x2s-v1` usa os arquivos versionados de `data/culm`, 20 passos de 2 s e saídas a cada 10 s. O manifesto fixado em `docs/reproducibility-case.json` combina os hashes SHA-256 dos arquivos CAS, SERAFIN, CLI e QSL. O teste automatizado falha se qualquer entrada mudar. Uma alteração consciente exige novo identificador e revisão científica; não se atualiza silenciosamente o hash esperado.

```bash
python -m scripts.reproducibility manifest \
  --output runs/reproducibility/case-manifest.json
```

## Inventário do ambiente

Execute depois de ativar o ambiente TELEMAC usado pela máquina:

```bash
python -m scripts.reproducibility inventory \
  --output runs/reproducibility/environment.json
```

Campos `null` indicam ferramenta ausente ou variável de ambiente não configurada; não significam versão zero.

## Matriz mínima de testes

Em cada ambiente, rode a suíte Python e o build web:

```bash
python -m pytest -q
npm run build --prefix frontend
```

Com `TELEMAC_EXECUTABLE`, `HOMETEL`, `SYSTELCFG` e `USETELCFG` configurados, execute o caso serial e MPI:

```bash
python -m scripts.reproducibility run \
  --ncores 1 --output runs/reproducibility/serial
python -m scripts.reproducibility run \
  --ncores 2 --output runs/reproducibility/mpi-2
python -m scripts.reproducibility compare \
  runs/reproducibility/serial/result.slf \
  runs/reproducibility/mpi-2/result.slf \
  --output runs/reproducibility/serial-vs-mpi.json
```

O comando de comparação retorna código diferente de zero se topologia, coordenadas, instantes, variáveis ou tolerâncias falharem.

## Comparação Mac–VM

1. Execute o caso serial no Mac e na VM a partir do mesmo commit do projeto e do mesmo commit TELEMAC.
2. Copie apenas o diretório de artefatos de uma máquina para a outra, sem substituir entradas versionadas.
3. Compare os dois `result.slf` com o comando acima.
4. Arquive os dois `report.json`, o relatório de comparação e os inventários.

Na comparação entre arquiteturas, informe o perfil dedicado:

```bash
python -m scripts.reproducibility compare \
  runs/reproducibility/mac/serial/result.slf \
  runs/reproducibility/vm/serial/result.slf \
  --tolerances docs/reproducibility-cross-platform-tolerances.json \
  --output runs/reproducibility/mac-vs-vm.json
```

As tolerâncias em `docs/reproducibility-tolerances.json` são portões para serial/MPI na mesma plataforma. `docs/reproducibility-cross-platform-tolerances.json` cobre ARM64/x86_64 e permite até 0,03 m/s em `VELOCITY U`, acima dos 0,0261 m/s observados. Os limites incluem pequena margem sobre as diferenças máximas registradas. Eles não representam erro aceitável para nível, velocidade, sedimentos ou metais no Tapajós.

## Critério de aceite da Fase 1

A base é considerada reproduzível quando:

1. o repositório está limpo e os commits estão registrados;
2. os hashes do caso de referência coincidem;
3. testes Python e build web passam;
4. execuções serial e MPI terminam e geram SERAFIN legível;
5. serial/MPI e Mac/VM passam pelos portões registrados;
6. toda divergência é explicada antes de atualizar qualquer tolerância.

Credenciais, tokens, `.venv`, `node_modules`, logs e resultados temporários nunca entram no Git.
