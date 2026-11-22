#!/usr/bin/env python3
"""
MOTOR DE VOZ ACTORAL + DISEÑO SONORO GENJUTSU + MASTERIZACIÓN EBU R128
Genera locución bi-fase para Candidato C (Gemini 3.8 Flash TTS con fallback Edge-TTS),
diseña y mezcla efectos de ilusión óptica Genjutsu (riser + fractura + sub-bass boom +
cama atmosférica con sidechain ducking) y masteriza a -14.0 LUFS / -1.0 dBTP en 2 pasadas.
"""

import argparse
import asyncio
import base64
import io
import json
import os
import re
import subprocess
import sys
import urllib.request
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PERSONAJE_HIPERREALISTA.tools.motor_personaje import (  # noqa: E402
    PROJECT_ROOT,
    VIDEO_DIR,
    load_character_config,
)
from PERSONAJE_HIPERREALISTA.tools.studio_api_client import ElevenLabsStudioClient  # noqa: E402


def probe_audio_duration(path: Path) -> float:
    """Devuelve la duración exacta en segundos de un archivo de audio con ffprobe."""
    if not path.exists():
        return 0.0
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=15).decode().strip()
        return max(0.0, float(out))
    except Exception:
        return 0.0


def parse_two_act_script(script_text: str) -> Tuple[str, str]:
    """
    Divide el guion en Acto 1 (normal) y Acto 2 (Genjutsu) usando el marcador [GENJUTSU].
    Si no existe marcador y hay varias oraciones, divide en el corte de oración cercano a la mitad.
    """
    cleaned = re.sub(r"\s+", " ", (script_text or "").strip())
    if not cleaned:
        raise ValueError("El guion está vacío; proporciona texto para locución.")

    marker = re.search(r"\[genjutsu\]", cleaned, flags=re.IGNORECASE)
    if marker:
        act1 = cleaned[: marker.start()].strip()
        act2 = cleaned[marker.end() :].strip()
        if not act1 and act2:
            return act2, ""
        return act1, act2

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
    if len(sentences) >= 2:
        total_words = len(cleaned.split())
        acc = 0
        split_idx = 1
        best_diff = total_words
        for idx in range(1, len(sentences)):
            acc += len(sentences[idx - 1].split())
            diff = abs(acc - total_words / 2.0)
            if diff < best_diff:
                best_diff = diff
                split_idx = idx
        return " ".join(sentences[:split_idx]), " ".join(sentences[split_idx:])

    return cleaned, ""


def normalize_audio_to_pcm_wav(
    src_path: Path,
    dst_wav: Path,
    sample_rate: int = 48000,
    channels: int = 2,
    trim_silence: bool = True,
) -> Path:
    """Convierte cualquier entrada de audio en PCM WAV limpio (48kHz estéreo) sin clics."""
    if not src_path.exists():
        raise FileNotFoundError(f"Archivo de audio no encontrado: {src_path}")
    dst_wav.parent.mkdir(parents=True, exist_ok=True)

    filters = [
        "highpass=f=75",
        "equalizer=f=150:width_type=q:w=1.0:g=1.2",
        "equalizer=f=3200:width_type=q:w=1.2:g=1.5",
        "equalizer=f=6800:width_type=q:w=1.8:g=-1.2",
    ]
    if trim_silence:
        filters.append(
            "silenceremove=start_periods=1:start_duration=0.04:start_threshold=-45dB,"
            "areverse,silenceremove=start_periods=1:start_duration=0.04:start_threshold=-45dB,areverse"
        )
    filters.append("afade=t=in:st=0:d=0.008")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src_path),
        "-af",
        ",".join(filters),
        "-ar",
        str(sample_rate),
        "-ac",
        str(channels),
        "-c:a",
        "pcm_s16le",
        str(dst_wav),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Error normalizando audio ({src_path.name}): {proc.stderr[-400:]}")
    return dst_wav


def _wrap_pcm_l16_wav(raw: bytes, mime_type: str = "") -> bytes:
    """Envuelve PCM crudo L16 en cabecera WAV si la respuesta no contiene RIFF."""
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


def _synthesize_gemini_tts(
    text: str,
    out_wav: Path,
    voice: str,
    style: str,
    models: List[str],
) -> bool:
    """Genera audio hablado vía Gemini TTS REST API soportando esquemas 3.8 y 3.1/2.5 + PCM crudo."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or not text.strip():
        return False

    for model in models:
        if "3.8" in model:
            body: Dict[str, Any] = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": text,
                                "speech_metadata": {"style": style},
                            }
                        ],
                    }
                ],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {"voiceConfig": {"voice": voice}},
                },
            }
        else:
            prompt_text = f"{style}\n\nLee exactamente el siguiente texto con voz humana natural:\n\n{text}" if style else text
            body = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt_text}],
                    }
                ],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
                },
            }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.load(resp)
            parts = data["candidates"][0]["content"]["parts"]
            inline = next(p["inlineData"] for p in parts if "inlineData" in p)
            raw = base64.b64decode(inline["data"])
            if len(raw) < 1024:
                continue
            raw_wav = _wrap_pcm_l16_wav(raw, inline.get("mimeType", ""))
            raw_path = out_wav.with_suffix(".gemini_raw.wav")
            raw_path.write_bytes(raw_wav)
            normalize_audio_to_pcm_wav(raw_path, out_wav)
            raw_path.unlink(missing_ok=True)
            if probe_audio_duration(out_wav) >= 0.35:
                return True
        except Exception as exc:
            print(f"[AUDIO-PERSONAJE] Aviso con {model}: {exc}", flush=True)
    return False


async def _synthesize_edge_tts_async(
    text: str,
    out_wav: Path,
    voice: str,
    rate: str,
    pitch: str,
) -> Tuple[bool, List[Dict[str, Any]]]:
    """Fallback Edge-TTS capturando marcas reales WordBoundary."""
    try:
        import edge_tts

        communicate = edge_tts.Communicate(
            text, voice, rate=rate, pitch=pitch, boundary="WordBoundary"
        )
        raw_mp3 = out_wav.with_suffix(".edge.mp3")
        audio_bytes = bytearray()
        words: List[Dict[str, Any]] = []
        async for chunk in communicate.stream():
            ctype = chunk.get("type")
            if ctype == "audio":
                audio_bytes.extend(chunk["data"])
            elif ctype == "WordBoundary":
                w_start = round(chunk.get("offset", 0) / 10_000_000, 3)
                w_end = round(
                    (chunk.get("offset", 0) + chunk.get("duration", 0)) / 10_000_000, 3
                )
                words.append(
                    {
                        "text": str(chunk.get("text", "")),
                        "start": w_start,
                        "end": max(w_start + 0.05, w_end),
                    }
                )
        if len(audio_bytes) < 512:
            return False, []
        raw_mp3.write_bytes(audio_bytes)
        normalize_audio_to_pcm_wav(raw_mp3, out_wav)
        raw_mp3.unlink(missing_ok=True)
        return probe_audio_duration(out_wav) >= 0.35, words
    except Exception as exc:
        print(f"[AUDIO-PERSONAJE] Aviso Edge-TTS: {exc}", flush=True)
        return False, []


def _run_async(coro: Any) -> Any:
    """Ejecuta una corrutina de forma segura incluso si ya existe un event loop activo."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def _detect_speech_blocks_ffmpeg(wav_path: Path, total_dur: float) -> List[Tuple[float, float]]:
    """Detecta bloques activos de voz mediante silencedetect para alinear subtítulos."""
    cmd = [
        "ffmpeg",
        "-i",
        str(wav_path),
        "-af",
        "silencedetect=noise=-32dB:d=0.18",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    silences: List[Tuple[float, float]] = []
    cur_start: Optional[float] = None
    for line in proc.stderr.splitlines():
        m_start = re.search(r"silence_start:\s*([0-9.]+)", line)
        m_end = re.search(r"silence_end:\s*([0-9.]+)", line)
        if m_start:
            cur_start = float(m_start.group(1))
        elif m_end and cur_start is not None:
            silences.append((cur_start, float(m_end.group(1))))
            cur_start = None
    if cur_start is not None and cur_start < total_dur:
        silences.append((cur_start, total_dur))

    blocks: List[Tuple[float, float]] = []
    pos = 0.0
    for s_start, s_end in silences:
        if s_start - pos >= 0.12:
            blocks.append((round(pos, 3), round(s_start, 3)))
        pos = max(pos, s_end)
    if total_dur - pos >= 0.12:
        blocks.append((round(pos, 3), round(total_dur, 3)))
    return blocks or [(0.0, round(total_dur, 3))]


def _concat_wav_with_pauses(
    segments: List[Tuple[Optional[Path], float]],
    out_wav: Path,
    sample_rate: int = 48000,
    channels: int = 2,
) -> Path:
    """Concatena segmentos WAV y pausas de silencio exactas en un único PCM WAV."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    filter_parts: List[str] = []
    concat_inputs: List[str] = []
    in_idx = 0

    for seg_path, dur_or_pad in segments:
        if seg_path is not None:
            cmd.extend(["-i", str(seg_path)])
            filter_parts.append(
                f"[{in_idx}:a]aresample={sample_rate},aformat=sample_fmts=s16:channel_layouts=stereo[s{in_idx}]"
            )
            concat_inputs.append(f"[s{in_idx}]")
            in_idx += 1
        elif dur_or_pad > 0.005:
            cmd.extend(
                [
                    "-f",
                    "lavfi",
                    "-t",
                    f"{dur_or_pad:.3f}",
                    "-i",
                    f"anullsrc=r={sample_rate}:cl=stereo",
                ]
            )
            filter_parts.append(f"[{in_idx}:a]aformat=sample_fmts=s16:channel_layouts=stereo[s{in_idx}]")
            concat_inputs.append(f"[s{in_idx}]")
            in_idx += 1

    if not concat_inputs:
        raise ValueError("No hay segmentos de audio válidos para concatenar.")

    filter_parts.append(
        f"{''.join(concat_inputs)}concat=n={len(concat_inputs)}:v=0:a=1[outa]"
    )
    cmd.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[outa]",
            "-ar",
            str(sample_rate),
            "-ac",
            str(channels),
            "-c:a",
            "pcm_s16le",
            str(out_wav),
        ]
    )
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Error concatenando pista de voz: {proc.stderr[-400:]}")
    return out_wav


def _build_word_boundaries_from_acts(
    act_entries: List[Tuple[int, str, float, float, List[Dict[str, Any]], Optional[List[Tuple[float, float]]]]],
) -> List[Dict[str, Any]]:
    """
    Combina marcas WordBoundary reales (si las dio Edge-TTS) o las distribuye
    sobre los bloques acústicos reales de voz de cada acto, preservando el índice de acto.
    """
    all_words: List[Dict[str, Any]] = []
    for act_num, text, offset, dur, raw_words, speech_blocks in act_entries:
        if not text.strip():
            continue
        if raw_words:
            for w in raw_words:
                all_words.append(
                    {
                        "act": act_num,
                        "text": w["text"],
                        "start": round(offset + float(w["start"]), 3),
                        "end": round(offset + float(w["end"]), 3),
                    }
                )
            continue

        tokens = text.split()
        if not tokens:
            continue

        blocks = speech_blocks or [(0.0, dur)]
        total_speech_dur = sum(max(0.05, b_end - b_start) for b_start, b_end in blocks)
        weights = [
            max(2.0, float(len(re.sub(r"[^\w]", "", t))) + (1.8 if t.endswith((".", "?", "!")) else 0.0))
            for t in tokens
        ]
        total_w = sum(weights)

        # Mapear tiempo acumulado de habla dentro de los bloques activos reales (saltando pausas)
        cum_s = 0.0
        for tok, w in zip(tokens, weights):
            span_speech = total_speech_dur * (w / total_w)
            w_start_rel = _map_speech_pos_to_timeline(cum_s, blocks)
            w_end_rel = _map_speech_pos_to_timeline(cum_s + span_speech, blocks)
            all_words.append(
                {
                    "act": act_num,
                    "text": tok,
                    "start": round(offset + w_start_rel, 3),
                    "end": round(offset + max(w_start_rel + 0.08, w_end_rel), 3),
                }
            )
            cum_s += span_speech
    return all_words


def _map_speech_pos_to_timeline(pos_in_speech: float, blocks: List[Tuple[float, float]]) -> float:
    """Convierte una posición en tiempo acumulado de habla a tiempo real en el segmento."""
    rem = max(0.0, pos_in_speech)
    for b_start, b_end in blocks:
        span = max(0.05, b_end - b_start)
        if rem <= span:
            return b_start + rem
        rem -= span
    return blocks[-1][1]


def synthesize_actor_speech(
    script_text: str,
    out_dir: Path,
    config: Optional[Dict[str, Any]] = None,
    external_audio_file: Optional[Path] = None,
    prefer_edge: bool = False,
    prefer_elevenlabs: bool = False,
) -> Dict[str, Any]:
    """
    Genera la pista de voz limpia (VOZ_LIMPIA.wav) en 48kHz estéreo, calcula el punto
    exacto del cue Genjutsu y guarda WORD_BOUNDARIES.json en out_dir.
    Soporta cascada ElevenLabs (/with-timestamps) -> Gemini 3.8 Flash TTS -> Edge-TTS.
    """
    cfg = config or load_character_config()
    acfg = cfg["audio"]
    s_cfg = cfg.get("studio_apis", {})
    sample_rate = int(acfg.get("sample_rate", 48000))
    channels = int(acfg.get("channels", 2))
    lead_in = float(acfg.get("lead_in_sec", 0.20))
    gap_sec = float(acfg.get("silence_gap_sec", 0.50))
    tail_pad = float(acfg.get("tail_pad_sec", 0.60))

    out_dir.mkdir(parents=True, exist_ok=True)
    clean_wav = out_dir / "VOZ_LIMPIA.wav"
    act1_text, act2_text = parse_two_act_script(script_text)

    if external_audio_file is not None:
        raw_norm = out_dir / "_ext_norm.wav"
        normalize_audio_to_pcm_wav(Path(external_audio_file), raw_norm, sample_rate, channels)
        dur_ext = probe_audio_duration(raw_norm)
        _concat_wav_with_pauses(
            [(None, lead_in), (raw_norm, 0.0), (None, tail_pad)],
            clean_wav,
            sample_rate,
            channels,
        )
        raw_norm.unlink(missing_ok=True)
        total_dur = probe_audio_duration(clean_wav)
        blocks = _detect_speech_blocks_ffmpeg(clean_wav, total_dur)
        cue_sec = round(lead_in + dur_ext * 0.48, 3)
        if len(blocks) >= 2:
            cue_sec = round((blocks[0][1] + blocks[1][0]) / 2.0, 3)
        words = _build_word_boundaries_from_acts(
            [(1, f"{act1_text} {act2_text}".strip(), lead_in, dur_ext, [], None)]
        )
        (out_dir / "WORD_BOUNDARIES.json").write_text(
            json.dumps(words, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return {
            "voice_wav": str(clean_wav),
            "engine": "external_audio",
            "act1_text": act1_text,
            "act2_text": act2_text,
            "act1_duration_sec": round(cue_sec, 3),
            "act2_duration_sec": round(max(0.0, total_dur - cue_sec), 3),
            "genjutsu_cue_sec": cue_sec,
            "total_duration_sec": round(total_dur, 3),
            "word_boundaries_path": str(out_dir / "WORD_BOUNDARIES.json"),
        }

    models = list(acfg.get("gemini_models", ["gemini-3.8-flash-tts"]))
    gem_voice = str(acfg.get("gemini_voice", "Puck"))
    edge_voice = str(acfg.get("edge_voice", "es-MX-JorgeNeural"))
    el_voice = str(s_cfg.get("elevenlabs_voice_id", "pNInz6obpgDQGcFmaJgB"))
    el_model = str(s_cfg.get("elevenlabs_model_id", "eleven_multilingual_v2"))
    use_el_first = (
        bool(prefer_elevenlabs or s_cfg.get("prefer_elevenlabs", False) or str(acfg.get("tts_primary", "")).lower() == "elevenlabs")
        and not prefer_edge
        and bool(os.getenv("ELEVENLABS_API_KEY", "").strip())
    )
    el_client = ElevenLabsStudioClient(default_voice_id=el_voice, default_model_id=el_model) if use_el_first else None

    def _synth_one(
        text: str,
        tag: str,
        style: str,
        edge_rate: str,
        edge_pitch: str,
        el_settings: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Path, str, List[Dict[str, Any]]]:
        seg_wav = out_dir / f"_seg_{tag}.wav"
        if el_client is not None and el_client.is_configured():
            ok_el, el_words = el_client.synthesize_with_timestamps(
                text,
                seg_wav,
                voice_id=el_voice,
                model_id=el_model,
                voice_settings=el_settings,
                sample_rate=sample_rate,
                channels=channels,
            )
            if ok_el:
                return seg_wav, f"elevenlabs:{el_voice}", el_words
        if not prefer_edge and _synthesize_gemini_tts(text, seg_wav, gem_voice, style, models):
            return seg_wav, f"gemini:{gem_voice}", []
        ok_edge, w_bounds = _run_async(
            _synthesize_edge_tts_async(text, seg_wav, edge_voice, edge_rate, edge_pitch)
        )
        if not ok_edge:
            raise RuntimeError(
                f"No se pudo sintetizar la locución ({tag}) ni con ElevenLabs/Gemini TTS ni con Edge-TTS."
            )
        return seg_wav, f"edge:{edge_voice}", w_bounds

    seg1_wav, eng1, w1 = _synth_one(
        act1_text,
        "act1",
        str(acfg.get("style_act1", "")),
        str(acfg.get("edge_rate_act1", "+8%")),
        str(acfg.get("edge_pitch_act1", "+1Hz")),
        s_cfg.get("elevenlabs_act1_settings"),
    )
    dur1 = probe_audio_duration(seg1_wav)
    blocks1 = _detect_speech_blocks_ffmpeg(seg1_wav, dur1) if not w1 else None

    segments: List[Tuple[Optional[Path], float]] = [(None, lead_in), (seg1_wav, 0.0)]
    act_entries: List[Tuple[int, str, float, float, List[Dict[str, Any]], Optional[List[Tuple[float, float]]]]] = [
        (1, act1_text, lead_in, dur1, w1, blocks1)
    ]

    seg2_wav: Optional[Path] = None
    dur2 = 0.0
    if act2_text:
        seg2_wav, _, w2 = _synth_one(
            act2_text,
            "act2",
            str(acfg.get("style_act2", "")),
            str(acfg.get("edge_rate_act2", "-4%")),
            str(acfg.get("edge_pitch_act2", "-6Hz")),
            s_cfg.get("elevenlabs_act2_settings"),
        )
        dur2 = probe_audio_duration(seg2_wav)
        blocks2 = _detect_speech_blocks_ffmpeg(seg2_wav, dur2) if not w2 else None
        segments.append((None, gap_sec))
        segments.append((seg2_wav, 0.0))
        act_entries.append((2, act2_text, lead_in + dur1 + gap_sec, dur2, w2, blocks2))
        cue_sec = round(lead_in + dur1 + gap_sec * 0.5, 3)
    else:
        cue_sec = round(lead_in + dur1 * 0.45, 3)

    segments.append((None, tail_pad))
    _concat_wav_with_pauses(segments, clean_wav, sample_rate, channels)

    seg1_wav.unlink(missing_ok=True)
    if seg2_wav is not None:
        seg2_wav.unlink(missing_ok=True)

    total_dur = probe_audio_duration(clean_wav)
    words = _build_word_boundaries_from_acts(act_entries)
    wb_path = out_dir / "WORD_BOUNDARIES.json"
    wb_path.write_text(json.dumps(words, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "voice_wav": str(clean_wav),
        "engine": eng1,
        "act1_text": act1_text,
        "act2_text": act2_text,
        "act1_duration_sec": round(dur1, 3),
        "act2_duration_sec": round(dur2, 3),
        "genjutsu_cue_sec": cue_sec,
        "total_duration_sec": round(total_dur, 3),
        "word_boundaries_path": str(wb_path),
    }


def synthesize_genjutsu_illusion_sfx(
    out_wav: Path,
    duration_sec: float = 1.25,
    sample_rate: int = 48000,
) -> Path:
    """
    Sintetiza un efecto sonoro cinematográfico de fractura Genjutsu (elevación inversa +
    resonancia cristalina disonante descendente + pulso sub-grave) en 48kHz estéreo PCM.
    """
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    n_samples = int(round(duration_sec * sample_rate))
    t = np.linspace(0.0, duration_sec, n_samples, endpoint=False, dtype=np.float64)

    # Momento de fractura óptica en t_hit = 0.28s
    t_hit = min(0.28, duration_sec * 0.25)
    pre_mask = t < t_hit
    post_t = np.maximum(0.0, t - t_hit)

    # 1. Pre-swell invertido (succión óptica antes de romper realidad)
    pre_env = np.where(pre_mask, (t / max(1e-6, t_hit)) ** 2.4, 0.0)
    pre_sweep = np.sin(2.0 * np.pi * (180.0 + 950.0 * (t / max(1e-6, t_hit)) ** 2) * t) * pre_env * 0.35

    # 2. Resonancia cristalina ilusoria con caída de pitch (estilo activación ocular live-action)
    post_env = np.where(t >= t_hit, np.exp(-post_t * 3.1), 0.0)
    freq_drop = 1.0 - 0.14 * (1.0 - np.exp(-post_t * 4.0))
    chime_l = (
        0.42 * np.sin(2.0 * np.pi * 1046.5 * freq_drop * post_t)
        + 0.30 * np.sin(2.0 * np.pi * 1567.98 * freq_drop * post_t + 0.4)
        + 0.22 * np.sin(2.0 * np.pi * 2217.46 * freq_drop * post_t + 0.9)
    ) * post_env
    chime_r = (
        0.42 * np.sin(2.0 * np.pi * 1053.0 * freq_drop * post_t + 0.25)
        + 0.30 * np.sin(2.0 * np.pi * 1559.0 * freq_drop * post_t + 0.7)
        + 0.22 * np.sin(2.0 * np.pi * 2231.0 * freq_drop * post_t + 1.2)
    ) * post_env

    # 3. Pulso sub-bass de impacto en t_hit (88 Hz -> 38 Hz)
    sub_env = np.where(t >= t_hit, np.exp(-post_t * 4.5), 0.0)
    sub_phase = 2.0 * np.pi * (38.0 * post_t + 50.0 * (1.0 - np.exp(-post_t * 7.0)) / 7.0)
    sub_hit = 0.70 * np.sin(sub_phase) * sub_env

    sig_l = pre_sweep + chime_l + sub_hit
    sig_r = pre_sweep + chime_r + sub_hit

    # Fade suave en bordes (10 ms) para evitar clics
    fade_n = min(int(0.01 * sample_rate), n_samples // 10)
    if fade_n > 0:
        ramp_in = np.linspace(0.0, 1.0, fade_n)
        ramp_out = np.linspace(1.0, 0.0, fade_n)
        sig_l[:fade_n] *= ramp_in
        sig_r[:fade_n] *= ramp_in
        sig_l[-fade_n:] *= ramp_out
        sig_r[-fade_n:] *= ramp_out

    peak = max(float(np.max(np.abs(sig_l))), float(np.max(np.abs(sig_r))), 1e-8)
    scale = 0.78 / peak
    pcm = np.stack([sig_l * scale, sig_r * scale], axis=1)
    pcm_i16 = np.clip(pcm * 32767.0, -32768, 32767).astype(np.int16)

    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_i16.tobytes())
    return out_wav


def _find_first_asset(candidates: List[str], search_dirs: List[Path]) -> Optional[Path]:
    for d in search_dirs:
        for name in candidates:
            p = d / name
            if p.exists() and p.is_file():
                return p
    return None


def resolve_sfx_assets(config: Optional[Dict[str, Any]] = None) -> Dict[str, Optional[Path]]:
    """Localiza o genera los stems SFX y cama musical desde rutas reales del repositorio."""
    cfg = config or load_character_config()
    acfg = cfg["audio"]
    sfx_dirs = [(PROJECT_ROOT / d).resolve() for d in acfg.get("sfx_search_dirs", [])]
    music_dirs = [(PROJECT_ROOT / d).resolve() for d in acfg.get("music_search_dirs", [])]

    genjutsu_sfx = VIDEO_DIR / "assets" / "SFX_GENJUTSU_FRACTURE.wav"
    if not genjutsu_sfx.exists():
        synthesize_genjutsu_illusion_sfx(genjutsu_sfx, sample_rate=int(acfg.get("sample_rate", 48000)))

    return {
        "genjutsu_fracture": genjutsu_sfx,
        "riser": _find_first_asset(["SFX_RISER_LOW.wav"], sfx_dirs),
        "boom": _find_first_asset(["SFX_DARK_BOOM.wav", "SFX_FLOODGATE_BOOM.wav"], sfx_dirs),
        "wing_flap": _find_first_asset(["FOLEY_COAT_FLAP.wav", "SFX_WHOOSH_CINEMATIC.wav"], sfx_dirs),
        "music_bed": _find_first_asset(list(acfg.get("music_bed_candidates", [])), music_dirs),
    }


def measure_audio_loudness(audio_path: Path) -> Dict[str, float]:
    """Mide LUFS integrado, True Peak y LRA con el filtro loudnorm de FFmpeg."""
    cmd = [
        "ffmpeg",
        "-i",
        str(audio_path),
        "-af",
        "loudnorm=I=-14.0:TP=-1.0:LRA=7.0:print_format=json",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Error midiendo sonoridad de {audio_path}: {proc.stderr[-300:]}")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", proc.stderr, flags=re.DOTALL)
    if not m:
        raise RuntimeError(f"No se pudo leer el JSON de loudnorm para {audio_path}.")
    raw = json.loads(m.group(0))
    return {
        "input_i": float(raw["input_i"]),
        "input_tp": float(raw["input_tp"]),
        "input_lra": float(raw["input_lra"]),
        "input_thresh": float(raw["input_thresh"]),
        "target_offset": float(raw.get("target_offset", 0.0)),
    }


def mix_genjutsu_soundscape(
    voice_wav: Path,
    out_master_wav: Path,
    cue_sec: float,
    config: Optional[Dict[str, Any]] = None,
    include_music: bool = True,
) -> Dict[str, Any]:
    """
    Mezcla VOZ_LIMPIA.wav con SFX Genjutsu (riser + fractura + boom + aleteo de cuervo)
    y cama musical oscura opcional con sidechain ducking, masterizado en 2 pasadas a -14.0 LUFS.
    """
    cfg = config or load_character_config()
    acfg = cfg["audio"]
    sr = int(acfg.get("sample_rate", 48000))
    target_i = float(acfg.get("target_lufs", -14.0))
    target_tp = float(acfg.get("target_tp", -1.0))
    target_lra = float(acfg.get("target_lra", 7.0))

    voice_dur = probe_audio_duration(voice_wav)
    if voice_dur <= 0.2:
        raise ValueError(f"La pista de voz está vacía o corrupta: {voice_wav}")

    assets = resolve_sfx_assets(cfg)
    out_master_wav.parent.mkdir(parents=True, exist_ok=True)
    pre_master = out_master_wav.with_suffix(".pre_loudnorm.wav")

    cmd = ["ffmpeg", "-y", "-i", str(voice_wav)]
    music_path = assets.get("music_bed") if include_music else None
    use_music = bool(music_path and music_path.exists())
    if use_music:
        filter_lines: List[str] = [
            f"[0:a]aresample={sr},aformat=sample_fmts=fltp:channel_layouts=stereo,asplit=2[voice_mix][voice_sc]"
        ]
    else:
        filter_lines = [
            f"[0:a]aresample={sr},aformat=sample_fmts=fltp:channel_layouts=stereo[voice_mix]"
        ]
    mix_labels: List[str] = ["[voice_mix]"]
    idx = 1

    def _add_sfx(path: Optional[Path], start_sec: float, vol: float, tag: str, trim_sec: Optional[float] = None, fade_in: float = 0.01) -> None:
        nonlocal idx
        if path is None or not path.exists():
            return
        cmd.extend(["-i", str(path)])
        delay_ms = max(0, int(round(start_sec * 1000)))
        steps = [f"aresample={sr}", "aformat=sample_fmts=fltp:channel_layouts=stereo"]
        if trim_sec is not None:
            steps.append(f"atrim=0:{trim_sec:.3f},asetpts=PTS-STARTPTS")
        if fade_in > 0:
            steps.append(f"afade=t=in:st=0:d={fade_in:.3f}")
        steps.append(f"volume={vol:.3f}")
        steps.append(f"adelay={delay_ms}|{delay_ms}")
        filter_lines.append(f"[{idx}:a]{','.join(steps)}[{tag}]")
        mix_labels.append(f"[{tag}]")
        idx += 1

    # Riser previo terminando sobre cue_sec
    riser_path = assets.get("riser")
    if riser_path and riser_path.exists():
        riser_dur = min(1.4, probe_audio_duration(riser_path))
        if riser_dur > 0.2:
            riser_start = max(0.0, cue_sec - riser_dur * 0.88)
            cmd.extend(["-i", str(riser_path)])
            delay_ms = int(round(riser_start * 1000))
            filter_lines.append(
                f"[{idx}:a]aresample={sr},aformat=sample_fmts=fltp:channel_layouts=stereo,"
                f"atrim=0:{riser_dur:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.35,"
                f"afade=t=out:st={max(0.05, riser_dur - 0.15):.3f}:d=0.15,"
                f"volume=0.30,adelay={delay_ms}|{delay_ms}[sfx_riser]"
            )
            mix_labels.append("[sfx_riser]")
            idx += 1

    # Fractura óptica Genjutsu + Sub-Bass Boom + Aleteo sutil de plumas
    _add_sfx(assets.get("genjutsu_fracture"), max(0.0, cue_sec - 0.25), 0.42, "sfx_frac", trim_sec=1.25)
    _add_sfx(assets.get("boom"), max(0.0, cue_sec - 0.03), 0.34, "sfx_boom", trim_sec=1.80)
    _add_sfx(assets.get("wing_flap"), max(0.0, cue_sec + 0.18), 0.24, "sfx_wing", trim_sec=0.90)

    # Cama musical oscura con sidechain ducking bajo la voz
    if use_music and music_path is not None:
        cmd.extend(["-stream_loop", "-1", "-i", str(music_path)])
        fade_out_st = max(0.2, voice_dur - 0.65)
        filter_lines.append(
            f"[{idx}:a]aresample={sr},aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"atrim=0:{voice_dur:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=0.40,afade=t=out:st={fade_out_st:.3f}:d=0.60,"
            f"volume=0.18[mus_raw];"
            f"[mus_raw][voice_sc]sidechaincompress=threshold=0.03:ratio=4.5:attack=15:release=250[mus_duck]"
        )
        mix_labels.append("[mus_duck]")
        idx += 1

    filter_lines.append(
        f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:duration=first:normalize=0:dropout_transition=0,"
        f"alimiter=limit=0.95[premaster]"
    )

    cmd.extend(
        [
            "-filter_complex",
            ";".join(filter_lines),
            "-map",
            "[premaster]",
            "-t",
            f"{voice_dur:.3f}",
            "-ar",
            str(sr),
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(pre_master),
        ]
    )
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Error mezclando audio Genjutsu: {proc.stderr[-500:]}")

    # Pasada 1 & 2 EBU R128 linear=true
    stats_p1 = measure_audio_loudness(pre_master)
    ln_filter = (
        f"loudnorm=I={target_i}:TP={target_tp}:LRA={target_lra}:"
        f"measured_I={stats_p1['input_i']}:measured_TP={stats_p1['input_tp']}:"
        f"measured_LRA={stats_p1['input_lra']}:measured_thresh={stats_p1['input_thresh']}:"
        f"offset={stats_p1['target_offset']}:linear=true"
    )
    cmd_p2 = [
        "ffmpeg",
        "-y",
        "-i",
        str(pre_master),
        "-af",
        ln_filter,
        "-ar",
        str(sr),
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        str(out_master_wav),
    ]
    proc2 = subprocess.run(cmd_p2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    pre_master.unlink(missing_ok=True)
    if proc2.returncode != 0:
        raise RuntimeError(f"Error en loudnorm 2da pasada: {proc2.stderr[-500:]}")

    final_stats = measure_audio_loudness(out_master_wav)
    return {
        "master_wav": str(out_master_wav),
        "duration_sec": round(probe_audio_duration(out_master_wav), 3),
        "integrated_lufs": final_stats["input_i"],
        "true_peak_dbtp": final_stats["input_tp"],
        "lra_lu": final_stats["input_lra"],
        "cue_sec": round(cue_sec, 3),
        "assets_used": {k: str(v) if v else None for k, v in assets.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generador de Voz + SFX Genjutsu para Candidato C")
    parser.add_argument("--script", type=str, default=None, help="Guion (soporta marcador [GENJUTSU])")
    parser.add_argument("--audio-file", type=str, default=None, help="Audio externo opcional")
    parser.add_argument("--out-dir", type=str, default=str(VIDEO_DIR / "test_audio"))
    parser.add_argument("--prefer-edge", action="store_true", help="Forzar Edge-TTS en lugar de Gemini/ElevenLabs")
    parser.add_argument("--prefer-elevenlabs", action="store_true", help="Priorizar ElevenLabs TTS con timestamps")
    parser.add_argument("--no-music", action="store_true", help="Mezclar sin cama musical de fondo")
    args = parser.parse_args()

    cfg = load_character_config()
    script = args.script or cfg["default_test_script"]
    out_dir = Path(args.out_dir).resolve()

    speech = synthesize_actor_speech(
        script,
        out_dir,
        config=cfg,
        external_audio_file=Path(args.audio_file) if args.audio_file else None,
        prefer_edge=args.prefer_edge,
        prefer_elevenlabs=args.prefer_elevenlabs,
    )
    mix = mix_genjutsu_soundscape(
        Path(speech["voice_wav"]),
        out_dir / "AUDIO_MASTER.wav",
        cue_sec=speech["genjutsu_cue_sec"],
        config=cfg,
        include_music=not args.no_music,
    )
    print(json.dumps({"speech": speech, "mix": mix}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
