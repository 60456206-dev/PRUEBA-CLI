#!/usr/bin/env python3
"""
TIKTOK RADAR · Generador Automático de Portadas / Miniaturas 9:16 y Hashtags Virales
1. Genera una miniatura 9:16 (1080x1920) de ultra alto impacto (High CTR) para TikTok.
2. Diseñada respetando la "Safe Zone" de TikTok (3:4 center crop) para que el titular
   y el badge nunca se corten al visualizarse en el grid del perfil de TikTok.
3. Genera el banco de hashtags optimizado por género y tema + copy listo para pegar.
4. Exporta:
   - PORTADA_TIKTOK_916.jpg
   - HASHTAGS_TIKTOK.txt
   - Actualiza metadata.json con {"hashtags", "hashtags_str", "tiktok_caption", "cover_file"}
"""

import argparse
import base64
import io
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Cargar claves de entorno automáticamente si existen
for _env_p in [
    Path.home() / ".api_keys.env",
    Path("/workspaces/PRUEBA-CLI/.api_keys.env"),
    Path("/workspaces/PRUEBA-CLI/.env"),
]:
    if _env_p.exists():
        for _line in _env_p.read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if _line.startswith("export "):
                _line = _line[7:]
            if "=" in _line and not _line.startswith("#"):
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

ROOT_DIR = Path(__file__).resolve().parent.parent
ENTREGAS_DIR = ROOT_DIR / "entregas"
_MONT_BOLD = Path("/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf")
_MONT_REG = Path("/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf")
FONT_BOLD = str(_MONT_BOLD) if _MONT_BOLD.exists() else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = str(_MONT_REG) if _MONT_REG.exists() else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _kw_match(k: str, txt: str) -> bool:
    pat = rf"\b{re.escape(k)}\b" if (len(k) <= 4 and " " not in k) else rf"\b{re.escape(k)}"
    return bool(re.search(pat, txt, re.IGNORECASE))


def _is_non_aviation_disaster(genre: str, title: str) -> bool:
    genre_up = (genre or "").upper()
    title_low = (title or "").lower()
    has_flight = any(_kw_match(k, title_low) for k in [
        "avión", "avion", "vuelo", "flight", "plane", "boeing", "airbus", "aircraft", "mayday", "aerolínea", "aeropuerto", "faa", "ntsb"
    ])
    if "CATASTROF" in genre_up and "AVIACION" not in genre_up:
        return not has_flight
    has_disaster = any(_kw_match(k, title_low) for k in [
        "lluvia", "lluvias", "inundaci", "sismo", "terremoto", "temblor", "huaico", "aluvión", "tsunami", "volcán", "volcan"
    ])
    return has_disaster and not has_flight


def _detect_category_flags(genre: str, title: str) -> Tuple[bool, bool, bool]:
    """Devuelve (is_cyber, is_ai, is_space) sin falsos positivos por subcadenas cortas."""
    title_low = (title or "").lower()
    genre_up = (genre or "G1").upper()

    if "G2" in genre_up or "CIBER" in genre_up:
        return True, False, False
    if "G3" in genre_up or "HARDWARE" in genre_up or "ROBOTICA" in genre_up:
        return False, True, False
    if "G4" in genre_up or "ESPACIO" in genre_up:
        return False, False, True
    if "AVIACION" in genre_up or "G1" in genre_up:
        return False, False, False

    is_cyber = any(_kw_match(k, title_low) for k in [
        "ciber", "hacker", "ransomware", "malware", "exploit", "breach", "zero-day", "dark web", "ciberataque", "ddos"
    ])
    is_ai = any(_kw_match(k, title_low) for k in [
        "ia", "ai", "chip", "chips", "semiconductor", "nvidia", "openai", "gemini", "hardware", "intel", "amd", "tsmc", "2nm"
    ])
    is_space = any(_kw_match(k, title_low) for k in [
        "espacio", "nasa", "esa", "orbita", "luna", "marte", "satelite", "cohete", "james webb", "astronomia", "spacex", "starship"
    ])
    return is_cyber, is_ai, is_space


# ==============================================================================
# 1. GENERADOR DE HASHTAGS Y COPY VIRAL PARA TIKTOK
# ==============================================================================

def generate_tiktok_hashtags(genre: str, title: str, source: str = "") -> Dict[str, Any]:
    """Genera el lote de hashtags categorizados y el copy optimizado para máxima viralidad."""
    is_cyber, is_ai, is_space = _detect_category_flags(genre, title)

    # Tags fundamentales de alcance masivo en TikTok
    core_tags = ["#tiktoknoticias", "#noticiashoy", "#parati", "#fyp", "#ultimahora", "#viral", "#aprendecontiktok"]

    # Tags temáticos según categoría
    if is_cyber:
        cat_tags = ["#ciberseguridad", "#hackers", "#seguridadinformatica", "#ransomware", "#tecnologia", "#darkweb", "#cybersecurity", "#ciberataque", "#techtok"]
        topic_emoji = "💻"
        category_name = "ALERTA DE CIBERSEGURIDAD"
        question_cta = "El incidente pone a prueba la resiliencia de los sistemas críticos frente a vectores de última generación."
    elif is_ai:
        cat_tags = ["#inteligenciaartificial", "#ia", "#chips", "#hardware", "#semiconductores", "#nvidia", "#tecnologia", "#futuro", "#techcrunch", "#techtok"]
        topic_emoji = "🤖"
        category_name = "TECNOLOGÍA & GUERRA DE CHIPS"
        question_cta = "Un avance decisivo en la arquitectura de cómputo que redefine la carrera global de hardware."
    elif is_space:
        cat_tags = ["#espacio", "#nasa", "#astronomia", "#universo", "#ciencia", "#exploracionespacial", "#satelite", "#cohete", "#cienciatiktok"]
        topic_emoji = "🚀"
        category_name = "MISIÓN ESPACIAL & CIENCIA EXTREMA"
        question_cta = "Un hito astronómico que abre una nueva era en la comprensión de nuestro sistema y el cosmos."
    elif _is_non_aviation_disaster(genre, title):
        cat_tags = ["#emergencia", "#alerta", "#catastrofe", "#climaextremo", "#desastrenatural", "#ultimahora", "#prevencion"]
        topic_emoji = "🚨"
        category_name = "ALERTA DE EMERGENCIA & CATÁSTROFES"
        question_cta = "Autoridades y equipos de rescate monitorean la evolución crítica en las zonas afectadas."
    else:
        # Default: Aviación
        cat_tags = ["#aviacion", "#accidenteaereo", "#emergenciaaerea", "#vuelo", "#pilotos", "#cajanegra", "#boeing", "#aeropuerto", "#seguridadaerea"]
        topic_emoji = "✈️"
        category_name = "AVIACIÓN & SEGURIDAD AÉREA"
        question_cta = "Las autoridades aeronáuticas y peritos analizan los parámetros de vuelo para el dictamen oficial."

    # Extracción de palabras clave del título
    clean_words = re.findall(r"[a-záéíóúñA-ZÁÉÍÓÚÑ0-9]{4,}", title)
    stop_words = {"para", "este", "esta", "estos", "estas", "como", "sobre", "entre", "desde", "hasta", "segun", "noticia", "reporte", "incluye", "medidas", "dictaran"}
    dynamic_tags = []
    for w in clean_words:
        w_low = w.lower()
        if w_low not in stop_words and len(dynamic_tags) < 3:
            tag = f"#{w_low}"
            if tag not in cat_tags and tag not in core_tags:
                dynamic_tags.append(tag)

    all_tags = cat_tags + dynamic_tags + core_tags
    # Deduplicar manteniendo orden
    seen = set()
    unique_tags = []
    for t in all_tags:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)

    hashtags_str = " ".join(unique_tags)

    # Redacción del Copy listo para pegar en TikTok
    tiktok_caption = (
        f"{topic_emoji} 🔴 {title.upper()}\n\n"
        f"🚨 Informe completo de última hora. {question_cta}\n\n"
        f"📡 Cobertura 24/7 en TikTok Radar.\n"
        f"{hashtags_str}"
    )

    return {
        "category_name": category_name,
        "topic_emoji": topic_emoji,
        "question_cta": question_cta,
        "hashtags": unique_tags,
        "hashtags_str": hashtags_str,
        "tiktok_caption": tiktok_caption,
    }


# ==============================================================================
# 2. GENERADOR DE TITULAR GANCHO EN ESPAÑOL (HIGH CTR)
# ==============================================================================

def extract_cover_headline(title: str, genre: str = "G1") -> List[Tuple[str, str]]:
    """
    Genera 2 o 3 líneas de titular gancho para portada 9:16 OBLIGATORIAMENTE EN ESPAÑOL,
    traduciendo y adaptando la noticia al lenguaje de impacto de TikTok.
    Colores: Línea 1 blanca, Línea 2 Amarillo Neón (#FFE500), Línea 3 blanca.
    """
    key = os.getenv("GEMINI_API_KEY")
    if key:
        prompt = f"""Genera el titular gancho para una miniatura/portada de TikTok en ESPAÑOL de ultra alto impacto (CTR masivo).
Noticia original: {title}
REGLAS ESTRICTAS:
- 100% EN ESPAÑOL (prohibido inglés salvo marcas como Nvidia, Google, Apple o siglas de dominio público).
- Exactamente 3 líneas de texto (máximo 2 a 3 palabras por línea).
- En MAYÚSCULAS y con lenguaje directo y dramático.
- Rigor factual: NO inventes fuego, llamas, explosiones ni víctimas si el titular original no los menciona.
- Formato de respuesta JSON estricto: ["LINEA 1", "LINEA 2", "LINEA 3"]"""

        for model in ["gemini-3.5-flash-lite", "gemini-3.8-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
                body = {"contents": [{"parts": [{"text": prompt}]}]}
                req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = json.load(resp)
                    ans = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    m = re.search(r'\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]', ans)
                    if m:
                        l1, l2, l3 = m.group(1).strip().upper(), m.group(2).strip().upper(), m.group(3).strip().upper()
                        return [(l1, "white"), (l2, "#FFE500"), (l3, "white")]
            except Exception:
                pass

    clean_title = re.sub(r"^[¿\s]+|[?!\s]+$", "", title or "").strip()
    if ":" in clean_title:
        clean_title = clean_title.split(":")[0].strip()

    title_low = clean_title.lower()

    # Detecciones contextuales específicas en español
    if any(k in title_low for k in ["lluvia", "lluvias", "inundaci", "aluvion"]):
        return [("ESTADO DE", "white"), ("EMERGENCIA", "#FFE500"), ("POR LLUVIAS", "white")]
    if any(k in title_low for k in ["sismo", "terremoto", "temblor"]):
        return [("ALERTA SÍSMICA", "white"), ("TERREMOTO", "#FFE500"), ("EN EL PERÚ", "white")]
    if any(k in title_low for k in ["victima", "víctima", "victimas", "víctimas"]):
        return [("ACCIDENTE AÉREO", "white"), ("VÍCTIMAS", "#FFE500"), ("CONFIRMADAS", "white")]
    if any(k in title_low for k in ["altitud", "mayday", "vuelo", "aereo", "avion", "caida", "plane", "flight"]):
        return [("MAYDAY EN VUELO", "white"), ("CAÍDA CRÍTICA", "#FFE500"), ("DE ALTITUD", "white")]
    if any(k in title_low for k in ["ciber", "hacker", "ransomware", "hospital", "breach", "cyber"]):
        return [("CIBERATAQUE", "white"), ("PARALIZA REDES", "#FFE500"), ("ZERO-DAY", "white")]
    if any(k in title_low for k in ["china", "nvidia", "gpu", "order", "export"]):
        return [("CHINA", "white"), ("SE QUEDA", "#FFE500"), ("SIN CHIPS", "white")]
    if any(k in title_low for k in ["2nm", "chip", "semiconductor", "tsmc", "intel", "hardware"]):
        return [("NUEVO CHIP 2NM", "white"), ("REVOLUCIÓN", "#FFE500"), ("EN HARDWARE", "white")]
    if any(k in title_low for k in ["espacio", "nasa", "luna", "orbita", "sonda", "space"]):
        return [("MISIÓN ESPACIAL", "white"), ("ALERTA ORBITAL", "#FFE500"), ("EN VIVO", "white")]

    return [("ALERTA DE", "white"), ("ÚLTIMA HORA", "#FFE500"), ("EN VIVO", "white")]


# ==============================================================================
# 3. GENERADOR DE FONDO CON MODELO DE IA DEDICADO (FLUX / RAYTRACING)
# ==============================================================================

def _make_chiaroscuro_backdrop(accent_rgb: Tuple[int, int, int], theme: str = "universal") -> Image.Image:
    """Genera un fondo documental claroscuro 1080x1920 con geometría temática vectorial (sin marcas de agua)."""
    w, h = 1080, 1920
    img = Image.new("RGBA", (w, h), (8, 12, 20, 255))
    draw = ImageDraw.Draw(img)

    # Gradiente radial central suave
    ar, ag, ab = accent_rgb
    cx, cy = w // 2, 820
    for r in range(900, 40, -24):
        t = 1.0 - (r / 900.0)
        cr = int(8 + ar * 0.22 * (t ** 1.6))
        cg = int(12 + ag * 0.22 * (t ** 1.6))
        cb = int(20 + ab * 0.22 * (t ** 1.6))
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(cr, cg, cb, 255))

    # Grilla táctica sutil
    for gx in range(0, w, 90):
        draw.line([(gx, 0), (gx, h)], fill=(255, 255, 255, 11), width=1)
    for gy in range(0, h, 90):
        draw.line([(0, gy), (w, gy)], fill=(255, 255, 255, 11), width=1)

    # Geometría editorial sutil acorde al género (cero texto ruidoso ni marcas de agua)
    ring_col = (ar, ag, ab, 48)
    ring_soft = (255, 255, 255, 26)
    if theme == "space":
        for rad in (260, 420, 620):
            draw.arc([cx - rad, cy - int(rad * 0.48), cx + rad, cy + int(rad * 0.48)], 0, 360, fill=ring_col, width=2)
        draw.ellipse([cx - 560, 1180, cx + 560, 2300], outline=ring_soft, width=2)
    elif theme == "cyber":
        for rad in (220, 380, 540, 700):
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=ring_col, width=2)
        draw.line([(cx - 720, cy), (cx + 720, cy)], fill=ring_soft, width=1)
        draw.line([(cx, cy - 720), (cx, cy + 720)], fill=ring_soft, width=1)
    elif theme == "hardware":
        for step in (240, 380, 520):
            draw.rectangle([cx - step, cy - step, cx + step, cy + step], outline=ring_col, width=2)
        for off in (-320, -160, 160, 320):
            draw.line([(cx + off, 280), (cx + off, cy - 240)], fill=ring_soft, width=2)
            draw.line([(cx + off, cy + 240), (cx + off, 1640)], fill=ring_soft, width=2)
    else:
        for rad in (260, 440, 620):
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=ring_col, width=2)
        draw.line([(90, cy), (w - 90, cy)], fill=ring_soft, width=2)

    return img


def _try_gemini_image_cover(prompt: str, timeout_sec: int = 25) -> Optional[bytes]:
    """Intenta generar fondo limpio 9:16 vía Gemini Native Image API si GEMINI_API_KEY tiene cuota."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    for model in ("gemini-2.5-flash-image", "gemini-3.1-flash-image"):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"]},
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                res = json.loads(resp.read().decode("utf-8"))
            parts = res.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            for part in parts:
                inline = part.get("inlineData") or {}
                b64_data = inline.get("data")
                if b64_data:
                    raw = base64.b64decode(b64_data)
                    if len(raw) >= 35_000:
                        return raw
        except Exception as e:
            print(f"[PORTADA-AI] Aviso {model}: {e}", flush=True)
    return None


def generate_ai_cover_background(genre: str, title: str, delivery_dir: Path, force_regen: bool = False) -> Image.Image:
    """
    Genera u obtiene el fondo oficial de la portada en vertical 9:16 (1080x1920):
    1. Si existe un plano cinematográfico Flow (SH02/SH07), extrae un fotograma nítido libre de marcas de agua.
    2. Si existe caché válido PORTADA_AI_BASE.jpg, lo reutiliza salvo force_regen.
    3. Intenta Gemini Native Image API y solo usa Pollinations si hay POLLINATIONS_API_KEY autenticada (para evitar marcas de agua).
    4. Fallback: fotograma limpio si hubo Flow, o fondo claroscuro vectorial temático sin marcas de agua.
    """
    is_cyber, is_ai, is_space = _detect_category_flags(genre, title)
    is_disaster = _is_non_aviation_disaster(genre, title)
    theme_name = "cyber" if is_cyber else ("hardware" if is_ai else ("space" if is_space else "aviation"))

    # 1. Priorizar fotograma cinematográfico real de Google Flow si existe (cero marcas de agua y máxima coherencia)
    shots_dir = delivery_dir / "shots"
    for cand_shot in ["SH07.mp4", "SH02.mp4", "SH12.mp4"]:
        cand_path = shots_dir / cand_shot
        if cand_path.exists() and cand_path.stat().st_size > 100_000:
            tmp_shot_frame = delivery_dir / "_temp_flow_cover.jpg"
            cmd = [
                "ffmpeg", "-y", "-ss", "00:00:01.5", "-i", str(cand_path),
                "-frames:v", "1", "-q:v", "2", str(tmp_shot_frame)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if tmp_shot_frame.exists() and tmp_shot_frame.stat().st_size > 20_000:
                try:
                    raw_img = Image.open(tmp_shot_frame).convert("RGBA")
                    raw_img = raw_img.resize((1080, 1920), Image.Resampling.LANCZOS)
                    tmp_shot_frame.unlink(missing_ok=True)
                    print(f"[PORTADA] 🎬 Fondo extraído directamente de plano Flow ({cand_shot}).", flush=True)
                    return raw_img
                except Exception:
                    tmp_shot_frame.unlink(missing_ok=True)

    # 2. Caché existente de portada IA si es válido (>35KB)
    ai_cache = delivery_dir / "PORTADA_AI_BASE.jpg"
    if not force_regen and ai_cache.exists() and ai_cache.stat().st_size > 35_000:
        try:
            cached = Image.open(ai_cache).convert("RGBA")
            cached = cached.resize((1080, 1920), Image.Resampling.LANCZOS)
            print(f"[PORTADA-AI] ♻️ Reutilizando PORTADA_AI_BASE.jpg en caché.", flush=True)
            return cached
        except Exception:
            pass

    base_style = (
        "Vertical 9:16, prestigious scientific documentary poster aesthetic, dramatic chiaroscuro studio lighting, "
        "deep carbon vignetted shadows with directional rim light, tactile textured surface patina inspired by Veritasium "
        "and Jakub Misiek illustrations, subtle analog film grain, high subject contrast, masterpiece quality, no text, no captions, no watermark"
    )

    clean_title_ctx = re.sub(r"[^\w\s\-:]", " ", title or "").strip()[:100]
    if is_cyber:
        prompt = (
            f"{base_style}, scene inspired by '{clean_title_ctx}', matte black server vault corridor in deep carbon shadows, "
            f"single dramatic spotlight on fiber optic cables, subtle crimson LED pulse, cyber investigation mood"
        )
        accent_rgb = (230, 57, 70)
    elif is_ai:
        prompt = (
            f"{base_style}, scene inspired by '{clean_title_ctx}', glowing nanometer microchip silicon wafer floating in dark cleanroom space, "
            f"amber golden chiaroscuro lighting, intricate sub-micron traces"
        )
        accent_rgb = (244, 162, 97)
    elif is_space:
        prompt = (
            f"{base_style}, scene inspired by '{clean_title_ctx}', spacecraft or launch booster illuminated by warm chiaroscuro spotlight "
            f"against deep cosmic darkness and orbital atmospheric rim light"
        )
        accent_rgb = (255, 183, 3)
    elif is_disaster:
        prompt = (
            f"{base_style}, scene inspired by '{clean_title_ctx}', dramatic emergency lights cutting through storm mist at night, "
            f"cinematic chiaroscuro atmosphere, deep slate shadows"
        )
        accent_rgb = (251, 133, 0)
    else:
        prompt = (
            f"{base_style}, scene inspired by '{clean_title_ctx}', twin-engine jet banking through dark storm clouds, "
            f"dramatic amber cockpit rim light, wing beacon cutting volumetric mist"
        )
        accent_rgb = (251, 133, 0)

    # 3A. Intentar Gemini Native Image API (cero marcas de agua y alta fidelidad al titular)
    gemini_bytes = _try_gemini_image_cover(prompt)
    if gemini_bytes:
        try:
            img = Image.open(io.BytesIO(gemini_bytes)).convert("RGBA")
            img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
            ai_cache.write_bytes(gemini_bytes)
            print(f"[PORTADA-AI] ✅ Imagen de portada generada con Gemini Image ({len(gemini_bytes)} bytes)", flush=True)
            return img
        except Exception as e:
            print(f"[PORTADA-AI] ⚠️ Error decodificando imagen Gemini: {e}", flush=True)

    # 3B. Pollinations solo si hay API key explícita (el tier anónimo estampa marca de agua pollinations.ai)
    pollinations_key = os.environ.get("POLLINATIONS_API_KEY", "").strip()
    if pollinations_key:
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&model=flux&nologo=true"
        try:
            print("[PORTADA-AI] 🎨 Generando fondo cinemático 9:16 con Pollinations autenticado...", flush=True)
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0", "Authorization": f"Bearer {pollinations_key}"},
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                ctype = (resp.headers.get("Content-Type") or "").lower()
                data = resp.read()
                if "image" not in ctype or len(data) < 35_000:
                    raise RuntimeError(f"Respuesta no válida de API imagen ({ctype}, {len(data)} bytes)")
                img = Image.open(io.BytesIO(data)).convert("RGBA")
                img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                ai_cache.write_bytes(data)
                print(f"[PORTADA-AI] ✅ Imagen de portada generada por IA con éxito: {len(data)} bytes", flush=True)
                return img
        except Exception as e:
            print(f"[PORTADA-AI] ⚠️ Falló Pollinations autenticado: {e}. Activando fallback limpio...", flush=True)

    # 4. Fallback a fotograma limpio SOLO si hubo planos Flow en shots/, o fondo claroscuro vectorial limpio
    video_mp4 = delivery_dir / "NOTICIERO_FINAL_62S.mp4"
    tmp_frame = delivery_dir / "_temp_raw_frame.jpg"
    has_any_flow = shots_dir.exists() and any(shots_dir.glob("SH*.mp4"))
    if has_any_flow and video_mp4.exists() and video_mp4.stat().st_size > 100_000:
        cmd = [
            "ffmpeg", "-y",
            "-ss", "00:00:08.0",
            "-i", str(video_mp4),
            "-frames:v", "1",
            "-q:v", "2",
            str(tmp_frame)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if tmp_frame.exists():
            try:
                raw_img = Image.open(tmp_frame).convert("RGBA")
                raw_img = raw_img.resize((1080, 1920), Image.Resampling.LANCZOS)
                bg = raw_img.filter(ImageFilter.GaussianBlur(radius=4))
                tmp_frame.unlink(missing_ok=True)
                return bg
            except Exception:
                tmp_frame.unlink(missing_ok=True)

    print("[PORTADA] 🛡️ Usando fondo vectorial claroscuro limpio (cero marcas de agua).", flush=True)
    return _make_chiaroscuro_backdrop(accent_rgb, theme=theme_name)


# ==============================================================================
# 4. COMPOSICIÓN GRÁFICA DE LA PORTADA 9:16 (1080x1920)
# ==============================================================================

def generate_tiktok_cover(delivery_dir: Path, output_filename: str = "PORTADA_TIKTOK_916.jpg") -> Path:
    """
    Sintetiza la portada oficial en 9:16 (1080x1920) con renderizado vectorial, safe zone 3:4,
    badge superior, titular de alto impacto y rótulos de broadcast.
    """
    delivery_dir = Path(delivery_dir).resolve()
    meta_file = delivery_dir / "metadata.json"
    meta = {}
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    title = meta.get("title", "ALERTA DE ÚLTIMA HORA")
    genre = meta.get("genre", "G1")
    source = meta.get("source", "PRENSA OFICIAL")

    # 1. Obtener fondo generado por Modelo de IA dedicado
    bg_img = generate_ai_cover_background(genre, title, delivery_dir)

    # 2. Capa de oscurecimiento y gradientes profesionales
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    # Gradiente superior suave (0 a 500)
    for y in range(0, 500):
        alpha = int(210 * (1 - y / 500)**1.2)
        draw_ov.line([(0, y), (1080, y)], fill=(6, 12, 24, alpha))

    # Gradiente inferior suave (1220 a 1920) sin bloque opaco abrupto
    for y in range(1220, 1920):
        factor = min(1.0, (y - 1220) / 700)
        alpha = int(215 * factor)
        draw_ov.line([(0, y), (1080, y)], fill=(6, 12, 24, alpha))

    # Determinación de colores adaptativos por temática
    is_cyber, is_ai, is_space = _detect_category_flags(genre, title)
    is_disaster = _is_non_aviation_disaster(genre, title)
    if is_cyber:
        accent_hex = "#E63946"
        border_rgba = (230, 57, 70, 220)
        inner_rgba = (241, 250, 238, 90)
        badge_bg = (180, 20, 30)
        badge_label = "CIBERATAQUE CRÍTICO EN VIVO"
        sub_text = "INFORME EN 60s · CENTRO SOC ALERTA ZERO-DAY"
    elif is_ai:
        accent_hex = "#F4A261"
        border_rgba = (244, 162, 97, 220)
        inner_rgba = (231, 111, 81, 100)
        badge_bg = (200, 75, 40)
        badge_label = "GUERRA DE CHIPS Y HARDWARE"
        sub_text = "INFORME EN 60s · LITOGRAFÍA 2NM HIGH-NA"
    elif is_space:
        accent_hex = "#FFB703"
        border_rgba = (255, 183, 3, 220)
        inner_rgba = (157, 78, 221, 110)
        badge_bg = (120, 35, 180)
        badge_label = "MISIÓN ESPACIAL EN VIVO"
        sub_text = "INFORME EN 60s · TELEMETRÍA DEEP SPACE"
    elif is_disaster:
        accent_hex = "#FB8500"
        border_rgba = (251, 133, 0, 220)
        inner_rgba = (255, 255, 255, 90)
        badge_bg = (190, 35, 30)
        badge_label = "ALERTA DE EMERGENCIA EN VIVO"
        sub_text = "INFORME EN 60s · COBERTURA DE CATÁSTROFE"
    else:
        # Default: Aviación
        accent_hex = "#FB8500"
        border_rgba = (251, 133, 0, 220)
        inner_rgba = (255, 255, 255, 90)
        badge_bg = (210, 30, 30)
        badge_label = "EMERGENCIA AÉREA EN VIVO"
        sub_text = "INFORME EN 60s · RADAR TÁCTICO DE VUELO"

    # Caja central táctica en Safe Zone TikTok 3:4 (Y: 560 a 1210, bien encima de 1400)
    center_box = [(40, 560), (1040, 1210)]
    draw_ov.rounded_rectangle(center_box, radius=28, fill=(14, 18, 26, 240), outline=border_rgba, width=3)
    draw_ov.rounded_rectangle([(46, 566), (1034, 1204)], radius=22, fill=(0, 0, 0, 0), outline=inner_rgba, width=1)

    img = Image.alpha_composite(bg_img, overlay)
    draw = ImageDraw.Draw(img)

    # 3. Tipografías cargadas (prioriza Montserrat oficial)
    font_bold_path = FONT_BOLD if Path(FONT_BOLD).exists() else "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    f_badge = ImageFont.truetype(font_bold_path, 32)
    f_sub = ImageFont.truetype(font_bold_path, 26)
    f_foot = ImageFont.truetype(font_bold_path, 25)

    # 4. Badge Superior (Píldora de Impacto)
    badge_bbox = f_badge.getbbox(badge_label)
    bw = min(940, badge_bbox[2] - badge_bbox[0] + 70)
    bh = 60
    bx = (1080 - bw) // 2
    by = 600

    draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=30, fill=badge_bg, outline=(255, 255, 255), width=2)
    draw.ellipse([(bx + 18, by + 18), (bx + 42, by + 42)], fill=(255, 255, 255))
    draw.ellipse([(bx + 23, by + 23), (bx + 37, by + 37)], fill=(255, 220, 0))
    draw.text((bx + 52, by + 12), badge_label, font=f_badge, fill="white")

    # 5. Titular Gancho con ajuste dinámico de tamaño para no desbordar caja (x=40..1040)
    headline_lines = extract_cover_headline(title, genre)
    title_size = 66
    while title_size > 44:
        f_test = ImageFont.truetype(font_bold_path, title_size)
        if all((f_test.getbbox(ln)[2] - f_test.getbbox(ln)[0]) <= 910 for ln, _ in headline_lines):
            break
        title_size -= 4
    f_title = ImageFont.truetype(font_bold_path, title_size)

    start_y = 705 if len(headline_lines) == 3 else 750

    for text_line, color in headline_lines:
        t_bbox = f_title.getbbox(text_line)
        tw = t_bbox[2] - t_bbox[0]
        tx = (1080 - tw) // 2
        draw.text((tx + 5, start_y + 5), text_line, font=f_title, fill="black")
        draw.text((tx, start_y), text_line, font=f_title, fill=color, stroke_width=7, stroke_fill="black")
        start_y += int(title_size * 1.28)

    # 6. Píldora inferior contextual dentro de la caja táctica
    sub_bbox = f_sub.getbbox(sub_text)
    sw = min(940, sub_bbox[2] - sub_bbox[0] + 40)
    sh = 52
    sx = (1080 - sw) // 2
    sy = 1110
    draw.rounded_rectangle([(sx, sy), (sx + sw, sy + sh)], radius=16, fill=(18, 24, 34), outline=border_rgba, width=2)
    draw.text((sx + 20, sy + 12), sub_text, font=f_sub, fill=accent_hex)

    # 7. Rótulos informativos dentro de la Safe Zone TikTok (Y: 140..1400)
    foot_text = "RADAR 24/7 · REPORTE OFICIAL VERIFICADO"
    fb_box = f_foot.getbbox(foot_text)
    fw = fb_box[2] - fb_box[0]
    fx = (1080 - fw) // 2
    draw.text((fx, 1265), foot_text, font=f_foot, fill="#E0E0E0")

    top_text = f"INFORME ESPECIAL · {source.upper()}"
    tb_box = f_foot.getbbox(top_text)
    tw = tb_box[2] - tb_box[0]
    tx = (1080 - tw) // 2
    draw.text((tx, 290), top_text, font=f_foot, fill="#F0F0F0")

    # 8. Exportar portada final
    out_cover_jpg = delivery_dir / output_filename
    img_rgb = img.convert("RGB")
    img_rgb.save(out_cover_jpg, quality=95)

    # 9. Generar Hashtags y Copy para TikTok
    tag_info = generate_tiktok_hashtags(genre, title, source)
    hashtags_file = delivery_dir / "HASHTAGS_TIKTOK.txt"
    hashtags_file.write_text(tag_info["tiktok_caption"], encoding="utf-8")

    # 10. Actualizar metadata.json con los datos de portada y hashtags
    meta["cover_file"] = output_filename
    meta["hashtags"] = tag_info["hashtags"]
    meta["hashtags_str"] = tag_info["hashtags_str"]
    meta["tiktok_caption"] = tag_info["tiktok_caption"]
    meta["category_badge"] = badge_label
    meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    # 11. Actualizar PAQUETE_NOTICIERO_LISTO.md
    report_file = delivery_dir / "PAQUETE_NOTICIERO_LISTO.md"
    if report_file.exists():
        content = report_file.read_text(encoding="utf-8")
        if "## Portada 9:16 y Hashtags de TikTok" not in content:
            addon = (
                f"\n\n## Portada 9:16 y Hashtags de TikTok\n\n"
                f"- **Portada Oficial 9:16:** `{output_filename}` (1080x1920 centrada en safe zone 3:4)\n"
                f"- **Copy y Hashtags Listos para Pegar:**\n\n"
                f"```text\n{tag_info['tiktok_caption']}\n```\n"
            )
            report_file.write_text(content + addon, encoding="utf-8")

    print(f"✅ Portada 9:16 generada: {out_cover_jpg} ({out_cover_jpg.stat().st_size / 1024:.1f} KB)")
    print(f"✅ Hashtags generados en: {hashtags_file}")
    return out_cover_jpg


def main():
    parser = argparse.ArgumentParser(description="Generador de Portadas 9:16 y Hashtags TikTok")
    parser.add_argument("--dir", type=str, default=None, help="Carpeta de entrega (por defecto la más reciente)")
    args = parser.parse_args()

    if args.dir:
        target_dir = Path(args.dir).resolve()
    else:
        candidates = sorted(
            [d for d in ENTREGAS_DIR.iterdir() if d.is_dir() and (d / "metadata.json").exists()],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            print(f"Error: No hay carpetas de entrega en {ENTREGAS_DIR}")
            sys.exit(1)
        target_dir = candidates[0]

    print(f"Generando portada y hashtags para: {target_dir.name}")
    generate_tiktok_cover(target_dir)


if __name__ == "__main__":
    main()
