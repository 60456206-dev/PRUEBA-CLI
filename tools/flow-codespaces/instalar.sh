#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y --no-install-recommends chromium chromium-sandbox tigervnc-standalone-server tigervnc-tools novnc websockify openbox xdotool x11-utils fonts-liberation python3-pil python3-xlib
sudo mkdir -p /tmp/.X11-unix
sudo chmod 1777 /tmp/.X11-unix
