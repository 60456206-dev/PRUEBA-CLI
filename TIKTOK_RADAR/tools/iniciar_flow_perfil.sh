#!/usr/bin/env bash
# ==============================================================================
# TIKTOK RADAR · Gestor de Múltiples Cuentas / Perfiles de Google Flow en AWS
# Uso:
#   bash iniciar_flow_perfil.sh cuenta_2          # Abre Chrome en RDP para iniciar sesión
#   bash iniciar_flow_perfil.sh --listar          # Muestra cuentas y estado de cooldown
#   bash iniciar_flow_perfil.sh --reset-cooldown  # Limpia cooldowns manualmente
# ==============================================================================
set -e

PROFILES_ROOT="$HOME/flow-profiles"
PRIMARY_PROFILE="$HOME/flow-profile"
STATE_FILE="$HOME/.flow_profiles_state.json"

mkdir -p "$PROFILES_ROOT"

if [ "${1:-}" = "--listar" ]; then
    python3 - << 'PY'
import json, os, time
from pathlib import Path

root = Path(os.path.expanduser("~/flow-profiles"))
primary = Path(os.path.expanduser("~/flow-profile"))
state_file = Path(os.path.expanduser("~/.flow_profiles_state.json"))
state = {}
if state_file.exists():
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        state = {}

candidates = []
if primary.exists():
    candidates.append(primary)
if root.exists():
    for d in sorted(root.iterdir()):
        if d.is_dir() and not d.name.startswith("."):
            candidates.append(d)

now = time.time()
print("=== PERFILES GOOGLE FLOW DETECTADOS ===")
if not candidates:
    print("  (Ninguno todavía. Ejecuta: bash ~/iniciar_flow_perfil.sh cuenta_2)")
for p in candidates:
    key = str(p.resolve())
    info = state.get(key, {})
    cd = float(info.get("cooldown_until", 0) or 0)
    reason = info.get("reason", "ok")
    if cd > now:
        mins = int((cd - now) // 60)
        status = f"COOLDOWN ({reason}, restan {mins} min)"
    elif reason == "session_expired":
        status = "SESION_EXPIRADA (requiere re-login)"
    else:
        status = "DISPONIBLE"
    print(f"  - {p} -> {status}")
PY
    exit 0
fi

if [ "${1:-}" = "--reset-cooldown" ]; then
    rm -f "$STATE_FILE"
    echo "✅ Cooldowns de perfiles Flow reiniciados ($STATE_FILE eliminado)."
    exit 0
fi

PROFILE_NAME="${1:-}"
if [ -z "$PROFILE_NAME" ]; then
    echo "Uso: bash $0 <nombre_cuenta>   (ej: cuenta_2)"
    echo "     bash $0 --listar"
    echo "     bash $0 --reset-cooldown"
    exit 1
fi

if [ "$PROFILE_NAME" = "principal" ] || [ "$PROFILE_NAME" = "cuenta_1" ]; then
    TARGET_DIR="$PRIMARY_PROFILE"
else
    TARGET_DIR="$PROFILES_ROOT/$PROFILE_NAME"
fi

mkdir -p "$TARGET_DIR"
rm -f "$TARGET_DIR/SingletonLock" "$TARGET_DIR/SingletonCookie" "$TARGET_DIR/SingletonSocket"

echo "Abriendo Google Chrome con perfil aislado: $TARGET_DIR"
echo "Inicia sesión en Google Flow con tu cuenta y cierra la ventana al terminar."
google-chrome \
  --user-data-dir="$TARGET_DIR" \
  --no-first-run \
  --no-default-browser-check \
  "https://labs.google/fx/es/tools/flow" &
