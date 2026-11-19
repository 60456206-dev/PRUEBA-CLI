#!/usr/bin/env python3
"""
MOTOR DE VÍDEO HIPERREALISTA + VFX LIVE-ACTION 'GENJUTSU' (Sin pérdida de poros)
Implementa la arquitectura de 4 capas para preservar el hiperrealismo en vídeo:
1. Anclaje First-Frame / Last-Frame (KF1 Normal -> KF2 Genjutsu Live-Action) con restauración óptica 85mm RAW.
2. Separación de Frecuencias (Frequency Separation): restaura altas frecuencias de poros sobre clips I2V/Lip-Sync.
3. Transición Cinematográfica Genjutsu sincronizada al cue de audio (fractura cromática radial + pulso carmesí + micro-shake).
4. Exportación Master Broadcast 9:16 (1080x1920 @ 24fps, H.264 High Profile CRF 16 + Temporal CMOS Grain + Audio/ASS).
"""

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PERSONAJE_HIPERREALISTA.tools.motor_personaje import (  # noqa: E402
    PROJECT_ROOT,
    SEED_DIR,
    DNA_DIR,
    SHEET_DIR,
    VIDEO_DIR,
    extract_biometric_dna_signature,
    load_character_config,
)


def compute_identity_similarity(master_dna_npy: Path, target_dna_npy: Path) -> float:
    """Calcula la similitud coseno entre la semilla oficial y el nuevo plano."""
    v1 = np.load(master_dna_npy)
    v2 = np.load(target_dna_npy)
    sim = float(np.dot(v1, v2) / ((np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-8))
    return round(sim * 100.0, 2)


def fit_vertical_cover(img: Image.Image, width: int = 1080, height: int = 1920) -> Image.Image:
    """Recorta y reescala una imagen manteniendo relación 9:16 exacta sin deformar."""
    iw, ih = img.size
    target_ratio = width / height
    curr_ratio = iw / ih
    if curr_ratio > target_ratio:
        new_w = int(round(ih * target_ratio))
        left = max(0, (iw - new_w) // 2)
        img = img.crop((left, 0, left + new_w, ih))
    elif curr_ratio < target_ratio:
        new_h = int(round(iw / target_ratio))
        top = max(0, (ih - new_h) // 2)
        img = img.crop((0, top, iw, top + new_h))
    return img.resize((width, height), Image.Resampling.LANCZOS)


def escape_ffmpeg_filter_path(path: Path) -> str:
    """Escapa rutas para filtros FFmpeg (subtitles=...) evitando fallos por ':' o espacios."""
    s = str(path.resolve())
    for old, new in (
        ("\\", "\\\\"),
        (":", "\\:"),
        ("'", "\\'"),
        ("[", "\\["),
        ("]", "\\]"),
        (",", "\\,"),
        (";", "\\;"),
    ):
        s = s.replace(old, new)
    return s


def probe_media_duration(path: Path) -> float:
    """Devuelve la duración en segundos de audio o vídeo mediante ffprobe."""
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


def compute_high_frequency_band(ref_arr: np.ndarray, blur_radius: float = 2.2) -> np.ndarray:
    """Precalcula la banda espacial de alta frecuencia (poros/microtextura) de una imagen RAW."""
    ref_u8 = np.clip(ref_arr, 0, 255).astype(np.uint8)
    ref_low = np.asarray(
        Image.fromarray(ref_u8, mode="RGB").filter(ImageFilter.GaussianBlur(radius=blur_radius)),
        dtype=np.float32,
    )
    return np.clip(ref_arr - ref_low, -28.0, 28.0)


def apply_high_frequency_band(
    frame_arr: np.ndarray,
    high_freq: np.ndarray,
    strength: float = 0.45,
) -> np.ndarray:
    """Reinyecta una banda de alta frecuencia precalculada en los tonos medios del fotograma."""
    if strength <= 0.0:
        return frame_arr
    luma = 0.299 * frame_arr[:, :, 0] + 0.587 * frame_arr[:, :, 1] + 0.114 * frame_arr[:, :, 2]
    mid_mask = np.clip(1.0 - np.abs(luma - 130.0) / 115.0, 0.15, 1.0)[:, :, None]
    return np.clip(frame_arr + high_freq * (strength * mid_mask), 0.0, 255.0)


def restore_high_frequency_pores(
    frame_arr: np.ndarray,
    ref_arr: np.ndarray,
    strength: float = 0.45,
) -> np.ndarray:
    """
    Separación de frecuencias: extrae la banda de alta frecuencia de la referencia 85mm RAW
    (poros, folículos y micro-textura) y la reinyecta suavemente en los tonos medios
    de fotogramas estáticos alineados para revertir el suavizado plástico.
    """
    if strength <= 0.0:
        return frame_arr
    high_freq = compute_high_frequency_band(ref_arr)
    return apply_high_frequency_band(frame_arr, high_freq, strength=strength)


def enhance_moving_frame_microtexture(
    frame_arr: np.ndarray,
    strength: float = 0.45,
) -> np.ndarray:
    """
    Realza micro-textura de piel y barba calculada sobre el PROPIO fotograma en movimiento
    (multi-escala local en tonos medios, sin superponer mapas estáticos ni causar texture sticking).
    """
    if strength <= 0.0:
        return frame_arr
    frame_u8 = np.clip(frame_arr, 0, 255).astype(np.uint8)
    frame_img = Image.fromarray(frame_u8, mode="RGB")
    blur_fine = np.asarray(frame_img.filter(ImageFilter.GaussianBlur(radius=1.0)), dtype=np.float32)
    blur_med = np.asarray(frame_img.filter(ImageFilter.GaussianBlur(radius=2.0)), dtype=np.float32)
    detail = np.clip((frame_arr - blur_fine) * 0.72 + (blur_fine - blur_med) * 0.38, -22.0, 22.0)

    luma = 0.299 * frame_arr[:, :, 0] + 0.587 * frame_arr[:, :, 1] + 0.114 * frame_arr[:, :, 2]
    mid_mask = np.clip(1.0 - np.abs(luma - 130.0) / 108.0, 0.15, 1.0)[:, :, None]
    return np.clip(frame_arr + detail * (strength * 1.75 * mid_mask), 0.0, 255.0)


def compute_transition_state(
    t: float,
    cue_sec: float,
    transition_window_sec: float = 0.9,
) -> Tuple[float, float]:
    """Devuelve (alpha_kf2, glitch_amp) para el instante temporal t."""
    half = max(0.15, transition_window_sec / 2.0)
    t_start = max(0.0, cue_sec - half)
    t_end = cue_sec + half

    if t < t_start:
        return 0.0, 0.0
    if t < t_end:
        u = (t - t_start) / max(1e-6, t_end - t_start)
        alpha = u * u * (3.0 - 2.0 * u)
        glitch_amp = math.sin(u * math.pi)
        return alpha, glitch_amp
    return 1.0, 0.08 * (0.5 + 0.5 * math.sin((t - t_end) * 4.5))


def apply_genjutsu_optical_vfx(
    base_arr: np.ndarray,
    alpha: float,
    glitch_amp: float,
    frame_idx: int,
    total_frames: int,
    rng: np.random.Generator,
    width: int = 1080,
    height: int = 1920,
    grain_sigma: float = 2.2,
    push_in_zoom: float = 0.06,
) -> Image.Image:
    """Aplica fractura cromática radial, pulso carmesí, micro-shake, grano CMOS y push-in."""
    work = base_arr.copy()

    if glitch_amp > 0.05:
        shift_px = int(round(glitch_amp * 18))
        if shift_px > 0:
            r_ch = Image.fromarray(np.clip(work[:, :, 0], 0, 255).astype(np.uint8))
            r_zoom = r_ch.resize(
                (width + shift_px * 2, height + shift_px * 2), Image.Resampling.BILINEAR
            ).crop((shift_px, shift_px, shift_px + width, shift_px + height))
            work[:, :, 0] = np.asarray(r_zoom, dtype=np.float32) * (1.0 + 0.22 * glitch_amp)

        if 0.35 < alpha < 0.75:
            flash = math.sin((alpha - 0.35) / 0.40 * math.pi) * 0.28
            work[:, :, 0] = np.clip(work[:, :, 0] + flash * 90.0, 0, 255)
            work[:, :, 1] = np.clip(work[:, :, 1] * (1.0 - flash * 0.35), 0, 255)
            work[:, :, 2] = np.clip(work[:, :, 2] * (1.0 - flash * 0.35), 0, 255)

    # Grano temporal orgánico de sensor CMOS para preservar poros en H.264
    if grain_sigma > 0:
        temporal_grain = rng.normal(0.0, grain_sigma, size=(height, width, 1)).astype(np.float32)
        work = work + temporal_grain

    frame_arr = np.clip(work, 0, 255).astype(np.uint8)
    frame_img = Image.fromarray(frame_arr, mode="RGB")

    # Empuje óptico lento + micro-vibración anamórfica en pico de fractura
    zoom = 1.0 + push_in_zoom * (frame_idx / max(1, total_frames - 1))
    if glitch_amp > 0.45:
        zoom += 0.015 * glitch_amp
    cw, ch = max(16, int(width / zoom)), max(16, int(height / zoom))
    shake_x = int(round(math.sin(frame_idx * 2.1) * 3.0 * glitch_amp)) if glitch_amp > 0.35 else 0
    shake_y = int(round(math.cos(frame_idx * 2.7) * 3.0 * glitch_amp)) if glitch_amp > 0.35 else 0
    x0 = max(0, min(width - cw, (width - cw) // 2 + shake_x))
    y0 = max(0, min(height - ch, int((height - ch) * 0.38) + shake_y))

    return frame_img.crop((x0, y0, x0 + cw, y0 + ch)).resize(
        (width, height), Image.Resampling.LANCZOS
    )


def encode_frames_to_mp4(
    frames_dir: Path,
    out_mp4: Path,
    fps: int = 24,
    crf: int = 18,
    preset: str = "medium",
    audio_path: Optional[Path] = None,
    subtitle_path: Optional[Path] = None,
    maxrate: str = "12M",
    bufsize: str = "24M",
) -> Path:
    """Codifica una secuencia frame_%04d.jpg a MP4 H.264 High Profile con bitrate broadcast acotado."""
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%04d.jpg"),
    ]
    if audio_path is not None:
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio no encontrado para muxing: {audio_path}")
        cmd.extend(["-i", str(audio_path)])

    if subtitle_path is not None:
        if not subtitle_path.exists():
            raise FileNotFoundError(f"Subtítulos ASS no encontrados: {subtitle_path}")
        esc_ass = escape_ffmpeg_filter_path(subtitle_path)
        cmd.extend(["-vf", f"subtitles='{esc_ass}'"])

    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-profile:v",
            "high",
            "-crf",
            str(crf),
            "-preset",
            preset,
            "-maxrate",
            str(maxrate),
            "-bufsize",
            str(bufsize),
            "-pix_fmt",
            "yuv420p",
        ]
    )
    if audio_path is not None:
        cmd.extend(["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest"])
    else:
        cmd.append("-an")

    cmd.extend(["-movflags", "+faststart", str(out_mp4)])
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Error codificando vídeo final en FFmpeg:\n{proc.stderr[-800:]}")
    return out_mp4


def build_genjutsu_comparison_sheet(
    master_seed: Path,
    kf1_path: Path,
    kf2_path: Path,
    out_sheet: Path,
) -> Path:
    """
    Construye una hoja técnica 3-en-1 que demuestra cómo el Candidato C mantiene
    su rostro, poros y barba de 2 días entre la Semilla 0, el Plano Hablando (KF1)
    y el Estado Genjutsu Live-Action (KF2).
    """
    w_card, h_card = 540, 960
    board_w = w_card * 3 + 120
    board_h = h_card + 160

    board = Image.new("RGB", (board_w, board_h), (12, 14, 19))
    draw = ImageDraw.Draw(board)

    font_b = "/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf"
    font_r = "/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf"
    try:
        f_head = ImageFont.truetype(font_b, 24)
        f_title = ImageFont.truetype(font_b, 18)
        f_sub = ImageFont.truetype(font_r, 14)
    except Exception:
        f_head = f_title = f_sub = ImageFont.load_default()

    draw.text(
        (30, 24),
        "PIPELINE DE CONTINUIDAD HIPERREALISTA · ANCLAJE DE KEYFRAMES + LIVE-ACTION GENJUTSU",
        fill=(245, 247, 250),
        font=f_head,
    )
    draw.text(
        (30, 58),
        "Personaje Oficial: CANDIDATO C (29 años) · Lente 85mm f/1.8 RAW · Restauración de Poros por Separación de Frecuencias",
        fill=(230, 57, 70),
        font=f_sub,
    )

    items = [
        ("1. SEMILLA OFICIAL (1:1 -> 9:16)", master_seed, "ADN Base Bloqueado · Poros 85mm RAW"),
        ("2. KEYFRAME 1: HABLANDO A CÁMARA", kf1_path, "Mirada frontal + Gesto de manos · Estudio cálido"),
        ("3. KEYFRAME 2: GENJUTSU LIVE-ACTION", kf2_path, "Luz eclipse carmesí + Plumas en bokeh · Piel 100% real"),
    ]

    for idx, (title, p, sub) in enumerate(items):
        x0 = 30 + idx * (w_card + 30)
        y0 = 96
        img_resized = fit_vertical_cover(Image.open(p).convert("RGB"), w_card, h_card)
        board.paste(img_resized, (x0, y0))

        border_col = (230, 57, 70) if idx == 2 else (65, 78, 102)
        draw.rectangle([x0 - 2, y0 - 2, x0 + w_card + 2, y0 + h_card + 2], outline=border_col, width=2)

        dna = extract_biometric_dna_signature(p, f"OFICIAL_C_STAGE_{idx+1}")
        fy = y0 + h_card + 12
        draw.text((x0 + 8, fy), f"{title}  |  Poros: {dna['pore_texture_energy']}", fill=(255, 255, 255), font=f_title)
        draw.text((x0 + 8, fy + 24), sub, fill=(175, 185, 200), font=f_sub)

    out_sheet.parent.mkdir(parents=True, exist_ok=True)
    board.save(out_sheet, quality=95)
    print(f"[GENJUTSU-SHEET] ✅ Hoja de continuidad guardada en: {out_sheet}")
    return out_sheet


def render_genjutsu_master_video(
    kf1_path: Path,
    kf2_path: Path,
    out_mp4: Path,
    duration_sec: Optional[float] = 6.0,
    fps: int = 24,
    cue_sec: Optional[float] = None,
    transition_window_sec: float = 0.9,
    audio_path: Optional[Path] = None,
    subtitle_path: Optional[Path] = None,
    crf: int = 18,
    preset: str = "medium",
    grain_sigma: float = 1.6,
    pore_strength: float = 0.30,
    maxrate: str = "12M",
    bufsize: str = "24M",
) -> Path:
    """
    Renderiza el vídeo maestro 1080x1920 @ 24fps (H.264 High Profile CRF 16) desde KF1 -> KF2,
    sincronizado al cue exacto del audio cuando se provee pista masterizada y subtítulos ASS.
    """
    if duration_sec is None:
        if audio_path is not None and audio_path.exists():
            duration_sec = max(2.0, probe_media_duration(audio_path))
        else:
            duration_sec = 6.0
    if cue_sec is None:
        cue_sec = min(2.65, duration_sec * 0.44)

    tmp_dir = out_mp4.parent / f"_frames_{out_mp4.stem}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    W, H = 1080, 1920
    img1 = fit_vertical_cover(Image.open(kf1_path).convert("RGB"), W, H)
    img2 = fit_vertical_cover(Image.open(kf2_path).convert("RGB"), W, H)

    arr1 = np.asarray(img1, dtype=np.float32)
    arr2 = np.asarray(img2, dtype=np.float32)

    total_frames = max(12, int(round(duration_sec * fps)))
    rng = np.random.default_rng(seed=2026)
    hf1 = compute_high_frequency_band(arr1) if pore_strength > 0 else None
    hf2 = compute_high_frequency_band(arr2) if pore_strength > 0 else None

    try:
        for f in range(total_frames):
            t = f / fps
            alpha, glitch_amp = compute_transition_state(t, cue_sec, transition_window_sec)
            base = arr1 * (1.0 - alpha) + arr2 * alpha
            if hf1 is not None and hf2 is not None and pore_strength > 0:
                hf_blend = hf1 * (1.0 - alpha) + hf2 * alpha
                base = apply_high_frequency_band(base, hf_blend, strength=pore_strength)
            frame_out = apply_genjutsu_optical_vfx(
                base,
                alpha=alpha,
                glitch_amp=glitch_amp,
                frame_idx=f,
                total_frames=total_frames,
                rng=rng,
                width=W,
                height=H,
                grain_sigma=grain_sigma,
            )
            frame_out.save(tmp_dir / f"frame_{f:04d}.jpg", quality=96)

        encode_frames_to_mp4(
            tmp_dir,
            out_mp4,
            fps=fps,
            crf=crf,
            preset=preset,
            audio_path=audio_path,
            subtitle_path=subtitle_path,
            maxrate=maxrate,
            bufsize=bufsize,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"[VIDEO-MASTER] 🎬 Vídeo Genjutsu Hiperrealista exportado en: {out_mp4} ({out_mp4.stat().st_size / 1024:.1f} KB)")
    return out_mp4


def process_i2v_video_with_pore_restoration(
    input_video: Path,
    kf1_path: Path,
    kf2_path: Path,
    out_mp4: Path,
    cue_sec: float,
    audio_path: Optional[Path] = None,
    subtitle_path: Optional[Path] = None,
    fps: int = 24,
    crf: int = 18,
    preset: str = "medium",
    grain_sigma: float = 1.6,
    pore_strength: float = 0.48,
    transition_window_sec: float = 0.9,
    maxrate: str = "12M",
    bufsize: str = "24M",
) -> Path:
    """
    Postprocesa un clip crudo generado por Flow Veo 3.1 / OmniHuman / Kling Avatar / HeyGen / Hallo2:
    normaliza a 1080x1920 @ 24fps, realza micro-textura adaptativa por frame (cero texture sticking),
    inyecta la fractura Genjutsu en cue_sec y muxea audio + subtítulos con bitrate broadcast acotado.
    """
    if not input_video.exists():
        raise FileNotFoundError(f"No existe el vídeo I2V de entrada: {input_video}")

    W, H = 1080, 1920
    work_dir = out_mp4.parent / f"_i2v_work_{out_mp4.stem}"
    in_frames_dir = work_dir / "in_frames"
    out_frames_dir = work_dir / "out_frames"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    in_frames_dir.mkdir(parents=True, exist_ok=True)
    out_frames_dir.mkdir(parents=True, exist_ok=True)

    try:
        vf_scale = (
            f"fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{H}"
        )
        cmd_extract = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_video),
            "-vf",
            vf_scale,
            "-q:v",
            "2",
            str(in_frames_dir / "in_%04d.jpg"),
        ]
        proc = subprocess.run(cmd_extract, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Error extrayendo frames de I2V ({input_video.name}): {proc.stderr[-500:]}")

        extracted = sorted(in_frames_dir.glob("in_*.jpg"))
        if not extracted:
            raise RuntimeError(f"El vídeo de entrada no produjo fotogramas: {input_video}")

        target_frames = len(extracted)
        if audio_path is not None and audio_path.exists():
            aud_dur = probe_media_duration(audio_path)
            if aud_dur > 0:
                target_frames = max(target_frames, int(round(aud_dur * fps)))

        rng = np.random.default_rng(seed=2026)

        for f in range(target_frames):
            t = f / fps
            src_idx = min(f, len(extracted) - 1)
            src_arr = np.asarray(Image.open(extracted[src_idx]).convert("RGB"), dtype=np.float32)

            alpha, glitch_amp = compute_transition_state(t, cue_sec, transition_window_sec)
            restored = enhance_moving_frame_microtexture(src_arr, strength=pore_strength)

            frame_out = apply_genjutsu_optical_vfx(
                restored,
                alpha=alpha,
                glitch_amp=glitch_amp,
                frame_idx=f,
                total_frames=target_frames,
                rng=rng,
                width=W,
                height=H,
                grain_sigma=grain_sigma,
                push_in_zoom=0.03,
            )
            frame_out.save(out_frames_dir / f"frame_{f:04d}.jpg", quality=96)

        encode_frames_to_mp4(
            out_frames_dir,
            out_mp4,
            fps=fps,
            crf=crf,
            preset=preset,
            audio_path=audio_path,
            subtitle_path=subtitle_path,
            maxrate=maxrate,
            bufsize=bufsize,
        )
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    return out_mp4


def main() -> None:
    parser = argparse.ArgumentParser(description="Motor de Vídeo Genjutsu Hiperrealista")
    parser.add_argument("--input-video", type=str, default=None, help="Clip I2V/Lip-Sync externo a restaurar")
    parser.add_argument("--audio", type=str, default=None, help="Pista de audio WAV/MP3 para muxing")
    parser.add_argument("--subtitles", type=str, default=None, help="Archivo ASS opcional")
    parser.add_argument("--cue-sec", type=float, default=None, help="Segundo exacto de activación Genjutsu")
    parser.add_argument("--duration", type=float, default=None, help="Duración en segundos (auto si hay audio)")
    parser.add_argument("--out", type=str, default=str(VIDEO_DIR / "DEMO_GENJUTSU_CUSTOM.mp4"))
    args = parser.parse_args()

    cfg = load_character_config()
    kf1 = PROJECT_ROOT / cfg["personaje"]["kf1_normal"]
    kf2 = PROJECT_ROOT / cfg["personaje"]["kf2_genjutsu"]
    vcfg = cfg["video"]
    out_mp4 = Path(args.out).resolve()
    audio_p = Path(args.audio).resolve() if args.audio else None
    sub_p = Path(args.subtitles).resolve() if args.subtitles else None

    if args.input_video:
        dur = args.duration or (probe_media_duration(audio_p) if audio_p else probe_media_duration(Path(args.input_video)))
        cue = args.cue_sec if args.cue_sec is not None else max(1.0, dur * 0.45)
        process_i2v_video_with_pore_restoration(
            input_video=Path(args.input_video).resolve(),
            kf1_path=kf1,
            kf2_path=kf2,
            out_mp4=out_mp4,
            cue_sec=cue,
            audio_path=audio_p,
            subtitle_path=sub_p,
            fps=int(vcfg["fps"]),
            crf=int(vcfg["crf"]),
            preset=str(vcfg["preset"]),
            grain_sigma=float(vcfg["temporal_grain_sigma"]),
            pore_strength=float(vcfg["pore_restoration_strength"]),
            transition_window_sec=float(vcfg["transition_window_sec"]),
            maxrate=str(vcfg.get("maxrate", "12M")),
            bufsize=str(vcfg.get("bufsize", "24M")),
        )
    else:
        render_genjutsu_master_video(
            kf1_path=kf1,
            kf2_path=kf2,
            out_mp4=out_mp4,
            duration_sec=args.duration,
            fps=int(vcfg["fps"]),
            cue_sec=args.cue_sec,
            transition_window_sec=float(vcfg["transition_window_sec"]),
            audio_path=audio_p,
            subtitle_path=sub_p,
            crf=int(vcfg["crf"]),
            preset=str(vcfg["preset"]),
            grain_sigma=float(vcfg["temporal_grain_sigma"]),
            pore_strength=float(vcfg["pore_restoration_strength"]),
            maxrate=str(vcfg.get("maxrate", "12M")),
            bufsize=str(vcfg.get("bufsize", "24M")),
        )


if __name__ == "__main__":
    main()
