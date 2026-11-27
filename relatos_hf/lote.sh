#!/bin/bash
# Renderiza varios relatos en paralelo (2 a la vez). Uso: bash relatos_hf/lote.sh 4 5 7 ...
cd "$(dirname "$0")/.."
printf '%s\n' "$@" | xargs -P 2 -I{} sh -c 'python3 relatos_hf/motor.py {} > relatos_hf/proyectos/log_{}.txt 2>&1 && echo "OK {}" || echo "FALLA {}"'
