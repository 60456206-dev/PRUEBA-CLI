#!/usr/bin/env bash
# ==============================================================================
# TIKTOK RADAR · Instalador Automático para Servidor AWS (Ubuntu 22.04 / 24.04)
# Ejecuta este script en tu servidor AWS para configurar todo el entorno autónomo.
# ==============================================================================

set -e

echo "=== [1/6] Actualizando sistema e instalando dependencias base ==="
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv ffmpeg git curl wget x11-utils xvfb

echo "=== [2/6] Instalando Google Chrome Oficial (Estable) ==="
if ! command -v google-chrome &> /dev/null; then
    wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt-get install -y /tmp/chrome.deb || sudo apt-get -f install -y
    rm -f /tmp/chrome.deb
    echo "Google Chrome instalado correctamente."
else
    echo "Google Chrome ya estaba instalado."
fi

echo "=== [3/6] Instalando dependencias de Python (Edge-TTS, Playwright) ==="
pip install --break-system-packages edge-tts playwright aiohttp
playwright install --with-deps || true

echo "=== [4/6] Configurando entorno de escritorio ligero y RDP para acceso remoto ==="
sudo apt-get install -y xfce4 xfce4-goodies xrdp
echo "xfce4-session" > ~/.xsession
sudo systemctl enable xrdp
sudo systemctl restart xrdp

echo "=== [5/6] Creando lanzador de Google Chrome persistente para Flow ==="
mkdir -p ~/flow-chrome-profile
cat << 'EOF' > ~/iniciar_flow_chrome.sh
#!/usr/bin/env bash
# Abre Chrome con tu perfil persistente y el puerto CDP 9222 activo para Playwright
google-chrome \
  --user-data-dir=$HOME/flow-chrome-profile \
  --remote-debugging-port=9222 \
  --no-first-run \
  --no-default-browser-check \
  "https://labs.google/flow" &
EOF
chmod +x ~/iniciar_flow_chrome.sh

echo "=============================================================================="
echo "¡INSTALACIÓN COMPLETADA CON ÉXITO EN TU SERVIDOR AWS!"
echo "=============================================================================="
echo "Siguientes pasos sencillos:"
echo "1. Conéctate por Escritorio Remoto (RDP) a tu servidor usando el túnel SSH."
echo "2. Ejecuta: ~/iniciar_flow_chrome.sh"
echo "3. Inicia sesión en tu cuenta de Google Flow (UNA SOLA VEZ)."
echo "4. Listo: El servidor ya puede generar vídeos en piloto automático."
echo "=============================================================================="
