#!/usr/bin/env python3
"""
TIKTOK RADAR · Monitor y Bot Interactivo de WhatsApp en Servidor AWS
1. Notificaciones Automáticas:
   - Envía avisos a tu WhatsApp cuando inicia la producción, cada vez que se completa un plano (SH01..SH13)
     y cuando el vídeo final NOTICIERO_FINAL_62S.mp4 queda ensamblado y listo.
2. Interacción Bidireccional con Antigravity (`agy`):
   - Escucha mensajes entrantes desde WhatsApp (Webhook) y los procesa ejecutando `agy`
     en modo desatendido (`--dangerously-skip-permissions -p "pregunta"`), respondiendo directamente a tu WhatsApp.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_FILE = Path(os.path.expanduser("~/.whatsapp_config.json"))
ROOT_DIR = Path(__file__).resolve().parent.parent
ENTREGAS_DIR = ROOT_DIR / "entregas"
LOG_FILE = Path(os.path.expanduser("~/produccion_radar.log"))


def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "provider": "callmebot",  # 'callmebot' (100% gratuito) o 'twilio'
        "phone": os.getenv("WHATSAPP_PHONE", ""),
        "apikey": os.getenv("CALLMEBOT_APIKEY", ""),
        "twilio_sid": os.getenv("TWILIO_SID", ""),
        "twilio_token": os.getenv("TWILIO_TOKEN", ""),
        "twilio_from": os.getenv("TWILIO_FROM", "whatsapp:+14155238886"),
    }


def send_whatsapp(message: str) -> bool:
    """Envía un mensaje de texto directamente a tu WhatsApp personal."""
    cfg = load_config()
    provider = cfg.get("provider", "callmebot")
    phone = cfg.get("phone", "").strip()
    apikey = cfg.get("apikey", "").strip()

    if not phone:
        print(f"[WHATSAPP-DRY-RUN] No se configuró número de teléfono en {CONFIG_FILE}. Mensaje:\n{message}\n")
        return False

    try:
        if provider == "callmebot":
            # CallMeBot API: Gratuita, sin suscripciones ni tarjetas de crédito
            # Formato de URL: https://api.callmebot.com/whatsapp.php?phone=[phone]&text=[text]&apikey=[apikey]
            clean_phone = re.sub(r"[^\d+]", "", phone)
            encoded_text = urllib.parse.quote(message)
            url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_text}&apikey={apikey}"
            req = urllib.request.Request(url, headers={"User-Agent": "TikTokRadarBot/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                status = resp.status
                return status == 200
        elif provider == "twilio":
            sid = cfg.get("twilio_sid", "")
            token = cfg.get("twilio_token", "")
            from_num = cfg.get("twilio_from", "whatsapp:+14155238886")
            to_num = f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone
            url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
            data = urllib.parse.urlencode({"To": to_num, "From": from_num, "Body": message}).encode("utf-8")
            req = urllib.request.Request(url, data=data)
            auth_str = f"{sid}:{token}".encode("ascii")
            import base64
            req.add_header("Authorization", f"Basic {base64.b64encode(auth_str).decode('ascii')}")
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status in (200, 201)
    except Exception as e:
        print(f"[WHATSAPP ERROR] Falló al enviar mensaje: {e}", flush=True)
        return False
    return False


def ask_agy(prompt: str) -> str:
    """Ejecuta una consulta al agente Antigravity instalado en el servidor usando --dangerously-skip-permissions."""
    agy_bin = shutil_which("agy") or os.path.expanduser("~/.local/bin/agy")
    if not os.path.exists(agy_bin):
        return f"Error: No se encontró el binario 'agy' en {agy_bin}."

    try:
        cmd = [
            agy_bin,
            "--dangerously-skip-permissions",
            "-p",
            f"Eres el supervisor del servidor AWS en ~/TIKTOK-NEWS. Responde de forma muy concisa para WhatsApp: {prompt}",
        ]
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )
        out = proc.stdout.strip()
        if not out and proc.stderr:
            out = f"Aviso de agy: {proc.stderr[:200]}"
        return out or "Antigravity procesó la solicitud pero no generó texto de salida."
    except Exception as e:
        return f"Error al ejecutar agy: {e}"


def shutil_which(cmd: str) -> Optional[str]:
    import shutil
    return shutil.which(cmd)


def monitor_loop(poll_interval: int = 10) -> None:
    """Escanea el log y la carpeta de entregas para enviar avisos progresivos a WhatsApp."""
    print("Iniciando Monitor de WhatsApp para TikTok Radar...", flush=True)
    send_whatsapp("🤖 *TikTok Radar Monitor Iniciado*\nSupervisando producción autónoma en el servidor AWS...")

    reported_shots = set()
    reported_final = False
    last_log_size = 0

    while True:
        try:
            # 1. Comprobar planos completados en la última carpeta de entrega
            latest_dirs = sorted(
                [d for d in ENTREGAS_DIR.iterdir() if d.is_dir() and (d / "metadata.json").exists()],
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )
            if latest_dirs:
                cur_dir = latest_dirs[0]
                shots_dir = cur_dir / "shots"
                if shots_dir.exists():
                    for shot_file in sorted(shots_dir.glob("SH*.mp4")):
                        shot_id = shot_file.stem
                        if shot_id not in reported_shots and shot_file.stat().st_size > 50_000:
                            reported_shots.add(shot_id)
                            size_mb = shot_file.stat().st_size / (1024 * 1024)
                            msg = f"🎬 *Plano {shot_id} Listo*\nDescargado y verificado en Flow ({size_mb:.1f} MB)\nAvance: {len(reported_shots)}/13 planos."
                            print(f"[MONITOR] Notificando {shot_id} a WhatsApp...")
                            send_whatsapp(msg)

                # 2. Comprobar vídeo final ensamblado
                final_mp4 = cur_dir / "NOTICIERO_FINAL_62S.mp4"
                if final_mp4.exists() and not reported_final and final_mp4.stat().st_size > 1_000_000:
                    reported_final = True
                    msg = (
                        f"🎉 *¡NOTICIERO FINAL 62S TERMINADO!*\n"
                        f"📁 Carpeta: {cur_dir.name}\n"
                        f"📦 Tamaño: {final_mp4.stat().st_size / (1024*1024):.1f} MB\n"
                        f"🚀 Listo para publicar en TikTok (>60s)."
                    )
                    print("[MONITOR] Notificando MÁSTER FINAL a WhatsApp...")
                    send_whatsapp(msg)

        except Exception as e:
            print(f"[MONITOR AVISO] {e}", flush=True)

        time.sleep(poll_interval)


class WhatsAppWebhookHandler(BaseHTTPRequestHandler):
    """Maneja mensajes entrantes de WhatsApp para responder usando agy."""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(body)

        incoming_msg = parsed.get("Body", [parsed.get("text", [""])])[0].strip()
        from_number = parsed.get("From", [parsed.get("phone", [""])])[0].strip()

        print(f"[INCOMING WHATSAPP] De {from_number}: '{incoming_msg}'", flush=True)

        if incoming_msg:
            # Consultar a agy con la orden o pregunta recibida
            answer = ask_agy(incoming_msg)
            reply = f"🤖 *Respuesta de Antigravity (AWS):*\n{answer}"
            send_whatsapp(reply)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"WhatsApp Bot Active for TikTok Radar")


def run_webhook_server(port: int = 5055):
    server = HTTPServer(("0.0.0.0", port), WhatsAppWebhookHandler)
    print(f"Servidor Webhook de WhatsApp escuchando en puerto {port}...", flush=True)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Monitor y Bot de WhatsApp para TikTok Radar")
    parser.add_argument("--test-msg", type=str, default=None, help="Enviar mensaje de prueba y salir")
    parser.add_argument("--server", action="store_true", help="Iniciar servidor webhook para preguntas bidireccionales")
    parser.add_argument("--port", type=int, default=5055, help="Puerto para webhook")
    args = parser.parse_args()

    if args.test_msg:
        ok = send_whatsapp(args.test_msg)
        print("Mensaje enviado con éxito." if ok else "Fallo al enviar mensaje.")
        sys.exit(0 if ok else 1)

    if args.server:
        import threading
        t = threading.Thread(target=monitor_loop, daemon=True)
        t.start()
        run_webhook_server(args.port)
    else:
        monitor_loop()


if __name__ == "__main__":
    main()
