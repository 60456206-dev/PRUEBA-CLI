#!/usr/bin/env python3
"""
CONECTORES API DE ESTUDIO PARA PERSONAJE HIPERREALISTA (CANDIDATO C)
Soporta:
1. ElevenLabs TTS (`/v1/text-to-speech/{voice_id}/with-timestamps`) -> audio + word boundaries.
2. fal.ai Queue API:
   - ByteDance OmniHuman v1.5 (`fal-ai/bytedance/omnihuman/v1.5`)
   - Kling AI Avatar v2 Pro (`fal-ai/kling-video/ai-avatar/v2/pro`)
3. HeyGen v3 Avatar IV (`POST /v3/videos`, `GET /v3/videos/{video_id}`).
"""

import base64
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


def _probe_duration_safe(path: Path) -> float:
    if not path.exists():
        return 0.0
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            stderr=subprocess.STDOUT,
            timeout=15,
        ).decode().strip()
        return max(0.0, float(out))
    except Exception:
        return 0.0


def _verify_video_file(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 10_000:
        return False
    return _probe_duration_safe(path) > 0.2


def alignment_chars_to_word_boundaries(alignment: Dict[str, Any]) -> List[Dict[str, Any]]:
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
                words.append(
                    {
                        "text": "".join(buf),
                        "start": round(w_start, 3),
                        "end": round(max(w_start + 0.05, w_end), 3),
                    }
                )
                buf = []
                w_start = None
                w_end = 0.0
        else:
            if w_start is None:
                w_start = st
            buf.append(ch)
            w_end = max(w_end, en)

    if buf and w_start is not None:
        words.append(
            {
                "text": "".join(buf),
                "start": round(w_start, 3),
                "end": round(max(w_start + 0.05, w_end), 3),
            }
        )
    return words


def _http_json(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    timeout: float = 45.0,
) -> Dict[str, Any]:
    data_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data_bytes, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def _download_binary(url: str, out_path: Path, timeout: float = 120.0) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "PersonajeStudioClient/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        out_path.write_bytes(resp.read())
    return out_path


class ElevenLabsStudioClient:
    """Cliente REST para ElevenLabs TTS con timestamps de palabra exactos."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_voice_id: str = "pNInz6obpgDQGcFmaJgB",
        default_model_id: str = "eleven_multilingual_v2",
    ) -> None:
        self.api_key = (api_key if api_key is not None else os.getenv("ELEVENLABS_API_KEY", "")).strip()
        self.default_voice_id = default_voice_id
        self.default_model_id = default_model_id

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def synthesize_with_timestamps(
        self,
        text: str,
        out_wav: Path,
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
        voice_settings: Optional[Dict[str, Any]] = None,
        sample_rate: int = 48000,
        channels: int = 2,
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        if not self.api_key or not text.strip():
            return False, []

        vid = (voice_id or self.default_voice_id).strip()
        mid = (model_id or self.default_model_id).strip()
        settings = dict(
            voice_settings
            or {
                "stability": 0.45,
                "similarity_boost": 0.78,
                "style": 0.35,
                "use_speaker_boost": True,
                "speed": 0.98,
            }
        )
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps"
        payload = {
            "text": text,
            "model_id": mid,
            "voice_settings": settings,
            "apply_text_normalization": "auto",
        }
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            data = _http_json(url, method="POST", headers=headers, payload=payload, timeout=45.0)
            b64_audio = data.get("audio_base64") or ""
            if not b64_audio:
                return False, []
            raw_mp3 = base64.b64decode(b64_audio)
            if len(raw_mp3) < 512:
                return False, []

            out_wav.parent.mkdir(parents=True, exist_ok=True)
            tmp_mp3 = out_wav.with_suffix(".el_raw.mp3")
            tmp_mp3.write_bytes(raw_mp3)
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(tmp_mp3),
                "-af",
                "highpass=f=75,silenceremove=start_periods=1:start_duration=0.04:start_threshold=-45dB,"
                "areverse,silenceremove=start_periods=1:start_duration=0.04:start_threshold=-45dB,areverse,"
                "afade=t=in:st=0:d=0.008",
                "-ar",
                str(sample_rate),
                "-ac",
                str(channels),
                "-c:a",
                "pcm_s16le",
                str(out_wav),
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            tmp_mp3.unlink(missing_ok=True)
            if proc.returncode != 0 or _probe_duration_safe(out_wav) < 0.35:
                return False, []

            alignment = data.get("alignment") or data.get("normalized_alignment") or {}
            words = alignment_chars_to_word_boundaries(alignment) if isinstance(alignment, dict) else []
            return True, words
        except Exception as exc:
            print(f"[STUDIO-ELEVENLABS] Aviso TTS: {exc}", flush=True)
            return False, []


class FalStudioAvatarClient:
    """Cliente Queue API para fal.ai OmniHuman v1.5 y Kling AI Avatar v2 Pro."""

    ENDPOINTS: Dict[str, str] = {
        "fal_omnihuman": "https://queue.fal.run/fal-ai/bytedance/omnihuman/v1.5",
        "fal_kling_avatar": "https://queue.fal.run/fal-ai/kling-video/ai-avatar/v2/pro",
    }

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = (api_key if api_key is not None else os.getenv("FAL_KEY", "")).strip()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    @staticmethod
    def _encode_image_data_uri(image_path: Path) -> str:
        ext = image_path.suffix.lower()
        mime = "image/png" if ext == ".png" else ("image/webp" if ext == ".webp" else "image/jpeg")
        b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{b64}"

    @staticmethod
    def _encode_audio_data_uri(audio_path: Path) -> str:
        if audio_path.suffix.lower() == ".mp3":
            b64 = base64.b64encode(audio_path.read_bytes()).decode("ascii")
            return f"data:audio/mpeg;base64,{b64}"
        tmp_mp3 = audio_path.with_suffix(".fal_tmp.mp3")
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(audio_path), "-b:a", "192k", "-ar", "48000", str(tmp_mp3)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            b64 = base64.b64encode(tmp_mp3.read_bytes()).decode("ascii")
            return f"data:audio/mpeg;base64,{b64}"
        finally:
            tmp_mp3.unlink(missing_ok=True)

    def _resolve_media_input(self, source: Union[str, Path], kind: str) -> str:
        s = str(source).strip()
        if s.startswith(("http://", "https://", "data:")):
            return s
        p = Path(s).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Archivo de entrada ({kind}) no encontrado para fal.ai: {p}")
        return self._encode_image_data_uri(p) if kind == "image" else self._encode_audio_data_uri(p)

    def generate_talking_avatar(
        self,
        image_source: Union[str, Path],
        audio_source: Union[str, Path],
        out_mp4: Path,
        model: str = "fal_omnihuman",
        prompt: str = (
            "Photorealistic 85mm live-action studio portrait speaking naturally to camera with subtle hand "
            "and head gestures, authentic blinking, natural human skin pores, slow subtle camera push-in."
        ),
        resolution: Optional[str] = None,
        turbo_mode: bool = False,
        poll_interval_sec: float = 3.0,
        timeout_sec: float = 360.0,
    ) -> Path:
        if not self.api_key:
            raise RuntimeError("FAL_KEY no configurada. Exporta FAL_KEY en ~/.api_keys.env o .env para usar fal.ai.")
        if model not in self.ENDPOINTS:
            raise ValueError(f"Modelo fal.ai no soportado: {model}. Opciones: {sorted(self.ENDPOINTS.keys())}")

        endpoint = self.ENDPOINTS[model]
        image_uri = self._resolve_media_input(image_source, "image")
        audio_uri = self._resolve_media_input(audio_source, "audio")

        payload: Dict[str, Any] = {
            "image_url": image_uri,
            "audio_url": audio_uri,
        }
        if prompt:
            payload["prompt"] = prompt

        if model == "fal_omnihuman":
            resolved_res = resolution
            if not resolved_res:
                aud_p = Path(str(audio_source))
                aud_dur = _probe_duration_safe(aud_p) if not str(audio_source).startswith(("http://", "https://", "data:")) else 0.0
                # OmniHuman v1.5 soporta hasta 30s en 1080p y hasta 60s en 720p
                resolved_res = "720p" if aud_dur > 30.0 else "1080p"
            payload["resolution"] = resolved_res
            payload["turbo_mode"] = bool(turbo_mode)

        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

        print(f"[STUDIO-FAL] Enviando trabajo a {model} ({endpoint})...", flush=True)
        submit_resp = _http_json(endpoint, method="POST", headers=headers, payload=payload, timeout=60.0)

        result_payload: Dict[str, Any]
        if isinstance(submit_resp.get("video"), dict) and submit_resp["video"].get("url"):
            result_payload = submit_resp
        else:
            status_url = submit_resp.get("status_url")
            response_url = submit_resp.get("response_url")
            if not status_url or not response_url:
                raise RuntimeError(f"Respuesta inesperada de fal.ai Queue API: {submit_resp}")

            deadline = time.monotonic() + timeout_sec
            while True:
                st_resp = _http_json(status_url, method="GET", headers={"Authorization": f"Key {self.api_key}"}, timeout=30.0)
                status = str(st_resp.get("status") or "").upper()
                if status == "COMPLETED":
                    break
                if status in ("FAILED", "ERROR", "CANCELLED"):
                    raise RuntimeError(f"Trabajo fal.ai ({model}) falló: {st_resp}")
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Timeout esperando finalización de fal.ai ({model}) tras {timeout_sec:.0f}s.")
                time.sleep(poll_interval_sec)

            result_payload = _http_json(response_url, method="GET", headers={"Authorization": f"Key {self.api_key}"}, timeout=45.0)

        video_url = ((result_payload.get("video") or {}).get("url") or result_payload.get("video_url") or "").strip()
        if not video_url:
            raise RuntimeError(f"fal.ai ({model}) completó sin 'video.url' en respuesta: {result_payload}")

        _download_binary(video_url, out_mp4, timeout=120.0)
        if not _verify_video_file(out_mp4):
            raise RuntimeError(f"El vídeo descargado de fal.ai ({model}) no pasó verificación ffprobe: {out_mp4}")
        print(f"[STUDIO-FAL] ✅ Lip-Sync descargado ({model}): {out_mp4.name}", flush=True)
        return out_mp4


class HeyGenAvatarIVClient:
    """Cliente REST v3 para HeyGen Avatar IV (`/v3/videos`)."""

    BASE_URL = "https://api.heygen.com"

    def __init__(self, api_key: Optional[str] = None, default_avatar_id: str = "") -> None:
        self.api_key = (api_key if api_key is not None else os.getenv("HEYGEN_API_KEY", "")).strip()
        self.default_avatar_id = default_avatar_id.strip()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_avatar_iv_video(
        self,
        audio_url: str,
        out_mp4: Path,
        avatar_id: Optional[str] = None,
        title: str = "Candidato C Avatar IV",
        resolution: str = "1080p",
        aspect_ratio: str = "auto",
        poll_interval_sec: float = 4.0,
        timeout_sec: float = 360.0,
    ) -> Path:
        if not self.api_key:
            raise RuntimeError("HEYGEN_API_KEY no configurada. Exporta HEYGEN_API_KEY en ~/.api_keys.env o .env.")
        av_id = (avatar_id or self.default_avatar_id).strip()
        if not av_id:
            raise RuntimeError("Falta heygen_avatar_id en config_personaje.json o parámetro avatar_id.")
        clean_audio = (audio_url or "").strip()
        if not clean_audio.startswith(("http://", "https://")):
            raise ValueError("HeyGen /v3/videos requiere una URL HTTPS pública para `audio_url` (--public-audio-url).")

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "type": "avatar",
            "avatar_id": av_id,
            "engine": {"type": "avatar_iv"},
            "audio_url": clean_audio,
            "title": title,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
        }
        create_resp = _http_json(f"{self.BASE_URL}/v3/videos", method="POST", headers=headers, payload=payload, timeout=45.0)
        video_id = (
            create_resp.get("video_id")
            or (create_resp.get("data") or {}).get("video_id")
            or ""
        ).strip()
        if not video_id:
            raise RuntimeError(f"HeyGen /v3/videos no devolvió video_id: {create_resp}")

        status_url = f"{self.BASE_URL}/v3/videos/{video_id}"
        deadline = time.monotonic() + timeout_sec
        video_url = ""
        while True:
            poll_resp = _http_json(status_url, method="GET", headers={"x-api-key": self.api_key}, timeout=30.0)
            inner = poll_resp.get("data") if isinstance(poll_resp.get("data"), dict) else poll_resp
            status = str(inner.get("status") or poll_resp.get("status") or "").lower()
            if status in ("completed", "success"):
                video_url = str(inner.get("video_url") or poll_resp.get("video_url") or "").strip()
                break
            if status in ("failed", "error"):
                raise RuntimeError(f"HeyGen Avatar IV falló para {video_id}: {poll_resp}")
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timeout esperando vídeo HeyGen {video_id} tras {timeout_sec:.0f}s.")
            time.sleep(poll_interval_sec)

        if not video_url:
            raise RuntimeError(f"HeyGen completó {video_id} sin video_url.")
        _download_binary(video_url, out_mp4, timeout=120.0)
        if not _verify_video_file(out_mp4):
            raise RuntimeError(f"El vídeo descargado de HeyGen no pasó verificación ffprobe: {out_mp4}")
        print(f"[STUDIO-HEYGEN] ✅ Avatar IV descargado: {out_mp4.name}", flush=True)
        return out_mp4


def get_studio_api_status(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Reporta estado de disponibilidad de las APIs de estudio sin exponer secretos."""
    s_cfg = (config or {}).get("studio_apis", {}) if isinstance(config, dict) else {}
    has_el = bool(os.getenv("ELEVENLABS_API_KEY", "").strip())
    has_fal = bool(os.getenv("FAL_KEY", "").strip())
    has_hg = bool(os.getenv("HEYGEN_API_KEY", "").strip())
    return {
        "elevenlabs": {
            "configured": has_el,
            "env_var": "ELEVENLABS_API_KEY",
            "endpoint": "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
            "preferred_in_config": bool(s_cfg.get("prefer_elevenlabs", False)),
        },
        "fal_omnihuman": {
            "configured": has_fal,
            "env_var": "FAL_KEY",
            "endpoint": FalStudioAvatarClient.ENDPOINTS["fal_omnihuman"],
        },
        "fal_kling_avatar": {
            "configured": has_fal,
            "env_var": "FAL_KEY",
            "endpoint": FalStudioAvatarClient.ENDPOINTS["fal_kling_avatar"],
        },
        "heygen_avatar_iv": {
            "configured": has_hg,
            "env_var": "HEYGEN_API_KEY",
            "endpoint": f"{HeyGenAvatarIVClient.BASE_URL}/v3/videos",
            "avatar_id_set": bool(str(s_cfg.get("heygen_avatar_id", "")).strip()),
        },
    }
