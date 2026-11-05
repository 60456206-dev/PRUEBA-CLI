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
for _env_p in [Path.home() / ".api_keys.env", Path("/workspaces/PRUEBA-CLI/.api_keys.env")]:
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
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _kw_match(k: str, txt: str) -> bool:
    return bool(re.search(rf"\b{re.escape(k)}\b", txt)) if len(k) <= 3 else (k in txt)


def _detect_category_flags(genre: str, title: str) -> Tuple[bool, bool, bool, bool]:
    """Devuelve (is_peru, is_cyber, is_ai, is_space) sin falsos positivos por subcadenas cortas."""
    title_low = (title or "").lower()
    genre_up = (genre or "G1").upper()

    if "PERU" in genre_up or "DESASTRE" in genre_up:
        return True, False, False, False
    if "G2" in genre_up or "CIBER" in genre_up:
        return False, True, False, False
    if "G3" in genre_up or "HARDWARE" in genre_up or "ROBOTICA" in genre_up:
        return False, False, True, False
    if "G4" in genre_up or "ESPACIO" in genre_up:
        return False, False, False, True
    if "AVIACION" in genre_up:
        return False, False, False, False

    is_peru = any(_kw_match(k, title_low) for k in [
        "perú", "peru", "lima", "arequipa", "piura", "indeci", "sismo", "huaico", "terremoto",
        "lluvias", "lluvia", "andina", "rpp", "el niño", "costa verde"
    ])
    is_cyber = any(_kw_match(k, title_low) for k in [
        "ciber", "hacker", "ransomware", "malware", "exploit", "breach", "zero-day", "dark web", "ciberataque", "ddos"
    ])
    is_ai = any(_kw_match(k, title_low) for k in [
        "ia", "ai", "chip", "chips", "semiconductor", "nvidia", "openai", "gemini", "hardware", "intel", "amd", "tsmc", "2nm"
    ])
    is_space = any(_kw_match(k, title_low) for k in [
        "espacio", "nasa", "esa", "orbita", "luna", "marte", "satelite", "cohete", "james webb", "astronomia", "spacex", "starship"
    ])
    return is_peru, is_cyber, is_ai, is_space


# ==============================================================================
# 1. GENERADOR DE HASHTAGS Y COPY VIRAL PARA TIKTOK
# ==============================================================================

def generate_tiktok_hashtags(genre: str, title: str, source: str = "") -> Dict[str, Any]:
    """Genera el lote de hashtags categorizados y el copy optimizado para máxima viralidad."""
    is_peru, is_cyber, is_ai, is_space = _detect_category_flags(genre, title)

    # Tags fundamentales de alcance masivo en TikTok
    core_tags = ["#tiktoknoticias", "#noticiashoy", "#parati", "#fyp", "#ultimahora", "#viral", "#aprendecontiktok"]

    # Tags temáticos según categoría
    if is_peru:
        cat_tags = ["#peru", "#noticiasperu", "#indeci", "#sismo", "#terremoto", "#emergenciaperu", "#lima", "#alertaperu", "#rppnoticias", "#noticiastiktok"]
        topic_emoji = "🇵🇪"
        category_name = "EMERGENCIA NACIONAL PERÚ"
        question_cta = "¿Consideras que las autoridades están preparadas para esta emergencia? Comenta 👇"
    elif is_cyber:
        cat_tags = ["#ciberseguridad", "#hackers", "#seguridadinformatica", "#ransomware", "#tecnologia", "#darkweb", "#cybersecurity", "#ciberataque", "#techtok"]
        topic_emoji = "💻"
        category_name = "ALERTA DE CIBERSEGURIDAD"
        question_cta = "¿Crees que los sistemas bancarios y de salud son realmente seguros? Deja tu opinión 👇"
    elif is_ai:
        cat_tags = ["#inteligenciaartificial", "#ia", "#chips", "#hardware", "#semiconductores", "#nvidia", "#tecnologia", "#futuro", "#techcrunch", "#techtok"]
        topic_emoji = "🤖"
        category_name = "TECNOLOGÍA & GUERRA DE CHIPS"
        question_cta = "¿Crees que este nuevo avance superará la inteligencia humana pronto? Te leo en comentarios 👇"
    elif is_space:
        cat_tags = ["#espacio", "#nasa", "#astronomia", "#universo", "#ciencia", "#exploracionespacial", "#satelite", "#cohete", "#cienciatiktok"]
        topic_emoji = "🚀"
        category_name = "MISIÓN ESPACIAL & CIENCIA EXTREMA"
        question_cta = "¿Tendremos colonias humanas en la Luna antes del 2030? Comenta tu predicción 👇"
    else:
        # Default: Aviación
        cat_tags = ["#aviacion", "#accidenteaereo", "#emergenciaaerea", "#vuelo", "#pilotos", "#cajanegra", "#boeing", "#aeropuerto", "#seguridadaerea"]
        topic_emoji = "✈️"
        category_name = "AVIACIÓN & SEGURIDAD AÉREA"
        question_cta = "¿Qué crees que falló en los protocolos de vuelo? Déjame tu punto de vista 👇"

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

def generate_ai_cover_background(genre: str, title: str, delivery_dir: Path) -> Image.Image:
    """
    Genera el fondo oficial de la portada en vertical 9:16 (1080x1920) utilizando un modelo de IA
    dedicado a creación de imágenes (Flux / Pollinations API) con estética cinematográfica y raytracing.
    """
    is_peru, is_cyber, is_ai, is_space = _detect_category_flags(genre, title)

    if is_peru:
        prompt = (
            "Dramatic cinematic vertical 9:16 poster background of torrential rains, flood waters rushing, "
            "emergency rescue convoy lights in Peruvian mountain valley, Unreal Engine 5.4 Lumen raytracing, "
            "volumetric mist, dark tactical mood, masterpiece 3D render, no text, no people"
        )
    elif is_cyber:
        prompt = (
            "Dramatic cinematic vertical 9:16 poster background of high-density server vault corridor with cold neon cyan "
            "and warning crimson LED lights, glowing fiber optics, RTX raytracing reflections on matte black server racks, "
            "dark cyber thriller aesthetic, masterpiece 3D render, no text"
        )
    elif is_ai:
        prompt = (
            "Dramatic cinematic vertical 9:16 poster background of a glowing 2nm microchip silicon wafer floating with "
            "intricate iridescent golden circuits, Unreal Engine 5.4 Lumen raytracing reflections, dark high-tech cleanroom "
            "laboratory atmosphere, volumetric lighting, no text, no people, no face masks"
        )
    elif is_space:
        prompt = (
            "Dramatic cinematic vertical 9:16 poster background of an advanced interplanetary spacecraft with glowing "
            "violet plasma thrusters in deep space, crescent Earth curvature below, Octane path tracer lighting, starry background, no text"
        )
    else:
        prompt = (
            "Dramatic cinematic vertical 9:16 poster background of a modern executive jet flying through dark stormy clouds and rain, "
            "cockpit glowing with amber alarm lights and cyan glass screens, RTX raytracing reflections, cinematic angle, no text"
        )

    ai_cache = delivery_dir / "PORTADA_AI_BASE.jpg"
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&model=flux&nologo=true"

    try:
        print("[PORTADA-AI] 🎨 Generando fondo cinemático 9:16 con modelo de IA dedicado (Flux)...", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
            ai_cache.write_bytes(data)
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
            print(f"[PORTADA-AI] ✅ Imagen de portada generada por IA con éxito: {len(data)} bytes", flush=True)
            return img
    except Exception as e:
        print(f"[PORTADA-AI] ⚠️ Falló generación con modelo de IA: {e}. Activando fallback...", flush=True)

    # Fallback a fotograma del vídeo o gradiente
    video_mp4 = delivery_dir / "NOTICIERO_FINAL_62S.mp4"
    tmp_frame = delivery_dir / "_temp_raw_frame.jpg"
    if video_mp4.exists() and video_mp4.stat().st_size > 100_000:
        cmd = [
            "ffmpeg", "-y",
            "-ss", "00:00:03.0",
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
                bg = raw_img.filter(ImageFilter.GaussianBlur(radius=5))
                tmp_frame.unlink(missing_ok=True)
                return bg
            except Exception:
                pass

    return Image.new("RGBA", (1080, 1920), (6, 15, 30, 255))


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

    # Gradiente superior (0 a 540)
    for y in range(0, 540):
        alpha = int(240 * (1 - y / 540)**1.2)
        draw_ov.line([(0, y), (1080, y)], fill=(6, 12, 24, alpha))

    # Gradiente inferior (1180 a 1920) - 100% opaco a partir de 1320 para limpiar texto inferior
    for y in range(1180, 1920):
        factor = min(1.0, (y - 1180) / 140)
        alpha = int(255 * factor)
        draw_ov.line([(0, y), (1080, y)], fill=(6, 12, 24, alpha))

    # Caja central táctica en Safe Zone TikTok 3:4 (Y: 570 a 1220)
    center_box = [(40, 570), (1040, 1220)]
    draw_ov.rounded_rectangle(center_box, radius=28, fill=(8, 16, 28, 238), outline=(0, 229, 255, 190), width=3)
    draw_ov.rounded_rectangle([(46, 576), (1034, 1214)], radius=22, fill=(0, 0, 0, 0), outline=(255, 170, 0, 90), width=1)

    img = Image.alpha_composite(bg_img, overlay)
    draw = ImageDraw.Draw(img)

    # 3. Tipografías cargadas
    font_bold_path = FONT_BOLD if Path(FONT_BOLD).exists() else "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    f_badge = ImageFont.truetype(font_bold_path, 32)
    f_title = ImageFont.truetype(font_bold_path, 68)
    f_sub = ImageFont.truetype(font_bold_path, 28)
    f_foot = ImageFont.truetype(font_bold_path, 26)

    # 4. Badge Superior (Píldora Roja de Impacto)
    is_peru, is_cyber, is_ai, is_space = _detect_category_flags(genre, title)

    if is_peru:
        badge_label = "ALERTA MAXIMA EN PERU"
        sub_text = "INFORME EN 60s · INDECI ACTIVA PROTOCOLO"
    elif is_cyber:
        badge_label = "CIBERATAQUE CRITICO EN VIVO"
        sub_text = "INFORME EN 60s · CENTRO SOC ALERTA ZERO-DAY"
    elif is_ai:
        badge_label = "GUERRA DE CHIPS Y HARDWARE"
        sub_text = "INFORME EN 60s · LITOGRAFIA 2NM HIGH-NA"
    elif is_space:
        badge_label = "MISIÓN ESPACIAL EN VIVO"
        sub_text = "INFORME EN 60s · TELEMETRIA DEEP SPACE NASA"
    else:
        badge_label = "EMERGENCIA AEREA EN VIVO"
        sub_text = "INFORME EN 60s · RADAR TACTICO DE VUELO"

    badge_bbox = f_badge.getbbox(badge_label)
    bw = badge_bbox[2] - badge_bbox[0] + 70
    bh = 60
    bx = (1080 - bw) // 2
    by = 610

    # Dibujar cápsula con punto de luz rojo de alerta
    draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=30, fill=(225, 15, 35), outline=(255, 255, 255), width=2)
    draw.ellipse([(bx + 18, by + 18), (bx + 42, by + 42)], fill=(255, 255, 255))
    draw.ellipse([(bx + 23, by + 23), (bx + 37, by + 37)], fill=(255, 220, 0))
    draw.text((bx + 52, by + 12), badge_label, font=f_badge, fill="white")

    # 5. Titular Gancho (2 a 3 líneas de texto contrastado)
    headline_lines = extract_cover_headline(title, genre)
    start_y = 715 if len(headline_lines) == 3 else 760

    for text_line, color in headline_lines:
        t_bbox = f_title.getbbox(text_line)
        tw = t_bbox[2] - t_bbox[0]
        tx = (1080 - tw) // 2
        # Sombra negra profunda
        draw.text((tx + 5, start_y + 5), text_line, font=f_title, fill="black")
        # Trazo negro grueso de 7px para corte agresivo
        draw.text((tx, start_y), text_line, font=f_title, fill=color, stroke_width=7, stroke_fill="black")
        start_y += 88

    # 6. Píldora inferior contextual dentro de la caja táctica
    sub_bbox = f_sub.getbbox(sub_text)
    sw = sub_bbox[2] - sub_bbox[0] + 40
    sh = 52
    sx = (1080 - sw) // 2
    sy = 1120
    draw.rounded_rectangle([(sx, sy), (sx + sw, sy + sh)], radius=16, fill=(12, 28, 48), outline=(0, 229, 255), width=2)
    draw.text((sx + 20, sy + 11), sub_text, font=f_sub, fill="#00E5FF")

    # 7. Rótulos informativos fuera de la caja
    foot_text = "RADAR 24/7 · COMENTA TU OPINION ▼"
    fb_box = f_foot.getbbox(foot_text)
    fw = fb_box[2] - fb_box[0]
    fx = (1080 - fw) // 2
    draw.text((fx, 1540), foot_text, font=f_foot, fill="#AAAAAA")

    top_text = f"INFORME ESPECIAL · {source.upper()}"
    tb_box = f_foot.getbbox(top_text)
    tw = tb_box[2] - tb_box[0]
    tx = (1080 - tw) // 2
    draw.text((tx, 340), top_text, font=f_foot, fill="#00E5FF")

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
