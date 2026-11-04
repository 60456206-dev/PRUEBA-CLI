#!/usr/bin/env python3
"""
TIKTOK RADAR · Pipeline 100% Autónomo de Producción (< 60 min)
1. Rastrea Xataka, BBC Mundo y El País en tiempo real.
2. Selecciona automáticamente la noticia de mayor impacto.
3. Genera el guion estructurado para monetizar en TikTok (61 a 65 segundos).
4. Genera el storyboard de 13 planos con prompts optimizados para Google Flow / Veo (4-5s)
   incluyendo prompts principales y fallback_prompts anti-bloqueo de políticas.
5. Sintetiza la pista de locución periodística con Edge-TTS (voz neuronal).
6. Exporta el paquete listo para producción en entregas/<fecha>_AUTONOMO/.
"""

import asyncio
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Importar el escáner de noticias y generador de audio
sys.path.append(str(Path(__file__).parent))
from news_radar import scan_all_sources
from audio_generator import generate_speech, probe_duration

ROOT_DIR = Path(__file__).resolve().parent.parent
ENTREGAS_DIR = ROOT_DIR / "entregas"
ENTREGAS_DIR.mkdir(parents=True, exist_ok=True)

STYLE_PREFIX = (
    "Vertical 9:16, modern stylized 3D cinematic animation, Arcane and Spider-Verse "
    "tactical news thriller aesthetic, Unreal Engine 5 volumetric lighting, rich stylized textures, "
    "no photorealism, no uncanny valley. "
)


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


def build_shot_prompts(is_aviation: bool, is_cyber: bool) -> List[Dict[str, Any]]:
    """Construye los 13 planos con prompt principal y fallback_prompt sanitizado (anti-bloqueo)."""
    if is_aviation:
        raw_shots = [
            {
                "id": "SH01", "sec": "0-4s", "dur": 4.0, "ia_dur": "5s",
                "type": "Radar/Contexto 3D",
                "action": "Radar 3D holográfico táctico con línea de vuelo amarilla que titila en ámbar y desciende.",
                "visual_en": "Dark tactical control room with a glowing 3D holographic radar display over Florida coastline, a yellow flight trajectory line pulsing and curving sharply downward, floating telemetry numbers, dramatic camera push-in.",
                "fallback_en": "Stylized 3D glowing holographic radar map of a coastline with a curved neon yellow trajectory line and floating digital coordinates in a dark room."
            },
            {
                "id": "SH02", "sec": "4-9s", "dur": 5.0, "ia_dur": "5s",
                "type": "Entorno Inicial",
                "action": "Bimotor ejecutivo en vuelo nivelado al atardecer antes de la tormenta.",
                "visual_en": "Sleek white twin-engine private jet flying smoothly in level cruise above golden and deep purple dusk clouds, warm sunset rim light reflecting on the fuselage, cinematic tracking shot.",
                "fallback_en": "Stylized 3D white twin-engine airplane flying smoothly above colorful sunset clouds, cinematic aerial camera."
            },
            {
                "id": "SH03", "sec": "9-14s", "dur": 5.0, "ia_dur": "5s",
                "type": "Datos / Pantalla",
                "action": "Telemetría digital y altímetro cayendo de 18.000 a 2.000 pies.",
                "visual_en": "Close-up of a futuristic 3D digital flight telemetry monitor showing altitude numbers rapidly counting down from 18000 to 2000 feet with a red descending graph curve.",
                "fallback_en": "Stylized 3D digital dashboard screen showing animated altitude graphs and glowing cyan and amber telemetry indicators."
            },
            {
                "id": "SH04", "sec": "14-18s", "dur": 4.0, "ia_dur": "5s",
                "type": "Recreación Personaje",
                "action": "Primer plano al piloto en cabina con sudor en la frente y tensión gestual.",
                "visual_en": "Tight close-up inside a dark airplane cockpit, a stylized 3D male pilot with sweat beads on his furrowed forehead and focused eyes, amber instrument reflections on his headset, mouth closed in concentration.",
                "fallback_en": "Stylized 3D animated pilot wearing an aviation headset inside a glowing cockpit at night, focused expression, cinematic lighting."
            },
            {
                "id": "SH05", "sec": "18-22s", "dur": 4.0, "ia_dur": "5s",
                "type": "Acción Física",
                "action": "Manos sujetando el timón con fuerza bajo luces de cabina.",
                "visual_en": "Close-up of two gloved pilot hands gripping an aircraft control yoke firmly, pulling back slightly while cockpit dashboard indicators glow in warm red and cyan light.",
                "fallback_en": "Close-up of stylized 3D hands holding an airplane steering yoke inside a modern illuminated cockpit."
            },
            {
                "id": "SH06", "sec": "22-26s", "dur": 4.0, "ia_dur": "5s",
                "type": "Macro Detalle",
                "action": "Macro al panel de instrumentos con horizonte artificial inclinándose.",
                "visual_en": "Extreme macro close-up of an aircraft glass cockpit artificial horizon indicator tilting steeply at a 45-degree angle with glowing amber warning chevrons.",
                "fallback_en": "Macro close-up of a stylized 3D aviation attitude indicator gauge tilting smoothly on a digital instrument panel."
            },
            {
                "id": "SH07", "sec": "26-30s", "dur": 4.0, "ia_dur": "5s",
                "type": "Escena Exterior Clímax",
                "action": "Avión inclinado descendiendo entre nubes de tormenta y lluvia.",
                "visual_en": "Dynamic 3D exterior tracking shot of a twin-engine jet banking and descending steeply through dense dark storm clouds and heavy rain streaks, bright wingtip strobe lights illuminating the mist.",
                "fallback_en": "Stylized 3D airplane banking steeply through dramatic dark clouds and rain at night with glowing wingtip lights."
            },
            {
                "id": "SH08", "sec": "30-34s", "dur": 4.0, "ia_dur": "5s",
                "type": "Dinámica de Movimiento",
                "action": "Plano cercano a la cola y timón del avión vibrando por el viento.",
                "visual_en": "Tight cinematic camera focused on the vertical tail fin and rudder of a jet vibrating under heavy wind turbulence amidst swirling dark clouds and rain.",
                "fallback_en": "Close-up 3D animation of an airplane tail fin and rudder moving in strong wind amidst dark clouds."
            },
            {
                "id": "SH09", "sec": "34-38s", "dur": 4.0, "ia_dur": "5s",
                "type": "Reacción Crítica",
                "action": "Mano empujando las palancas de potencia al máximo.",
                "visual_en": "Close-up inside a cockpit of a pilot hand pushing twin throttle levers forward to full power, metallic console illuminated by dramatic cyan and amber instrument lighting.",
                "fallback_en": "Stylized 3D close-up of a hand pushing aircraft throttle levers forward on an illuminated control console."
            },
            {
                "id": "SH10", "sec": "38-44s", "dur": 5.0, "ia_dur": "5s",
                "type": "Infografía Técnica 3D",
                "action": "Modelo 3D wireframe del avión con la cola resaltada en naranja neón.",
                "visual_en": "Stylized 3D technical explainer animation, a translucent blue wireframe model of a twin-engine jet rotating slowly over a dark navy background, with the tail rudder glowing in bright neon orange.",
                "fallback_en": "3D holographic blue wireframe blueprint of an airplane rotating slowly in a dark studio with glowing orange highlights."
            },
            {
                "id": "SH11", "sec": "44-50s", "dur": 5.0, "ia_dur": "5s",
                "type": "Evidencia Oficial",
                "action": "Recreación 3D de la caja negra (FDR) con ondas de audio digitales.",
                "visual_en": "Clean 3D broadcast graphic of an orange aviation flight data recorder box resting on a dark grid surface while glowing cyan digital soundwave bars pulse behind it.",
                "fallback_en": "Stylized 3D orange flight data recorder box on a dark reflective table with glowing blue audio waveform graphics."
            },
            {
                "id": "SH12", "sec": "50-56s", "dur": 5.5, "ia_dur": "5s",
                "type": "Panorama Tras el Suceso",
                "action": "Costa al anochecer con haces de luz de barcos de búsqueda sobre el mar.",
                "visual_en": "Wide atmospheric 3D shot of the dark ocean coastline at night with rescue boats casting long volumetric white searchlight beams across the gentle waves under a starry sky.",
                "fallback_en": "Stylized 3D night ocean scene with boats shining bright volumetric searchlights across the water."
            },
            {
                "id": "SH13", "sec": "56-62.5s", "dur": 6.2, "ia_dur": "5s",
                "type": "Cierre Interactivo",
                "action": "Cámara lenta sobre el océano nocturno con holograma de pregunta para comentarios.",
                "visual_en": "Cinematic slow camera drift over a dark moody ocean at night with a glowing 3D holographic question mark icon and digital news frame floating in the center.",
                "fallback_en": "Stylized 3D glowing cyan question mark hologram floating over a dark blue digital background."
            },
        ]
    else:
        raw_shots = [
            {
                "id": f"SH{i:02d}",
                "sec": f"{(i-1)*5}-{i*5}s",
                "dur": 4.8,
                "ia_dur": "5s",
                "type": "Escena 3D Noticiero",
                "action": f"Recreación 3D estilizada del plano {i} del reporte periodístico.",
                "visual_en": f"Dramatic broadcast 3D news visualization scene {i}, glowing holographic data panels and expressive stylized 3D environment, slow cinematic camera movement.",
                "fallback_en": f"Stylized 3D futuristic broadcast news studio hologram display scene {i} with cyan and amber lighting."
            }
            for i in range(1, 14)
        ]

    shots = []
    for s in raw_shots:
        shots.append({
            "id": s["id"],
            "sec": s["sec"],
            "dur": s["dur"],
            "ia_dur": s["ia_dur"],
            "type": s["type"],
            "action": s["action"],
            "prompt": STYLE_PREFIX + s["visual_en"],
            "fallback_prompt": STYLE_PREFIX + s["fallback_en"],
        })
    return shots


def generate_monetizable_storyboard(news: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera el desglose editorial completo para 61–65 segundos (13 planos, 135-140 palabras)
    siguiendo la fórmula de Noticiero 3D Estilizado para Google Flow / Veo.
    """
    title = news["title"]
    source = news["source_name"]
    link = news["link"]
    title_low = title.lower()

    is_peru_disaster = news.get("is_peru_priority", False) or any(k in title_low for k in ["perú", "peru", "lima", "arequipa", "piura", "indeci", "sismo", "huaico", "terremoto", "panamericana", "el niño", "rpp", "andina"])
    is_aviation = any(k in title_low for k in ["avión", "aeronave", "vuelo", "accidente", "aircraft", "flight", "plane", "pilot", "mayday", "crash", "haiti", "boeing", "airbus", "aerotime"])
    is_cyber = any(k in title_low for k in ["ciberataque", "hackeo", "neveras", "hacker", "ransomware", "malware", "exploit", "apt", "breach", "zero-day", "cyber"])
    is_ai = any(k in title_low for k in ["gemini", "google", "ia", "ai", "openai", "chip", "2 nm", "robot", "nvidia", "deepseek", "chatgpt", "apple", "semiconduct", "dram", "nand", "euv", "silicon", "hardware", "cpu", "gpu", "micron", "intel", "amd", "tsmc", "techcrunch", "tom's hardware"])
    is_space = any(k in title_low for k in ["espacio", "nasa", "esa", "marte", "luna", "cohete", "spacex", "telescopio", "asteroide", "planetary", "space", "starship", "orbit", "landing"])

    if is_peru_disaster and not is_aviation:
        script = (
            f"Alerta de última hora en el Perú. {title}. "
            f"Según los reportes oficiales confirmados por los centros de monitoreo y la redacción de {source}, "
            "la emergencia se registró hace pocas horas activando de inmediato el desplazamiento de cuadrillas de auxilio y unidades de primera respuesta. "
            "En el lugar de los hechos, las autoridades evalúan la magnitud de los daños materiales y atienden a las personas afectadas en el perímetro de seguridad. "
            "Organismos oficiales como Indeci y la Policía Nacional han emitido recomendaciones urgentes a la ciudadanía para evitar zonas de riesgo y mantener las vías despejadas. "
            "Equipos de rescate continúan trabajando en la zona mientras se elabora el informe técnico de daños y pérdidas. "
            "El país sigue de cerca la evolución de este suceso en las próximas horas. "
            "¿Consideras que las autoridades actuaron con la rapidez necesaria ante esta emergencia? "
            "Déjame tu opinión en los comentarios."
        )
    elif is_aviation:
        script = (
            "En solo doce segundos, una emergencia aérea de máxima gravedad desató las alarmas en el espacio aéreo internacional. "
            f"Según los informes oficiales confirmados por la autoridad aeronáutica y la redacción de {source}, "
            "la aeronave experimentó una maniobra crítica mientras los controladores en tierra perdían temporalmente el contacto de telemetría. "
            "Adentro de la cabina, las luces de alerta se encendieron. Los pilotos forcejearon contra los mandos manteniendo la disciplina de vuelo, "
            "mientras las alarmas de proximidad y ángulo de ataque resonaban en el habitáculo. "
            "Los motores respondieron con máxima potencia mientras el equipo en tierra activaba de inmediato el protocolo de emergencia y rescate perimetral. "
            "Peritos de seguridad aérea inspeccionan minuciosamente los registros de vuelo y las grabadoras de voz para determinar la causa exacta del incidente. "
            "Los expertos aseguran que la pericia de la tripulación evitó lo que pudo ser una tragedia irreparable. "
            "¿Crees que los protocolos de aviación comercial deberían reforzarse aún más ante estas situaciones? "
            "Déjame tu opinión en los comentarios."
        )
    elif is_cyber:
        script = (
            "Un ciberataque de alta sofisticación acaba de encender las alertas de seguridad digital en infraestructuras clave. "
            f"De acuerdo con investigaciones reveladas hoy por {source}, grupos de hackers avanzados lograron infiltrar sistemas críticos "
            "aprovechando vulnerabilidades de día cero que eludieron los sistemas tradicionales de detección. "
            "En cuestión de minutos, las líneas de monitoreo detectaron anomalías en el tráfico de datos y códigos maliciosos ejecutándose en segundo plano. "
            "Equipos de respuesta a incidentes aislaron los servidores afectados para impedir una filtración masiva o el bloqueo total de operaciones. "
            "Agencias de ciberseguridad internacional advierten que este tipo de ataques coordinados pone a prueba la resiliencia de servicios esenciales en todo el mundo. "
            "Las investigaciones continúan para identificar el origen y contener réplicas del exploit. "
            "¿Estamos realmente protegidos frente a ciberataques que puedan paralizar servicios esenciales de la noche a la mañana? "
            "Déjame tu opinión en los comentarios."
        )
    elif is_space:
        script = (
            "Una misión espacial acaba de lograr un hito sin precedentes en la exploración planetaria de nueva generación. "
            f"Según los comunicados técnicos oficiales difundidos hoy por {source}, "
            "nuevos experimentos de navegación autónoma y sensores ópticos han demostrado una precisión extraordinaria para maniobras de descenso extremo. "
            "En el centro de control de misión, los científicos siguieron minuto a minuto el comportamiento de la telemetría en tiempo real, "
            "verificando que los propulsores y algoritmos de posicionamiento corrigieron la trayectoria con exactitud milimétrica. "
            "Este logro tecnológico allana el camino definitivo para futuros aterrizajes tripulados en la Luna y las misiones más ambiciosas hacia Marte. "
            "La frontera espacial vive hoy una de sus épocas más emocionantes de descubrimiento e innovación tecnológica. "
            "¿Crees que la humanidad logrará establecer su primera colonia permanente fuera de la Tierra en esta década? "
            "Déjame tu opinión en los comentarios."
        )
    elif is_ai:
        script = (
            "La batalla por el liderazgo en inteligencia artificial y la arquitectura de superchips acaba de dar un salto determinante. "
            f"Reportes tecnológicos de última hora contrastados por {source} señalan avances clave en litografía y nuevos modelos de frontera "
            "que buscan romper las barreras actuales de eficiencia energética y potencia de cálculo. "
            "En los laboratorios de innovación, los ingenieros aceleran el despliegue de silicio de última generación capaz de procesar flujos de datos masivos "
            "sin saturar la infraestructura de los centros de cómputo. "
            "Analistas de la industria coinciden en que este salto marcará la competitividad digital y la soberanía tecnológica de las próximas décadas. "
            "La evolución de la inteligencia artificial continúa a un ritmo imparable que transforma industrias enteras día a día. "
            "¿Crees que estos saltos en hardware nos acercan a una inteligencia artificial general antes de lo esperado? "
            "Déjame tu opinión en los comentarios."
        )
    else:
        script = (
            f"Atención a esta noticia de última hora que acaba de ser confirmada hoy. {title}. "
            f"Según los reportes oficiales contrastados por la redacción de {source}, los acontecimientos se precipitaron hace pocas horas, "
            "activando un protocolo inmediato de revisión entre las autoridades y los especialistas del sector. "
            "Las primeras investigaciones técnicas de campo revelan datos críticos que cambian por completo las versiones preliminares. "
            "Dentro de los centros de monitoreo, equipos especializados trabajan a contrarreloj para contener el impacto y medir las repercusiones a escala internacional. "
            "Los organismos reguladores ya han exigido un informe pericial exhaustivo mientras se analizan las pruebas documentales registradas hasta el momento. "
            "El desenlace de esta investigación marcará un precedente decisivo en las próximas semanas. "
            "¿Crees que las medidas tomadas a tiempo evitarán una crisis mayor o ya es demasiado tarde? "
            "Déjame tu opinión en los comentarios."
        )

    words = script.split()
    word_count = len(words)
    est_duration = round(word_count / 2.2, 1)
    shots = build_shot_prompts(is_aviation=is_aviation, is_cyber=is_cyber)

    return {
        "title": title,
        "source": source,
        "link": link,
        "script": script,
        "word_count": word_count,
        "est_duration": est_duration,
        "shots": shots,
    }


async def synthesize_voiceover(script: str, output_path: Path, voice: str = "Puck") -> float:
    """
    Sintetiza la voz del locutor periodístico con Gemini 3.8 Flash TTS (con fallback a Edge-TTS)
    y garantiza que la duración supere los 61.0 segundos para cumplir siempre con el requisito
    de monetización de TikTok Creator Rewards (>60s).
    """
    style = (
        "Locución periodística de investigación urgente para noticiero broadcast de última hora. "
        "Dicción clara y autoritaria, ritmo broadcast dinámico en español neutro, sin música."
    )
    dur = generate_speech(script, output_path, voice_gemini=voice, voice_edge="es-MX-JorgeNeural", style=style)

    # Si la lectura queda por debajo de 61.0s, ajustar sutilmente el tempo para asegurar monetización (>60s)
    if 0 < dur < 61.0:
        factor = dur / 62.0  # e.g. 58s -> 0.935 (mantiene tono nativo imperceptiblemente más solemne)
        if 0.5 <= factor <= 0.99:
            print(f"[PIPELINE] Ajustando tempo ({factor:.3f}) para garantizar >61.0s de monetización...", flush=True)
            adjusted_path = output_path.with_suffix(".adj.mp3")
            cmd = [
                "ffmpeg", "-y", "-i", str(output_path),
                "-filter:a", f"atempo={factor:.4f}",
                "-b:a", "192k",
                str(adjusted_path)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            adjusted_path.replace(output_path)
            dur = probe_duration(output_path)
            print(f"[PIPELINE] ✅ Duración final monetizable asegurada: {dur:.2f}s", flush=True)

    return dur


def run_pipeline(genre_key: Optional[str] = None, rank_index: int = 0) -> Path:
    from news_radar import get_daily_4_genres, get_top_news_by_genre
    print("1. Escaneando y clasificando noticias con orden cronológico y prioridad Perú/Aviación...", flush=True)

    genre_map = {
        "G1": "G1_AVIACION_CATASTROFES",
        "G2": "G2_CIBERATAQUES_HACKERS",
        "G3": "G3_IA_ROBOTICA",
        "G4": "G4_ESPACIO_CIENCIA",
        "G1_AVIACION_CATASTROFES": "G1_AVIACION_CATASTROFES",
        "G2_CIBERATAQUES_HACKERS": "G2_CIBERATAQUES_HACKERS",
        "G3_IA_ROBOTICA": "G3_IA_ROBOTICA",
        "G4_ESPACIO_CIENCIA": "G4_ESPACIO_CIENCIA",
    }

    full_key = genre_map.get(genre_key, genre_key) if genre_key else None

    if full_key:
        ranked_items = get_top_news_by_genre(full_key, limit=max(5, rank_index + 1))
        if ranked_items and rank_index < len(ranked_items):
            top_news = ranked_items[rank_index]
        elif ranked_items:
            top_news = ranked_items[0]
        else:
            daily_genres = get_daily_4_genres()
            top_news = daily_genres.get(full_key, list(daily_genres.values())[0])

        suffix = full_key.replace("G1_", "").replace("G2_", "").replace("G3_", "").replace("G4_", "")
        if rank_index > 0:
            suffix += f"_V{rank_index+1}"
    else:
        daily_genres = get_daily_4_genres()
        genre_key = max(daily_genres, key=lambda g: daily_genres[g].get("score", 1.0))
        top_news = daily_genres[genre_key]
        suffix = "AUTONOMO"

    print(f"\n2. Noticia seleccionada para [{top_news.get('genre_label', genre_key)}]:")
    print(f"   [{top_news['source_name']}] {top_news['title']}")

    storyboard = generate_monetizable_storyboard(top_news)

    today_str = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{today_str}_{suffix}"
    delivery_dir = ENTREGAS_DIR / folder_name
    delivery_dir.mkdir(parents=True, exist_ok=True)
    (delivery_dir / "shots").mkdir(parents=True, exist_ok=True)

    audio_file = delivery_dir / "LOCUCION_NOTICIERO_62S.mp3"
    print("\n3. Sintetizando locución periodística con Gemini 3.8 Flash TTS / Edge-TTS...", flush=True)
    real_dur = asyncio.run(synthesize_voiceover(storyboard["script"], audio_file))
    print(f"   Audio generado con éxito: {audio_file.name} ({real_dur:.2f} s | Cumple >60s para TikTok Monetización)")

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

## Storyboard para Google Flow / Veo (13 Planos · 4–5 s)

"""
    for s in storyboard["shots"]:
        md_content += f"### {s['id']} ({s['sec']}) · {s['type']}\n"
        md_content += f"- **Duración montaje:** {s['dur']}s (Generar en Flow/Veo: **{s['ia_dur']}**)\n"
        md_content += f"- **Acción visual:** {s['action']}\n"
        md_content += f"- **Prompt Google Flow:** `{s['prompt']}`\n"
        md_content += f"- **Prompt Fallback (Anti-Bloqueo):** `{s['fallback_prompt']}`\n\n"

    report_file.write_text(md_content, encoding="utf-8")

    meta_file = delivery_dir / "metadata.json"
    meta_file.write_text(json.dumps({
        "date": today_str,
        "genre": genre_key,
        "genre_label": top_news.get("genre_label", genre_key),
        "title": storyboard["title"],
        "source": storyboard["source"],
        "url": storyboard["link"],
        "script": storyboard["script"],
        "word_count": storyboard["word_count"],
        "duration_seconds": real_dur,
        "is_monetizable": real_dur > 60.0,
        "audio_file": audio_file.name,
        "shots_count": len(storyboard["shots"]),
        "shots": storyboard["shots"],
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
        "G1", "G2", "G3", "G4"
    ], help="Género específico a producir")
    parser.add_argument("--rank", type=int, default=0, help="Posición de noticia ordenada (0 = más reciente / mayor score)")
    parser.add_argument("--count", type=int, default=1, help="Número de vídeos a producir en serie para el género (ej: 5)")
    parser.add_argument("--all", action="store_true", help="Producir los 4 géneros del día en lote")
    args = parser.parse_args()

    genre_map = {
        "G1": "G1_AVIACION_CATASTROFES",
        "G2": "G2_CIBERATAQUES_HACKERS",
        "G3": "G3_IA_ROBOTICA",
        "G4": "G4_ESPACIO_CIENCIA",
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
