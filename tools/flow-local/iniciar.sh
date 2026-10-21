#!/usr/bin/env bash
set -euo pipefail
base_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ "${1:-}" == "--comprobar" ]]; then
  python3 "$base_dir/preparar.py"
  exit 0
fi
if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  echo 'Ejecuta este archivo en la terminal del escritorio Linux de tu computadora, no en Codespaces ni por SSH sin escritorio.' >&2
  exit 1
fi
browser_bin=''
for candidate in google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "$candidate" >/dev/null 2>&1; then
    browser_bin="$(command -v "$candidate")"
    break
  fi
done
if [[ -z "$browser_bin" ]]; then
  echo 'Necesitas Google Chrome o Chromium instalado en tu computadora.' >&2
  exit 1
fi
python3 "$base_dir/preparar.py"
profile_dir="${XDG_DATA_HOME:-$HOME/.local/share}/master-series-flow/browser"
mkdir -p "$profile_dir"
chmod 700 "$profile_dir"
exec "$browser_bin" --user-data-dir="$profile_dir" --new-window "file://$base_dir/preparado/index.html" 'https://labs.google/fx/tools/flow'
