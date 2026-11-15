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
import re
import shutil
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

# ==============================================================================
# Catálogo Maestro de Soundtracks Virales Epidemic Sound por Categoría
# Seleccionados para máxima retención, ritmo bailable/tensionante y empoderamiento
# ==============================================================================
GENRE_SOUNDTRACK_CATALOG = {
    "G3_IA_HARDWARE": {
        "title": "STYLE",
        "artist": "Ballpoint",
        "bpm": 118,
        "style": "Dark Synth / Modern Viral Empowerment Beat (Washing Machine / Tech Energy)",
        "id": "03e71f7f-ad6f-4845-9fbd-9fce110cfa5e",
        "bass_file": "G3_TECH_STYLE_BASS.mp3",
        "inst_file": "G3_TECH_STYLE_INSTRUMENTS.mp3"
    },
    "G2_CIBERATAQUES": {
        "title": "Deadlock",
        "artist": "Lennon Hutton",
        "bpm": 115,
        "style": "Cyberpunk Dark Electro Pulse / Urgent Hacker Investigation",
        "id": "db0a04d3-c17d-4601-8e8a-454ef7698454",
        "bass_file": "G2_CYBER_DEADLOCK_BASS.mp3",
        "inst_file": "G2_CYBER_DEADLOCK_INSTRUMENTS.mp3"
    },
    "G1_AVIACION": {
        "title": "Trace",
        "artist": "Lennon Hutton",
        "bpm": 156,
        "style": "Cinematic Action Thriller / High Altitude Tension Pulse",
        "id": "3c1ad0de-8456-4677-86fe-bb3153624738",
        "bass_file": "G1_AVIATION_TRACE_BASS.mp3",
        "inst_file": "G1_AVIATION_TRACE_INSTRUMENTS.mp3"
    },
    "G4_ESPACIO": {
        "title": "Mindscape",
        "artist": "Lennon Hutton",
        "bpm": 108,
        "style": "Cosmic Atmospheric Synthwave / Futuristic Orbit Drive",
        "id": "4cb08b97-fa28-4f38-9b9c-3e71a2d98b5f",
        "bass_file": "G4_SPACE_MINDSCAPE_BASS.mp3",
        "inst_file": "G4_SPACE_MINDSCAPE_INSTRUMENTS.mp3"
    }
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


def get_genre_soundtrack(genre: str, target_dir: Optional[Path] = None) -> Tuple[Path, Path]:
    """
    Devuelve las rutas locales de los stems (BASS, INSTRUMENTS) oficiales de Epidemic Sound
    para el género de noticia seleccionado. Si no existen localmente, intenta descargarlos vía MCP.
    """
    assets_dir = target_dir or DEFAULT_ASSETS_DIR
    genre_upper = (genre or "G1").upper()

    # Selección de categoría musical
    if any(k in genre_upper for k in ["G1", "AVIACION", "AVIACIÓN", "MAYDAY", "VUELO", "AEREO", "AÉREO", "AVION", "AVIÓN", "ACCIDENTE"]):
        key = "G1_AVIACION"
    elif any(k in genre_upper for k in ["G2", "CIBER", "HACKER", "CYBER", "RANSOMWARE"]):
        key = "G2_CIBERATAQUES"
    elif any(k in genre_upper for k in ["G4", "ESPACIO", "NASA", "ORBITA", "ÓRBITA", "CIENCIA", "STARSHIP"]):
        key = "G4_ESPACIO"
    elif any(k in genre_upper for k in ["G3", "ROBOTICA", "ROBÓTICA", "HARDWARE", "CHIP", "SEMICONDUCTOR"]) or re.search(r"\bIA\b|\bAI\b", genre_upper):
        key = "G3_IA_HARDWARE"
    else:
        key = "G3_IA_HARDWARE"

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

    # Limpiar marcas previas para evitar desincronización si cambia el motor de voz
    for stale_name in ("SENTENCE_BOUNDARIES.json", "WORD_BOUNDARIES.json"):
        stale_bounds = output_path.parent / stale_name
        if stale_bounds.exists():
            try:
                stale_bounds.unlink()
            except Exception:
                pass

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


async def _generate_speech_edge_async(text: str, output_path: Path, voice: str = "es-MX-JorgeNeural") -> bool:
    try:
        import edge_tts
        # Capturar WordBoundary reales además de reconstruir SentenceBoundary
        communicate = edge_tts.Communicate(text, voice, rate="+12%", pitch="+1Hz", boundary="WordBoundary")
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

        output_path.parent.mkdir(parents=True, exist_ok=True)
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
        print(f"[AUDIO-TTS] ✅ Locución Edge-TTS completada con marcas ({len(word_entries)} palabras): {output_path.name} ({dur:.2f} s)", flush=True)
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


def generate_speech(
    text: str,
    output_path: Path,
    voice_gemini: str = "Fenrir",
    voice_edge: str = "es-MX-JorgeNeural",
    style: Optional[str] = None,
    tighten: bool = True
) -> float:
    """Genera locución intentando primero Gemini TTS y con fallback automático a Edge-TTS."""
    # 1. Intentar Gemini Flash TTS
    ok = generate_speech_gemini(text, output_path, voice=voice_gemini, style=style)
    if not ok:
        print("[AUDIO-TTS] Activando fallback gratuito Edge-TTS...", flush=True)
        asyncio.run(_generate_speech_edge_async(text, output_path, voice=voice_edge))

    dur = probe_duration(output_path)
    if tighten:
        dur = tighten_audio_dead_air(output_path)
    if not (output_path.parent / "WORD_BOUNDARIES.json").exists():
        extract_word_boundaries_whisper(output_path)
    return dur


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
