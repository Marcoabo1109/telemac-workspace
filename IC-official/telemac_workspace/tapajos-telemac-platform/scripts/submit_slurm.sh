#!/bin/bash
#SBATCH --job-name=tapajos
#SBATCH --ntasks=32
#SBATCH --time=02:00:00
#SBATCH --output=telemac-%j.log
set -euo pipefail
: "${TELEMAC_ENV:?Defina o script de ambiente TELEMAC do cluster}"
source "$TELEMAC_ENV"
: "${CAS_FILE:?Defina o caminho do caso revisado}"
cd "$(dirname "$CAS_FILE")"
telemac2d.py "$(basename "$CAS_FILE")" --ncsize="${SLURM_NTASKS:-${TELEMAC_NCORES:-32}}"
