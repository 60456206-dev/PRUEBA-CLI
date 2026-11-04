#!/usr/bin/env bash
# Muestra el código QR actual generado por el WhatsApp Bot
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QR_FILE="$BOT_DIR/qr_ascii.txt"
LOG_FILE="$BOT_DIR/bot.log"

if [ -f "$QR_FILE" ]; then
    echo "======================================================================"
    echo "📱 ESCANEA ESTE CÓDIGO QR EN TU WHATSAPP (Dispositivos vinculados):"
    echo "======================================================================"
    cat "$QR_FILE"
    echo "======================================================================"
else
    echo "Esperando que el bot genere el código QR (revisando últimos logs)..."
    tail -n 30 "$LOG_FILE" 2>/dev/null || journalctl -u tiktok-whatsapp-bot -n 30 --no-pager
fi
