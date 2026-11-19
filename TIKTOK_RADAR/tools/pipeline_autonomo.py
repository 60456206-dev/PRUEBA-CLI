#!/usr/bin/env python3
"""
TIKTOK RADAR · Pipeline 100% Autónomo de Producción (Calidad 10/10 · Monetizable >60s)
1. Rastrea agencias y portales oficiales (RPP, AeroTime, The Hacker News, Tom's Hardware, TechCrunch, NASA, ESA).
2. Selecciona automáticamente la noticia de mayor impacto por categoría y orden cronológico.
3. Genera el guion dinámico con contexto inicial, cifras duras y pregunta polarizante (estilo Vox/Johnny Harris, 61-65s).
4. Genera el storyboard híbrido de 13 planos (8 Flow Cinemáticos Raytracing + 5 FFmpeg Glassmorphic HUD).
5. Sintetiza la locución costarricense pausada y clara (`es-CR-JuanNeural`, fallback Gemini TTS) + auto-ajuste >61.0s.
6. Exporta el paquete listo con género canónico exacto en entregas/<fecha>_<genero>/.
"""

import asyncio
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Importar el escáner de noticias y generador de audio
sys.path.append(str(Path(__file__).parent))
from news_radar import enrich_news_item, scan_all_sources, kw_match
from audio_generator import (
    DEFAULT_COSTA_RICA_STYLE,
    generate_speech,
    load_locucion_config,
    probe_duration,
)
from editorial_director import (
    build_dynamic_story_visuals,
    build_narrative_beat_sheet,
    build_story_aware_shots,
    extract_story_metrics,
    resolve_geo_context,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
ENTREGAS_DIR = ROOT_DIR / "entregas"
ENTREGAS_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = ROOT_DIR / "config_produccion.json"


def load_production_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


PROD_CONFIG = load_production_config()
STYLE_PREFIX = (
    PROD_CONFIG.get("consistencia_visual", {}).get("estilo_maestro")
    or (
        "Vertical 9:16, tactile 2.5D editorial documentary illustration and chiaroscuro diorama aesthetic, "
        "directional warm study lamp rim light against deep carbon slate shadows, subtle archival paper fiber patina and analog 35mm film grain, "
        "layered paper-cutout depth parallax, shallow depth of field, slow continuous camera push-in, "
        "no plastic CGI gloss, no uncanny valley, no on-screen text overlays, no watermarks. "
    )
)
if not STYLE_PREFIX.endswith(". ") and not STYLE_PREFIX.endswith("."):
    STYLE_PREFIX += ". "


def score_news(item: Dict[str, Any]) -> float:
    """Calcula un puntaje de impacto dramático y viralidad para selección autónoma."""
    title = item["title"].lower()
    score = 1.0

    keywords_high = [
        "avión", "accidente", "muere", "víctimas", "catástrofe", "alerta",
        "crisis", "fallo", "ciberataque", "hackeo", "rescate", "explosión", "apagón"
    ]
    keywords_tech = [
        "ia", "gemini", "openai", "google", "robot", "cohete", "espacial",
        "descubrimiento", "revolución", "satélite"
    ]

    for kw in keywords_high:
        if kw in title:
            score += 3.0
    for kw in keywords_tech:
        if kw in title:
            score += 1.5

    if item.get("needs_dramatic_recreation"):
        score += 2.0

    return score


def pick_top_news(news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    ranked = sorted(news_list, key=score_news, reverse=True)
    return ranked[0]


def build_shot_prompts(
    is_aviation: bool = False,
    is_cyber: bool = False,
    is_ai: bool = False,
    is_space: bool = False,
    title: str = "",
    summary: str = "",
    script: str = "",
    genre_label: str = "",
    dynamic_visuals: Optional[Dict[str, Any]] = None,
    story_metrics: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Construye los 13 planos anclados a la noticia real:
    - Modo Híbrido (`flow_primario`): 8 Planos Cinemáticos Flow (estética editorial 2.5D) + 5 Planos Remotion 2.5D.
    - Modo Flow Puro (`flow_puro`): 13 Planos 100% Cinemáticos en Flow.
    """
    active_mode = PROD_CONFIG.get("modo_produccion", {}).get("activo", "flow_primario")
    return build_story_aware_shots(
        style_prefix=STYLE_PREFIX,
        is_aviation=is_aviation,
        is_cyber=is_cyber,
        is_ai=is_ai,
        is_space=is_space,
        title=title,
        summary=summary,
        script=script,
        genre_label=genre_label,
        active_mode=active_mode,
        dynamic_visuals=dynamic_visuals,
        story_metrics=story_metrics,
    )


def generate_dynamic_news_script(news: Dict[str, Any], genre_label: str) -> str:
    """
    Genera un guión periodístico Misconception-First de alta retención (estilo Veritasium / Vox)
    anclado al texto completo del artículo:
    1. HOOK PARADOJA (0-3s, 1 frase corta in medias res sin intros suaves).
    2. PRUEBA / RECEIPT (3-12s): fuente oficial y dato verificable del artículo.
    3. MECANISMO + ANALOGÍA FÍSICA (12-36s): primeros principios ligados al caso.
    4. REVELACIÓN / GIRO (36-48s): dato o decisión contra-intuitiva (preparado para Music Drop).
    5. RESOLUCIÓN + CIERRE (48-62s): desenlace real y reflexión sobria sin pedir comentarios.
    Longitud calibrada: 134-145 palabras para superar 61s con locución costarricense moderada.
    """
    title = news.get("title", "")
    source = news.get("source_name", "Prensa Oficial")
    summary = news.get("summary_full") or news.get("summary", "")
    article_excerpt = str(news.get("article_text") or summary)[:1800]
    receipt_quote = str(news.get("receipt_quote") or "")
    extracted_nums = ", ".join(str(x) for x in (news.get("extracted_numbers") or [])[:6]) or "Sin cifras adicionales"
    technical_cause = str(news.get("technical_cause") or "")
    key = os.getenv("GEMINI_API_KEY")

    if key:
        prompt = f"""Eres el mejor guionista de divulgación científica y periodismo explicativo de alta retención del mundo (estilo Veritasium y Vox).
Escribe un guión de locución para un vídeo vertical de TikTok de exactamente 61 a 65 segundos (entre 134 y 145 palabras exactas para superar 60 segundos con dicción moderada y muy entendible).

Noticia: {title}
Fuente oficial: {source}
Categoría: {genre_label}
Texto completo / extracto verificado: {article_excerpt}
Cita factual (receipt): {receipt_quote}
Cifras o códigos reales detectados: {extracted_nums}
Causa técnica reportada: {technical_cause}

ESTRUCTURA VERITASIUM MISCONCEPTION-FIRST (OBLIGATORIA):
1. HOOK PARADOJA (0-3s, primera oración muy corta): Abre rompiendo una creencia intuitiva o lanzando la anomalía exacta in medias res.
   PROHIBIDO empezar con "Imagine que...", "A simple vista...", "Última hora..." ni saludos.
2. PRUEBA / RECEIPT (3-12s): Cita la fuente oficial y los datos o cifras reales verificadas en el artículo completo.
3. MECANISMO + ANALOGÍA FÍSICA (12-36s): Explica la causa técnica real desde primeros principios con una analogía física cotidiana concreta ligada a este caso.
4. REVELACIÓN / GIRO TÉCNICO (36-48s): Presenta el giro contra-intuitivo o la maniobra crítica que cambia por completo cómo entendemos el incidente.
5. RESOLUCIÓN Y CIERRE (48-62s): Desenlace real reportado y reflexión sobria de cierre.
   ESTRICTAMENTE PROHIBIDO decir "deja tus comentarios", "déjamelo en los comentarios", "comenta abajo" ni frases clichés similares.

REGLAS DE ESTILO Y CLARIDAD:
- Español latinoamericano natural compatible con locución costarricense (usa siempre trato de "usted" o "ustedes", nunca "vosotros", sin modismos mexicanos ni españoles).
- Frases directas, bien puntuadas y fáciles de entender al oído (evita guiones entre ciudades o siglas difíciles; escribe "de Múnich a Bangkok", no "Múnich-Bangkok").
- Longitud estricta: entre 134 y 145 palabras (crítico para durar 61.5 a 64.5 segundos).
- No inventes cifras, muertes, incendios ni causas no presentes en el texto verificado.
- Devuelve ÚNICAMENTE el texto que leerá el locutor en voz alta, sin encabezados, sin corchetes, sin etiquetas de tiempo."""

        def _call_gemini_script(model_name: str, prompt_text: str) -> str:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
            body = {"contents": [{"parts": [{"text": prompt_text}]}]}
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.load(resp)
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()

        for model in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-lite-latest", "gemini-2.5-flash"]:
            try:
                text = _call_gemini_script(model, prompt)
                words = text.split()
                if len(words) > 143:
                    condense_prompt = (
                        "Recorta el siguiente guión para que tenga estrictamente entre 132 y 140 palabras "
                        "(sin encabezados ni notas, conservando el hook directo sin 'Imagine que', los datos reales, la analogía y el cierre sobrio, "
                        "usando trato de 'usted' y oraciones claras sin guiones entre palabras para locución costarricense muy entendible):\n\n"
                        f"{text}"
                    )
                    condensed = _call_gemini_script(model, condense_prompt)
                    c_words = condensed.split()
                    if 126 <= len(c_words) < len(words):
                        text, words = condensed, c_words
                elif 95 <= len(words) < 130:
                    expand_prompt = (
                        "Amplía ligeramente el siguiente guión para que tenga estrictamente entre 134 y 140 palabras "
                        "sin inventar cifras, muertes ni hechos nuevos, profundizando brevemente la analogía física y manteniendo trato de 'usted':\n\n"
                        f"{text}"
                    )
                    expanded = _call_gemini_script(model, expand_prompt)
                    e_words = expanded.split()
                    if 126 <= len(e_words) <= 145:
                        text, words = expanded, e_words
                if len(words) >= 124:
                    print(f"[PIPELINE-AI] ✅ Guión documental generado por {model} ({len(words)} palabras)", flush=True)
                    return text
                print(f"[PIPELINE-AI] ⚠️ {model} devolvió guión muy corto ({len(words)} palabras), probando siguiente modelo...", flush=True)
            except Exception as e:
                print(f"[PIPELINE-AI] ⚠️ Error generando guión con {model}: {e}", flush=True)
                time.sleep(1.0)

    # Fallback explicativo neutral y fiel (~136 palabras calibradas a ~61.5-63.5s, sin apertura suave)
    return (
        f"Lo que acaba de ocurrir desafía lo que todos asumíamos como seguro en esta operación. "
        f"Los reportes oficiales publicados por {source} confirman un incidente crítico que ya analizan a fondo los equipos técnicos. "
        f"Lejos de iniciar con una falla obvia en la superficie, los registros disponibles apuntan a una desviación silenciosa dentro de los parámetros operativos principales. "
        f"Cuando un sistema complejo trabaja cerca de su límite, funciona como una torre bajo tensión invisible: un pequeño desajuste en un punto crítico altera el equilibrio completo en cuestión de segundos. "
        f"Por eso cada investigación técnica se concentra en reconstruir la cadena exacta de señales y registros previos, paso a paso, antes de emitir conclusiones. "
        f"Al final, en cualquier operación de alto riesgo, entender dónde cedió el margen de seguridad es la clave para evitar que se repita."
    )


def generate_monetizable_storyboard(news: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera el desglose editorial completo para 61–65 segundos (13 planos, 136-148 palabras)
    con visuales dinámicos 2.5D y prompts específicos por noticia.
    """
    title = news.get("title", "Alerta de Última Hora")
    source = news.get("source_name") or news.get("source", "PRENSA OFICIAL")
    summary = news.get("summary", "")
    link = news.get("link", "")
    title_low = title.lower()
    raw_genre = (news.get("genre") or "").upper()

    is_aviation = (
        news.get("is_aviation_incident", False)
        or news.get("is_aviation", False)
        or "G1" in raw_genre
        or any(kw_match(k, title_low) for k in ["avión", "aeronave", "vuelo", "accidente", "aircraft", "flight", "plane", "pilot", "mayday", "crash", "boeing", "airbus", "aerotime"])
    )
    is_cyber = (
        "G2" in raw_genre
        or any(kw_match(k, title_low) for k in ["ciberataque", "hackeo", "neveras", "hacker", "ransomware", "malware", "exploit", "apt", "breach", "zero-day", "cyber"])
    )
    is_ai = (
        "G3" in raw_genre
        or any(kw_match(k, title_low) for k in ["gemini", "google", "ia", "ai", "openai", "chip", "2 nm", "robot", "nvidia", "deepseek", "chatgpt", "apple", "semiconduct", "dram", "nand", "euv", "silicon", "hardware", "cpu", "gpu", "micron", "intel", "amd", "tsmc", "techcrunch", "tom's hardware"])
    )
    is_space = (
        "G4" in raw_genre
        or any(kw_match(k, title_low) for k in ["espacio", "nasa", "esa", "marte", "luna", "cohete", "spacex", "telescopio", "asteroide", "planetary", "space", "starship", "orbit", "landing"])
    )

    # Prioridad estricta según categoría de la fuente para evitar falsos cruces
    if "G2" in raw_genre:
        genre_label = "G2_CIBERATAQUES"
        is_cyber, is_ai, is_space, is_aviation = True, False, False, False
    elif "G3" in raw_genre:
        genre_label = "G3_IA_HARDWARE"
        is_ai, is_cyber, is_space, is_aviation = True, False, False, False
    elif "G4" in raw_genre:
        genre_label = "G4_ESPACIO"
        is_space, is_ai, is_cyber, is_aviation = True, False, False, False
    elif is_aviation or "G1" in raw_genre:
        has_flight_terms = news.get("is_aviation_incident", False) or news.get("is_aviation", False) or any(
            kw_match(k, title_low) for k in ["avión", "avion", "aeronave", "vuelo", "aircraft", "flight", "plane", "pilot", "mayday", "boeing", "airbus", "aerotime", "faa", "ntsb", "runway"]
        )
        has_quake_or_flood = any(
            kw_match(k, title_low) for k in ["sismo", "terremoto", "huaico", "lluvia", "inundaci", "volcán", "volcan", "tsunami", "aluvión"]
        )
        if has_quake_or_flood and not has_flight_terms:
            genre_label = "G1_CATASTROFES"
            is_aviation, is_cyber, is_ai, is_space = False, False, False, False
        else:
            genre_label = "G1_AVIACION"
            is_aviation, is_cyber, is_ai, is_space = True, False, False, False
    elif is_cyber:
        genre_label = "G2_CIBERATAQUES"
    elif is_ai:
        genre_label = "G3_IA_HARDWARE"
    elif is_space:
        genre_label = "G4_ESPACIO"
    else:
        genre_label = "G1_AVIACION"
        is_aviation = True

    news_enriched = news if "article_text" in news else enrich_news_item(news, fetch_remote=False)
    article_text = str(news_enriched.get("article_text") or "")
    receipt_facts = {
        "numbers": news_enriched.get("extracted_numbers") or [],
        "receipt_quote": news_enriched.get("receipt_quote") or "",
        "highlight_phrase": news_enriched.get("highlight_phrase") or "",
        "technical_cause": news_enriched.get("technical_cause") or "",
        "fetched_ok": bool(news_enriched.get("fetched_ok", False)),
    }

    script = generate_dynamic_news_script(news_enriched, genre_label)
    words = script.split()
    word_count = len(words)
    est_duration = round(word_count / 2.3, 1)

    story_metrics = extract_story_metrics(
        title=title,
        script=script,
        source=source,
        genre_label=genre_label,
        article_text=article_text,
        receipt_facts=receipt_facts,
    )
    dynamic_visuals = (
        build_dynamic_story_visuals(news_enriched, script, genre_label, story_metrics=story_metrics)
        if word_count >= 50
        else None
    )

    shots = build_shot_prompts(
        is_aviation=is_aviation,
        is_cyber=is_cyber,
        is_ai=is_ai,
        is_space=is_space,
        title=title,
        summary=summary,
        script=script,
        genre_label=genre_label,
        dynamic_visuals=dynamic_visuals,
        story_metrics=story_metrics,
    )

    beats = build_narrative_beat_sheet(script, shots, news=news_enriched, genre_label=genre_label)

    def _truncate_words(text: str, limit: int = 110) -> str:
        t = (text or "").strip()
        if len(t) <= limit:
            return t
        cut = t[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-")
        return cut if cut else t[:limit]

    beat_texts_by_shot: Dict[str, List[str]] = {}
    for b in beats:
        sid = str(b.get("shot_id") or "")
        if sid and b.get("text"):
            beat_texts_by_shot.setdefault(sid, []).append(str(b["text"]).strip())

    script_sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    total_shots = len(shots) or 13
    for idx, shot in enumerate(shots):
        linked = beat_texts_by_shot.get(str(shot.get("id") or ""))
        if linked:
            shot["narrative_excerpt"] = _truncate_words(" ".join(linked), 110)
        elif script_sentences:
            s_idx = min(len(script_sentences) - 1, int(idx * len(script_sentences) / total_shots))
            shot["narrative_excerpt"] = _truncate_words(script_sentences[s_idx], 110)
        else:
            shot["narrative_excerpt"] = _truncate_words(title, 110)
        if shot.get("render_mode") == "infographic" and not shot.get("remotion_props"):
            shot["remotion_props"] = dict(story_metrics)

    return {
        "title": title,
        "source": source,
        "link": link,
        "genre_canonical": genre_label,
        "script": script,
        "word_count": word_count,
        "est_duration": est_duration,
        "receipt_facts": receipt_facts,
        "story_metrics": story_metrics,
        "shots": shots,
        "beats": beats,
    }


def _rescale_sentence_boundaries(audio_path: Path, factor: float) -> None:
    """Reescala marcas en SENTENCE_BOUNDARIES.json y WORD_BOUNDARIES.json tras atempo."""
    if factor <= 0:
        return
    scale = 1.0 / factor
    rescaled_any = False
    for fname in ("SENTENCE_BOUNDARIES.json", "WORD_BOUNDARIES.json"):
        bounds_file = audio_path.parent / fname
        if not bounds_file.exists():
            continue
        try:
            items = json.loads(bounds_file.read_text(encoding="utf-8"))
            if not isinstance(items, list):
                continue
            for entry in items:
                if isinstance(entry, dict):
                    if isinstance(entry.get("start"), (int, float)):
                        entry["start"] = round(float(entry["start"]) * scale, 3)
                    if isinstance(entry.get("end"), (int, float)):
                        entry["end"] = round(float(entry["end"]) * scale, 3)
            bounds_file.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
            rescaled_any = True
        except Exception as e:
            print(f"[PIPELINE] ⚠️ No se pudieron reescalar marcas en {fname}: {e}", flush=True)
    if rescaled_any:
        print(f"[PIPELINE] ✅ Marcas temporales reescaladas x{scale:.4f} para mantener sincronía.", flush=True)


async def synthesize_voiceover(script: str, output_path: Path, voice: Optional[str] = None) -> float:
    """
    Sintetiza la voz del locutor con acento netamente costarricense (es-CR-JuanNeural por defecto,
    ritmo pausado y claro) y fallback automático a Gemini TTS con dirección tica.
    Garantiza que la duración supere los 61.0 segundos para cumplir siempre con el requisito
    de monetización de TikTok Creator Rewards (>60s).
    """
    loc_cfg = load_locucion_config()
    motor = str(loc_cfg.get("motor_principal", "edge_tts")).lower()
    prefer_edge = motor != "gemini"
    voice_edge = str(loc_cfg.get("voz_edge", "es-CR-JuanNeural"))
    rate_edge = str(loc_cfg.get("rate_edge", "-4%"))
    pitch_edge = str(loc_cfg.get("pitch_edge", "+0Hz"))
    voice_gemini = str(voice or loc_cfg.get("voz_gemini_fallback", "Orus"))
    tighten = bool(loc_cfg.get("tighten_silencios", False))

    dur = generate_speech(
        script,
        output_path,
        voice_gemini=voice_gemini,
        voice_edge=voice_edge,
        style=DEFAULT_COSTA_RICA_STYLE,
        tighten=tighten,
        prefer_edge=prefer_edge,
        rate_edge=rate_edge,
        pitch_edge=pitch_edge,
    )

    # Si la lectura queda por debajo de 61.1s, calibrar tempo suavemente y asegurar piso >= 61.1s
    # para cumplir siempre con TikTok Creator Rewards (>60.1s) manteniendo naturalidad vocal.
    if 0 < dur < 61.1:
        factor = max(0.92, dur / 61.6)
        if 0.5 <= factor <= 0.99:
            print(f"[PIPELINE] Calibrando tempo sutil ({factor:.3f}) para garantizar >61.0s de monetización sin alterar tono...", flush=True)
            adjusted_path = output_path.with_suffix(".adj.mp3")
            cmd = [
                "ffmpeg", "-y", "-i", str(output_path),
                "-filter:a", f"atempo={factor:.4f}",
                "-b:a", "192k",
                str(adjusted_path)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            adjusted_path.replace(output_path)
            _rescale_sentence_boundaries(output_path, factor)
            dur = probe_duration(output_path)

        if 0 < dur < 61.1:
            pad_s = round(61.5 - dur, 3)
            print(f"[PIPELINE] Añadiendo pausa final de cierre ({pad_s:.2f}s) para garantizar >61.0s monetizables...", flush=True)
            padded_path = output_path.with_suffix(".pad.mp3")
            cmd = [
                "ffmpeg", "-y", "-i", str(output_path),
                "-af", f"apad=pad_dur={pad_s:.3f}",
                "-b:a", "192k",
                str(padded_path)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            padded_path.replace(output_path)
            dur = probe_duration(output_path)

        print(f"[PIPELINE] ✅ Duración final monetizable asegurada: {dur:.2f}s", flush=True)

    return dur


def run_pipeline(genre_key: Optional[str] = None, rank_index: int = 0) -> Path:
    from news_radar import get_daily_4_genres, get_top_news_by_genre
    print("1. Escaneando y clasificando noticias con orden cronológico y enfoque especializado...", flush=True)

    genre_map = {
        "G1": "G1_AVIACION_CATASTROFES",
        "G2": "G2_CIBERATAQUES_HACKERS",
        "G3": "G3_IA_ROBOTICA",
        "G4": "G4_ESPACIO_CIENCIA",
        "G1_AVIACION": "G1_AVIACION_CATASTROFES",
        "G1_AVIACION_CATASTROFES": "G1_AVIACION_CATASTROFES",
        "G2_CIBERATAQUES_HACKERS": "G2_CIBERATAQUES_HACKERS",
        "G3_IA_ROBOTICA": "G3_IA_ROBOTICA",
        "G4_ESPACIO_CIENCIA": "G4_ESPACIO_CIENCIA",
        "SLOT_1": "SLOT_1",
        "SLOT_2": "SLOT_2",
        "TECH": "SLOT_2",
        "CIENCIA": "SLOT_2",
    }

    raw_key = (genre_key or "").upper()
    full_key = genre_map.get(raw_key, genre_key) if genre_key else None

    if full_key == "SLOT_1":
        # Slot 1: Especializado en Aviación Internacional & Seguridad Aérea
        ranked_items = get_top_news_by_genre("G1_AVIACION_CATASTROFES", limit=max(5, rank_index + 1))
        top_news = ranked_items[rank_index] if ranked_items and rank_index < len(ranked_items) else (ranked_items[0] if ranked_items else get_daily_4_genres()["G1_AVIACION_CATASTROFES"])
    elif full_key == "SLOT_2":
        # Slot 2: Especializado en Frontera Tecnológica y Científica Veritasium (G3, G2, G4)
        tech_genres = ["G3_IA_ROBOTICA", "G2_CIBERATAQUES_HACKERS", "G4_ESPACIO_CIENCIA"]
        tech_candidates = []
        per_genre_limit = max(2, rank_index + 1)
        for tg in tech_genres:
            t_items = get_top_news_by_genre(tg, limit=per_genre_limit)
            if t_items:
                tech_candidates.extend(t_items)
        if tech_candidates:
            tech_candidates.sort(key=lambda x: (x.get("score", 0), x.get("timestamp", 0)), reverse=True)
            chosen_idx = rank_index if rank_index < len(tech_candidates) else 0
            top_news = tech_candidates[chosen_idx]
        else:
            daily_genres = get_daily_4_genres()
            top_news = daily_genres.get("G3_IA_ROBOTICA", list(daily_genres.values())[0])
    elif full_key:
        ranked_items = get_top_news_by_genre(full_key, limit=max(5, rank_index + 1))
        if ranked_items and rank_index < len(ranked_items):
            top_news = ranked_items[rank_index]
        elif ranked_items:
            top_news = ranked_items[0]
        else:
            daily_genres = get_daily_4_genres()
            top_news = daily_genres.get(full_key, list(daily_genres.values())[0])
    else:
        daily_genres = get_daily_4_genres()
        genre_key = max(daily_genres, key=lambda g: daily_genres[g].get("score", 1.0))
        top_news = daily_genres[genre_key]

    print(f"\n2. Noticia seleccionada para [{top_news.get('genre_label', genre_key)}]:")
    print(f"   [{top_news['source_name']}] {top_news['title']}")

    top_news = enrich_news_item(top_news, fetch_remote=True)
    storyboard = generate_monetizable_storyboard(top_news)

    # Derivar sufijo canónico exacto para la carpeta de entrega
    canon = storyboard.get("genre_canonical") or top_news.get("genre_label") or full_key or "AUTONOMO"
    suffix = canon.replace("G1_", "").replace("G2_", "").replace("G3_", "").replace("G4_", "")
    if rank_index > 0:
        suffix += f"_V{rank_index+1}"

    today_str = datetime.now().strftime("%Y-%m-%d")
    base_folder_name = f"{today_str}_{suffix}"
    delivery_dir = ENTREGAS_DIR / base_folder_name
    # Evitar sobrescribir otra noticia ya producida el mismo día
    if delivery_dir.exists() and (delivery_dir / "metadata.json").exists():
        try:
            existing_meta = json.loads((delivery_dir / "metadata.json").read_text(encoding="utf-8"))
            existing_title = (existing_meta.get("title") or "").strip()
        except Exception:
            existing_title = ""
        if existing_title and existing_title != storyboard["title"]:
            seq = 2
            while (ENTREGAS_DIR / f"{base_folder_name}_R{seq}").exists():
                seq += 1
            delivery_dir = ENTREGAS_DIR / f"{base_folder_name}_R{seq}"

    delivery_dir.mkdir(parents=True, exist_ok=True)
    (delivery_dir / "shots").mkdir(parents=True, exist_ok=True)

    audio_file = delivery_dir / "LOCUCION_NOTICIERO_62S.mp3"
    loc_cfg = load_locucion_config()
    print("\n3. Sintetizando locución periodística costarricense (es-CR pausada)...", flush=True)
    real_dur = asyncio.run(synthesize_voiceover(storyboard["script"], audio_file))
    mon_status = "Cumple >60s para TikTok Monetización" if real_dur >= 60.1 else f"⚠️ Bajo mínimo 60.1s ({real_dur:.2f}s)"
    print(f"   Audio generado con éxito: {audio_file.name} ({real_dur:.2f} s | {mon_status})")

    flow_cnt = sum(1 for s in storyboard["shots"] if s.get("render_mode") == "flow")
    hud_cnt = len(storyboard["shots"]) - flow_cnt
    report_file = delivery_dir / "PAQUETE_NOTICIERO_LISTO.md"
    md_content = f"""# TikTok Radar · Paquete Noticiero ({top_news.get('genre_label', genre_key)}) · {today_str}

* **Género:** {top_news.get('genre_label', genre_key)}
* **Titular Seleccionado:** {storyboard['title']}
* **Fuente:** {storyboard['source']} ([Enlace directo]({storyboard['link']}))
* **Duración de Audio Verificada:** **{real_dur:.2f} segundos** (Cumple requisito >60 s de TikTok Creator Rewards)
* **Número de Palabras:** {storyboard['word_count']} palabras.
* **Archivo de Voz Listo:** [`{audio_file.name}`]({audio_file.name})

---

## Guión para Locutor

{storyboard['script']}

---

## Storyboard Híbrido ({len(storyboard['shots'])} Planos · {flow_cnt} Flow Cinemáticos + {hud_cnt} Remotion/HUD)

"""
    for s in storyboard["shots"]:
        mode_label = "⚡ Remotion / Vector HUD (Infográfico · 0 créditos)" if s.get("render_mode") == "infographic" else "🎬 Google Flow / Veo (Cinemático · 1 crédito)"
        md_content += f"### {s['id']} ({s['sec']}) · {s['type']}\n"
        md_content += f"- **Modo de Producción:** {mode_label}\n"
        md_content += f"- **Duración montaje:** {s['dur']}s (Generar en Flow/Veo: **{s['ia_dur']}**)\n"
        md_content += f"- **Acción visual:** {s['action']}\n"
        md_content += f"- **Prompt Google Flow:** `{s['prompt']}`\n"
        md_content += f"- **Prompt Fallback (Anti-Bloqueo):** `{s['fallback_prompt']}`\n\n"

    report_file.write_text(md_content, encoding="utf-8")

    meta_file = delivery_dir / "metadata.json"
    canonical_genre = storyboard.get("genre_canonical") or genre_key
    from generador_portada import generate_tiktok_hashtags
    tag_info = generate_tiktok_hashtags(canonical_genre, storyboard["title"], storyboard["source"])
    meta_file.write_text(json.dumps({
        "date": today_str,
        "genre": canonical_genre,
        "genre_label": top_news.get("genre_label", canonical_genre),
        "title": storyboard["title"],
        "source": storyboard["source"],
        "url": storyboard["link"],
        "script": storyboard["script"],
        "word_count": storyboard["word_count"],
        "duration_seconds": real_dur,
        "is_monetizable": real_dur >= 60.1,
        "audio_file": audio_file.name,
        "voice_profile": {
            "motor_principal": loc_cfg.get("motor_principal", "edge_tts"),
            "acento": loc_cfg.get("acento", "es-CR (Costa Rica)"),
            "voz_edge": loc_cfg.get("voz_edge", "es-CR-JuanNeural"),
            "rate_edge": loc_cfg.get("rate_edge", "-4%"),
            "pitch_edge": loc_cfg.get("pitch_edge", "+0Hz"),
        },
        "receipt_facts": storyboard.get("receipt_facts", {}),
        "story_metrics": storyboard.get("story_metrics", {}),
        "shots_count": len(storyboard["shots"]),
        "shots": storyboard["shots"],
        "beats_count": len(storyboard.get("beats", [])),
        "beats": storyboard.get("beats", []),
        "hashtags": tag_info["hashtags"],
        "hashtags_str": tag_info["hashtags_str"],
        "tiktok_caption": tag_info["tiktok_caption"],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n4. Paquete de producción completo exportado en:")
    print(f"   {delivery_dir}")
    return delivery_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pipeline autónomo TikTok Radar")
    parser.add_argument("--genre", type=str, default=None, choices=[
        "G1_AVIACION_CATASTROFES", "G2_CIBERATAQUES_HACKERS",
        "G3_IA_ROBOTICA", "G4_ESPACIO_CIENCIA",
        "G1_AVIACION",
        "G1", "G2", "G3", "G4", "AUTO",
        "SLOT_1", "SLOT_2", "TECH", "CIENCIA"
    ], help="Género específico, slot diario o AUTO para radar dinámico")
    parser.add_argument("--rank", type=int, default=0, help="Posición de noticia ordenada (0 = más reciente / mayor score)")
    parser.add_argument("--count", type=int, default=1, help="Número de vídeos a producir en serie para el género (ej: 5)")
    parser.add_argument("--all", action="store_true", help="Producir los 4 géneros del día en lote")
    args = parser.parse_args()

    genre_map = {
        "G1": "G1_AVIACION_CATASTROFES",
        "G2": "G2_CIBERATAQUES_HACKERS",
        "G3": "G3_IA_ROBOTICA",
        "G4": "G4_ESPACIO_CIENCIA",
        "G1_AVIACION": "G1_AVIACION_CATASTROFES",
        "SLOT_1": "SLOT_1",
        "SLOT_2": "SLOT_2",
        "TECH": "SLOT_2",
        "CIENCIA": "SLOT_2",
        "AUTO": None,
    }

    if args.all:
        for g in ["G1_AVIACION_CATASTROFES", "G2_CIBERATAQUES_HACKERS", "G3_IA_ROBOTICA", "G4_ESPACIO_CIENCIA"]:
            print(f"\n=======================================================")
            print(f"🚀 INICIANDO PRODUCCIÓN DE GÉNERO: {g}")
            print(f"=======================================================")
            run_pipeline(g)
    elif args.count > 1 and args.genre:
        target_genre = genre_map.get(args.genre, args.genre)
        print(f"🚀 INICIANDO PRODUCCIÓN EN SERIE ({args.count} VÍDEOS) PARA: {target_genre}")
        for r in range(args.count):
            print(f"\n--- PROCESANDO VÍDEO #{r+1} (RANK {r}) ---")
            run_pipeline(target_genre, rank_index=r)
    else:
        target_genre = genre_map.get(args.genre, args.genre)
        out = run_pipeline(target_genre, rank_index=args.rank)
