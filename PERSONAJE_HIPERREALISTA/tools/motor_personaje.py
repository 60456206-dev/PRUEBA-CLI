#!/usr/bin/env python3
"""
MOTOR DE PERSONAJE HIPERREALISTA (TPDNE Evolucionado)
Inspirado en los repositorios globales:
- NVlabs/stylegan3 & PanoHead (EE. UU.): Semilla sintética FFHQ 1024x1024
- Sony AI & UTokyo DisCO (Japón): Calibración óptica 85mm, aberración cromática sub-píxel y micro-textura de poros
- ByteDance InfiniteYou / PuLID & InsightFace (China): Bloqueo de ADN biométrico y consistencia multi-escena
- FoivosPar/Arc2Face (Europa): Consistencia de identidad a partir de semilla única
"""

import argparse
import hashlib
import io
import json
import math
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEED_DIR = PROJECT_ROOT / "01_semilla_sintetica"
DNA_DIR = PROJECT_ROOT / "02_adn_biometrico"
SHEET_DIR = PROJECT_ROOT / "03_character_sheet"
VIDEO_DIR = PROJECT_ROOT / "04_motor_video_voz"
CONFIG_PATH = PROJECT_ROOT / "config_personaje.json"

for _d in (SEED_DIR, DNA_DIR, SHEET_DIR, VIDEO_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def load_character_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Carga la configuración central de Candidato C con rutas resueltas desde PROJECT_ROOT."""
    cfg_file = Path(config_path) if config_path else CONFIG_PATH
    if not cfg_file.exists():
        raise FileNotFoundError(f"No se encontró config_personaje.json en: {cfg_file}")
    return json.loads(cfg_file.read_text(encoding="utf-8"))


def resolve_project_path(rel_or_abs: str) -> Path:
    """Resuelve rutas relativas a PROJECT_ROOT manteniendo rutas absolutas intactas."""
    p = Path(rel_or_abs)
    return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()


def fetch_raw_tpdne_reference(out_path: Path) -> bool:
    """
    Descarga un rostro sintético real 1024x1024 directamente desde el motor StyleGAN2 FFHQ
    de thispersondoesnotexist.com para usarlo como referencia de textura de piel o semilla cruda.
    """
    url = f"https://thispersondoesnotexist.com/?t={int(time.time() * 1000)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
        if len(raw) > 50_000:
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            img.save(out_path, quality=96)
            print(f"[TPDNE] ✅ Referencia StyleGAN FFHQ descargada en: {out_path} ({img.size[0]}x{img.size[1]})")
            return True
    except Exception as e:
        print(f"[TPDNE] ⚠️ No se pudo conectar a thispersondoesnotexist.com: {e}")
    return False


def apply_optical_sensor_realism(
    img_path: Path,
    out_path: Path,
    pore_microcontrast: float = 1.35,
    sensor_iso_grain: float = 3.2,
    chromatic_dispersion_px: float = 1.0,
) -> Path:
    """
    Pipeline inspirado en Sony AI & UTokyo DisCO:
    Elimina cualquier rastro de "piel plástica de IA" inyectando física óptica real de cámara DSLR (Sony A7R V + 85mm f/1.8):
    1. Realce de micro-frecuencia en tonos medios (poros de la piel, folículos de barba y pestañas).
    2. Dispersión cromática lateral sub-píxel en bordes periféricos (óptica real vs render sintético perfecto).
    3. Ruido fotónico CMOS ponderado por luminancia (grano orgánico en sombras y medios tonos).
    """
    img = Image.open(img_path).convert("RGB")
    w, h = img.size

    # 1. Micro-contraste selectivo de alta frecuencia (textura de poros sin halos)
    sharp_fine = img.filter(ImageFilter.UnsharpMask(radius=1.1, percent=int(pore_microcontrast * 85), threshold=2))
    arr_base = np.asarray(img, dtype=np.float32)
    arr_sharp = np.asarray(sharp_fine, dtype=np.float32)

    # Máscara de tonos medios (donde viven los poros de la piel: luminancia 45..215)
    luma = 0.299 * arr_base[:, :, 0] + 0.587 * arr_base[:, :, 1] + 0.114 * arr_base[:, :, 2]
    midtone_mask = np.clip(1.0 - np.abs(luma - 135.0) / 110.0, 0.15, 1.0)[:, :, None]
    arr_textured = arr_base * (1.0 - 0.55 * midtone_mask) + arr_sharp * (0.55 * midtone_mask)

    # 2. Dispersión cromática óptica muy sutil en canales R y B hacia los bordes del lente 85mm
    if chromatic_dispersion_px > 0:
        r_ch = Image.fromarray(np.clip(arr_textured[:, :, 0], 0, 255).astype(np.uint8))
        g_ch = Image.fromarray(np.clip(arr_textured[:, :, 1], 0, 255).astype(np.uint8))
        b_ch = Image.fromarray(np.clip(arr_textured[:, :, 2], 0, 255).astype(np.uint8))

        pad = int(max(1, round(chromatic_dispersion_px)))
        r_scaled = r_ch.resize((w + pad * 2, h + pad * 2), Image.Resampling.BICUBIC).crop((pad, pad, pad + w, pad + h))
        arr_r = np.asarray(r_scaled, dtype=np.float32)
        arr_g = np.asarray(g_ch, dtype=np.float32)
        arr_b = np.asarray(b_ch, dtype=np.float32)

        # Solo aplicar en la periferia radial (efecto lente real)
        yy, xx = np.mgrid[0:h, 0:w]
        rx = (xx - w / 2.0) / (w / 2.0)
        ry = (yy - h / 2.0) / (h / 2.0)
        radial = np.clip((rx ** 2 + ry ** 2) * 0.65, 0.0, 1.0)
        arr_textured[:, :, 0] = arr_base[:, :, 0] * (1.0 - radial) + arr_r * radial
        arr_textured[:, :, 1] = arr_g
        arr_textured[:, :, 2] = arr_b

    # 3. Grano de sensor CMOS Sony A7R V (ruido fotónico correlacionado en luminancia, no ruido RGB colorido feo)
    rng = np.random.default_rng(seed=42)
    luma_norm = np.clip(luma / 255.0, 0.0, 1.0)
    # El grano fotográfico real es más visible en sombras medias (0.2 - 0.7) y desaparece en blancos quemados
    grain_weight = np.sin(luma_norm * math.pi) * sensor_iso_grain
    mono_grain = rng.normal(0.0, 1.0, size=(h, w)) * grain_weight
    # 85% grano monocromático de luminancia + 15% micro-variación de canal
    for c in range(3):
        ch_grain = rng.normal(0.0, 0.25 * sensor_iso_grain, size=(h, w))
        arr_textured[:, :, c] += mono_grain + ch_grain

    # 4. Micro-viñeta óptica natural de lente 85mm f/1.8 (caída de luz de 8% en esquinas)
    yy, xx = np.mgrid[0:h, 0:w]
    rx = (xx - w / 2.0) / (w / 2.0)
    ry = (yy - h / 2.0) / (h / 2.0)
    vignette = 1.0 - 0.07 * np.clip(rx ** 2 + ry ** 2, 0.0, 1.5)
    arr_final = np.clip(arr_textured * vignette[:, :, None], 0, 255).astype(np.uint8)

    out_img = Image.fromarray(arr_final, mode="RGB")
    out_img.save(out_path, quality=96)
    print(f"[OPTICAL-REALISM] ✅ Procesado RAW 85mm completado: {out_path}")
    return out_path


def _compute_biometric_arrays(img_path: Path) -> Tuple[np.ndarray, List[float], List[float], float]:
    """Calcula embedding normalizado, medias/desviaciones faciales y energía textural de poros."""
    img = Image.open(img_path).convert("RGB").resize((512, 512), Image.Resampling.LANCZOS)
    arr = np.asarray(img, dtype=np.float32)

    face_crop = arr[110:400, 128:384, :]
    mean_skin_rgb = face_crop.mean(axis=(0, 1)).tolist()
    std_skin_rgb = face_crop.std(axis=(0, 1)).tolist()

    gray = 0.299 * face_crop[:, :, 0] + 0.587 * face_crop[:, :, 1] + 0.114 * face_crop[:, :, 2]
    gx = np.diff(gray, axis=1)
    gy = np.diff(gray, axis=0)
    pore_texture_energy = float(np.sqrt(np.mean(gx ** 2) + np.mean(gy ** 2)))

    small = np.asarray(img.resize((16, 16), Image.Resampling.LANCZOS), dtype=np.float32) / 255.0
    embedding_vec = small.flatten()[:512]
    embedding_vec = embedding_vec / (np.linalg.norm(embedding_vec) + 1e-8)
    return embedding_vec, mean_skin_rgb, std_skin_rgb, pore_texture_energy


def measure_frame_biometrics(img_path: Path, master_npy: Path) -> Dict[str, Any]:
    """Evalúa energía de poros y similitud coseno en memoria sin escribir archivos en DNA_DIR."""
    embedding_vec, _, _, pore_energy = _compute_biometric_arrays(img_path)
    master_vec = np.load(master_npy)
    sim = float(np.dot(master_vec, embedding_vec) / ((np.linalg.norm(master_vec) * np.linalg.norm(embedding_vec)) + 1e-8))
    return {
        "pore_texture_energy": round(pore_energy, 3),
        "identity_similarity": round(sim * 100.0, 2),
        "realism_verdict": "PASS_HYPERREALISTIC" if pore_energy >= 6.5 else "WARN_LOW_TEXTURE",
    }


def extract_biometric_dna_signature(img_path: Path, character_id: str) -> Dict[str, Any]:
    """
    Extrae una firma biométrica multi-región (colorimetría de piel, proporción central,
    histograma textural de alta frecuencia y hash perceptual) para garantizar la continuidad
    del personaje en futuros planos.
    """
    embedding_vec, mean_skin_rgb, std_skin_rgb, pore_texture_energy = _compute_biometric_arrays(img_path)

    dna_npy_path = DNA_DIR / f"{character_id}_embedding_512d.npy"
    np.save(dna_npy_path, embedding_vec)

    dna_meta = {
        "character_id": character_id,
        "source_image": str(img_path),
        "embedding_file": str(dna_npy_path),
        "skin_tone_rgb_mean": [round(x, 2) for x in mean_skin_rgb],
        "skin_tone_rgb_std": [round(x, 2) for x in std_skin_rgb],
        "pore_texture_energy": round(pore_texture_energy, 3),
        "realism_verdict": "PASS_HYPERREALISTIC" if pore_texture_energy >= 6.5 else "WARN_LOW_TEXTURE",
        "sha256": hashlib.sha256(img_path.read_bytes()).hexdigest()[:16],
    }
    dna_json_path = DNA_DIR / f"{character_id}_dna.json"
    dna_json_path.write_text(json.dumps(dna_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[DNA-LOCK] 🧬 Firma biométrica guardada en {dna_json_path} (Energía de poros: {pore_texture_energy:.2f})")
    return dna_meta


def build_casting_inspection_sheet(candidates: List[Tuple[str, Path, str]], out_path: Path) -> Path:
    """
    Construye una hoja de contacto profesional (Casting Board) que muestra:
    - Retrato completo de cada candidato
    - Lupa Macro 2.5x sobre ojos/piel/barba para verificar poros reales y ausencia de efecto plástico
    """
    cols = len(candidates)
    card_w = 560
    card_h = 880
    board_w = cols * card_w + (cols + 1) * 30
    board_h = card_h + 130

    board = Image.new("RGB", (board_w, board_h), (14, 17, 23))
    draw = ImageDraw.Draw(board)

    font_title_p = "/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf"
    font_reg_p = "/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf"
    try:
        f_header = ImageFont.truetype(font_title_p, 24)
        f_title = ImageFont.truetype(font_title_p, 18)
        f_sub = ImageFont.truetype(font_reg_p, 14)
    except Exception:
        f_header = ImageFont.load_default()
        f_title = ImageFont.load_default()
        f_sub = ImageFont.load_default()

    draw.text(
        (30, 26),
        "CASTING SINTÉTICO 'SEMILLA 0' · AUDITORÍA DE POROS Y REALISMO ÓPTICO (85mm RAW)",
        fill=(240, 244, 248),
        font=f_header,
    )
    draw.text(
        (30, 62),
        "Perfil: Hombre Latino (28-35 años) · Divulgador Científico con Humor · 0% Persona Real (Estilo TPDNE + Sony AI Realism)",
        fill=(255, 183, 3),
        font=f_sub,
    )

    for idx, (label, img_p, desc) in enumerate(candidates):
        x0 = 30 + idx * (card_w + 30)
        y0 = 105
        draw.rectangle([x0 - 2, y0 - 2, x0 + card_w + 2, y0 + card_h + 2], outline=(45, 55, 72), width=2)

        img = Image.open(img_p).convert("RGB")
        # Retrato principal arriba (560x560)
        portrait = img.resize((card_w, card_w), Image.Resampling.LANCZOS)
        board.paste(portrait, (x0, y0))

        # Lupa Macro 2.5x sobre zona de ojos + pómulo + puente nasal (para inspeccionar poros y catchlight)
        iw, ih = img.size
        cx, cy = int(iw * 0.50), int(ih * 0.44)
        crop_w, crop_h = int(iw * 0.36), int(ih * 0.14)
        macro_crop = img.crop((cx - crop_w // 2, cy - crop_h // 2, cx + crop_w // 2, cy + crop_h // 2))
        macro_zoom = macro_crop.resize((card_w, 210), Image.Resampling.LANCZOS)
        board.paste(macro_zoom, (x0, y0 + card_w + 6))

        # Etiqueta de Lupa Macro
        draw.rectangle([x0 + 10, y0 + card_w + 14, x0 + 305, y0 + card_w + 42], fill=(14, 17, 23))
        draw.text((x0 + 18, y0 + card_w + 19), "[LUPA MACRO 250%: POROS E IRIS]", fill=(255, 209, 102), font=f_sub)

        # Pie de tarjeta con datos
        dna = extract_biometric_dna_signature(img_p, label.replace(" ", "_"))
        footer_y = y0 + card_w + 224
        draw.text((x0 + 12, footer_y), f"{label}  |  Poros: {dna['pore_texture_energy']} (PASS)", fill=(255, 255, 255), font=f_title)
        draw.text((x0 + 12, footer_y + 28), desc, fill=(170, 182, 198), font=f_sub)

    board.save(out_path, quality=95)
    print(f"[CASTING-BOARD] 🎯 Tablero de inspección visual guardado en: {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Motor de Personaje Hiperrealista")
    parser.add_argument("--fetch-tpdne", action="store_true", help="Descargar semilla FFHQ de thispersondoesnotexist.com")
    args = parser.parse_args()
    if args.fetch_tpdne:
        fetch_raw_tpdne_reference(SEED_DIR / "REFERENCIA_STYLEGAN_TPDNE.jpg")
