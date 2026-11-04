#!/usr/bin/env python3
"""
TIKTOK RADAR · Generador y Gestor de Audio de Alta Fidelidad (Broadcast)
1. Locución: Google Gemini 3.8 Flash TTS con dirección actoral periodística y auto-fallback a Edge-TTS.
2. Música y Foley: Epidemic Sound MCP API con descarga y caché de stems (BASS + INSTRUMENTS) y SFX de estudio.
"""

import asyncio
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Cargar .env si existe
for env_path in [Path.home() / ".api_keys.env", Path(__file__).resolve().parent.parent / ".env"]:
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
EPIDEMIC_SOUND = os.getenv("EPIDEMIC_SOUND", "")

MCP_URL = "https://www.epidemicsound.com/a/mcp-service/mcp"
DEFAULT_ASSETS_DIR = Path(__file__).resolve().parent.parent / "audio_assets"
DEFAULT_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Tracks y SFX preseleccionados de Epidemic Sound para Noticiero 3D de alta tensión
EPIDEMIC_PRESETS = {
    "music": [
        ("NEWS_THRILLER_BASS", "55900695-564d-45bd-bde7-672cca5e827e", "BASS", "Oro (Bass) - Tensión oscura de noticiero"),
        ("NEWS_THRILLER_INSTRUMENTS", "55900695-564d-45bd-bde7-672cca5e827e", "INSTRUMENTS", "Oro (Instruments) - Pulso rítmico"),
        ("PULSE_ACTION_BASS", "87893ebf-9476-46ff-9cc1-f1227748c791", "BASS", "Shifting Ground (Bass) - Urgencia táctica"),
        ("PULSE_ACTION_INSTRUMENTS", "87893ebf-9476-46ff-9cc1-f1227748c791", "INSTRUMENTS", "Shifting Ground (Instruments) - Cuerdas de alerta"),
    ],
    "sfx": [
        ("SFX_RISER_LOW", "e705e6f7-6b2b-4083-99de-2ef6327a6771", "Designed Riser Low - Subida de tensión antes del corte"),
        ("SFX_DARK_BOOM", "582229d4-ce16-4e09-8c9e-6b0d9ecace82", "Cinematic Dark Boom - Impacto en transiciones clave"),
        ("SFX_RUMBLE_RISING", "bfaede35-d903-46d5-9c01-548e591177d3", "Low Rising Rumble - Tensión continua de fondo"),
    ]
}


def probe_duration(path: Path) -> float:
    """Calcula duración exacta en segundos con ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ]
        return float(subprocess.check_output(cmd).decode().strip())
    except Exception:
        return 0.0


# -----------------------------------------------------------------------------
# 1. Locución Profesional con Gemini 3.8 Flash TTS
# -----------------------------------------------------------------------------

def generate_speech_gemini(
    text: str,
    output_path: Path,
    voice: str = "Fenrir",
    style: Optional[str] = None
) -> bool:
    """Genera locución con Gemini 3.8 Flash TTS y metadatos de dirección dramática y apasionada."""
    key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
    if not key:
        return False

    if not style:
        style = (
            "Locución apasionada, vibrante y con profunda emoción dramática para noticiero de última hora en TikTok. "
            "Ritmo dinámico, enérgico y acelerado, con inflexiones vivas de asombro y tensión periodística en las cifras y exclamaciones. "
            "Cero monotonía, cero tono plano o robótico; locución llena de convicción, nervio y adrenalina."
        )

    models_to_try = ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts", "gemini-3.1-flash-tts-preview"]

    for model in models_to_try:
        body = {
            "contents": [{
                "role": "user",
                "parts": [{
                    "text": text,
                    "speech_metadata": {
                        "style": style
                    }
                }]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "voice": voice
                    }
                }
            }
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            print(f"[AUDIO-TTS] Generando locución con {model} (Voz: {voice})...", flush=True)
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.load(resp)
            parts = data["candidates"][0]["content"]["parts"]
            inline = next(p["inlineData"] for p in parts if "inlineData" in p)
            raw = base64.b64decode(inline["data"])

            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Si el destino es mp3 pero gemini devuelve wav, convertir con ffmpeg
            if output_path.suffix.lower() == ".mp3" and raw[:4] == b"RIFF":
                tmp_wav = output_path.with_suffix(".tmp.wav")
                tmp_wav.write_bytes(raw)
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(tmp_wav), "-b:a", "192k", str(output_path)],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                if tmp_wav.exists():
                    tmp_wav.unlink()
            else:
                output_path.write_bytes(raw)

            dur = probe_duration(output_path)
            print(f"[AUDIO-TTS] ✅ Locución Gemini completada: {output_path.name} ({dur:.2f} s)", flush=True)
            return True
        except Exception as e:
            print(f"[AUDIO-TTS] ⚠️ Error con {model}: {e}. Probando alternativa...", flush=True)

    return False


async def _generate_speech_edge_async(text: str, output_path: Path, voice: str = "es-MX-JorgeNeural") -> bool:
    try:
        import edge_tts
        # Aceleración a +12% y tono para transmitir emoción y energía periodística en lugar de lectura calmada
        communicate = edge_tts.Communicate(text, voice, rate="+12%", pitch="+1Hz")
        await communicate.save(str(output_path))
        dur = probe_duration(output_path)
        print(f"[AUDIO-TTS] ✅ Locución Edge-TTS fallback completada: {output_path.name} ({dur:.2f} s)", flush=True)
        return True
    except Exception as e:
        print(f"[AUDIO-TTS] ❌ Falló también Edge-TTS: {e}", flush=True)
        return False


def generate_speech(
    text: str,
    output_path: Path,
    voice_gemini: str = "Fenrir",
    voice_edge: str = "es-MX-JorgeNeural",
    style: Optional[str] = None
) -> float:
    """Genera locución intentando primero Gemini TTS y con fallback automático a Edge-TTS."""
    # 1. Intentar Gemini Flash TTS
    ok = generate_speech_gemini(text, output_path, voice=voice_gemini, style=style)
    if not ok:
        print("[AUDIO-TTS] Activando fallback gratuito Edge-TTS...", flush=True)
        asyncio.run(_generate_speech_edge_async(text, output_path, voice=voice_edge))

    return probe_duration(output_path)


# -----------------------------------------------------------------------------
# 2. Epidemic Sound MCP API (Música y Efectos de Estudio)
# -----------------------------------------------------------------------------

def mcp_call(payload: dict, session_id: Optional[str] = None) -> Tuple[Optional[str], dict]:
    key = os.getenv("EPIDEMIC_SOUND") or EPIDEMIC_SOUND
    if not key:
        return None, {"error": "No EPIDEMIC_SOUND key provided"}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {key}",
        "User-Agent": "TikTokRadar-MCP-Client/2.0",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = urllib.request.Request(MCP_URL, data=json.dumps(payload).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        sid = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
        body = resp.read().decode()
        for line in body.splitlines():
            if line.startswith("data: {"):
                return sid, json.loads(line[6:])
        return sid, {"raw": body}


def download_file(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    req = urllib.request.Request(url, headers={"User-Agent": "TikTokRadar-MCP-Client/2.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())
    return True


def ensure_epidemic_assets(target_dir: Optional[Path] = None) -> Dict[str, Path]:
    """
    Descarga o reutiliza los stems de música y SFX de Epidemic Sound en target_dir.
    Devuelve un diccionario con las rutas locales listas para FFmpeg.
    """
    out_dir = target_dir or DEFAULT_ASSETS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    results: Dict[str, Path] = {}

    key = os.getenv("EPIDEMIC_SOUND") or EPIDEMIC_SOUND
    if not key:
        print("[AUDIO-EPIDEMIC] ⚠️ No se detectó EPIDEMIC_SOUND. Se usará fallback sintético.", flush=True)
        return results

    # Comprobar si ya están todos en caché
    all_cached = True
    for name, _, _, _ in EPIDEMIC_PRESETS["music"]:
        dest = out_dir / f"{name}.wav"
        if not (dest.exists() and dest.stat().st_size > 5000):
            all_cached = False
    for name, _, _ in EPIDEMIC_PRESETS["sfx"]:
        dest = out_dir / f"{name}.wav"
        if not (dest.exists() and dest.stat().st_size > 5000):
            all_cached = False

    if all_cached:
        for name, _, _, _ in EPIDEMIC_PRESETS["music"]:
            results[name] = out_dir / f"{name}.wav"
        for name, _, _ in EPIDEMIC_PRESETS["sfx"]:
            results[name] = out_dir / f"{name}.wav"
        return results

    try:
        sid, _ = mcp_call({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "tiktok_radar", "version": "2.0.0"},
            },
        })

        # Descargar Stems de Música
        for name, rec_id, stem, desc in EPIDEMIC_PRESETS["music"]:
            dest = out_dir / f"{name}.wav"
            if dest.exists() and dest.stat().st_size > 5000:
                results[name] = dest
                continue

            print(f"[AUDIO-EPIDEMIC] Descargando stem {name} ({stem})...", flush=True)
            _, res = mcp_call({
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": "DownloadRecording",
                    "arguments": {"id": rec_id, "options": {"fileType": "WAV", "stemType": stem}},
                },
            }, sid)
            data = json.loads(res["result"]["content"][0]["text"])
            asset_url = data["data"]["recordingDownload"]["assetUrl"]
            download_file(asset_url, dest)
            results[name] = dest

        # Descargar Efectos SFX
        for name, sfx_id, desc in EPIDEMIC_PRESETS["sfx"]:
            dest = out_dir / f"{name}.wav"
            if dest.exists() and dest.stat().st_size > 5000:
                results[name] = dest
                continue

            print(f"[AUDIO-EPIDEMIC] Descargando SFX {name}...", flush=True)
            _, res = mcp_call({
                "jsonrpc": "2.0",
                "id": 20,
                "method": "tools/call",
                "params": {
                    "name": "DownloadSoundEffect",
                    "arguments": {"id": sfx_id, "options": {"fileType": "WAV"}},
                },
            }, sid)
            data = json.loads(res["result"]["content"][0]["text"])
            asset_url = data["data"]["soundEffectDownload"]["assetUrl"]
            download_file(asset_url, dest)
            results[name] = dest

    except Exception as e:
        print(f"[AUDIO-EPIDEMIC] ⚠️ Falló descarga de activos Epidemic: {e}. Se mantendrán los archivos existentes o fallback.", flush=True)

    return results


if __name__ == "__main__":
    print("Probando audio_generator...")
    test_out = Path("/tmp/test_gemini_tts.mp3")
    dur = generate_speech("Atención, prueba de locución periodística de alta fidelidad.", test_out)
    print("Duración generada:", dur, "segundos.")
