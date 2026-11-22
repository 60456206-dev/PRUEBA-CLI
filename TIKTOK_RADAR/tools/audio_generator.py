#!/usr/bin/env python3
"""
TIKTOK RADAR · Generador y Gestor de Audio de Alta Fidelidad (Broadcast)
1. Locución: Voz humana de estudio vía Gemini TTS (`gemini-3.8-flash-tts`, voz `Charon` con
   respaldo automático `gemini-3.1-flash-tts-preview` / `gemini-2.5-flash-preview-tts`),
   alineación acústica DP palabra a palabra (`WORD_BOUNDARIES.json`) y fallback Edge-TTS / ElevenLabs.
2. Música y Foley: Epidemic Sound MCP API con descarga y caché de stems (BASS + INSTRUMENTS) y SFX de estudio.
"""

import asyncio
import base64
import concurrent.futures
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Cargar .env si existe
for env_path in [
    Path.home() / ".api_keys.env",
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent / ".env",
]:
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
ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config_produccion.json"
DEFAULT_ASSETS_DIR = ROOT_DIR / "audio_assets"
DEFAULT_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_LOCUCION_CONFIG: Dict[str, Any] = {
    "motor_principal": "gemini",
    "acento": "es-PE (Peruano coloquial cercano)",
    "voz_gemini": "Puck",
    "voz_gemini_fallback": "Puck",
    "gemini_models": [
        "gemini-3.8-flash-tts",
        "gemini-3.8-flash-lite-tts",
        "gemini-3.1-flash-tts-preview",
        "gemini-2.5-flash-preview-tts",
    ],
    "voz_edge": "en-US-AndrewMultilingualNeural",
    "rate_edge": "+6%",
    "pitch_edge": "+0Hz",
    "tighten_silencios": False,
    "palabras_objetivo": "220-236",
    "elevenlabs_enabled": False,
    "elevenlabs_voice_id": "pNInz6obpgDQGcFmaJgB",
    "elevenlabs_model_id": "eleven_multilingual_v2",
    "elevenlabs_stability": 0.40,
    "elevenlabs_similarity_boost": 0.78,
    "elevenlabs_style": 0.42,
    "elevenlabs_speed": 1.04,
}

DEFAULT_PERUVIAN_COLLOQUIAL_STYLE = (
    "Chico peruano de Lima (28 a 32 años) con acento peruano 100% auténtico, natural y coloquial — "
    "cadencia limeña/peruana genuina, cálida, cercana y súper familiar, como conversando en confianza con un amigo "
    "o contando una historia increíble frente a cámara en YouTube/TikTok (cero locutor acartonado de noticiero, "
    "cero formalidad rígida, cero acento mexicano, colombiano ni español). "
    "Habla con energía real, ágil y fluida (alrededor de 185 a 195 palabras por minuto; NADA lento ni arrastrado, "
    "tampoco atropellado), con entonación viva y expresiva en cada giro de la historia, énfasis orgánico en los datos clave "
    "y respiraciones suaves y limpias en micrófono de estudio sin jadeos ruidosos."
)
DEFAULT_COSTA_RICA_STYLE = DEFAULT_PERUVIAN_COLLOQUIAL_STYLE
DEFAULT_HUMAN_NARRATOR_STYLE = DEFAULT_PERUVIAN_COLLOQUIAL_STYLE


def load_locucion_config() -> Dict[str, Any]:
    """Lee la configuración de locución desde config_produccion.json con valores peruanos coloquiales."""
    cfg = dict(DEFAULT_LOCUCION_CONFIG)
    if CONFIG_PATH.exists():
        try:
            raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            loc = raw.get("locucion")
            if isinstance(loc, dict):
                cfg.update(loc)
        except Exception:
            pass
    return cfg


def _clear_stale_boundaries(output_path: Path) -> None:
    """Elimina marcas previas de palabras/oraciones antes de una nueva síntesis."""
    for stale_name in ("SENTENCE_BOUNDARIES.json", "WORD_BOUNDARIES.json"):
        stale_bounds = output_path.parent / stale_name
        if stale_bounds.exists():
            try:
                stale_bounds.unlink()
            except Exception:
                pass


def _run_coro_sync(coro: Any) -> Any:
    """Ejecuta una corrutina incluso si ya existe un event loop activo en el hilo actual."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()

# ==============================================================================
# Catálogo Maestro de Soundtracks Cinematográficos Epidemic Sound por Categoría
# Seleccionados y arreglados a ~65s FULL (tambores + cuerdas + clímax)
# ==============================================================================
GENRE_SOUNDTRACK_CATALOG = {
    "G3_IA_HARDWARE": {
        "title": "Observatory",
        "artist": "Out To The World",
        "bpm": 128,
        "style": "Modern Investigative Documentary / Energetic Tech Synth & Crisp Drums",
        "id": "0c47304b-4e50-43b2-8230-2397e7991316",
        "full_file": "G3_TECH_OBSERVATORY_64S_FULL.mp3",
        "bass_file": "G3_TECH_STYLE_BASS.mp3",
        "inst_file": "G3_TECH_STYLE_INSTRUMENTS.mp3",
    },
    "G2_CIBERATAQUES": {
        "title": "Dark Future Rock Beat",
        "artist": "Def Lev",
        "bpm": 100,
        "style": "Cyberpunk Dark Thriller / Driving Electronic Pulse & Heavy Drums",
        "id": "db5e6eb9-deb3-46dc-85a8-664f08902fb8",
        "full_file": "G2_CYBER_DARKFUTURE_64S_FULL.mp3",
        "bass_file": "G2_CYBER_DEADLOCK_BASS.mp3",
        "inst_file": "G2_CYBER_DEADLOCK_INSTRUMENTS.mp3",
    },
    "G1_AVIACION": {
        "title": "One",
        "artist": "Hampus Naeselius",
        "bpm": 125,
        "style": "Cinematic Action Thriller / Hans Zimmer Style Tension Strings & Drums",
        "id": "171be0bd-6cbe-4932-bff8-1b8129c471f0",
        "full_file": "G1_AVIATION_ONE_64S_FULL.mp3",
        "bass_file": "G1_AVIATION_TRACE_BASS.mp3",
        "inst_file": "G1_AVIATION_TRACE_INSTRUMENTS.mp3",
    },
    "G4_ESPACIO": {
        "title": "Last Frontier",
        "artist": "Hampus Naeselius",
        "bpm": 87,
        "style": "Epic Cosmic Documentary / Interstellar Style Strings & Orchestral Climax",
        "id": "10cdcb7d-e251-444a-af68-4f989b23a593",
        "full_file": "G4_SPACE_LASTFRONTIER_64S_FULL.mp3",
        "bass_file": "G4_SPACE_MINDSCAPE_BASS.mp3",
        "inst_file": "G4_SPACE_MINDSCAPE_INSTRUMENTS.mp3",
    },
}

# Stems y SFX complementarios
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


def _resolve_genre_soundtrack_key(genre: str) -> str:
    """Mapea el género o titular de noticia a la clave canónica de GENRE_SOUNDTRACK_CATALOG."""
    genre_upper = (genre or "G1").upper()
    if any(k in genre_upper for k in ["G1", "AVIACION", "AVIACIÓN", "MAYDAY", "VUELO", "AEREO", "AÉREO", "AVION", "AVIÓN", "ACCIDENTE"]):
        return "G1_AVIACION"
    if any(k in genre_upper for k in ["G2", "CIBER", "HACKER", "CYBER", "RANSOMWARE"]):
        return "G2_CIBERATAQUES"
    if any(k in genre_upper for k in ["G4", "ESPACIO", "NASA", "ORBITA", "ÓRBITA", "CIENCIA", "STARSHIP"]):
        return "G4_ESPACIO"
    if any(k in genre_upper for k in ["G3", "ROBOTICA", "ROBÓTICA", "HARDWARE", "CHIP", "SEMICONDUCTOR"]) or re.search(r"\bIA\b|\bAI\b", genre_upper):
        return "G3_IA_HARDWARE"
    return "G3_IA_HARDWARE"


def _extract_mcp_json_data(res: Dict[str, Any]) -> Dict[str, Any]:
    txt = res.get("result", {}).get("content", [{}])[0].get("text", "{}")
    return json.loads(txt) if isinstance(txt, str) and txt.strip().startswith("{") else {}


def download_arranged_soundtrack_65s(
    recording_id: str,
    dest_path: Path,
    target_ms: int = 65000,
    session_id: Optional[str] = None,
) -> bool:
    """
    Solicita un arreglo automático de ~65s en Epidemic Sound (`EditRecording`) con intro, cuerpo y
    clímax comprimido para TikTok; descarga el máster FULL editado con respaldo automático a `DownloadRecording(FULL)`.
    """
    key_env = os.getenv("EPIDEMIC_SOUND") or EPIDEMIC_SOUND
    if not key_env:
        return False

    try:
        sid = session_id
        if not sid:
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

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        _, edit_res = mcp_call({
            "jsonrpc": "2.0",
            "id": 81,
            "method": "tools/call",
            "params": {
                "name": "EditRecording",
                "arguments": {
                    "id": recording_id,
                    "input": {
                        "targetDurationMs": int(target_ms),
                        "downloadAudioFormat": "MP3",
                        "skipStems": True,
                        "maxResults": 1,
                    },
                },
            },
        }, sid)
        edit_data = _extract_mcp_json_data(edit_res)
        job_id = ((edit_data.get("data") or {}).get("recordingEdit") or {}).get("id")

        asset_url: Optional[str] = None
        if job_id:
            for _ in range(15):
                _, poll_res = mcp_call({
                    "jsonrpc": "2.0",
                    "id": 82,
                    "method": "tools/call",
                    "params": {"name": "PollEditRecordingJob", "arguments": {"id": job_id}},
                }, sid)
                poll_data = _extract_mcp_json_data(poll_res)
                job_obj = (poll_data.get("data") or {}).get("recordingEditJob") or {}
                status = str(job_obj.get("status") or "").upper()
                if status == "COMPLETED":
                    edit_obj = job_obj.get("edit") or (job_obj.get("edits") or [None])[0] or {}
                    edit_id = edit_obj.get("id")
                    if edit_id:
                        try:
                            _, dl_res = mcp_call({
                                "jsonrpc": "2.0",
                                "id": 83,
                                "method": "tools/call",
                                "params": {
                                    "name": "DownloadRecordingEdit",
                                    "arguments": {"input": {"jobId": job_id, "editId": edit_id}},
                                },
                            }, sid)
                            dl_data = _extract_mcp_json_data(dl_res).get("data") or {}
                            for k in ("recordingEditDownload", "downloadRecordingEdit", "recordingDownload"):
                                if isinstance(dl_data.get(k), dict) and dl_data[k].get("assetUrl"):
                                    asset_url = dl_data[k]["assetUrl"]
                                    break
                            if not asset_url:
                                m_url = re.search(r"https://[^\s\"']+\.(?:mp3|wav)[^\s\"']*", json.dumps(dl_data))
                                if m_url:
                                    asset_url = m_url.group(0)
                        except Exception:
                            asset_url = None
                    if not asset_url:
                        asset_url = edit_obj.get("fullMixPreviewUrl")
                    break
                if status in ("FAILED", "ERROR"):
                    break
                time.sleep(1.5)

        if not asset_url:
            _, full_res = mcp_call({
                "jsonrpc": "2.0",
                "id": 84,
                "method": "tools/call",
                "params": {
                    "name": "DownloadRecording",
                    "arguments": {"id": recording_id, "options": {"fileType": "MP3", "stemType": "FULL"}},
                },
            }, sid)
            full_data = _extract_mcp_json_data(full_res)
            asset_url = ((full_data.get("data") or {}).get("recordingDownload") or {}).get("assetUrl")

        if asset_url:
            tmp_dl = dest_path.with_suffix(".dl.tmp.mp3")
            download_file(asset_url, tmp_dl)
            if tmp_dl.exists() and tmp_dl.stat().st_size > 20_000:
                tmp_dl.replace(dest_path)
                return True
            tmp_dl.unlink(missing_ok=True)
    except Exception as e:
        print(f"[AUDIO-EPIDEMIC] Aviso al arreglar/descargar soundtrack 65s ({recording_id}): {e}", flush=True)
    return False


def get_genre_full_soundtrack(genre: str, target_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Devuelve la ruta local del soundtrack FULL arreglado a ~65s (`*_64S_FULL.mp3`) para la categoría.
    Si no existe localmente y hay clave `EPIDEMIC_SOUND`, lo arregla y descarga vía MCP.
    """
    assets_dir = target_dir or DEFAULT_ASSETS_DIR
    key = _resolve_genre_soundtrack_key(genre)
    entry = GENRE_SOUNDTRACK_CATALOG[key]
    full_name = entry.get("full_file")
    if not full_name:
        return None
    full_path = assets_dir / full_name
    if full_path.exists() and full_path.stat().st_size > 20_000:
        return full_path
    if download_arranged_soundtrack_65s(entry["id"], full_path, target_ms=65000):
        return full_path
    return None


def get_genre_soundtrack(genre: str, target_dir: Optional[Path] = None) -> Tuple[Path, Path]:
    """
    Devuelve las rutas locales de los stems (BASS, INSTRUMENTS) oficiales de Epidemic Sound
    para el género de noticia seleccionado. Si no existen localmente, intenta descargarlos vía MCP.
    """
    assets_dir = target_dir or DEFAULT_ASSETS_DIR
    key = _resolve_genre_soundtrack_key(genre)

    entry = GENRE_SOUNDTRACK_CATALOG[key]
    bass_path = assets_dir / entry["bass_file"]
    inst_path = assets_dir / entry["inst_file"]

    # Si ya existen, retornarlos inmediatamente
    if bass_path.exists() and inst_path.exists():
        return bass_path, inst_path

    # Si falta alguno y hay credenciales de Epidemic Sound, intentar descarga
    key_env = os.getenv("EPIDEMIC_SOUND") or EPIDEMIC_SOUND
    if key_env:
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
            for stem_type, path in [("BASS", bass_path), ("INSTRUMENTS", inst_path)]:
                if not path.exists():
                    _, res = mcp_call({
                        "jsonrpc": "2.0",
                        "id": 80,
                        "method": "tools/call",
                        "params": {
                            "name": "DownloadRecording",
                            "arguments": {"id": entry["id"], "options": {"fileType": "MP3", "stemType": stem_type}},
                        },
                    }, sid)
                    txt = res["result"]["content"][0]["text"]
                    url = json.loads(txt)["data"]["recordingDownload"]["assetUrl"]
                    download_file(url, path)
            if bass_path.exists() and inst_path.exists():
                return bass_path, inst_path
        except Exception as e:
            print(f"[AUDIO-EPIDEMIC] Aviso al descargar stems de {key}: {e}", flush=True)

    # Fallback general a los archivos ya cacheados
    fb_bass = assets_dir / "NEWS_THRILLER_BASS.mp3"
    fb_inst = assets_dir / "NEWS_THRILLER_INSTRUMENTS.mp3"
    if fb_bass.exists() and fb_inst.exists():
        return fb_bass, fb_inst

    return bass_path, inst_path


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
# 1. Locución Profesional Hiperhumana con Gemini TTS
# -----------------------------------------------------------------------------

def _clean_text_for_tts(text: str) -> str:
    """Limpia marcas Markdown simples sin alterar palabras ni signos de puntuación."""
    cleaned = re.sub(r"[*_`~]+", "", text or "")
    return re.sub(r"\s+", " ", cleaned).strip()


def _wrap_pcm_as_wav(raw: bytes, mime_type: str = "") -> bytes:
    """Envuelve PCM L16 crudo en una cabecera WAV válida si la respuesta no trae RIFF."""
    if raw[:4] == b"RIFF":
        return raw
    rate_m = re.search(r"rate=(\d+)", mime_type or "", flags=re.IGNORECASE)
    sample_rate = int(rate_m.group(1)) if rate_m else 24000
    ch_m = re.search(r"channels=(\d+)", mime_type or "", flags=re.IGNORECASE)
    channels = int(ch_m.group(1)) if ch_m else 1
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(raw)
    return buf.getvalue()


def _finalize_voice_audio(raw_wav: bytes, output_path: Path) -> None:
    """
    Recorta únicamente silencio muerto inicial y final (preservando respiraciones internas)
    y exporta la locución limpia a 48 kHz de alta fidelidad.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_wav = output_path.with_suffix(".gemini_raw.wav")
    tmp_wav.write_bytes(raw_wav)
    af_trim = (
        "silenceremove=start_periods=1:start_duration=0.04:start_threshold=-46dB,"
        "areverse,silenceremove=start_periods=1:start_duration=0.04:start_threshold=-46dB,areverse,"
        "afade=t=in:st=0:d=0.008"
    )
    try:
        if output_path.suffix.lower() == ".wav":
            cmd = [
                "ffmpeg", "-y", "-i", str(tmp_wav),
                "-af", af_trim,
                "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
                str(output_path),
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-i", str(tmp_wav),
                "-af", af_trim,
                "-ar", "48000", "-ac", "1", "-b:a", "256k",
                str(output_path),
            ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        if output_path.suffix.lower() == ".mp3":
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(tmp_wav), "-ar", "48000", "-b:a", "256k", str(output_path)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        else:
            output_path.write_bytes(raw_wav)
    finally:
        tmp_wav.unlink(missing_ok=True)


def generate_speech_gemini(
    text: str,
    output_path: Path,
    voice: str = "Puck",
    style: Optional[str] = None,
    models: Optional[List[str]] = None,
) -> bool:
    """Genera locución hiperhumana con Gemini TTS soportando esquemas 3.8 y 3.1/2.5 + PCM crudo."""
    key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
    if not key or not (text or "").strip():
        return False

    _clear_stale_boundaries(output_path)
    clean_text = _clean_text_for_tts(text)

    if not style:
        style = DEFAULT_COSTA_RICA_STYLE

    loc_cfg = load_locucion_config()
    models_to_try = list(
        models
        or loc_cfg.get("gemini_models")
        or [
            "gemini-3.8-flash-tts",
            "gemini-3.8-flash-lite-tts",
            "gemini-3.1-flash-tts-preview",
            "gemini-2.5-flash-preview-tts",
        ]
    )

    for model in models_to_try:
        is_v38 = "3.8" in model
        if is_v38:
            body: Dict[str, Any] = {
                "contents": [{
                    "role": "user",
                    "parts": [{
                        "text": clean_text,
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
        else:
            prompt_text = f"{style}\n\nLee exactamente el siguiente guion con voz humana natural:\n\n{clean_text}"
            body = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": prompt_text}]
                }],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {
                                "voiceName": voice
                            }
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
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.load(resp)
            parts = data["candidates"][0]["content"]["parts"]
            inline = next(p["inlineData"] for p in parts if "inlineData" in p)
            raw = base64.b64decode(inline["data"])
            if len(raw) < 1024:
                raise RuntimeError("Respuesta de audio demasiado corta.")
            raw_wav = _wrap_pcm_as_wav(raw, inline.get("mimeType", ""))
            _finalize_voice_audio(raw_wav, output_path)

            dur = probe_duration(output_path)
            print(f"[AUDIO-TTS] ✅ Locución Gemini completada: {output_path.name} ({dur:.2f} s)", flush=True)
            return True
        except urllib.error.HTTPError as e:
            print(f"[AUDIO-TTS] ⚠️ Error HTTP {e.code} con {model}: {e}. Probando alternativa...", flush=True)
            if e.code == 429:
                time.sleep(2.0)
        except Exception as e:
            print(f"[AUDIO-TTS] ⚠️ Error con {model}: {e}. Probando alternativa...", flush=True)

    return False


def _alignment_chars_to_word_boundaries(alignment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convierte alignment carácter a carácter de ElevenLabs en marcas de palabra exactas."""
    chars = alignment.get("characters") or []
    starts = alignment.get("character_start_times_seconds") or []
    ends = alignment.get("character_end_times_seconds") or []
    n = min(len(chars), len(starts), len(ends))
    if n == 0:
        return []

    words: List[Dict[str, Any]] = []
    buf: List[str] = []
    w_start: Optional[float] = None
    w_end: float = 0.0

    for i in range(n):
        ch = str(chars[i])
        st = float(starts[i])
        en = float(ends[i])
        if ch.isspace():
            if buf and w_start is not None:
                words.append({
                    "text": "".join(buf),
                    "start": round(w_start, 3),
                    "end": round(max(w_start + 0.05, w_end), 3),
                })
                buf = []
                w_start = None
                w_end = 0.0
        else:
            if w_start is None:
                w_start = st
            buf.append(ch)
            w_end = max(w_end, en)

    if buf and w_start is not None:
        words.append({
            "text": "".join(buf),
            "start": round(w_start, 3),
            "end": round(max(w_start + 0.05, w_end), 3),
        })
    return words


def generate_speech_elevenlabs(
    text: str,
    output_path: Path,
    voice_id: str,
    model_id: str = "eleven_multilingual_v2",
    voice_settings: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
) -> bool:
    """
    Sintetiza locución con ElevenLabs (`/with-timestamps`) y escribe WORD_BOUNDARIES.json
    y SENTENCE_BOUNDARIES.json directamente desde el alineamiento oficial de la respuesta.
    """
    key = (api_key or os.getenv("ELEVENLABS_API_KEY", "")).strip()
    if not key or not text.strip() or not voice_id.strip():
        return False

    _clear_stale_boundaries(output_path)
    loc_cfg = load_locucion_config()
    settings = dict(voice_settings or {
        "stability": float(loc_cfg.get("elevenlabs_stability", 0.45)),
        "similarity_boost": float(loc_cfg.get("elevenlabs_similarity_boost", 0.78)),
        "style": float(loc_cfg.get("elevenlabs_style", 0.35)),
        "use_speaker_boost": True,
        "speed": float(loc_cfg.get("elevenlabs_speed", 0.96)),
    })

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": settings,
        "apply_text_normalization": "auto",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        print(f"[AUDIO-TTS] Generando locución ElevenLabs ({model_id} | voice={voice_id})...", flush=True)
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.load(resp)
        b64_audio = data.get("audio_base64") or ""
        if not b64_audio:
            return False
        raw = base64.b64decode(b64_audio)
        if len(raw) < 512:
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.suffix.lower() == ".wav":
            tmp_mp3 = output_path.with_suffix(".el_tmp.mp3")
            tmp_mp3.write_bytes(raw)
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(tmp_mp3), "-ar", "48000", "-ac", "2", str(output_path)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            tmp_mp3.unlink(missing_ok=True)
        else:
            output_path.write_bytes(raw)

        alignment = data.get("alignment") or data.get("normalized_alignment") or {}
        word_entries = _alignment_chars_to_word_boundaries(alignment) if isinstance(alignment, dict) else []
        if word_entries:
            (output_path.parent / "WORD_BOUNDARIES.json").write_text(
                json.dumps(word_entries, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            sentences = _reconstruct_sentences_from_words(word_entries)
            if sentences:
                (output_path.parent / "SENTENCE_BOUNDARIES.json").write_text(
                    json.dumps(sentences, indent=2, ensure_ascii=False), encoding="utf-8"
                )
        dur = probe_duration(output_path)
        print(f"[AUDIO-TTS] ✅ Locución ElevenLabs completada ({len(word_entries)} palabras): {output_path.name} ({dur:.2f} s)", flush=True)
        return True
    except Exception as e:
        print(f"[AUDIO-TTS] ⚠️ Error ElevenLabs TTS: {e}. Activando fallback local...", flush=True)
        return False


def _reconstruct_sentences_from_words(word_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Agrupa marcas de palabra (WordBoundary) en oraciones completas con [start, end]."""
    sentences: List[Dict[str, Any]] = []
    cur_words: List[str] = []
    cur_start: Optional[float] = None
    cur_end: float = 0.0

    for entry in word_entries:
        txt = str(entry.get("text", "")).strip()
        if not txt:
            continue
        w_start = float(entry.get("start", 0.0))
        w_end = float(entry.get("end", w_start))
        if cur_start is None:
            cur_start = w_start
        cur_words.append(txt)
        cur_end = max(cur_end, w_end)
        if txt.endswith((".", "?", "!", ":", ";")):
            sentences.append({
                "text": " ".join(cur_words),
                "start": round(cur_start, 3),
                "end": round(max(cur_end, cur_start + 0.15), 3),
            })
            cur_words = []
            cur_start = None
            cur_end = 0.0

    if cur_words and cur_start is not None:
        sentences.append({
            "text": " ".join(cur_words),
            "start": round(cur_start, 3),
            "end": round(max(cur_end, cur_start + 0.15), 3),
        })
    return sentences


def extract_word_boundaries_whisper(audio_path: Path, language: str = "es") -> Optional[Path]:
    """
    Si faster-whisper está instalado en el servidor, extrae timestamps por palabra reales
    (WORD_BOUNDARIES.json) también para locuciones de Gemini TTS. Es totalmente opcional.
    """
    if not audio_path.exists():
        return None
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        return None

    try:
        model = WhisperModel(os.getenv("WHISPER_MODEL_SIZE", "base"), device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(audio_path), language=language, word_timestamps=True)
        words: List[Dict[str, Any]] = []
        sentences: List[Dict[str, Any]] = []
        for seg in segments:
            s_text = (seg.text or "").strip()
            if s_text:
                sentences.append({"text": s_text, "start": round(float(seg.start), 3), "end": round(float(seg.end), 3)})
            for w in getattr(seg, "words", None) or []:
                w_txt = (getattr(w, "word", "") or "").strip()
                if w_txt:
                    words.append({
                        "text": w_txt,
                        "start": round(float(w.start), 3),
                        "end": round(float(w.end), 3),
                    })
        if words:
            wb_path = audio_path.parent / "WORD_BOUNDARIES.json"
            wb_path.write_text(json.dumps(words, indent=2, ensure_ascii=False), encoding="utf-8")
            if sentences and not (audio_path.parent / "SENTENCE_BOUNDARIES.json").exists():
                (audio_path.parent / "SENTENCE_BOUNDARIES.json").write_text(
                    json.dumps(sentences, indent=2, ensure_ascii=False), encoding="utf-8"
                )
            print(f"[AUDIO-TTS] ✅ Marcas por palabra extraídas con Whisper: {len(words)} palabras.", flush=True)
            return wb_path
    except Exception as e:
        print(f"[AUDIO-TTS] Aviso Whisper word_timestamps omitido: {e}", flush=True)
    return None


async def _generate_speech_edge_async(
    text: str,
    output_path: Path,
    voice: str = "es-CR-JuanNeural",
    rate: str = "-4%",
    pitch: str = "+0Hz",
) -> bool:
    try:
        import edge_tts

        _clear_stale_boundaries(output_path)
        # Capturar WordBoundary reales además de reconstruir SentenceBoundary
        communicate = edge_tts.Communicate(
            text,
            voice,
            rate=rate,
            pitch=pitch,
            boundary="WordBoundary",
        )
        word_entries: List[Dict[str, Any]] = []
        sentences: List[Dict[str, Any]] = []
        audio_data = bytearray()
        async for chunk in communicate.stream():
            ctype = chunk.get("type")
            if ctype == "audio":
                audio_data.extend(chunk["data"])
            elif ctype == "WordBoundary":
                w_start = round(chunk.get("offset", 0) / 10_000_000, 3)
                w_end = round((chunk.get("offset", 0) + chunk.get("duration", 0)) / 10_000_000, 3)
                word_entries.append({
                    "text": chunk.get("text", ""),
                    "start": w_start,
                    "end": max(w_start + 0.05, w_end),
                })
            elif ctype == "SentenceBoundary":
                sentences.append({
                    "text": chunk.get("text", ""),
                    "start": round(chunk.get("offset", 0) / 10_000_000, 3),
                    "end": round((chunk.get("offset", 0) + chunk.get("duration", 0)) / 10_000_000, 3)
                })

        if not audio_data:
            raise RuntimeError("Edge-TTS devolvió stream de audio vacío.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.suffix.lower() == ".wav":
            tmp_mp3 = output_path.with_suffix(".tmp.mp3")
            tmp_mp3.write_bytes(audio_data)
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(tmp_mp3), "-ar", "48000", "-ac", "1", str(output_path)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            tmp_mp3.unlink(missing_ok=True)
        else:
            output_path.write_bytes(audio_data)

        if word_entries:
            (output_path.parent / "WORD_BOUNDARIES.json").write_text(
                json.dumps(word_entries, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            if not sentences:
                sentences = _reconstruct_sentences_from_words(word_entries)

        if sentences:
            bounds_file = output_path.parent / "SENTENCE_BOUNDARIES.json"
            bounds_file.write_text(json.dumps(sentences, indent=2, ensure_ascii=False), encoding="utf-8")

        dur = probe_duration(output_path)
        print(
            f"[AUDIO-TTS] ✅ Locución Edge-TTS ({voice} | rate={rate}) completada con marcas "
            f"({len(word_entries)} palabras): {output_path.name} ({dur:.2f} s)",
            flush=True,
        )
        return True
    except Exception as e:
        print(f"[AUDIO-TTS] ❌ Falló Edge-TTS: {e}", flush=True)
        return False


def tighten_audio_dead_air(
    input_path: Path,
    margin_sec: float = 0.15,
    silent_speed: float = 2.0,
    min_monetizable_duration: float = 60.5
) -> float:
    """
    Aplica auto-editor de forma no destructiva para acelerar micropausas
    de la locución sin distorsionar el tono ni romper la duración monetizable (>60s).
    """
    auto_editor_bin = shutil.which("auto-editor") or str(Path.home() / ".local" / "bin" / "auto-editor")
    if not auto_editor_bin or not os.path.exists(auto_editor_bin):
        return probe_duration(input_path)

    curr_dur = probe_duration(input_path)
    if curr_dur <= min_monetizable_duration:
        return curr_dur

    out_file = input_path.parent / f"_tight_{input_path.name}"
    cmd = [
        auto_editor_bin, str(input_path),
        "-m", f"{margin_sec}s",
        "--when-silent", f"speed:{silent_speed}",
        "-o", str(out_file),
        "-q"
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and out_file.exists():
            new_dur = probe_duration(out_file)
            if new_dur >= min_monetizable_duration:
                shutil.move(str(out_file), str(input_path))
                # Las marcas previas ya no coinciden tras recortar silencios
                if abs(new_dur - curr_dur) > 0.05:
                    for stale_name in ("SENTENCE_BOUNDARIES.json", "WORD_BOUNDARIES.json"):
                        stale_bounds = input_path.parent / stale_name
                        if stale_bounds.exists():
                            try:
                                stale_bounds.unlink()
                            except Exception:
                                pass
                print(f"[AUDIO-TTS] ⚡ auto-editor: pausas ajustadas ({curr_dur:.2f}s -> {new_dur:.2f}s)", flush=True)
                return new_dur
            else:
                if out_file.exists():
                    out_file.unlink()
    except Exception as e:
        print(f"[AUDIO-TTS] ⚠️ auto-editor omitido: {e}", flush=True)
    return curr_dur


def _phonetic_word_weight(word: str) -> float:
    """Estima peso temporal fonético de una palabra en español según sílabas, longitud y puntuación."""
    clean = re.sub(r"[^\wáéíóúüñ]", "", (word or "").lower(), flags=re.UNICODE)
    syllables = max(1, len(re.findall(r"[aeiouáéíóúü]+", clean)))
    punct_bonus = 0.45 if word.endswith((".", "?", "!")) else (0.25 if word.endswith((",", ";", ":")) else 0.0)
    return max(0.5, 0.65 * syllables + 0.12 * len(clean) + punct_bonus)


def _speech_pos_to_timeline(pos_in_speech: float, spans: List[Tuple[float, float]], is_start: bool) -> float:
    """Mapea una posición acumulada de habla activa a tiempo real en el audio."""
    rem = max(0.0, pos_in_speech)
    for idx, (s_start, s_end) in enumerate(spans):
        dur = max(0.01, s_end - s_start)
        if is_start:
            if rem < dur - 1e-6 or idx == len(spans) - 1:
                return min(s_end, s_start + rem)
        else:
            if rem <= dur + 1e-6 or idx == len(spans) - 1:
                return min(s_end, s_start + rem)
        rem -= dur
    return spans[-1][1]


def extract_word_boundaries_acoustic(audio_path: Path, script: str) -> Optional[Path]:
    """
    Alinea palabras del guion a la envolvente RMS real del audio mediante programación dinámica
    monotónica anclada a pausas acústicas reales (>=0.14s), generando WORD_BOUNDARIES.json y
    SENTENCE_BOUNDARIES.json con conteo exacto 1:1 respecto a `script.split()`.
    """
    words = (script or "").split()
    if not audio_path.exists() or not words:
        return None
    try:
        import numpy as np
    except ImportError:
        return None

    try:
        sr = 16000
        hop = 160  # 10 ms por cuadro
        pcm_bytes = subprocess.check_output(
            [
                "ffmpeg", "-v", "error", "-i", str(audio_path),
                "-ac", "1", "-ar", str(sr), "-f", "s16le", "-",
            ],
            stderr=subprocess.PIPE,
            timeout=30,
        )
        samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        total_dur = len(samples) / float(sr)
        if len(samples) < sr * 0.2:
            return None

        n_frames = len(samples) // hop
        if n_frames < 5:
            return None
        frames = samples[: n_frames * hop].reshape(n_frames, hop)
        rms = np.sqrt(np.mean(frames * frames, axis=1) + 1e-12)
        db = 20.0 * np.log10(rms + 1e-9)

        active_db = db[db > -65.0]
        if active_db.size == 0:
            return None
        ref_db = float(np.percentile(active_db, 95))
        thresh_db = max(-55.0, ref_db - 26.0)
        mask = (db >= thresh_db).copy()

        # Cerrar micro-huecos < 90ms (oclusivas sordas /p, t, k/)
        idx = 0
        while idx < n_frames:
            if not mask[idx]:
                j = idx
                while j < n_frames and not mask[j]:
                    j += 1
                if idx > 0 and j < n_frames and (j - idx) < 9:
                    mask[idx:j] = True
                idx = j
            else:
                idx += 1

        # Extraer tramos activos descartando ráfagas aisladas < 60ms
        raw_spans: List[Tuple[float, float]] = []
        idx = 0
        while idx < n_frames:
            if mask[idx]:
                j = idx
                while j < n_frames and mask[j]:
                    j += 1
                if (j - idx) >= 6:
                    raw_spans.append((round(idx * 0.01, 3), round(min(total_dur, j * 0.01), 3)))
                idx = j
            else:
                idx += 1

        speech_spans = raw_spans if raw_spans else [(0.0, round(total_dur, 3))]
        span_durs = [max(0.02, e - s) for s, e in speech_spans]
        total_speech_dur = sum(span_durs)

        # Identificar pausas reales (>= 0.14s) entre tramos activos
        gaps: List[Dict[str, float]] = []
        cum_s = 0.0
        for i in range(len(speech_spans) - 1):
            cum_s += span_durs[i]
            g_dur = speech_spans[i + 1][0] - speech_spans[i][1]
            if g_dur >= 0.14:
                gaps.append({"cum_speech": cum_s, "dur": g_dur})

        weights = [_phonetic_word_weight(w) for w in words]
        total_w = max(1e-6, sum(weights))
        cum_w: List[float] = []
        acc_w = 0.0
        for wt in weights:
            acc_w += wt
            cum_w.append(acc_w)
        exp_speech_t = [(cw / total_w) * total_speech_dur for cw in cum_w]

        # Alinear finales de oración fuerte con silencios reales mediante DP monotónica
        sent_ends = [i for i, w in enumerate(words[:-1]) if w.endswith((".", "?", "!", ";", ":"))]
        matched_pairs: List[Tuple[int, float]] = []
        if sent_ends and gaps:
            tol = max(2.5, 0.09 * total_speech_dur)
            n_s, n_g = len(sent_ends), len(gaps)
            dp = [[0.0] * (n_g + 1) for _ in range(n_s + 1)]
            choice = [[0] * (n_g + 1) for _ in range(n_s + 1)]  # 1: skip s, 2: skip g, 3: match

            for i in range(1, n_s + 1):
                w_idx = sent_ends[i - 1]
                exp_t = exp_speech_t[w_idx]
                for j in range(1, n_g + 1):
                    best = dp[i - 1][j]
                    act = 1
                    if dp[i][j - 1] > best:
                        best = dp[i][j - 1]
                        act = 2
                    drift = abs(gaps[j - 1]["cum_speech"] - exp_t)
                    if drift <= tol:
                        cand = dp[i - 1][j - 1] + 1.0 + min(0.6, gaps[j - 1]["dur"]) * 2.0 - 0.8 * (drift / tol)
                        if cand > best:
                            best = cand
                            act = 3
                    dp[i][j] = best
                    choice[i][j] = act

            raw_matches: List[Tuple[int, float]] = []
            i, j = n_s, n_g
            while i > 0 and j > 0:
                act = choice[i][j]
                if act == 3:
                    raw_matches.append((sent_ends[i - 1], gaps[j - 1]["cum_speech"]))
                    i -= 1
                    j -= 1
                elif act == 1:
                    i -= 1
                else:
                    j -= 1
            raw_matches.reverse()

            # Filtrar anclas cuya relación de palabras/tiempo sea físicamente coherente
            prev_w_excl = 0
            prev_s = 0.0
            n_words = len(words)
            for w_end_idx, g_cum in raw_matches:
                w_excl = w_end_idx + 1
                rem_words = n_words - w_excl
                seg_words = w_excl - prev_w_excl
                if (
                    seg_words >= 1
                    and (g_cum - prev_s) >= 0.04 * seg_words
                    and (total_speech_dur - g_cum) >= 0.04 * max(1, rem_words)
                ):
                    matched_pairs.append((w_excl, g_cum))
                    prev_w_excl = w_excl
                    prev_s = g_cum

        anchors: List[Tuple[int, float]] = [(0, 0.0), *matched_pairs, (len(words), total_speech_dur)]
        word_entries: List[Dict[str, Any]] = []
        prev_end = 0.0

        for a_idx in range(len(anchors) - 1):
            w0, s0 = anchors[a_idx]
            w1, s1 = anchors[a_idx + 1]
            if w1 <= w0:
                continue
            seg_wt = max(1e-6, sum(weights[w0:w1]))
            cur_s = s0
            for k in range(w0, w1):
                dur_s = (weights[k] / seg_wt) * max(0.01, s1 - s0)
                t_start = _speech_pos_to_timeline(cur_s, speech_spans, is_start=True)
                t_end = _speech_pos_to_timeline(cur_s + dur_s, speech_spans, is_start=False)
                t_start = max(prev_end, min(total_dur - 0.04, t_start))
                t_end = max(t_start + 0.04, min(total_dur, t_end))
                word_entries.append({
                    "text": words[k],
                    "start": round(t_start, 3),
                    "end": round(t_end, 3),
                })
                prev_end = t_end
                cur_s += dur_s

        if len(word_entries) != len(words):
            return None

        wb_path = audio_path.parent / "WORD_BOUNDARIES.json"
        wb_path.write_text(json.dumps(word_entries, indent=2, ensure_ascii=False), encoding="utf-8")
        sentences = _reconstruct_sentences_from_words(word_entries)
        if sentences:
            (audio_path.parent / "SENTENCE_BOUNDARIES.json").write_text(
                json.dumps(sentences, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        print(
            f"[AUDIO-TTS] ✅ Alineación acústica DP completada ({len(word_entries)} palabras, "
            f"{len(matched_pairs)} pausas ancladas).",
            flush=True,
        )
        return wb_path
    except Exception as e:
        print(f"[AUDIO-TTS] Aviso alineación acústica omitida: {e}", flush=True)
        return None


def generate_speech(
    text: str,
    output_path: Path,
    voice_gemini: Optional[str] = None,
    voice_edge: Optional[str] = None,
    style: Optional[str] = None,
    tighten: Optional[bool] = None,
    prefer_edge: Optional[bool] = None,
    rate_edge: Optional[str] = None,
    pitch_edge: Optional[str] = None,
) -> float:
    """Genera locución hiperhumana (ElevenLabs si está activado y hay clave, Gemini TTS por defecto y fallback Edge-TTS)."""
    loc_cfg = load_locucion_config()
    motor = str(loc_cfg.get("motor_principal", "gemini")).lower()
    use_edge_first = prefer_edge if prefer_edge is not None else (motor == "edge_tts")
    edge_voice = voice_edge or str(loc_cfg.get("voz_edge", "en-US-AndrewMultilingualNeural"))
    edge_rate = rate_edge or str(loc_cfg.get("rate_edge", "+6%"))
    edge_pitch = pitch_edge or str(loc_cfg.get("pitch_edge", "+0Hz"))
    gem_voice = voice_gemini or str(loc_cfg.get("voz_gemini") or loc_cfg.get("voz_gemini_fallback", "Puck"))
    resolved_style = style or DEFAULT_COSTA_RICA_STYLE
    should_tighten = bool(loc_cfg.get("tighten_silencios", False)) if tighten is None else tighten

    ok = False
    el_enabled = motor == "elevenlabs" or bool(loc_cfg.get("elevenlabs_enabled", False))
    if el_enabled and os.getenv("ELEVENLABS_API_KEY", "").strip():
        ok = generate_speech_elevenlabs(
            text,
            output_path,
            voice_id=str(loc_cfg.get("elevenlabs_voice_id", "pNInz6obpgDQGcFmaJgB")),
            model_id=str(loc_cfg.get("elevenlabs_model_id", "eleven_multilingual_v2")),
        )

    if not ok:
        if use_edge_first:
            print(f"[AUDIO-TTS] Generando locución Edge-TTS ({edge_voice} | rate={edge_rate})...", flush=True)
            ok = _run_coro_sync(
                _generate_speech_edge_async(text, output_path, voice=edge_voice, rate=edge_rate, pitch=edge_pitch)
            )
            if not ok:
                print("[AUDIO-TTS] Activando fallback Gemini TTS con dirección humana de estudio...", flush=True)
                ok = generate_speech_gemini(text, output_path, voice=gem_voice, style=resolved_style)
        else:
            ok = generate_speech_gemini(text, output_path, voice=gem_voice, style=resolved_style)
            if not ok:
                print(f"[AUDIO-TTS] Activando fallback Edge-TTS ({edge_voice} | rate={edge_rate})...", flush=True)
                _run_coro_sync(
                    _generate_speech_edge_async(text, output_path, voice=edge_voice, rate=edge_rate, pitch=edge_pitch)
                )

    dur = probe_duration(output_path)
    if should_tighten:
        dur = tighten_audio_dead_air(output_path)
    if not (output_path.parent / "WORD_BOUNDARIES.json").exists():
        extract_word_boundaries_whisper(output_path)
    if not (output_path.parent / "WORD_BOUNDARIES.json").exists():
        extract_word_boundaries_acoustic(output_path, text)
    return dur


def _write_stereo_wav(path: Path, sig_l: Any, sig_r: Any, sample_rate: int = 48000) -> Path:
    import numpy as np
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max(float(np.max(np.abs(sig_l))), float(np.max(np.abs(sig_r))), 1e-8)
    scale = min(1.0, 0.72 / peak)
    pcm = np.stack([sig_l * scale, sig_r * scale], axis=1)
    pcm_i16 = np.clip(pcm * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_i16.tobytes())
    return path


def ensure_editorial_sfx_palette(assets_dir: Optional[Path] = None) -> Dict[str, Path]:
    """
    Garantiza una paleta de SFX diegéticos sutiles en audio_assets/ junto al boom/riser existentes:
    - SFX_PAPER_FLIP.wav (~0.32s): roce táctil de papel archival.
    - SFX_HIGHLIGHTER_SWIPE.wav (~0.45s): barrido de marcador fieltro sobre papel.
    - SFX_TECH_CLICK.wav (~0.12s): clic mecánico de relé / obturador.
    """
    import numpy as np

    out_dir = Path(assets_dir) if assets_dir else DEFAULT_ASSETS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    sr = 48000
    rng = np.random.default_rng(seed=2026)

    paper_wav = out_dir / "SFX_PAPER_FLIP.wav"
    if not (paper_wav.exists() and paper_wav.stat().st_size > 1000):
        dur = 0.32
        n = int(round(dur * sr))
        t = np.linspace(0.0, dur, n, endpoint=False)
        noise = rng.normal(0.0, 1.0, n)
        # Paso-banda simple por diferencia de medias móviles para textura de fibra de papel
        k_short = np.ones(6) / 6.0
        k_long = np.ones(48) / 48.0
        bp = np.convolve(noise, k_short, mode="same") - np.convolve(noise, k_long, mode="same")
        env = np.sin(np.pi * np.clip(t / dur, 0.0, 1.0)) ** 1.4 * np.exp(-5.0 * np.maximum(0.0, t - 0.07))
        thump = 0.18 * np.sin(2 * np.pi * 135.0 * t) * np.exp(-32.0 * np.abs(t - 0.06))
        sig_l = bp * env * 0.75 + thump
        sig_r = np.roll(bp, 11) * env * 0.75 + thump
        _write_stereo_wav(paper_wav, sig_l, sig_r, sr)

    highlighter_wav = out_dir / "SFX_HIGHLIGHTER_SWIPE.wav"
    if not (highlighter_wav.exists() and highlighter_wav.stat().st_size > 1000):
        dur = 0.45
        n = int(round(dur * sr))
        t = np.linspace(0.0, dur, n, endpoint=False)
        noise = rng.normal(0.0, 1.0, n)
        felt = np.convolve(noise, np.ones(14) / 14.0, mode="same") - np.convolve(noise, np.ones(70) / 70.0, mode="same")
        env = np.sin(np.pi * np.clip(t / dur, 0.0, 1.0)) ** 1.15
        sweep = 0.22 * np.sin(2 * np.pi * (420.0 + 360.0 * (t / dur)) * t) * env
        sig_l = (felt * 0.65 * env) + sweep
        sig_r = (np.roll(felt, 19) * 0.65 * env) + sweep * 0.92
        _write_stereo_wav(highlighter_wav, sig_l, sig_r, sr)

    click_wav = out_dir / "SFX_TECH_CLICK.wav"
    if not (click_wav.exists() and click_wav.stat().st_size > 1000):
        dur = 0.12
        n = int(round(dur * sr))
        t = np.linspace(0.0, dur, n, endpoint=False)
        impulse = (
            0.55 * np.sin(2 * np.pi * 1650.0 * t) * np.exp(-65.0 * t)
            + 0.35 * np.sin(2 * np.pi * 420.0 * t) * np.exp(-42.0 * t)
            + 0.20 * rng.normal(0.0, 1.0, n) * np.exp(-90.0 * t)
        )
        _write_stereo_wav(click_wav, impulse, impulse * 0.96, sr)

    return {
        "boom": out_dir / "SFX_DARK_BOOM.wav",
        "riser": out_dir / "SFX_RISER_LOW.wav",
        "paper": paper_wav,
        "highlighter": highlighter_wav,
        "click": click_wav,
    }


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
