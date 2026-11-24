#!/bin/bash
# Renderiza todos los misterios con voz verificada (3 en paralelo) y guarda un log por video.
cd "$(dirname "$0")"
mkdir -p /tmp/claude-0/logs
ls audios/misterios/misterio_*_voz.mp3 | sed -E 's/.*misterio_([0-9]+)_voz.mp3/\1/' | \
  while read n; do ls "misterios nuevos"/misterio_${n}_*.mp4 >/dev/null 2>&1 || echo $n; done | \
  xargs -P 3 -I{} sh -c 'python3 misterios.py {} > /tmp/claude-0/logs/mis_{}.log 2>&1; echo "hecho {}"'
