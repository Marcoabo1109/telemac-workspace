#!/bin/bash
#PBS -N tapajos
#PBS -l select=1:ncpus=32:mpiprocs=32
#PBS -l walltime=02:00:00
set -euo pipefail
: "${TELEMAC_ENV:?Defina ambiente do cluster}"
source "$TELEMAC_ENV"
: "${CAS_FILE:?Defina caso revisado}"
cd "$(dirname "$CAS_FILE")"
telemac2d.py "$(basename "$CAS_FILE")" --ncsize="${TELEMAC_NCORES:-32}"
