#!/usr/bin/env bash
# ==============================================================================
# TIKTOK RADAR · Lanzador Programado para Cron en AWS
# ==============================================================================
set -e

GENRE="${1:-G1}"
RANK="${2:-0}"
LABEL="${3:-PRODUCCION}"

WORKSPACE_DIR="$HOME/TIKTOK-NEWS"
LOG_FILE="$HOME/produccion_radar.log"

export PATH="$HOME/.local/bin:$PATH"

# Cargar variables de entorno si existen
if [ -f "$HOME/.api_keys.env" ]; then
    source "$HOME/.api_keys.env"
fi
if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc" 2>/dev/null || true
fi

echo "======================================================================" >> "$LOG_FILE"
echo "⏰ [$(date -u '+%Y-%m-%d %H:%M:%S UTC')] INICIANDO PRODUCCIÓN AUTOMATIZADA: $LABEL ($GENRE, RANK $RANK)" >> "$LOG_FILE"
echo "======================================================================" >> "$LOG_FILE"

cd "$WORKSPACE_DIR"
python3 tools/ejecutar_todo.py --genre "$GENRE" --rank "$RANK" >> "$LOG_FILE" 2>&1

echo "✅ [$(date -u '+%Y-%m-%d %H:%M:%S UTC')] FINALIZADA ENTREGA: $LABEL" >> "$LOG_FILE"
