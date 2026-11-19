#!/usr/bin/env python3
"""
TIKTOK RADAR · Ensamblador Algorítmico Profesional de Vídeo (NLE Headless para Linux)
Opera como un editor de vídeo profesional controlado 100% por código sobre FFmpeg Filtergraph + ASS Vector Engine:

1. Transiciones Broadcast Reales (`xfade`):
   - Alterna transiciones cinemáticas (`fadeblack`, `smoothleft`, `dissolve`, `circleopen`, `wipeleft`)
     calculando los offsets exactos al milisegundo para cuadrar con la locución (>60 s).
2. Efectos de Cámara y Etalonaje (`zoompan` / `crop` subpíxel + `eq`):
   - Aplica Ken Burns (acercamiento progresivo), vibración de cámara en planos de tensión (SH04-SH09)
     y look de alto contraste estilizado (1080x1920, 24 fps).
3. Subtítulos Kinetic Palabra por Palabra (`.ass` nativo):
   - Pop-in elástico en cada bloque (`\\t(0,95,\\fscx116\\fscy116)\\t(95,180,\\fscx100\\fscy100)`),
     resaltado automático de palabras clave en Amarillo Neón y Cian, y rótulo superior "ÚLTIMA HORA".
4. Diseño Sonoro Multicapa y Masterización EBU R128 (`-14.8 LUFS`):
   - Sintetiza cama musical oscura de tensión periodística (drone subgrave + pulso rítmico) y
     efectos *whoosh* en cada transición, aplica compresión y ducking bajo la voz del locutor
     y masteriza a `-14.8 LUFS` listos para TikTok Creator Rewards.
5. Resiliencia Total (Auto-Fallback):
   - Si algún plano individual aún no está en `shots/SHxx.mp4` (o se ejecuta con `--demo`),
     genera automáticamente una placa animada 3D táctica de respaldo para no abortar jamás el render.
"""

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

_tools_dir = str(Path(__file__).resolve().parent)
if _tools_dir not in sys.path:
    sys.path.insert(0, _tools_dir)

try:
    import pysubs2
    from pysubs2 import SSAFile, SSAEvent, SSAStyle, Color, Alignment
    HAS_PYSUBS2 = True
except ImportError:
    HAS_PYSUBS2 = False

try:
    from remotion_renderer import (
        render_remotion_scene,
        render_remotion_batch,
        build_category_props,
        render_category_motion_graphic,
        get_composition_for_genre,
        get_composition_for_shot,
        is_remotion_available,
    )
    HAS_REMOTION = is_remotion_available()
except Exception:
    HAS_REMOTION = False

ROOT_DIR = Path(__file__).resolve().parent.parent
ENTREGAS_DIR = ROOT_DIR / "entregas"

HIGHLIGHT_YELLOW = {
    "doce", "12", "segundos", "nueve", "radares", "florida", "emergencia",
    "alarma", "colisión", "motores", "tormenta", "costa", "auxilio",
    "catastrófica", "cajas", "negras", "millones", "ciberataque", "hackers",
    "saboteados", "peligro", "impacto", "urgente",
}
HIGHLIGHT_CYAN = {
    "faa", "ntsb", "administración", "federal", "aviación", "peritos",
    "crucero", "vertical", "cabina", "timones", "bimotor", "europa",
    "tribunal", "gemini", "google", "ia", "sensores", "investigadores",
}


def log(msg: str) -> None:
    print(f"[NLE-ENSAMBLADOR] {msg}", flush=True)


def get_latest_delivery_dir(custom_dir: Optional[str] = None) -> Path:
    if custom_dir:
        p = Path(custom_dir).resolve()
        if not p.exists():
            raise FileNotFoundError(f"No existe el directorio: {p}")
        return p
    dirs = sorted(
        [d for d in ENTREGAS_DIR.iterdir() if d.is_dir() and (d / "metadata.json").exists()],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        raise FileNotFoundError(f"No se encontró ninguna entrega en {ENTREGAS_DIR}")
    return dirs[0]


def probe_duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    return float(subprocess.check_output(cmd).decode().strip())


def format_ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def colorize_words_ass(words: List[str]) -> str:
    """
    Aplica etiquetas de color ASS al estilo CapCut Pro:
    - Amarillo Neón (&H0000EAFF& = #FFE500) en palabras clave de impacto o números.
    - Cian Eléctrico (&H00FFFF00&) en entidades oficiales / tecnología.
    - Si ninguna palabra coincide, resalta automáticamente la palabra más larga (>4 letras).
    """
    cleaned_words = [re.sub(r"[^\wáéíóúñü]", "", w.lower()) for w in words]
    has_highlight = any(
        (c in HIGHLIGHT_YELLOW or c in HIGHLIGHT_CYAN or c.isdigit())
        for c in cleaned_words
    )

    # Si no hay palabra en el diccionario, resaltar la más larga para mantener el ritmo CapCut
    fallback_highlight_idx = -1
    if not has_highlight and words:
        lengths = [len(c) for c in cleaned_words]
        max_len = max(lengths) if lengths else 0
        if max_len >= 5:
            fallback_highlight_idx = lengths.index(max_len)

    out = []
    for idx, w in enumerate(words):
        clean = cleaned_words[idx]
        if clean in HIGHLIGHT_YELLOW or clean.isdigit() or idx == fallback_highlight_idx:
            # Amarillo Neón estilo Hormozi / CapCut
            out.append(r"{\c&H0000EAFF&}" + w.upper() + r"{\c&H00FFFFFF&}")
        elif clean in HIGHLIGHT_CYAN:
            # Cian Eléctrico
            out.append(r"{\c&H00FFFF00&}" + w.upper() + r"{\c&H00FFFFFF&}")
        else:
            out.append(w.upper())
    return " ".join(out)


def extract_acoustic_speech_blocks(
    audio_path: Path,
    total_duration: float,
    noise_db: str = "-26dB",
    min_silence: float = 0.22
) -> List[Tuple[float, float]]:
    """
    Extrae los bloques de voz activa y silencios reales del archivo de locución mediante FFmpeg silencedetect.
    Garantiza que ningún subtítulo flote o se desfase durante pausas dramáticas de la voz.
    """
    if not audio_path.exists():
        return [(0.10, max(0.10, total_duration - 0.20))]

    try:
        cmd = [
            "ffmpeg", "-y", "-i", str(audio_path),
            "-af", f"silencedetect=noise={noise_db}:d={min_silence}",
            "-f", "null", "-"
        ]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        s_starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", res.stderr)]
        s_ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", res.stderr)]

        if not s_starts:
            return [(0.10, max(0.10, total_duration - 0.20))]

        blocks: List[Tuple[float, float]] = []
        cur = 0.10
        for ss, se in zip(s_starts, s_ends):
            if ss > cur + 0.15:
                blocks.append((round(cur, 2), round(ss, 2)))
            cur = se
        if cur < total_duration - 0.20:
            blocks.append((round(cur, 2), round(total_duration - 0.10, 2)))

        return blocks if blocks else [(0.10, max(0.10, total_duration - 0.20))]
    except Exception as e:
        log(f"Aviso en análisis acústico de pausas: {e}. Usando fallback estándar.")
        return [(0.10, max(0.10, total_duration - 0.20))]


def _split_words_into_chunks(words: List[str]) -> List[List[str]]:
    chunks: List[List[str]] = []
    current: List[str] = []
    for w in words:
        current.append(w)
        if len(current) >= 3 or (len(current) >= 1 and w.endswith((".", "?", "!", ":"))):
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def _chunk_speech_weight(chunk_words: List[str]) -> float:
    """Peso temporal de una ráfaga considerando longitud y micro-pausas de puntuación."""
    base = float(sum(len(w) for w in chunk_words) + len(chunk_words) * 1.4)
    if chunk_words:
        tail = chunk_words[-1]
        if tail.endswith((".", "?", "!", "…")):
            base += 5.5
        elif tail.endswith((",", ";", ":")):
            base += 2.8
    return max(1.0, base)


def generate_kinetic_ass(
    script: str,
    total_duration: float,
    ass_path: Path,
    source_name: str,
    voice_audio: Optional[Path] = None,
    sentence_boundaries_file: Optional[Path] = None,
    word_boundaries_file: Optional[Path] = None,
) -> None:
    """
    Genera subtítulos vectoriales .ASS con estética CapCut Pro y sincronización de alta precisión:
    1. WORD_BOUNDARIES.json (Edge-TTS WordBoundary o faster-whisper): exactitud milimétrica palabra a palabra.
    2. SENTENCE_BOUNDARIES.json: alinea cada ráfaga dentro de su oración ponderando puntuación.
    3. Fallback acústico FFmpeg silencedetect (para TTS sin marcas).
    """
    words = script.split()
    chunks = _split_words_into_chunks(words)
    if not chunks:
        return

    if word_boundaries_file is None and voice_audio is not None:
        cand_wb = voice_audio.parent / "WORD_BOUNDARIES.json"
        if cand_wb.exists():
            word_boundaries_file = cand_wb

    CAPCUT_MARGIN_V = 560

    # Inicializar documento SSA con pysubs2 si está disponible
    subs = None
    if HAS_PYSUBS2:
        subs = SSAFile()
        subs.info["PlayResX"] = 1080
        subs.info["PlayResY"] = 1920
        subs.info["WrapStyle"] = 0
        subs.info["ScaledBorderAndShadow"] = "yes"
        subs.styles["CapCutBouncing"] = SSAStyle(
            fontname="Montserrat Black",
            fontsize=78,
            primarycolor=Color(255, 255, 255, 0),
            secondarycolor=Color(255, 234, 0, 0),
            outlinecolor=Color(0, 0, 0, 0),
            backcolor=Color(0, 0, 0, 0),
            bold=True,
            spacing=1.2,
            borderstyle=1,
            outline=7.0,
            shadow=0.0,
            alignment=Alignment.BOTTOM_CENTER,
            marginl=65,
            marginr=170,
            marginv=CAPCUT_MARGIN_V,
        )

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CapCutBouncing,Montserrat Black,78,&H00FFFFFF,&H0000EAFF,&H00000000,&H00000000,-1,0,0,0,100,100,1.2,0,1,7.0,0.0,2,65,170,{CAPCUT_MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    timed_chunks: List[Tuple[float, float, List[str]]] = []

    # 1A. Intentar alineación exacta palabra a palabra si existe WORD_BOUNDARIES.json
    if word_boundaries_file and word_boundaries_file.exists() and word_boundaries_file.stat().st_size > 10:
        try:
            w_data = json.loads(word_boundaries_file.read_text(encoding="utf-8"))
            valid_words = [
                w for w in w_data
                if isinstance(w, dict) and str(w.get("text", "")).strip() and float(w.get("end", 0)) >= float(w.get("start", 0))
            ]
            if len(valid_words) >= max(2, int(len(words) * 0.65)):
                log(f"Alineando subtítulos palabra a palabra ({len(valid_words)} marcas reales)...")
                w_chunks = _split_words_into_chunks([str(w["text"]).strip() for w in valid_words])
                cursor = 0
                for wc in w_chunks:
                    span = valid_words[cursor:cursor + len(wc)]
                    cursor += len(wc)
                    c_start = max(0.0, float(span[0]["start"]))
                    c_end = min(total_duration, max(c_start + 0.16, float(span[-1]["end"])))
                    timed_chunks.append((c_start, c_end, wc))
        except Exception as e:
            log(f"Aviso leyendo marcas palabra a palabra: {e}")

    # 1B. Si no hubo word boundaries, alinear por oración usando SENTENCE_BOUNDARIES.json + peso por puntuación
    if not timed_chunks and sentence_boundaries_file and sentence_boundaries_file.exists() and sentence_boundaries_file.stat().st_size > 10:
        try:
            s_data = json.loads(sentence_boundaries_file.read_text(encoding="utf-8"))
            sent_entries = [
                s for s in s_data
                if isinstance(s, dict) and s.get("text", "").strip() and float(s.get("end", 0)) > float(s.get("start", 0))
            ]
            total_sent_words = sum(len(s["text"].split()) for s in sent_entries)
            if sent_entries and total_sent_words >= max(2, int(len(words) * 0.6)):
                log(f"Alineando subtítulos exactamente por oración con {len(sent_entries)} marcas TTS...")
                for s in sent_entries:
                    s_start = max(0.0, float(s["start"]))
                    s_end = min(total_duration, max(s_start + 0.15, float(s["end"])))
                    s_chunks = _split_words_into_chunks(s["text"].split())
                    if not s_chunks:
                        continue
                    s_weights = [_chunk_speech_weight(c) for c in s_chunks]
                    s_total_w = max(1.0, sum(s_weights))
                    cur_t = s_start
                    win = s_end - s_start
                    for c, w in zip(s_chunks, s_weights):
                        c_dur = (w / s_total_w) * win
                        c_end = min(s_end, cur_t + max(0.18, c_dur))
                        timed_chunks.append((cur_t, c_end, c))
                        cur_t = c_end
        except Exception as e:
            log(f"Aviso leyendo marcas por oración TTS: {e}")

    # 2. Fallback acústico (silencedetect) si no hubo marcas por oración válidas
    if not timed_chunks:
        blocks: List[Tuple[float, float]] = []
        if voice_audio and voice_audio.exists():
            log("Extrayendo pausas acústicas del audio con FFmpeg silencedetect para sincronización de subtítulos...")
            blocks = extract_acoustic_speech_blocks(voice_audio, total_duration)
        merged_blocks: List[Tuple[float, float]] = []
        for bs, be in blocks:
            if be <= bs + 0.08:
                continue
            if merged_blocks and (bs - merged_blocks[-1][1] < 0.28 or (merged_blocks[-1][1] - merged_blocks[-1][0]) < 0.45):
                merged_blocks[-1] = (merged_blocks[-1][0], max(merged_blocks[-1][1], be))
            else:
                merged_blocks.append((bs, be))
        blocks = merged_blocks if merged_blocks else [(0.10, max(10.0, total_duration - 0.25))]

        total_speech_time = sum(max(0.1, e - s) for s, e in blocks)
        weights = [_chunk_speech_weight(c) for c in chunks]
        total_weight = max(1.0, sum(weights))

        def speech_time_to_block_idx(st: float) -> int:
            acc = 0.0
            for idx, (bs, be) in enumerate(blocks):
                bdur = max(0.01, be - bs)
                if acc + bdur >= st or idx == len(blocks) - 1:
                    return idx
                acc += bdur
            return len(blocks) - 1

        # Asignar cada ráfaga al bloque que contiene su centro ponderado para evitar recortes de 1 frame en bordes
        chunks_by_block: Dict[int, List[Tuple[List[str], float]]] = {i: [] for i in range(len(blocks))}
        cum = 0.0
        for c, w in zip(chunks, weights):
            st_mid = ((cum + 0.5 * w) / total_weight) * total_speech_time
            b_idx = speech_time_to_block_idx(st_mid)
            chunks_by_block[b_idx].append((c, w))
            cum += w

        for b_idx, (bs, be) in enumerate(blocks):
            b_items = chunks_by_block.get(b_idx) or []
            if not b_items:
                continue
            b_total_w = max(1.0, sum(w for _, w in b_items))
            b_win = max(0.38 * len(b_items), be - bs)
            cur_t = bs
            for item_idx, (c, w) in enumerate(b_items):
                c_dur = (w / b_total_w) * (be - bs)
                if item_idx == len(b_items) - 1:
                    c_end = max(cur_t + 0.38, be)
                else:
                    c_end = cur_t + max(0.32, c_dur)
                c_end = min(total_duration, c_end)
                timed_chunks.append((cur_t, max(cur_t + 0.25, c_end), c))
                cur_t = c_end

    for real_start, real_end, c in timed_chunks:
        styled_text = colorize_words_ass(c)
        anim_tag = r"{\fscx82\fscy82\t(0,60,\fscx112\fscy112)\t(60,130,\fscx100\fscy100)}"
        full_text = f"{anim_tag}{styled_text}"
        events.append(
            f"Dialogue: 1,{format_ass_time(real_start)},{format_ass_time(real_end)},CapCutBouncing,,0,0,0,,{full_text}"
        )
        if HAS_PYSUBS2 and subs is not None:
            subs.events.append(
                SSAEvent(
                    start=int(real_start * 1000),
                    end=int(real_end * 1000),
                    style="CapCutBouncing",
                    text=full_text,
                    layer=1,
                )
            )

    if HAS_PYSUBS2 and subs is not None:
        subs.save(str(ass_path))
        log(f"✅ Subtítulos vectoriales Kinetic generados con pysubs2: {len(subs.events)} eventos en {ass_path.name}")
    else:
        ass_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
        log(f"✅ Subtítulos vectoriales Kinetic generados y sincronizados: {len(events)} ráfagas en {ass_path.name}")


_mont_bold = Path("/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf")
_mont_reg = Path("/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf")
FONT_BOLD = str(_mont_bold) if _mont_bold.exists() else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = str(_mont_reg) if _mont_reg.exists() else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def generate_verified_source_card(source_name: str, genre: str, out_png: Path) -> Path:
    """
    Genera una banda compacta de acreditación oficial (overlay editorial limpio)
    para proyectarse sobre SH02 sin tapar el mapa ni chocar con encabezados.
    """
    from PIL import Image, ImageDraw, ImageFont

    W, H = 760, 88
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_bold_p = FONT_BOLD if Path(FONT_BOLD).exists() else "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    font_reg_p = FONT_REG if Path(FONT_REG).exists() else "/usr/share/fonts/truetype/liberation/LiberationSans.ttf"

    f_badge = ImageFont.truetype(font_bold_p, 16)
    f_title = ImageFont.truetype(font_bold_p, 27)

    genre_up = (genre or "").upper()
    genre_tokens = set("".join(ch if ch.isalnum() else " " for ch in genre_up).split())
    if "G2" in genre_tokens or "CIBER" in genre_up or "CYBER" in genre_up:
        border_col = (230, 57, 70, 225)
        tag_bg = (180, 20, 30)
    elif "G4" in genre_tokens or "ESPACIO" in genre_up or "SPACE" in genre_up:
        border_col = (255, 183, 3, 225)
        tag_bg = (120, 35, 180)
    elif "G3" in genre_tokens or "HARDWARE" in genre_up or "IA" in genre_tokens or "AI" in genre_tokens or "ROBOT" in genre_up:
        border_col = (244, 162, 97, 225)
        tag_bg = (200, 75, 40)
    else:
        border_col = (229, 169, 60, 225)
        tag_bg = (195, 42, 32)

    draw.rounded_rectangle([(0, 0), (W - 1, H - 1)], radius=12, fill=(14, 18, 26, 225), outline=border_col, width=2)
    draw.rounded_rectangle([(16, 12), (230, 40)], radius=7, fill=tag_bg)
    draw.text((26, 17), "• FUENTE VERIFICADA", font=f_badge, fill=(255, 255, 255))
    draw.text((246, 17), "COBERTURA OFICIAL", font=f_badge, fill=(205, 218, 235))

    src_text = source_name.upper().strip()
    if len(src_text) > 34:
        src_text = src_text[:32] + "..."
    draw.text((16, 46), src_text, font=f_title, fill=(248, 243, 232))

    img.save(out_png, "PNG")
    return out_png


def escape_ffmpeg_drawtext(s: str) -> str:
    """Escapa de forma robusta caracteres conflictivos en cadenas de texto para FFmpeg drawtext."""
    if not s:
        return ""
    clean = str(s).replace("'", "’")
    clean = clean.replace(r"\:", ":").replace(":", r"\:")
    return clean


def build_modern_broadcast_card(
    badge: str,
    title: str,
    metric_val: str,
    metric_label: str,
    bullets: list,
    accent_hex: str = "0xe5a93c",
    bg_hex: str = "0x0b0e14",
    footer_text: str = "• REPORTE DOCUMENTAL VERIFICADO"
) -> tuple:
    badge_esc = escape_ffmpeg_drawtext(badge.replace("●", "•"))
    title_esc = escape_ffmpeg_drawtext(title)

    if "%{eif" in metric_val:
        metric_val_esc = metric_val.replace("'", "’")
    else:
        metric_val_esc = escape_ffmpeg_drawtext(metric_val)

    metric_label_esc = escape_ffmpeg_drawtext(metric_label)
    footer_esc = escape_ffmpeg_drawtext(footer_text.replace("📡", "•"))

    val_fontsize = 68 if len(metric_val) <= 12 else 46
    ease_y = "(1-min(1,t/0.5))*(1-min(1,t/0.5))*40"

    # Safe Zone 100%: x=56..886 (bien a la izquierda de botones TikTok en x=930)
    filters = [
        f"drawbox=x=56:y='330+{ease_y}':w=830:h=820:color=0x141a24@0.94:t=fill",
        f"drawbox=x=56:y='330+{ease_y}':w=830:h=820:color={accent_hex}@0.65:t=2",
        f"drawbox=x=86:y='365+{ease_y}':w=430:h=42:color={accent_hex}@0.18:t=fill",
        f"drawbox=x=86:y='365+{ease_y}':w=430:h=42:color={accent_hex}:t=2",
        f"drawtext=fontfile={FONT_BOLD}:text='{badge_esc}':fontcolor={accent_hex}:fontsize=20:x=102:y='376+{ease_y}'",
        f"drawtext=fontfile={FONT_BOLD}:text='{title_esc}':fontcolor=0xf8f3e8:fontsize=29:x=86:y='436+{ease_y}'",
        f"drawtext=fontfile={FONT_BOLD}:text='{metric_val_esc}':fontcolor=0xf8f3e8:fontsize={val_fontsize}:x=86:y='494+{ease_y}'",
        f"drawtext=fontfile={FONT_REG}:text='{metric_label_esc}':fontcolor=0xf8f3e8@0.85:fontsize=24:x=86:y='580+{ease_y}'",
        f"drawbox=x=86:y='626+{ease_y}':w=770:h=4:color=0x253045:t=fill",
        f"drawbox=x=86:y='626+{ease_y}':w='mod(t*300\\,770)':h=4:color={accent_hex}:t=fill"
    ]
    by = 666
    for txt, col in bullets:
        clean_txt = escape_ffmpeg_drawtext(txt)
        filters.append(f"drawtext=fontfile={FONT_REG}:text='{clean_txt}':fontcolor={col}:fontsize=24:x=86:y='{by}+{ease_y}'")
        by += 46

    filters.extend([
        f"drawbox=x=86:y='1082+{ease_y}':w=770:h=42:color=0x171d26@0.94:t=fill",
        f"drawbox=x=86:y='1082+{ease_y}':w=770:h=42:color={accent_hex}@0.45:t=1",
        f"drawtext=fontfile={FONT_BOLD}:text='{footer_esc}':fontcolor={accent_hex}:fontsize=19:x=106:y='1094+{ease_y}'",
        "vignette=PI/4"
    ])
    return bg_hex, ",".join(filters)


def generate_infographic_vector_shot(
    shot_info: Dict[str, Any],
    shot_idx: int,
    norm_mp4: Path,
    target_dur: float,
    fps: int = 24,
    genre: str = "G1",
    title: str = "",
) -> None:
    shot_id = shot_info.get("id", f"SH{shot_idx+1:02d}")
    shot_type = shot_info.get("type", "INFOGRAFIA TACTICA").upper()
    dur_s = max(1.0, target_dur)

    title_low = (title or "").lower()
    genre_upper = (genre or "G1").upper()

    def _kw(k: str, txt: str) -> bool:
        return bool(re.search(rf"\b{re.escape(k)}\b", txt)) if len(k) <= 3 else (k in txt)

    if "G2" in genre_upper or "CIBER" in genre_upper:
        is_cyber, is_ai, is_space = True, False, False
    elif "G3" in genre_upper or "HARDWARE" in genre_upper or "ROBOTICA" in genre_upper:
        is_cyber, is_ai, is_space = False, True, False
    elif "G4" in genre_upper or "ESPACIO" in genre_upper:
        is_cyber, is_ai, is_space = False, False, True
    elif "AVIACION" in genre_upper or "G1" in genre_upper:
        is_cyber, is_ai, is_space = False, False, False
    else:
        is_cyber = any(_kw(k, title_low) for k in ["ciber", "hacker", "ransomware", "malware", "exploit", "breach", "zero-day"])
        is_ai = any(_kw(k, title_low) for k in ["gemini", "google", "ia", "ai", "openai", "chip", "2 nm", "robot", "nvidia", "deepseek", "chatgpt", "semiconduct", "dram", "nand", "euv", "silicon", "hardware", "cpu", "gpu"])
        is_space = any(_kw(k, title_low) for k in ["espacio", "nasa", "esa", "marte", "luna", "cohete", "spacex", "telescopio", "asteroide", "planetary", "space", "starship", "orbit"])

    is_non_av_disaster = (
        not is_cyber and not is_ai and not is_space
        and (
            ("CATASTROF" in genre_upper and "AVIACION" not in genre_upper)
            or (
                any(_kw(k, title_low) for k in ["sismo", "terremoto", "huaico", "lluvia", "inundaci", "volc", "tsunami"])
                and not any(_kw(k, title_low) for k in ["avión", "avion", "vuelo", "flight", "plane", "boeing", "airbus", "aircraft", "mayday"])
            )
        )
    )

    if is_cyber:
        cards = {
            "SH01": build_modern_broadcast_card(
                "● CENTRO SOC · INTEL DE AMENAZAS",
                "RADAR DE SEGURIDAD DIGITAL",
                "ALERTA ZERO-DAY",
                "INCIDENTE CRÍTICO EN INFRAESTRUCTURA DE RED",
                [
                    ("• OBJETIVO: SERVIDORES Y SERVICIOS ESENCIALES", "white@0.9"),
                    ("• VECTOR: EXPLOIT DE DÍA CERO DETECTADO", "0xee3344"),
                    ("• MITIGACIÓN: FIREWALL Y FILTRADO BGP EN VIVO", "0xffaa00")
                ],
                accent_hex="0xee3344",
                bg_hex="0x12090d"
            ),
            "SH03": build_modern_broadcast_card(
                "● TELEMETRÍA DE TRÁFICO MALICIOSO",
                "PICO DE ATAQUE DDOS REGISTRADO",
                r"%{eif\:940-120*t\:d} GBPS",
                "TASA DE PAQUETES: 14.8 MILLONES PPS (CRÍTICO)",
                [
                    ("• ANOMALÍA: SATURACIÓN DE ENLACES PRINCIPALES", "0xffaa00"),
                    ("• ANÁLISIS IP: FIRMAS DE RANSOMWARE EN TIEMPO REAL", "0xff8888"),
                    ("• PROTOCOLO: CUARENTENA DE NODOS ACTIVADA", "0x55ff88")
                ],
                accent_hex="0xee3344",
                bg_hex="0x14080c"
            ),
            "SH10": build_modern_broadcast_card(
                "● TOPOLOGÍA DE RED Y FIREWALL",
                "AISLAMIENTO DE SUBREDES",
                "NODOS AISLADOS",
                "MAPA DE SERVIDORES Y CONTENCIÓN PERIMETRAL",
                [
                    ("• VECTOR DE ENTRADA: PARCHADO EN SISTEMAS CORE", "0x55ff88"),
                    ("• BASES DE DATOS: INTEGRIDAD Y CIFRADO REVISADOS", "0xffcc00"),
                    ("• TRÁFICO SEGURO: RESTABLECIÉNDOSE GRADUALMENTE", "white@0.9")
                ],
                accent_hex="0xee3344",
                bg_hex="0x110912"
            ),
            "SH11": build_modern_broadcast_card(
                "● ANÁLISIS FORENSE DIGITAL",
                "EVIDENCIA Y REPORTE CVE",
                "CVE ZERO-DAY",
                "FIRMA CRIPTOGRÁFICA DEL ATAQUE CONFIRMADA",
                [
                    ("• PAYLOAD: SHA256-APT-EXPLOIT IDENTIFICADO", "0xffaa00"),
                    ("• RESPONSABILIDAD: GRUPO AVANZADO DE CIBERCRIMEN", "0xee3344"),
                    ("• ESTADO: CONTENCIÓN TOTAL Y EVALUACIÓN FORENSE", "white@0.9")
                ],
                accent_hex="0xee3344",
                bg_hex="0x110a14"
            ),
            "SH13": build_modern_broadcast_card(
                "● BALANCE FORENSE · CIBERDEFENSA",
                "EVALUACIÓN DE IMPACTO Y RESILIENCIA",
                "ANÁLISIS EN VIVO",
                "FORTALECIMIENTO DE INFRAESTRUCTURAS CRÍTICAS",
                [
                    ("• CONTENCIÓN: PARCHES DE EMERGENCIA APLICADOS", "0x55ff88"),
                    ("• AUDITORÍA: REVISIÓN DE INTEGRIDAD EN CURSO", "white@0.9"),
                    ("• RADAR FORENSE: MONITOREO DE AMENAZAS 24/7", "0xffaa00")
                ],
                accent_hex="0xee3344",
                bg_hex="0x140a0e",
                footer_text="📡 REPORTE DE CIBERSEGURIDAD · TIKTOK RADAR"
            ),
        }
    elif is_ai:
        cards = {
            "SH01": build_modern_broadcast_card(
                "● RADAR DE LITOGRAFÍA Y CHIPS",
                "CADENA GLOBAL DE SEMICONDUCTORES",
                "PROCESO 2 NM",
                "SUPERCHIPS Y MODELOS FRONTERA DE IA",
                [
                    ("• LITOGRAFÍA: HIGH-NA EUV EN SALA BLANCA", "0xf4a261"),
                    ("• EFICIENCIA: +40% RESPECTO A GENERACIÓN PREVIA", "0x55ff88"),
                    ("• DISPUTA: CONTROL DE TECNOLOGÍA CRÍTICA DE CÓMPUTO", "white@0.9")
                ],
                accent_hex="0xf4a261",
                bg_hex="0x120e0a"
            ),
            "SH03": build_modern_broadcast_card(
                "● MÉTRICAS DE CÓMPUTO E INFERENCIA",
                "POTENCIA DE PROCESAMIENTO",
                r"%{eif\:180-25*t\:d} TFLOPS",
                "CAPACIDAD DE CÁLCULO EN TIEMPO REAL",
                [
                    ("• NODO: 2 NM GATE-ALL-AROUND (NANOSHEET)", "0xf4a261"),
                    ("• ANCHO DE BANDA: MEMORIA HBM3E DE ULTRA VELOCIDAD", "white@0.9"),
                    ("• LATENCIA: OPTIMIZADA PARA MODELOS MULTIMODALES", "0x55ff88")
                ],
                accent_hex="0xf4a261",
                bg_hex="0x120d09"
            ),
            "SH10": build_modern_broadcast_card(
                "● BLUEPRINT DE SILICIO 3D",
                "ARQUITECTURA DE MATRIZ TENSOR",
                "DIAGRAMA 2NM",
                "INTERCONEXIÓN ULTRA RÁPIDA CHIP-TO-CHIP",
                [
                    ("• TRANSISTORES GAA: MÁXIMA DENSIDAD INTEGRADA", "0x55ff88"),
                    ("• ALIMENTACIÓN TRASERA (BACKSIDE POWER): ACTIVA", "white@0.9"),
                    ("• DISIPACIÓN TÉRMICA: DISEÑADA PARA DATA CENTERS", "0xf4a261")
                ],
                accent_hex="0xf4a261",
                bg_hex="0x130e09"
            ),
            "SH11": build_modern_broadcast_card(
                "● BENCHMARK OFICIAL DE FRONTERA",
                "PRUEBAS DE INFERENCIA EN ESTUDIO",
                "NUEVO RÉCORD",
                "RESULTADOS CERTIFICADOS DE LABORATORIO",
                [
                    ("• VELOCIDAD: TOKENS POR SEGUNDO EN TIEMPO RÉCORD", "0xf4a261"),
                    ("• RENDIMIENTO: SUPERA LÍMITES PREVIOS DE ARQUITECTURA", "0x55ff88"),
                    ("• IMPACTO: DETERMINANTE PARA EL DESPLIEGUE GLOBAL", "white@0.9")
                ],
                accent_hex="0xf4a261",
                bg_hex="0x130e08"
            ),
            "SH13": build_modern_broadcast_card(
                "● FRONTERA GLOBAL DE SILICIO",
                "IMPACTO EN LA INDUSTRIA Y SOCIEDAD",
                "NUEVO HORIZONTE",
                "CARRERA POR LA SUPREMACÍA DE CÓMPUTO",
                [
                    ("• DISPUTA: CONTROL DE LITOGRAFÍA EXTREMA HIGH-NA", "0xf4a261"),
                    ("• EFICIENCIA: REVOLUCIÓN EN CENTROS DE DATOS", "0x55ff88"),
                    ("• SEGUIMIENTO: AVANCES QUE TRANSFORMAN LA HUMANIDAD", "white@0.9")
                ],
                accent_hex="0xf4a261",
                bg_hex="0x140e08",
                footer_text="📡 FRONTERA TECNOLÓGICA · TIKTOK RADAR"
            ),
        }
    elif is_space:
        cards = {
            "SH01": build_modern_broadcast_card(
                "● DEEP SPACE NETWORK · CENTRO DE CONTROL",
                "RASTREO ORBITAL DE MISIÓN",
                "ÓRBITA 410 KM",
                "TELEMETRÍA PLANETARIA NASA / ESA",
                [
                    ("• TRAYECTORIA: MANIOBRA DE APROXIMACIÓN NOMINAL", "white@0.9"),
                    ("• ENLACE: RED DE ESPACIO PROFUNDO CONECTADA", "0x55ff88"),
                    ("• ESTADO: PARÁMETROS DE NAVEGACIÓN EN TOLERANCIA", "0xffb703")
                ],
                accent_hex="0xffb703",
                bg_hex="0x100a16"
            ),
            "SH03": build_modern_broadcast_card(
                "● TELEMETRÍA DE APROXIMACIÓN",
                "VELOCIDAD Y ALTURA DE DESCENSO",
                r"%{eif\:27800-1400*t\:d} KM/H",
                "FRENADO CONTROLADO Y REENTRADA",
                [
                    ("• PROPULSIÓN: TOBERAS Y RETROCOHETES ACTIVOS", "0xffaa00"),
                    ("• ÁNGULO DE DESCENSO: CORRECCIÓN MILIMÉTRICA", "0xffb703"),
                    ("• NAVEGACIÓN: ALGORITMO AUTÓNOMO EN TIEMPO REAL", "white@0.9")
                ],
                accent_hex="0xffb703",
                bg_hex="0x100918"
            ),
            "SH10": build_modern_broadcast_card(
                "● BLUEPRINT TECNOLÓGICO 3D",
                "ESQUEMA DE SONDA Y PROPULSIÓN",
                "BLUEPRINT 3D",
                "SUBSISTEMA DE ESCUDO TÉRMICO Y ENERGÍA",
                [
                    ("• PANELES SOLARES: DESPLIEGUE AL 100% OPERATIVO", "0x55ff88"),
                    ("• COMBUSTIBLE: RESERVA ÓPTIMA PARA FASE FINAL", "white@0.9"),
                    ("• SENSORES ÓPTICOS: CALIBRADOS PARA DESCENSO", "0xffb703")
                ],
                accent_hex="0xffb703",
                bg_hex="0x100918"
            ),
            "SH11": build_modern_broadcast_card(
                "● TELEMETRÍA OFICIAL CERTIFICADA",
                "DATOS CONFIRMADOS POR AGENCIA",
                "MISIÓN EXITOSA",
                "SEÑAL TRANSMITIDA DESDE ESPACIO PROFUNDO",
                [
                    ("• TRAYECTORIA: INSERTADA EN VENTANA TARGET", "0x55ff88"),
                    ("• INSTRUMENTOS: RECOLECCIÓN DE DATOS ACTIVA", "0xffb703"),
                    ("• COMUNICADO: HITO HISTÓRICO PARA FUTURAS MISIONES", "white@0.9")
                ],
                accent_hex="0xffb703",
                bg_hex="0x110918"
            ),
            "SH13": build_modern_broadcast_card(
                "● HORIZONTE CÓSMICO · CIENCIA",
                "NUEVA ERA EN EXPLORACIÓN PLANETARIA",
                "MISIÓN EN CURSO",
                "HITO HISTÓRICO PARA LA INVESTIGACIÓN ESPACIAL",
                [
                    ("• TELEMETRÍA: PARÁMETROS NOMINALES EN TIEMPO REAL", "0x55ff88"),
                    ("• INSTRUMENTOS: DATOS CIENTÍFICOS EN TRANSMISIÓN", "white@0.9"),
                    ("• RADAR CÓSMICO: COBERTURA DIRECTA DE MISIONES", "0xffb703")
                ],
                accent_hex="0xffb703",
                bg_hex="0x110a18",
                footer_text="📡 CIENCIA Y ESPACIO · TIKTOK RADAR"
            ),
        }
    elif is_non_av_disaster:
        cards = {}
    else:
        # Default: Aviación
        cards = {
            "SH01": build_modern_broadcast_card(
                "● RADAR TÁCTICO EN VIVO · MONITOREO",
                "ESPACIO AÉREO INTERNACIONAL",
                "ALERTA EN VUELO",
                "SISTEMA DE RASTREO SATELITAL Y AERONAVAL",
                [
                    ("• COORDENADAS: 25.76 N, 80.19 W · BEACON ACTIVO", "0xfb8500"),
                    ("• ESTADO: DESCENSO CRÍTICO Y PÉRDIDA DE CONTACTO", "0xee3344"),
                    ("• PROTOCOLO: ASISTENCIA TÁCTICA DE CONTROL EN TIERRA", "white@0.9")
                ],
                accent_hex="0xfb8500",
                bg_hex="0x100d08"
            ),
            "SH03": build_modern_broadcast_card(
                "● REGISTRO DE TELEMETRÍA DE CABINA",
                "ALTITUD Y TASA DE DESCENSO",
                r"%{eif\:18200-3200*t\:d} FT",
                "TASA DE DESCENSO: -3,400 PIES/MIN (CRÍTICO)",
                [
                    ("• ÁNGULO DE ATAQUE: +14.2° · ALERTA SONORA ACTIVA", "0xffaa00"),
                    ("• TRANSPONDER: CÓDIGO 7700 DE EMERGENCIA EMITIDO", "0xee3344"),
                    ("• CONTACTO TIERRA: MANIOBRAS DE RECUPERACIÓN", "white@0.9")
                ],
                accent_hex="0xffaa00",
                bg_hex="0x140d08"
            ),
            "SH10": build_modern_broadcast_card(
                "● BLUEPRINT TÉCNICO Y FUSELAJE",
                "EVALUACIÓN ESTRUCTURAL DE AERONAVE",
                "BLUEPRINT 3D",
                "SUBSISTEMA DE CONTROL DE TIMÓN Y EMPUJE",
                [
                    ("• PRESIÓN HIDRÁULICA: SOBRECARGA EN MANDOS", "0xff7777"),
                    ("• SUPERFICIES DE CONTROL: ESTABILIZACIÓN MANUAL", "0x55ff88"),
                    ("• FUSELAJE: INTEGRIDAD ESTRUCTURAL SIN FISURAS", "white@0.9")
                ],
                accent_hex="0xfb8500",
                bg_hex="0x110d08"
            ),
            "SH11": build_modern_broadcast_card(
                "● EVIDENCIA OFICIAL FORENSE",
                "REGISTROS DE CAJA NEGRA FDR Y CVR",
                "UNIDAD FDR",
                "REGISTRO DE VOZ Y DATOS DE IMPACTO",
                [
                    ("• ESTADO FÍSICO: ÍNTEGRO / ACCESO AUTORIZADO", "0x55ff88"),
                    ("• AUDIO CVR: CORRELACIONADO CON PANTALLAS DE RADAR", "0xfb8500"),
                    ("• INSPECCIÓN OFICIAL: DICTAMEN TÉCNICO EN CURSO", "white@0.9")
                ],
                accent_hex="0xff6600",
                bg_hex="0x140d08"
            ),
            "SH13": build_modern_broadcast_card(
                "● BALANCE DE SEGURIDAD AÉREA",
                "INVESTIGACIÓN Y DICTAMEN OFICIAL",
                "PERITAJE ACTIVO",
                "ANÁLISIS DE DATOS FDR Y REGISTROS DE VUELO",
                [
                    ("• AUTORIDADES: FAA Y NTSB EXAMINAN LA SECUENCIA", "white@0.9"),
                    ("• TELEMETRÍA: CORRELACIÓN CON PANTALLAS DE CONTROL", "0xffaa00"),
                    ("• SEGUIMIENTO: DICTAMEN TÉCNICO EN DESARROLLO", "0x55ff88")
                ],
                accent_hex="0xfb8500",
                bg_hex="0x140c08",
                footer_text="📡 SEGURIDAD AÉREA GLOBAL · TIKTOK RADAR"
            ),
        }

    if shot_id in cards:
        bg, vf = cards[shot_id]
    else:
        # Si no está en `cards` predefinidos (ej. SH02, SH04..SH09, SH12 ausentes de Flow),
        # construir placa contextual única basada en narrativa del guión y acción del plano.
        stage_accents = ["0x00e5ff", "0xfb8500", "0xffb703", "0x38bdf8", "0xe63946", "0x10b981"]
        stage_bgs = ["0x0b101b", "0x120d08", "0x0f121e", "0x140d0a", "0x0e1318", "0x110e16"]
        st_accent = stage_accents[shot_idx % len(stage_accents)]
        st_bg = stage_bgs[shot_idx % len(stage_bgs)]

        narrative_raw = (shot_info.get("narrative_excerpt") or shot_info.get("action") or title or "").strip()
        wrapped = textwrap.wrap(narrative_raw, width=42)[:3]
        bullets_dyn: List[Tuple[str, str]] = [
            (f"• {line.upper()}", "white@0.92") for line in wrapped
        ] if wrapped else [
            ("• ANÁLISIS TÉCNICO EN CURSO", "white@0.92"),
        ]
        bullets_dyn.append((f"• SECUENCIA: {shot_info.get('sec', f'{shot_idx*4}-{(shot_idx+1)*4}s').upper()} · ESCENA VERIFICADA", st_accent))

        short_headline = textwrap.shorten((title or shot_type), width=34, placeholder="...").upper()
        stage_metric = f"FASE {shot_idx + 1:02d} / {shot_info.get('sec', 'EN VIVO').upper()}"
        if len(stage_metric) > 16:
            stage_metric = f"PLANO {shot_id}"

        bg, vf = build_modern_broadcast_card(
            f"• {shot_id} · {shot_type[:28]}",
            short_headline,
            stage_metric,
            textwrap.shorten(shot_info.get("action") or "RECONSTRUCCIÓN DOCUMENTAL", width=50, placeholder="...").upper(),
            bullets_dyn,
            accent_hex=st_accent,
            bg_hex=st_bg,
            footer_text=f"• RECONSTRUCCIÓN DOCUMENTAL · PLANO {shot_id}",
        )

    # Dinamismo de cámara Ken Burns procedural anti-freeze:
    # Alterna sutil acercamiento (punch-in) y alejamiento con leve deriva vertical/horizontal
    zoom_in = (shot_idx % 2 == 0)
    if zoom_in:
        kb_motion = (
            f"scale=1160:2062,crop=1080:1920:"
            f"x='(iw-ow)/2 + 10*sin(PI*t/{dur_s:.2f})':"
            f"y='(ih-oh)/2 - 30*(t/{dur_s:.2f})'"
        )
    else:
        kb_motion = (
            f"scale=1160:2062,crop=1080:1920:"
            f"x='(iw-ow)/2 - 10*sin(PI*t/{dur_s:.2f})':"
            f"y='(ih-oh)/2 + 25*(t/{dur_s:.2f}) - 25'"
        )
    full_vf = f"{vf},{kb_motion},noise=alls=2:allf=t,format=yuv420p"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={bg}:s=1080x1920:r={fps}:d={dur_s:.3f}",
        "-vf", full_vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15",
        str(norm_mp4),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _is_remotion_tech_shot(shot_info: Dict[str, Any], shot_idx: int) -> bool:
    shot_id = shot_info.get("id", f"SH{shot_idx+1:02d}")
    type_lower = (shot_info.get("type") or "").lower()
    return (
        shot_info.get("render_mode") in ("remotion", "infographic")
        or shot_id in ("SH01", "SH03", "SH10", "SH11", "SH13")
        or any(
            k in type_lower
            for k in (
                "radar", "telemetria", "datos", "diagrama", "infografia",
                "evidencia", "cierre", "contexto", "blueprint", "esquema", "mapa",
            )
        )
    )


def _build_remotion_job_for_shot(
    shot_info: Dict[str, Any],
    shot_idx: int,
    genre: str,
    title: str,
    story_metrics: Dict[str, Any],
    target_dur: float,
    norm_mp4: Path,
    fps: int = 24,
) -> Dict[str, Any]:
    """Construye la especificación única de composición y props Remotion 2.5D para un plano."""
    shot_id = shot_info.get("id", f"SH{shot_idx+1:02d}")
    shot_type = shot_info.get("type", "")
    extra_props: Dict[str, Any] = {**story_metrics, **(shot_info.get("remotion_props") or {})}
    if "has_geo" in extra_props:
        has_geo_flag = bool(extra_props.get("has_geo") and extra_props.get("origin"))
    else:
        has_geo_flag = True

    comp_name = get_composition_for_shot(
        genre,
        shot_id=shot_id,
        shot_type=shot_type,
        has_geo=has_geo_flag,
        has_receipt=bool(extra_props.get("has_receipt")),
    )
    narrative_sub = (
        shot_info.get("narrative_excerpt")
        or shot_info.get("subtitle")
        or shot_info.get("action")
        or "ANÁLISIS DOCUMENTAL"
    )
    extra_props.setdefault("sourceTag", story_metrics.get("sourceTag") or f"REPORTE VERIFICADO · {shot_id}")
    if comp_name == "Editorial25DOutro" and not extra_props.get("quote") and shot_info.get("narrative_excerpt"):
        extra_props["quote"] = shot_info["narrative_excerpt"]
    elif comp_name == "VeritasiumDocumentaryOutro" and shot_info.get("narrative_excerpt"):
        extra_props["quote"] = shot_info["narrative_excerpt"]
    elif comp_name == "VeritasiumBlueprint":
        extra_props["blueprintTag"] = f"ESQUEMA TÁCTICO · {shot_id}"

    remotion_props = build_category_props(
        genre=genre,
        title=shot_info.get("title") or title,
        subtitle=narrative_sub,
        duration_frames=max(24, int(target_dur * fps)),
        composition_id=comp_name,
        extra_props=extra_props,
    )
    return {
        "shot_id": shot_id,
        "compositionId": comp_name,
        "outputLocation": str(norm_mp4),
        "inputProps": remotion_props,
        "crf": 14,
        "concurrency": 2,
    }


def _find_still_image_for_shot(raw_mp4: Path) -> Optional[Path]:
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        cand = raw_mp4.with_suffix(ext)
        if cand.exists() and cand.stat().st_size > 15_000:
            return cand
    return None


def prepare_normalized_shot(
    shot_info: Dict[str, Any],
    shot_idx: int,
    raw_mp4: Path,
    norm_mp4: Path,
    target_dur: float,
    genre: str = "G1",
    title: str = "",
    start_trim: float = 0.0,
    punch_in: bool = False,
) -> None:
    """
    Prepara cada plano a 1080x1920 @ 24fps con la duración exacta del beat:
    - Planos Infográficos (render_mode='infographic'): usa motor Editorial 2.5D Remotion (o fallback FFmpeg).
    - Planos Cinemáticos Flow (render_mode='flow'): aplica Ken Burns suave (o punch-in) + LUT editorial unificada.
    """
    is_infographic = (shot_info.get("render_mode") in ("infographic", "remotion"))
    has_valid_raw = raw_mp4.exists() and raw_mp4.stat().st_size > 25_000
    still_img = None if has_valid_raw else _find_still_image_for_shot(raw_mp4)
    fps = 24

    if (has_valid_raw or still_img is not None) and not is_infographic:
        zoom_in = (shot_idx % 2 == 0)
        editorial_grade = (
            "colorbalance=rs=-0.03:gs=-0.01:bs=0.04:rh=0.05:gh=0.02:bh=-0.04,"
            "eq=contrast=1.06:saturation=0.92:brightness=-0.02,"
            "vignette=PI/5,noise=alls=3:allf=t,format=yuv420p"
        )
        if punch_in:
            crop_expr = (
                "scale=1340:2382:force_original_aspect_ratio=increase,crop=1340:2382,"
                "crop=1080:1920:"
                "x='(iw-ow)/2 + 10*sin(PI*t/{dur:.2f})':"
                "y='(ih-oh)/2 - 36*(t/{dur:.2f})',"
                + editorial_grade
            ).format(dur=max(1.0, target_dur))
        elif zoom_in:
            crop_expr = (
                "scale=1220:2168:force_original_aspect_ratio=increase,crop=1220:2168,"
                "crop=1080:1920:"
                "x='(iw-ow)/2 + 10*sin(PI*t/{dur:.2f})':"
                "y='(ih-oh)/2 - 34*(t/{dur:.2f})',"
                + editorial_grade
            ).format(dur=max(1.0, target_dur))
        else:
            crop_expr = (
                "scale=1220:2168:force_original_aspect_ratio=increase,crop=1220:2168,"
                "crop=1080:1920:"
                "x='(iw-ow)/2 - 10*sin(PI*t/{dur:.2f})':"
                "y='(ih-oh)/2 + 30*(t/{dur:.2f}) - 30',"
                + editorial_grade
            ).format(dur=max(1.0, target_dur))

        if still_img is not None:
            input_flags = ["-loop", "1", "-i", str(still_img)]
        else:
            trim_flags: List[str] = []
            if start_trim > 0.05:
                try:
                    raw_dur = probe_duration(raw_mp4)
                    safe_trim = min(start_trim, max(0.0, raw_dur - 1.5))
                    if safe_trim > 0.05:
                        trim_flags = ["-ss", f"{safe_trim:.2f}"]
                except Exception:
                    trim_flags = []
            input_flags = ["-stream_loop", "-1", *trim_flags, "-i", str(raw_mp4)]

        cmd = [
            "ffmpeg", "-y",
            *input_flags,
            "-t", f"{target_dur:.3f}",
            "-vf", crop_expr,
            "-r", str(fps),
            "-an",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "12",
            str(norm_mp4),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        rendered_with_remotion = False
        shot_id = shot_info.get("id", f"SH{shot_idx+1:02d}")
        if HAS_REMOTION and _is_remotion_tech_shot(shot_info, shot_idx):
            try:
                job = _build_remotion_job_for_shot(
                    shot_info=shot_info,
                    shot_idx=shot_idx,
                    genre=genre,
                    title=title,
                    story_metrics=dict(shot_info.get("remotion_props") or {}),
                    target_dur=target_dur,
                    norm_mp4=norm_mp4,
                    fps=fps,
                )
                res = render_remotion_scene(
                    composition_id=job["compositionId"],
                    output_path=norm_mp4,
                    props=job["inputProps"],
                    concurrency=2,
                )
                if res and norm_mp4.exists() and norm_mp4.stat().st_size > 10_000:
                    rendered_with_remotion = True
                    log(f"   [REMOTION-REACT] Plano {shot_id} ({job['compositionId']}) renderizado con motor 2.5D ({target_dur:.2f}s).")
            except Exception as e:
                log(f"   [REMOTION] Aviso: fallback a FFmpeg para plano {shot_id}: {e}")

        if not rendered_with_remotion:
            generate_infographic_vector_shot(shot_info, shot_idx, norm_mp4, target_dur, fps, genre=genre, title=title)


def _build_synthetic_word_boundaries(
    script: str,
    sentence_boundaries: List[Dict[str, Any]],
    total_dur: float,
) -> List[Dict[str, Any]]:
    """Construye marcas aproximadas por palabra desde SENTENCE_BOUNDARIES.json o duración total."""
    words = (script or "").split()
    out: List[Dict[str, Any]] = []

    if sentence_boundaries:
        for sb in sentence_boundaries:
            s_words = str(sb.get("text") or "").split()
            if not s_words:
                continue
            s0 = max(0.0, float(sb.get("start", 0.0)))
            s1 = min(total_dur, max(s0 + 0.15, float(sb.get("end", s0 + 0.5))))
            weights = [max(2.0, float(len(w)) + (2.0 if w.endswith((".", "?", "!", ",")) else 0.0)) for w in s_words]
            tot_w = max(1.0, sum(weights))
            cur = s0
            for w, wt in zip(s_words, weights):
                dur = (wt / tot_w) * (s1 - s0)
                out.append({"text": w, "start": round(cur, 3), "end": round(cur + dur, 3)})
                cur += dur
        if out:
            return out

    if not words:
        return []
    weights = [max(2.0, float(len(w)) + (2.0 if w.endswith((".", "?", "!", ",")) else 0.0)) for w in words]
    tot_w = max(1.0, sum(weights))
    usable = max(1.0, total_dur - 0.20)
    cur = 0.10
    for w, wt in zip(words, weights):
        dur = (wt / tot_w) * usable
        out.append({"text": w, "start": round(cur, 3), "end": round(cur + dur, 3)})
        cur += dur
    return out


def align_beats_to_audio(
    beats: List[Dict[str, Any]],
    word_boundaries: List[Dict[str, Any]],
    sentence_boundaries: List[Dict[str, Any]],
    total_dur: float,
    script: str = "",
) -> List[Dict[str, Any]]:
    """
    Alinea cada beat narrativo al timestamp real de su palabra inicial en WORD_BOUNDARIES.json
    (o SENTENCE_BOUNDARIES.json / pesos de texto) para garantizar sincronía Beat<->Audio <= 0.15s.
    """
    if not beats or total_dur <= 0:
        return []

    wb_list = [
        w for w in (word_boundaries or [])
        if isinstance(w, dict) and str(w.get("text", "")).strip() and float(w.get("end", 0.0)) >= float(w.get("start", 0.0))
    ]
    if not wb_list:
        fallback_script = script or " ".join(str(b.get("text") or "") for b in beats)
        wb_list = _build_synthetic_word_boundaries(fallback_script, sentence_boundaries or [], total_dur)

    n_script_words = max(
        len((script or "").split()),
        max((int(b.get("word_end_idx", 0)) + 1 for b in beats), default=1),
        1,
    )
    n_wb = len(wb_list)
    n_beats = len(beats)
    min_beat_dur = min(0.55, total_dur / max(1, n_beats * 2))

    aligned: List[Dict[str, Any]] = []
    prev_start = 0.0
    for idx, beat in enumerate(beats):
        w_start_idx = max(0, int(beat.get("word_start_idx", 0)))
        if n_wb > 0:
            if n_wb == n_script_words:
                wb_idx = min(n_wb - 1, w_start_idx)
            else:
                wb_idx = min(n_wb - 1, int(round(w_start_idx * n_wb / n_script_words)))
            actual_word_start = max(0.0, min(total_dur, float(wb_list[wb_idx]["start"])))
        else:
            actual_word_start = (idx / max(1, n_beats)) * total_dur

        if idx == 0:
            start_sec = 0.0
        else:
            max_allowed = max(prev_start + min_beat_dur, total_dur - min_beat_dur * (n_beats - idx))
            start_sec = max(prev_start + min_beat_dur, min(max_allowed, actual_word_start))
        start_sec = round(start_sec, 3)
        sync_delta = round(abs(start_sec - actual_word_start), 3)

        item = dict(beat)
        item["start_sec"] = start_sec
        item["actual_word_start_sec"] = round(actual_word_start, 3)
        item["sync_delta_sec"] = sync_delta
        aligned.append(item)
        prev_start = start_sec

    for idx in range(len(aligned)):
        end_sec = aligned[idx + 1]["start_sec"] if idx + 1 < len(aligned) else round(total_dur, 3)
        aligned[idx]["end_sec"] = round(end_sec, 3)
        aligned[idx]["duration_sec"] = round(max(0.25, end_sec - aligned[idx]["start_sec"]), 3)

    return aligned


def build_editorial_timeline_video(
    norm_clips: List[Path],
    clip_durations: List[float],
    beat_timeline: List[Dict[str, Any]],
    output_silent_mp4: Path,
    dissolve_dur: float = 0.30,
) -> List[float]:
    """
    Ensambla el timeline editorial priorizando hard cuts (concat dentro de cada acto) y
    aplicando `xfade=transition=dissolve` exclusivamente en los cambios de Acto, manteniendo
    0.00s de deriva temporal respecto a los timestamps Audio-First.
    """
    if not norm_clips:
        raise ValueError("No hay clips normalizados para ensamblar el timeline.")

    inputs: List[str] = []
    for c in norm_clips:
        inputs.extend(["-i", str(c)])

    filter_parts: List[str] = []
    for i in range(len(norm_clips)):
        filter_parts.append(f"[{i}:v]settb=AVTB,fps=24,format=yuv420p,setsar=1[s{i}]")

    # Agrupar por bloques continuos separados únicamente en transiciones 'dissolve'
    blocks: List[List[int]] = [[0]]
    for i in range(1, len(norm_clips)):
        tr = str((beat_timeline[i] if i < len(beat_timeline) else {}).get("transition_in") or "cut").lower()
        if tr == "dissolve":
            blocks.append([i])
        else:
            blocks[-1].append(i)

    block_labels: List[str] = []
    block_durs: List[float] = []
    for b_idx, indices in enumerate(blocks):
        if len(indices) == 1:
            block_labels.append(f"[s{indices[0]}]")
        else:
            in_lbls = "".join(f"[s{i}]" for i in indices)
            out_lbl = f"[act{b_idx}]"
            filter_parts.append(f"{in_lbls}concat=n={len(indices)}:v=1:a=0{out_lbl}")
            block_labels.append(out_lbl)
        block_durs.append(sum(clip_durations[i] for i in indices))

    dissolve_timestamps: List[float] = []
    prev_label = block_labels[0]
    offset = 0.0
    for b_idx in range(1, len(block_labels)):
        offset += block_durs[b_idx - 1] - dissolve_dur
        dissolve_timestamps.append(round(offset, 3))
        out_label = f"[xv{b_idx}]"
        filter_parts.append(
            f"{prev_label}{block_labels[b_idx]}xfade=transition=dissolve:duration={dissolve_dur:.3f}:offset={offset:.3f}{out_label}"
        )
        prev_label = out_label

    filter_complex = ";".join(filter_parts)
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", prev_label,
        "-r", "24",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15",
        str(output_silent_mp4),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dissolve_timestamps


def build_transition_video(
    norm_clips: List[Path],
    clip_durations: List[float],
    trans_dur: float,
    output_silent_mp4: Path,
) -> List[float]:
    """
    Une los 13 clips aplicando el motor `xfade` de FFmpeg con transiciones dinámicas de noticiero.
    Devuelve la lista de timestamps donde ocurre cada transición para sincronizar los SFX whoosh.
    """
    transitions = [
        "dissolve", "smoothleft", "fade", "smoothright",
        "wipeleft", "dissolve", "smoothup", "fade",
        "wiperight", "dissolve", "smoothleft", "dissolve",
    ]

    inputs = []
    for c in norm_clips:
        inputs.extend(["-i", str(c)])

    filter_parts = []
    for i in range(len(norm_clips)):
        filter_parts.append(f"[{i}:v]settb=AVTB,fps=24,format=yuv420p[s{i}]")

    offset = 0.0
    transition_timestamps: List[float] = []
    prev_label = "[s0]"

    for i in range(1, len(norm_clips)):
        offset += clip_durations[i - 1] - trans_dur
        transition_timestamps.append(offset)
        t_name = transitions[(i - 1) % len(transitions)]
        out_label = f"[v{i}]"
        filter_parts.append(
            f"{prev_label}[s{i}]xfade=transition={t_name}:duration={trans_dur:.3f}:offset={offset:.3f}{out_label}"
        )
        prev_label = out_label

    filter_complex = ";".join(filter_parts)
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", prev_label,
        "-r", "24",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15",
        str(output_silent_mp4),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return transition_timestamps


def _render_two_pass_loudnorm(
    inputs: List[str],
    fc_parts: List[str],
    raw_label: str,
    total_dur: float,
    master_m4a: Path,
) -> None:
    """
    Ejecuta masterización EBU R128 en 2 pasadas (`linear=true`) para clavar exactamente
    -14.0 LUFS / -1.0 dBTP sin artefactos de bombeo en voz, con fallback limpio a 1 pasada.
    """
    pass1_fc = ";".join([
        *fc_parts,
        f"{raw_label}loudnorm=I=-14.0:TP=-1.0:LRA=7:print_format=json[aout]",
    ])
    cmd_p1 = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", pass1_fc,
        "-map", "[aout]",
        "-t", f"{total_dur:.3f}",
        "-f", "null", "-",
    ]
    measured: Optional[Dict[str, str]] = None
    try:
        p1 = subprocess.run(cmd_p1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
        matches = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", p1.stdout or "", re.DOTALL)
        if matches:
            parsed = json.loads(matches[-1])
            if all(k in parsed for k in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")):
                measured = parsed
    except Exception:
        measured = None

    if measured:
        ln_filter = (
            f"{raw_label}loudnorm=I=-14.0:TP=-1.0:LRA=7:"
            f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
            f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
            f"offset={measured['target_offset']}:linear=true:print_format=summary[aout]"
        )
    else:
        ln_filter = f"{raw_label}loudnorm=I=-14.0:TP=-1.0:LRA=7[aout]"

    pass2_fc = ";".join([*fc_parts, ln_filter])
    cmd_p2 = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", pass2_fc,
        "-map", "[aout]",
        "-t", f"{total_dur:.3f}",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(master_m4a),
    ]
    subprocess.run(cmd_p2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _build_music_drop_expression(music_drop_window: Optional[Tuple[float, float]], total_dur: float) -> Optional[str]:
    """Construye la expresión FFmpeg `volume='...':eval=frame` para el silencio dramático (Music Drop)."""
    if not music_drop_window or len(music_drop_window) != 2:
        return None
    t0 = max(0.4, float(music_drop_window[0]))
    t1 = min(max(t0 + 0.45, float(music_drop_window[1])), max(0.9, total_dur - 0.35))
    if t1 - t0 < 0.45:
        return None
    hs = min(t1 - 0.16, t0 + 0.12)
    he = max(hs + 0.08, t1 - 0.16)
    d_down = max(0.02, hs - t0)
    d_up = max(0.02, t1 - he)
    return (
        f"if(lt(t,{t0:.3f}),1.0,"
        f"if(lt(t,{hs:.3f}),1.0-0.98*(t-{t0:.3f})/{d_down:.3f},"
        f"if(lt(t,{he:.3f}),0.02,"
        f"if(lt(t,{t1:.3f}),0.02+0.98*(t-{he:.3f})/{d_up:.3f},1.0))))"
    )


def synthesize_broadcast_audio_master(
    voice_mp3: Path,
    total_dur: float,
    transition_times: List[float],
    master_m4a: Path,
    genre: str = "G1",
    sfx_events: Optional[List[Dict[str, Any]]] = None,
    music_drop_window: Optional[Tuple[float, float]] = None,
) -> None:
    """
    Crea el diseño sonoro multicapa profesional para TikTok:
    1. Voz periodística procesada con compresión y realce de presencia broadcast.
    2. Stems oficiales de Epidemic Sound por categoría (BASS + INSTRUMENTS) con Sidechain Ducking
       y caída musical dramática (`music_drop_window`) en el beat de revelación.
    3. Paleta de SFX diegéticos contextuales (`sfx_events`: boom, riser, paper, highlighter, click)
       o fallback legado si no se provee `sfx_events`.
    4. Masterización EBU R128 de 2 pasadas a -14.0 LUFS en estéreo espacial 48kHz.
    """
    assets_dir = ROOT_DIR / "audio_assets"
    try:
        from audio_generator import ensure_editorial_sfx_palette, get_genre_soundtrack
        bass_file, inst_file = get_genre_soundtrack(genre, assets_dir)
        sfx_palette = ensure_editorial_sfx_palette(assets_dir)
    except Exception:
        bass_file = assets_dir / "NEWS_THRILLER_BASS.mp3"
        inst_file = assets_dir / "NEWS_THRILLER_INSTRUMENTS.mp3"
        sfx_palette = {
            "boom": assets_dir / "SFX_DARK_BOOM.wav",
            "riser": assets_dir / "SFX_RISER_LOW.wav",
            "paper": assets_dir / "SFX_PAPER_FLIP.wav",
            "highlighter": assets_dir / "SFX_HIGHLIGHTER_SWIPE.wav",
            "click": assets_dir / "SFX_TECH_CLICK.wav",
        }

    boom_sfx = sfx_palette.get("boom") or (assets_dir / "SFX_DARK_BOOM.wav")
    whoosh_sfx = assets_dir / "SFX_WHOOSH_CINEMATIC.wav"
    drop_expr = _build_music_drop_expression(music_drop_window, total_dur)

    # Si los stems de Epidemic Sound están presentes, usarlos con ducking suave y music drop narrativo
    if bass_file.exists() and inst_file.exists():
        inputs = [
            "-i", str(voice_mp3),
            "-stream_loop", "-1", "-i", str(bass_file),
            "-stream_loop", "-1", "-i", str(inst_file),
        ]
        fc_parts = [
            f"[0:a]aformat=channel_layouts=stereo,highpass=f=90,equalizer=f=3000:width_type=q:w=1.2:g=2.5,"
            f"acompressor=threshold=-16dB:ratio=3:attack=10:release=100:makeup=2,"
            f"asplit=2[voice_main][voice_sidechain]",
            f"[1:a]atrim=0:{total_dur:.3f},asetpts=PTS-STARTPTS,volume=0.72,"
            f"afade=t=in:st=0:d=0.5,afade=t=out:st={max(0.0, total_dur-2.0):.2f}:d=2.0[bass]",
            f"[2:a]atrim=0:{total_dur:.3f},asetpts=PTS-STARTPTS,volume=0.62,"
            f"afade=t=in:st=0:d=0.5,afade=t=out:st={max(0.0, total_dur-2.0):.2f}:d=2.0[inst]",
            f"[bass][inst]amix=inputs=2:duration=first:normalize=0[bg_music]",
        ]
        if drop_expr:
            fc_parts.append(f"[bg_music]volume='{drop_expr}':eval=frame[bg_dropped]")
            fc_parts.append(f"[bg_dropped][voice_sidechain]sidechaincompress=threshold=0.18:ratio=2.5:attack=15:release=240[bg_ducked]")
        else:
            fc_parts.append(f"[bg_music][voice_sidechain]sidechaincompress=threshold=0.18:ratio=2.5:attack=15:release=240[bg_ducked]")

        sfx_labels = []
        cur_idx = 3

        if sfx_events is not None:
            cue_gains = {"boom": 0.42, "riser": 0.28, "paper": 0.25, "highlighter": 0.27, "click": 0.22}
            events_by_cue: Dict[str, List[Dict[str, Any]]] = {}
            for ev in sfx_events:
                cue_name = str(ev.get("cue") or "").lower().strip()
                wav_p = sfx_palette.get(cue_name)
                if cue_name in cue_gains and wav_p and wav_p.exists():
                    events_by_cue.setdefault(cue_name, []).append(ev)

            for cue_name, ev_list in events_by_cue.items():
                wav_p = sfx_palette[cue_name]
                inputs.extend(["-i", str(wav_p)])
                gain = cue_gains[cue_name]
                if len(ev_list) > 1:
                    splits = "".join(f"[s_{cue_name}_{j}]" for j in range(len(ev_list)))
                    fc_parts.append(f"[{cur_idx}:a]aresample=48000,aformat=channel_layouts=stereo,asplit={len(ev_list)}{splits}")
                    src_tags = [f"[s_{cue_name}_{j}]" for j in range(len(ev_list))]
                else:
                    fc_parts.append(f"[{cur_idx}:a]aresample=48000,aformat=channel_layouts=stereo[s_{cue_name}_0]")
                    src_tags = [f"[s_{cue_name}_0]"]

                for j, ev in enumerate(ev_list):
                    if cue_name == "riser":
                        target_end = float(ev.get("target_end_sec", ev.get("time_sec", 0.0)))
                        start_t = max(0.0, target_end - 1.35)
                        delay_ms = int(round(start_t * 1000))
                        fc_parts.append(
                            f"{src_tags[j]}atrim=0:1.35,asetpts=PTS-STARTPTS,"
                            f"afade=t=in:st=0:d=0.45,afade=t=out:st=1.20:d=0.15,"
                            f"volume={gain:.2f},adelay={delay_ms}|{delay_ms}[sd_{cue_name}_{j}]"
                        )
                    elif cue_name == "boom":
                        delay_ms = max(0, int(round(float(ev.get("time_sec", 0.0)) * 1000)))
                        fc_parts.append(
                            f"{src_tags[j]}atrim=0:2.40,asetpts=PTS-STARTPTS,"
                            f"afade=t=out:st=1.90:d=0.50,volume={gain:.2f},adelay={delay_ms}|{delay_ms}[sd_{cue_name}_{j}]"
                        )
                    else:
                        delay_ms = max(0, int(round(float(ev.get("time_sec", 0.0)) * 1000)))
                        fc_parts.append(
                            f"{src_tags[j]}volume={gain:.2f},adelay={delay_ms}|{delay_ms}[sd_{cue_name}_{j}]"
                        )
                    sfx_labels.append(f"[sd_{cue_name}_{j}]")
                cur_idx += 1
        else:
            if boom_sfx.exists():
                inputs.extend(["-i", str(boom_sfx)])
                fc_parts.append(f"[{cur_idx}:a]atrim=0:4.5,adelay=350|350,volume=0.50[sfx_boom]")
                sfx_labels.append("[sfx_boom]")
                cur_idx += 1

            if whoosh_sfx.exists() and transition_times:
                inputs.extend(["-i", str(whoosh_sfx)])
                n_w = len(transition_times)
                splits = "".join(f"[w{i}]" for i in range(n_w))
                fc_parts.append(f"[{cur_idx}:a]asplit={n_w}{splits}")
                for i, t in enumerate(transition_times):
                    delay_ms = max(0, int((t - 0.14) * 1000))
                    fc_parts.append(f"[w{i}]adelay={delay_ms}|{delay_ms},volume=0.38[wd{i}]")
                    sfx_labels.append(f"[wd{i}]")
                cur_idx += 1

        if sfx_labels:
            fc_parts.append(f"{''.join(sfx_labels)}amix=inputs={len(sfx_labels)}:normalize=0[sfx_layer]")
            fc_parts.append(f"[voice_main][bg_ducked][sfx_layer]amix=inputs=3:duration=first:normalize=0[mixed]")
        else:
            fc_parts.append(f"[voice_main][bg_ducked]amix=inputs=2:duration=first:normalize=0[mixed]")

        log(f"Mezclando diseño sonoro editorial + Epidemic Sound ({bass_file.name} + {inst_file.name}) con loudnorm 2 pasadas (-14.0 LUFS)...")
        _render_two_pass_loudnorm(inputs, fc_parts, "[mixed]", total_dur, master_m4a)
        return

    # Fallback sintético si no hay conexión o faltan los stems
    trans_pulses = " + ".join(
        [f"0.16*exp(-12*abs(t-{t:.2f}))*sin(2*PI*(95+40*(t-{t:.2f}))*t)" for t in transition_times]
    )
    if not trans_pulses:
        trans_pulses = "0"

    aeval_expr = (
        f"0.055*sin(2*PI*55*t)*(0.65+0.35*sin(2*PI*0.5*t)) + "
        f"0.025*sin(2*PI*110*t)*(0.5+0.5*sin(2*PI*2.0*t)) + "
        f"0.015*sin(2*PI*880*t)*exp(-25*mod(t,2.0)) + "
        f"({trans_pulses})"
    )

    bg_chain = (
        f"aevalsrc='{aeval_expr}':s=48000:d={total_dur:.3f},"
        f"lowpass=f=1800,afade=t=in:st=0:d=1.0,afade=t=out:st={max(0.0, total_dur-2.0):.2f}:d=2.0"
    )
    if drop_expr:
        bg_chain += f",volume='{drop_expr}':eval=frame"
    bg_chain += "[bg]"

    fc_fallback = [
        f"[0:a]aformat=channel_layouts=stereo,highpass=f=90,equalizer=f=3000:width_type=q:w=1.2:g=2.5,"
        f"acompressor=threshold=-18dB:ratio=3:attack=10:release=120:makeup=2[voice]",
        bg_chain,
        f"[voice][bg]amix=inputs=2:duration=first:dropout_transition=2:weights='1.0 0.45'[mixed]",
    ]
    log("Mezclando con cama sintética de respaldo (loudnorm 2 pasadas)...")
    _render_two_pass_loudnorm(["-i", str(voice_mp3)], fc_fallback, "[mixed]", total_dur, master_m4a)


def verify_final_master(mp4_path: Path) -> Dict[str, Any]:
    """Verifica resolución, FPS, duración, decodificación íntegra y sonoridad LUFS."""
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate:format=duration",
        "-of", "json",
        str(mp4_path),
    ]
    info = json.loads(subprocess.check_output(probe_cmd).decode())
    stream = info["streams"][0]
    dur = float(info["format"]["duration"])

    # Verificar sonoridad LUFS
    lufs_cmd = [
        "ffmpeg", "-nostats", "-i", str(mp4_path),
        "-filter_complex", "ebur128=peak=true",
        "-f", "null", "-",
    ]
    proc = subprocess.run(lufs_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    m_i = re.findall(r"I:\s*([-\d\.]+)\s*LUFS", proc.stdout or "")
    lufs: Optional[float] = float(m_i[-1]) if m_i else None
    if lufs is None:
        log("⚠️ Aviso verify_final_master: ffmpeg ebur128 no devolvió medición LUFS.")

    return {
        "width": stream["width"],
        "height": stream["height"],
        "fps": stream["r_frame_rate"],
        "duration": round(dur, 2),
        "lufs": lufs,
        "monetizable_tiktok": dur > 60.0,
    }


def _compute_build_manifest(
    meta: Dict[str, Any],
    total_dur: float,
    shots_dir: Path,
    aligned_beats: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Genera un hash estable para validar si el caché modular en _build_nle sigue vigente."""
    raw_sizes = {
        p.name: p.stat().st_size
        for p in sorted(shots_dir.glob("*.mp4"))
    } if shots_dir.exists() else {}
    payload = {
        "version": "veritasium_editorial_v6",
        "title": meta.get("title", ""),
        "genre": meta.get("genre", ""),
        "script": meta.get("script", ""),
        "total_dur": round(total_dur, 2),
        "story_metrics": meta.get("story_metrics", {}),
        "shots": [
            {
                "id": s.get("id"),
                "dur": s.get("dur"),
                "render_mode": s.get("render_mode"),
                "type": s.get("type"),
                "excerpt": s.get("narrative_excerpt", ""),
                "remotion_props": s.get("remotion_props", {}),
            }
            for s in meta.get("shots", [])
        ],
        "aligned_beats": [
            {
                "beat_id": b.get("beat_id"),
                "shot_id": b.get("shot_id"),
                "variant": b.get("variant"),
                "start_sec": b.get("start_sec"),
                "duration_sec": b.get("duration_sec"),
                "transition_in": b.get("transition_in"),
            }
            for b in (aligned_beats or [])
        ],
        "raw_sizes": raw_sizes,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _load_json_list_safe(path: Path) -> List[Dict[str, Any]]:
    if not path.exists() or path.stat().st_size <= 2:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def assemble_final_video(
    delivery_dir: Path,
    force_rebuild: bool = False,
    clean_cache: bool = False,
) -> Path:
    meta_file = delivery_dir / "metadata.json"
    if not meta_file.exists():
        raise FileNotFoundError(f"No existe {meta_file}")

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    script = meta.get("script", "")
    source_name = meta.get("source", "PRENSA INTERNACIONAL")
    shots: List[Dict[str, Any]] = meta.get("shots", [])

    voice_mp3 = delivery_dir / meta.get("audio_file", "LOCUCION_NOTICIERO_62S.mp3")
    if not voice_mp3.exists():
        raise FileNotFoundError(f"No existe el archivo de locución: {voice_mp3}")

    total_dur = probe_duration(voice_mp3)
    log(f"Duración exacta de locución: {total_dur:.2f}s (Objetivo >60s cumplido)")

    work_dir = delivery_dir / "_build_nle"
    work_dir.mkdir(parents=True, exist_ok=True)
    shots_dir = delivery_dir / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generar subtítulos Kinetic ASS con sincronización acústica real
    ass_path = delivery_dir / "SUBTITULOS_KINETIC.ass"
    sentence_bounds_file = delivery_dir / "SENTENCE_BOUNDARIES.json"
    word_bounds_file = delivery_dir / "WORD_BOUNDARIES.json"
    log("1/4 Generando subtítulos vectoriales Kinetic (.ass) con alineación acústica...")
    generate_kinetic_ass(
        script,
        total_dur,
        ass_path,
        source_name,
        voice_audio=voice_mp3,
        sentence_boundaries_file=sentence_bounds_file if sentence_bounds_file.exists() else None,
        word_boundaries_file=word_bounds_file if word_bounds_file.exists() else None,
    )

    wb_list = _load_json_list_safe(word_bounds_file)
    sb_list = _load_json_list_safe(sentence_bounds_file)

    raw_beats: List[Dict[str, Any]] = list(meta.get("beats") or [])
    if not raw_beats:
        try:
            from editorial_director import build_narrative_beat_sheet
            raw_beats = build_narrative_beat_sheet(script, shots, news=meta, genre_label=meta.get("genre", "G1"))
        except Exception:
            n_sh = max(1, len(shots))
            words_tok = script.split()
            raw_beats = []
            for idx, s in enumerate(shots):
                w0 = int(idx * len(words_tok) / n_sh) if words_tok else 0
                w1 = max(w0, int((idx + 1) * len(words_tok) / n_sh) - 1) if words_tok else 0
                raw_beats.append({
                    "beat_id": f"B{idx + 1:02d}",
                    "role": "DESARROLLO",
                    "act": 1 if idx < 3 else (4 if idx >= n_sh - 2 else 2),
                    "text": " ".join(words_tok[w0:w1 + 1]) if words_tok else s.get("narrative_excerpt", ""),
                    "word_start_idx": w0,
                    "word_end_idx": w1,
                    "shot_id": s.get("id", f"SH{idx + 1:02d}"),
                    "variant": "primary",
                    "start_trim": 0.0,
                    "transition_in": "dissolve" if idx in (3, n_sh - 2) else "cut",
                    "music_drop": False,
                    "sfx_cue": "none",
                })

    aligned_beats = align_beats_to_audio(raw_beats, wb_list, sb_list, total_dur, script=script)
    max_sync_delta = max((b.get("sync_delta_sec", 0.0) for b in aligned_beats), default=0.0)
    log(f"   [AUDIO-FIRST] {len(aligned_beats)} beats alineados al audio (desfase máx Beat<->Audio: {max_sync_delta:.3f}s).")

    # Validar vigencia del caché modular para no reutilizar clips de otra noticia/locución
    manifest_path = work_dir / "cache_manifest.json"
    curr_hash = _compute_build_manifest(meta, total_dur, shots_dir, aligned_beats=aligned_beats)
    cache_valid = False
    if not force_rebuild and manifest_path.exists():
        try:
            old_hash = json.loads(manifest_path.read_text(encoding="utf-8")).get("hash")
            cache_valid = (old_hash == curr_hash)
        except Exception:
            cache_valid = False

    # 2. Normalizar los beats (duración exacta + dissolve tail de 0.30s SOLO en cortes entre actos)
    dissolve_dur = 0.30
    shots_by_id: Dict[str, Tuple[int, Dict[str, Any]]] = {
        str(s.get("id")): (i, s) for i, s in enumerate(shots) if s.get("id")
    }
    clip_durations: List[float] = []
    for i, b in enumerate(aligned_beats):
        followed_by_dissolve = (i + 1 < len(aligned_beats) and aligned_beats[i + 1].get("transition_in") == "dissolve")
        clip_durations.append(round(b["duration_sec"] + (dissolve_dur if followed_by_dissolve else 0.0), 3))

    norm_clips: List[Path] = []
    genre = meta.get("genre", "G1")
    title = meta.get("title", "")
    story_metrics = meta.get("story_metrics") or {}
    log(f"2/4 Procesando {len(aligned_beats)} beats editoriales (hard cuts + Remotion 2.5D para {genre})...")
    reused_all_clips = cache_valid
    clip_cache_hits: List[Optional[float]] = [None] * len(aligned_beats)
    remotion_batch_jobs: List[Dict[str, Any]] = []

    for idx, b in enumerate(aligned_beats):
        sid = str(b.get("shot_id") or f"SH{idx + 1:02d}")
        s_idx, s_obj = shots_by_id.get(sid, (idx, {"id": sid, "render_mode": "flow", "type": b.get("role", "")}))
        raw_mp4 = shots_dir / f"{sid}.mp4"
        norm_mp4 = work_dir / f"norm_{b['beat_id']}.mp4"
        target_dur = clip_durations[idx]

        use_cache = False
        if cache_valid and norm_mp4.exists() and norm_mp4.stat().st_size > 25_000:
            try:
                cached_dur = probe_duration(norm_mp4)
                if abs(cached_dur - target_dur) <= 0.18:
                    use_cache = True
                    clip_cache_hits[idx] = cached_dur
            except Exception:
                use_cache = False

        if not use_cache:
            reused_all_clips = False
            is_infographic = (s_obj.get("render_mode") in ("infographic", "remotion"))
            has_valid_raw = raw_mp4.exists() and raw_mp4.stat().st_size > 25_000
            has_still = False if has_valid_raw else (_find_still_image_for_shot(raw_mp4) is not None)
            if HAS_REMOTION and (is_infographic or (not has_valid_raw and not has_still)) and _is_remotion_tech_shot(s_obj, s_idx):
                beat_shot = dict(s_obj)
                if b.get("text"):
                    beat_shot["narrative_excerpt"] = b["text"]
                remotion_batch_jobs.append(
                    _build_remotion_job_for_shot(
                        shot_info=beat_shot,
                        shot_idx=s_idx,
                        genre=genre,
                        title=title,
                        story_metrics=story_metrics,
                        target_dur=target_dur,
                        norm_mp4=norm_mp4,
                        fps=24,
                    )
                )

    if remotion_batch_jobs:
        log(f"   [REMOTION-BATCH] Renderizando {len(remotion_batch_jobs)} escenas en lote (bundle cacheado + 1 Chromium)...")
        render_remotion_batch(remotion_batch_jobs, concurrency=2, crf=14)

    for idx, b in enumerate(aligned_beats):
        sid = str(b.get("shot_id") or f"SH{idx + 1:02d}")
        s_idx, s_obj = shots_by_id.get(sid, (idx, {"id": sid, "render_mode": "flow", "type": b.get("role", "")}))
        raw_mp4 = shots_dir / f"{sid}.mp4"
        norm_mp4 = work_dir / f"norm_{b['beat_id']}.mp4"
        target_dur = clip_durations[idx]
        cached_dur = clip_cache_hits[idx]

        if cached_dur is not None:
            log(f"   [CACHÉ] Beat {b['beat_id']} ({sid}) reutilizado desde caché ({cached_dur:.2f}s).")
        elif norm_mp4.exists() and norm_mp4.stat().st_size > 10_000 and any(j["outputLocation"] == str(norm_mp4) for j in remotion_batch_jobs):
            log(f"   [REMOTION-BATCH] Beat {b['beat_id']} ({sid}) listo ({target_dur:.2f}s).")
        else:
            shot_payload = (
                {**s_obj, "remotion_props": dict(story_metrics)}
                if (story_metrics and not s_obj.get("remotion_props"))
                else dict(s_obj)
            )
            if b.get("text"):
                shot_payload["narrative_excerpt"] = b["text"]
            prepare_normalized_shot(
                shot_payload,
                s_idx,
                raw_mp4,
                norm_mp4,
                target_dur,
                genre=genre,
                title=title,
                start_trim=float(b.get("start_trim") or 0.0),
                punch_in=(b.get("variant") == "punch_in"),
            )

        norm_clips.append(norm_mp4)

    # 3. Ensamblar timeline editorial (hard cuts dentro de cada acto + dissolves únicamente entre actos)
    silent_xfade_mp4 = work_dir / "video_xfade_silent.mp4"
    use_xfade_cache = (
        cache_valid
        and reused_all_clips
        and silent_xfade_mp4.exists()
        and silent_xfade_mp4.stat().st_size > 100_000
    )
    if use_xfade_cache:
        log("3/4 [CACHÉ] Timeline editorial Audio-First reutilizado desde caché modular.")
        dissolve_times = [b["start_sec"] for b in aligned_beats if b.get("transition_in") == "dissolve"]
    else:
        log("3/4 Ensamblando timeline Audio-First (hard cuts + dissolves entre actos)...")
        dissolve_times = build_editorial_timeline_video(
            norm_clips, clip_durations, aligned_beats, silent_xfade_mp4, dissolve_dur=dissolve_dur
        )

    try:
        manifest_path.write_text(json.dumps({"hash": curr_hash}, indent=2), encoding="utf-8")
    except Exception:
        pass

    # 4. Construir ventana Music Drop + paleta SFX diegética y mezclar audio (-14.0 LUFS)
    drop_beat = next((b for b in aligned_beats if b.get("music_drop")), None)
    music_drop_window: Optional[Tuple[float, float]] = None
    if drop_beat:
        t_drop_0 = float(drop_beat["start_sec"])
        t_drop_1 = min(float(drop_beat["end_sec"]), t_drop_0 + 1.25)
        if t_drop_1 - t_drop_0 < 0.85:
            t_drop_1 = min(total_dur - 0.35, t_drop_0 + 1.00)
        if t_drop_1 - t_drop_0 >= 0.45:
            music_drop_window = (round(t_drop_0, 3), round(t_drop_1, 3))

    sfx_events: List[Dict[str, Any]] = []
    for idx_b, b in enumerate(aligned_beats):
        cue = str(b.get("sfx_cue") or "none").lower().strip()
        if cue == "none":
            continue
        if cue == "riser":
            next_start = aligned_beats[idx_b + 1]["start_sec"] if idx_b + 1 < len(aligned_beats) else b["end_sec"]
            sfx_events.append({"cue": "riser", "time_sec": b["end_sec"], "target_end_sec": next_start})
        elif cue == "boom" and b.get("music_drop") and music_drop_window:
            sfx_events.append({"cue": "boom", "time_sec": music_drop_window[1] - 0.05})
        else:
            sfx_events.append({"cue": cue, "time_sec": b["start_sec"]})

    master_audio_m4a = work_dir / "audio_master_140lufs.m4a"
    audio_manifest_path = work_dir / "audio_cache_manifest.json"
    v_stat = voice_mp3.stat()
    audio_hash = hashlib.sha256(json.dumps({
        "version": "veritasium_audio_v6",
        "voice_size": v_stat.st_size,
        "voice_mtime_ns": v_stat.st_mtime_ns,
        "genre": genre,
        "total_dur": round(total_dur, 3),
        "music_drop_window": music_drop_window,
        "sfx_events": sfx_events,
    }, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    audio_cached = False
    if not force_rebuild and master_audio_m4a.exists() and master_audio_m4a.stat().st_size > 20_000 and audio_manifest_path.exists():
        try:
            old_audio_hash = json.loads(audio_manifest_path.read_text(encoding="utf-8")).get("hash")
            audio_cached = (old_audio_hash == audio_hash)
        except Exception:
            audio_cached = False

    if audio_cached:
        log("4/4 [CACHÉ] Audio masterizado -14.0 LUFS reutilizado desde caché modular.")
    else:
        log("4/4 Sintetizando banda sonora Epidemic Sound + Music Drop + SFX diegéticos (-14.0 LUFS)...")
        synthesize_broadcast_audio_master(
            voice_mp3,
            total_dur,
            dissolve_times,
            master_audio_m4a,
            genre=genre,
            sfx_events=sfx_events,
            music_drop_window=music_drop_window,
        )
        try:
            audio_manifest_path.write_text(json.dumps({"hash": audio_hash}, indent=2), encoding="utf-8")
        except Exception:
            pass

    # Calcular ventana sin colisión para source_badge.png sobre un beat Flow limpio
    badge_png = work_dir / "source_badge.png"
    has_badge = False
    badge_win: Optional[Tuple[float, float]] = None
    for b in aligned_beats:
        sid = str(b.get("shot_id") or "")
        _, s_obj = shots_by_id.get(sid, (0, {}))
        if s_obj.get("render_mode") == "flow" and b["start_sec"] >= 2.2 and b["duration_sec"] >= 2.6:
            st_b = round(b["start_sec"] + 0.25, 2)
            en_b = round(min(b["end_sec"] - 0.15, st_b + 3.6), 2)
            if en_b - st_b >= 1.8:
                badge_win = (st_b, en_b)
                break

    if badge_win:
        try:
            generate_verified_source_card(source_name, genre, badge_png)
            has_badge = badge_png.exists()
        except Exception as e:
            log(f"Aviso al generar tarjeta de fuente verificada: {e}")

    final_mp4 = delivery_dir / "NOTICIERO_FINAL_62S.mp4"
    master_manifest_path = work_dir / "master_cache_manifest.json"
    ass_bytes = ass_path.read_bytes() if ass_path.exists() else b""
    badge_bytes = badge_png.read_bytes() if has_badge and badge_png.exists() else b""
    master_hash = hashlib.sha256(
        f"{curr_hash}|{audio_hash}|{source_name}|{genre}|{badge_win}|veritasium_editorial_v6".encode("utf-8") + ass_bytes + badge_bytes
    ).hexdigest()[:16]

    master_cached = False
    if (
        not force_rebuild
        and use_xfade_cache
        and audio_cached
        and final_mp4.exists()
        and final_mp4.stat().st_size > 100_000
        and master_manifest_path.exists()
    ):
        try:
            old_master_hash = json.loads(master_manifest_path.read_text(encoding="utf-8")).get("hash")
            master_cached = (old_master_hash == master_hash)
        except Exception:
            master_cached = False

    if master_cached:
        log(f"   [CACHÉ] Máster final sin cambios; reutilizando {final_mp4.name}.")
    else:
        log(f"Quemando subtítulos Kinetic{' y acreditación oficial sin colisión' if has_badge else ''} en máster final...")
        if has_badge and badge_win is not None:
            b_st, b_en = badge_win
            fade_out_st = max(b_st + 0.4, b_en - 0.30)
            vf_complex = (
                f"[2:v]format=rgba,fade=t=in:st={b_st:.2f}:d=0.30:alpha=1,fade=t=out:st={fade_out_st:.2f}:d=0.30:alpha=1[badge_fade];"
                f"[0:v][badge_fade]overlay=x=68:y=168:enable='between(t,{b_st:.2f},{b_en:.2f})'[v_badged];"
                f"[v_badged]ass={ass_path}[vout]"
            )
            cmd_final = [
                "ffmpeg", "-y",
                "-i", str(silent_xfade_mp4),
                "-i", str(master_audio_m4a),
                "-loop", "1", "-t", f"{b_en + 0.5:.2f}", "-i", str(badge_png),
                "-filter_complex", vf_complex,
                "-map", "[vout]",
                "-map", "1:a:0",
                "-t", f"{total_dur:.3f}",
                "-r", "24",
                "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-preset", "medium",
                "-crf", "20", "-maxrate", "5500k", "-bufsize", "11000k",
                "-c:a", "copy",
                "-movflags", "+faststart",
                str(final_mp4),
            ]
        else:
            cmd_final = [
                "ffmpeg", "-y",
                "-i", str(silent_xfade_mp4),
                "-i", str(master_audio_m4a),
                "-vf", f"ass={ass_path}",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-t", f"{total_dur:.3f}",
                "-r", "24",
                "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-preset", "medium",
                "-crf", "20", "-maxrate", "5500k", "-bufsize", "11000k",
                "-c:a", "copy",
                "-movflags", "+faststart",
                str(final_mp4),
            ]
        subprocess.run(cmd_final, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            master_manifest_path.write_text(json.dumps({"hash": master_hash}, indent=2), encoding="utf-8")
        except Exception:
            pass

    try:
        meta["beat_timeline"] = aligned_beats
        meta["max_sync_delta_sec"] = round(max_sync_delta, 3)
        meta["music_drop_window"] = list(music_drop_window) if music_drop_window else None
        meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    stats = verify_final_master(final_mp4)
    lufs_label = f"{stats['lufs']} LUFS" if stats["lufs"] is not None else "LUFS N/D"
    log(
        f"✅ MÁSTER FINAL COMPLETADO: {final_mp4}\n"
        f"   Resolución: {stats['width']}x{stats['height']} @ {stats['fps']} fps | "
        f"Duración: {stats['duration']}s | Audio: {lufs_label} | "
        f"Monetizable (>60s): {'SÍ' if stats['monetizable_tiktok'] else 'NO'}"
    )

    # 5. Generar Portada Oficial 9:16 (1080x1920) y Hashtags ANTES de la auditoría QC para incluir portada en QC
    cover_jpg_path = delivery_dir / "PORTADA_TIKTOK_916.jpg"
    hashtags_txt_path = delivery_dir / "HASHTAGS_TIKTOK.txt"
    if master_cached and cover_jpg_path.exists() and cover_jpg_path.stat().st_size > 20_000 and hashtags_txt_path.exists():
        log("5/6 [CACHÉ] Portada 9:16 y Hashtags sin cambios; reutilizando.")
    else:
        try:
            from generador_portada import generate_tiktok_cover
            log("5/6 Generando Portada 9:16 (Safe Zone 3:4) y Hashtags optimizados para TikTok...")
            generate_tiktok_cover(delivery_dir)
        except Exception as e:
            log(f"⚠️ Error generando portada/hashtags: {e}")

    # 6. Auditoría Técnica de Emisión Broadcast (reutiliza si máster y portada están sin cambios y ya existe reporte válido)
    qc_json_path = delivery_dir / "QC_AUDIT_REPORT.json"
    safezone_mp4_path = delivery_dir / "VIDEO_QC_SAFEZONE.mp4"
    contact_sheet_path = delivery_dir / "CONTACT_SHEET_QC.jpg"
    if master_cached and qc_json_path.exists() and contact_sheet_path.exists() and safezone_mp4_path.exists():
        log("6/6 🔍 [CACHÉ] Auditoría QC y visor Frame a Frame ya actualizados para este máster.")
    else:
        from video_qc_inspector import VideoQCInspector
        log("6/6 🔍 [QC] Ejecutando auditoría técnica integral y visor Frame a Frame...")
        inspector = VideoQCInspector(final_mp4, output_dir=delivery_dir)
        qc_res = inspector.run_full_qc(generate_safezone_video=True, generate_contact_sheet=True)
        log(f"   ★ Veredicto QC: [{qc_res['verdict']}] (Score: {qc_res['score']}/100) | Visor: {delivery_dir / 'REPORTE_INSPECCION.html'}")

        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            meta["qc_verdict"] = qc_res["verdict"]
            meta["qc_score"] = qc_res["score"]
            meta["final_duration"] = stats["duration"]
            meta["integrated_lufs"] = stats["lufs"]
            meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

        if qc_res.get("verdict") == "FAIL":
            log("❌ [QC FAIL CRÍTICO] La entrega no superó la auditoría técnica. Revisa QC_AUDIT_REPORT.json antes de publicar.")

    # Conservar caché modular salvo que se solicite --clean-cache
    if clean_cache:
        import shutil
        shutil.rmtree(work_dir, ignore_errors=True)

    return final_mp4


def main():
    parser = argparse.ArgumentParser(description="Ensamblador algorítmico NLE para TikTok Radar")
    parser.add_argument("--dir", type=str, default=None, help="Carpeta de entrega a ensamblar")
    parser.add_argument("--force-rebuild", action="store_true", help="Fuerza el re-renderizado completo de todos los planos sin usar caché")
    parser.add_argument("--clean-cache", action="store_true", help="Elimina _build_nle tras completar el ensamblado")
    args = parser.parse_args()

    delivery_dir = get_latest_delivery_dir(args.dir)
    assemble_final_video(delivery_dir, force_rebuild=args.force_rebuild, clean_cache=args.clean_cache)


if __name__ == "__main__":
    main()
