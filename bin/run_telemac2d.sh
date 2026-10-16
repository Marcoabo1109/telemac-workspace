#!/usr/bin/env bash
#
# run_telemac2d.sh — roda uma simulação TELEMAC2D via Docker e converte
# automaticamente o(s) arquivo(s) de resultado .slf para .vtk, formato
# que o ParaView no macOS (Apple Silicon) lê nativamente sem depender
# de plugin SERAFIN.
#
# Uso:
#   ./run_telemac2d.sh <arquivo.cas> [ncsize]
#
# Exemplo:
#   ./run_telemac2d.sh t2d_riogrande.cas
#   ./run_telemac2d.sh t2d_riogrande.cas 4
#
# Requisitos: rodar de dentro da pasta do caso (mesma pasta do .cas),
# com Docker Desktop aberto.
set -euo pipefail
IMAGE="jamal919/telemac:latest"
CAS_FILE="${1:-}"
NCSIZE="${2:-}"
if [[ -z "$CAS_FILE" ]]; then
    echo "Uso: $0 <arquivo.cas> [ncsize]"
    exit 1
fi
if [[ ! -f "$CAS_FILE" ]]; then
    echo "ERRO: arquivo '$CAS_FILE' não encontrado na pasta atual ($(pwd))."
    exit 1
fi
WORKDIR="$(pwd)"
echo "=================================================================="
echo "1/3 — Rodando simulação: $CAS_FILE"
echo "=================================================================="
if [[ -n "$NCSIZE" ]]; then
    docker run --rm -v "$WORKDIR":/mnt "$IMAGE" telemac2d.py "$CAS_FILE" --ncsize="$NCSIZE"
else
    docker run --rm -v "$WORKDIR":/mnt "$IMAGE" telemac2d.py "$CAS_FILE"
fi
echo ""
echo "=================================================================="
echo "2/3 — Identificando arquivo(s) de resultado no .cas"
echo "=================================================================="
# Extrai o nome do arquivo de resultado a partir da chave RESULTS FILE
# do .cas (formato: RESULTS FILE : 'nome_arquivo.slf')
RESULT_FILE=$(grep -i "RESULTS FILE" "$CAS_FILE" | head -1 | sed -E "s/.*[:=][[:space:]]*['\"]?([^'\";]+)['\"]?.*/\1/" | xargs)
if [[ -z "$RESULT_FILE" ]]; then
    echo "AVISO: não foi possível identificar automaticamente o arquivo RESULTS FILE no .cas."
    echo "Procurando arquivos .slf modificados recentemente na pasta..."
    RESULT_FILE=$(find . -maxdepth 1 -name "*.slf" -newer "$CAS_FILE" | head -1 | sed 's|^\./||')
fi
if [[ -z "$RESULT_FILE" || ! -f "$RESULT_FILE" ]]; then
    echo "ERRO: não encontrei o arquivo de resultado .slf gerado."
    echo "Confira manualmente com: ls -la *.slf"
    exit 1
fi
echo "Arquivo de resultado identificado: $RESULT_FILE"
echo ""
echo "=================================================================="
echo "3/3 — Convertendo $RESULT_FILE para .vtk (leitura nativa no ParaView)"
echo "=================================================================="
OUTPUT_VTK="${RESULT_FILE%.slf}.vtk"
BASENAME="${RESULT_FILE%.slf}"
docker run --rm -v "$WORKDIR":/mnt "$IMAGE" \
    converter.py srf2vtk "$RESULT_FILE" "$OUTPUT_VTK"
echo ""
# O converter.py pode gerar um único arquivo (nome.vtk) OU uma série
# temporal numerada (nome00000000.vtk, nome00000001.vtk, ...), dependendo
# de quantos timesteps existem no .slf. Checamos os dois casos.
SERIES_FILES=$(find . -maxdepth 1 -name "${BASENAME}[0-9]*.vtk" | sort)
if [[ -f "$OUTPUT_VTK" ]]; then
    echo "✅ Conversão concluída: $OUTPUT_VTK"
    echo "Abra esse arquivo no ParaView (File → Open)."
elif [[ -n "$SERIES_FILES" ]]; then
    N_FILES=$(echo "$SERIES_FILES" | wc -l | xargs)
    echo "✅ Conversão concluída: série temporal com $N_FILES arquivo(s):"
    echo "$SERIES_FILES" | sed 's/^\.\//   /'
    echo ""
    echo "No ParaView: File → Open e selecione qualquer um desses arquivos."
    echo "O ParaView detecta a sequência automaticamente e habilita a animação."
else
    echo "⚠️  A conversão pode ter usado uma sintaxe diferente da esperada."
    echo "Rode o comando abaixo para ver as opções corretas do converter.py:"
    echo ""
    echo "  docker run --rm $IMAGE converter.py srf2vtk --help"
fi