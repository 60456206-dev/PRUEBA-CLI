#!/usr/bin/env bash
# ==============================================================================
# TIKTOK RADAR · Instalador y Configurador del WhatsApp Bot Propio en AWS
# ==============================================================================

set -e

echo "=== [1/4] Verificando e instalando Node.js 20 LTS ==="
if ! command -v node &> /dev/null; then
    echo "Instalando Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "Node.js ya está instalado: $(node -v)"
fi

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOT_DIR"

echo "=== [2/4] Instalando dependencias de Node.js (whatsapp-web.js, express) ==="
npm install

echo "=== [3/4] Configurando servicio permanente en systemd ==="
sudo cp tiktok-whatsapp-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tiktok-whatsapp-bot
sudo systemctl restart tiktok-whatsapp-bot

echo "=== [4/4] Servicio iniciado con éxito ==="
echo "Estado del servicio:"
sudo systemctl status tiktok-whatsapp-bot --no-pager || true

echo ""
echo "=============================================================================="
echo "🎉 ¡BOT INSTALADO Y CORRIENDO COMO SERVICIO PERMANENTE EN SYSTEMD!"
echo "Para ver el código QR y vincular tu WhatsApp, ejecuta:"
echo "   bash $BOT_DIR/ver_qr.sh"
echo "=============================================================================="
