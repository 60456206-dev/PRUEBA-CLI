#!/usr/bin/env bash
set -euo pipefail
if ! command -v gh >/dev/null; then
  echo 'Falta GitHub CLI (gh) en esta computadora.' >&2
  exit 1
fi
if [[ -n "${CODESPACES:-}" ]]; then
  echo 'Ejecuta este archivo en tu computadora Linux, no en Codespaces.' >&2
  exit 1
fi
echo 'Mantén esta terminal abierta. Para desconectar, pulsa Ctrl+C.'
echo 'Si GitHub pide acceso, usa tu propia cuenta de GitHub.'
exec gh codespace ssh -c effective-space-bassoon-6vg6rvr59xv6crgg5 -- -N -L 127.0.0.1:8765:127.0.0.1:8765 -o ExitOnForwardFailure=yes -o ServerAliveInterval=30
