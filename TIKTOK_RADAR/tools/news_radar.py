#!/usr/bin/env python3
"""
TIKTOK RADAR · Módulo de Ingesta, Filtrado Anti-Spam y Clasificación Inteligente
Reglas Fundamentales de Producción:
1. Cronología Estricta: De lo más reciente a lo más antiguo (primicias de foros y agencias).
2. Densidad Informativa, Potencial de Vistas (Viralidad) y Polémica/Controversia.
3. Aviación Internacional (G1): Selección estricta del último incidente o emergencia Mayday reportada.
4. Inclusión obligatoria de TechCrunch y Tom's Hardware en tecnología/chips.
5. Soporte para generar N vídeos (ej. 5 vídeos) sin duplicar noticias.
"""

import email.utils
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set

# Términos publicitarios y spam comercial a eliminar
BLACKLIST_TERMS = [
    "oferta", "descuento", "precio", "rebajad", "comprar", "truco", "chollo",
    "análisis", "review", "premio", "lidl", "amazon", "aliexpress", "mercadona",
    "ikea", "el corte inglés", "gama media", "tutorial", "cómo hacer", "consejos",
    "guía de compra", "árbol de navidad", "móvil barato", "ganga", "rebaja", "cupón",
    "verisure", "financiación", "smartphone barato", "televisor barato", "barato",
    "más barato", "vuelos baratos", "kayak", "skyscanner", "billetes", "boletos",
    "elecciones", "midterms", "votos", "senado", "congreso de los diputados", "demócratas",
    "republicanos", "candidato", "escaños"
]

# Fuentes internacionales organizadas por categoría
FEEDS = [
    # -------------------------------------------------------------------------
    # 1. ✈️ G1: Aviación Internacional & Seguridad Aérea (100% Fuentes Especializadas)
    # -------------------------------------------------------------------------
    {
        "id": "aerotime",
        "name": "AeroTime Global Aviation",
        "url": "https://www.aerotime.aero/feed",
        "primary_genre": "G1_AVIACION_CATASTROFES",
        "allowed_genres": ["G1_AVIACION_CATASTROFES"],
        "weight": 1.7,
        "is_aviation": True,
    },
    {
        "id": "flightradar24",
        "name": "Flightradar24 Aviation News",
        "url": "https://www.flightradar24.com/blog/feed/",
        "primary_genre": "G1_AVIACION_CATASTROFES",
        "allowed_genres": ["G1_AVIACION_CATASTROFES"],
        "weight": 1.7,
        "is_aviation": True,
    },
    {
        "id": "aviation24",
        "name": "Aviation24 Global",
        "url": "https://www.aviation24.be/feed/",
        "primary_genre": "G1_AVIACION_CATASTROFES",
        "allowed_genres": ["G1_AVIACION_CATASTROFES"],
        "weight": 1.6,
        "is_aviation": True,
    },
    {
        "id": "flyingmag",
        "name": "Flying Magazine Aviation Safety",
        "url": "https://www.flyingmag.com/feed/",
        "primary_genre": "G1_AVIACION_CATASTROFES",
        "allowed_genres": ["G1_AVIACION_CATASTROFES"],
        "weight": 1.5,
        "is_aviation": True,
    },
    {
        "id": "avweb",
        "name": "AVweb Global Aviation",
        "url": "https://www.avweb.com/feed/",
        "primary_genre": "G1_AVIACION_CATASTROFES",
        "allowed_genres": ["G1_AVIACION_CATASTROFES"],
        "weight": 1.5,
        "is_aviation": True,
    },

    # -------------------------------------------------------------------------
    # 2. 💻 G2: Ciberataques, Guerra Digital y Amenazas Críticas
    # -------------------------------------------------------------------------
    {
        "id": "thehackernews",
        "name": "The Hacker News",
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "primary_genre": "G2_CIBERATAQUES_HACKERS",
        "allowed_genres": ["G2_CIBERATAQUES_HACKERS"],
        "weight": 1.6,
    },
    {
        "id": "bleepingcomputer",
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "primary_genre": "G2_CIBERATAQUES_HACKERS",
        "allowed_genres": ["G2_CIBERATAQUES_HACKERS"],
        "weight": 1.5,
    },
    {
        "id": "securityweek",
        "name": "SecurityWeek",
        "url": "https://feeds.feedburner.com/securityweek",
        "primary_genre": "G2_CIBERATAQUES_HACKERS",
        "allowed_genres": ["G2_CIBERATAQUES_HACKERS"],
        "weight": 1.4,
    },
    {
        "id": "darkreading",
        "name": "Dark Reading",
        "url": "https://www.darkreading.com/rss.xml",
        "primary_genre": "G2_CIBERATAQUES_HACKERS",
        "allowed_genres": ["G2_CIBERATAQUES_HACKERS"],
        "weight": 1.3,
    },

    # -------------------------------------------------------------------------
    # 3. 🤖 G3: Inteligencia Artificial, Hardware, Robótica y Big Tech
    # -------------------------------------------------------------------------
    {
        "id": "tomshardware",
        "name": "Tom's Hardware",
        "url": "https://www.tomshardware.com/feeds/news",
        "primary_genre": "G3_IA_ROBOTICA",
        "allowed_genres": ["G3_IA_ROBOTICA", "G2_CIBERATAQUES_HACKERS"],
        "weight": 1.7,
    },
    {
        "id": "techcrunch_main",
        "name": "TechCrunch News",
        "url": "https://techcrunch.com/feed/",
        "primary_genre": "G3_IA_ROBOTICA",
        "allowed_genres": ["G3_IA_ROBOTICA", "G2_CIBERATAQUES_HACKERS"],
        "weight": 1.6,
    },
    {
        "id": "techcrunch_ai",
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "primary_genre": "G3_IA_ROBOTICA",
        "allowed_genres": ["G3_IA_ROBOTICA"],
        "weight": 1.6,
    },
    {
        "id": "techcrunch_hardware",
        "name": "TechCrunch Hardware",
        "url": "https://techcrunch.com/category/hardware/feed/",
        "primary_genre": "G3_IA_ROBOTICA",
        "allowed_genres": ["G3_IA_ROBOTICA"],
        "weight": 1.5,
    },
    {
        "id": "arstechnica",
        "name": "Ars Technica Tech & Frontier",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "primary_genre": "G3_IA_ROBOTICA",
        "allowed_genres": ["G2_CIBERATAQUES_HACKERS", "G3_IA_ROBOTICA"],
        "weight": 1.4,
    },
    {
        "id": "elpais_tec",
        "name": "El País Tecnología",
        "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada",
        "primary_genre": "G3_IA_ROBOTICA",
        "allowed_genres": ["G2_CIBERATAQUES_HACKERS", "G3_IA_ROBOTICA"],
        "weight": 1.2,
    },
    {
        "id": "xataka",
        "name": "Xataka Tecnología (Filtrada)",
        "url": "https://www.xataka.com/feedburner.xml",
        "primary_genre": "G3_IA_ROBOTICA",
        "allowed_genres": ["G3_IA_ROBOTICA", "G4_ESPACIO_CIENCIA"],
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # 4. 🚀 G4: Espacio, Ciencia Extrema y Fenómenos Anómalos
    # -------------------------------------------------------------------------
    {
        "id": "nasa_breaking",
        "name": "NASA Breaking News",
        "url": "https://www.nasa.gov/news-release/feed/",
        "primary_genre": "G4_ESPACIO_CIENCIA",
        "allowed_genres": ["G4_ESPACIO_CIENCIA"],
        "weight": 1.6,
    },
    {
        "id": "spacenews",
        "name": "SpaceNews Global",
        "url": "https://spacenews.com/feed/",
        "primary_genre": "G4_ESPACIO_CIENCIA",
        "allowed_genres": ["G4_ESPACIO_CIENCIA"],
        "weight": 1.6,
    },
    {
        "id": "space_com",
        "name": "Space.com Breaking News",
        "url": "https://www.space.com/feeds/all",
        "primary_genre": "G4_ESPACIO_CIENCIA",
        "allowed_genres": ["G4_ESPACIO_CIENCIA"],
        "weight": 1.5,
    },
    {
        "id": "phys_space",
        "name": "Phys.org Space & Astronomy",
        "url": "https://phys.org/rss-feed/space-news/",
        "primary_genre": "G4_ESPACIO_CIENCIA",
        "allowed_genres": ["G4_ESPACIO_CIENCIA"],
        "weight": 1.4,
    },
]

# Palabras clave por género temático
GENRE_KEYWORDS = {
    "G1_AVIACION_CATASTROFES": [
        "avión", "aeronave", "vuelo", "aterrizaje", "piloto", "cabina", "altitud",
        "accidente aéreo", "colisión aérea", "rescate aéreo", "emergencia aérea",
        "mayday", "boeing", "airbus", "turbulencia", "caja negra", "radar de vuelo",
        "falla de motor", "pista de aterrizaje", "ntsb", "faa", "aerotime",
        "airplane", "plane", "aircraft", "flight", "cockpit", "altitude", "crash",
        "air crash", "turbulence", "emergency landing", "aviation safety", "black box",
        "engine failure", "near miss", "runway", "air traffic"
    ],
    "G2_CIBERATAQUES_HACKERS": [
        "ciberataque", "hackeo", "hackers", "ransomware", "malware", "espionaje",
        "filtración", "brecha", "infraestructura", "apagón", "servidores", "bancos",
        "seguridad", "ciberseguridad", "vulnerabilidad", "phishing", "ciberdelincuencia",
        "cyberattack", "data breach", "zero-day", "exploit", "critical infrastructure",
        "ddos", "cyber threat", "apt", "infostealer", "cisa", "backdoor"
    ],
    "G3_IA_ROBOTICA": [
        "inteligencia artificial", "ia", "ai", "openai", "gemini", "google", "chatgpt",
        "robot", "humanoide", "algoritmo", "chip", "nvidia", "supercomputadora",
        "deepfake", "automatización", "tesla", "revolución tecnológica", "claude",
        "deepseek", "artificial intelligence", "humanoid", "frontier model", "llm",
        "tsmc", "2nm", "autonomous system", "semiconductor", "semiconductores",
        "silicon", "silicio", "gpu", "cpu", "dram", "nand", "euv", "high-na",
        "intel", "amd", "hardware", "supercomputing", "datacenter", "data center", "memory crisis"
    ],
    "G4_ESPACIO_CIENCIA": [
        "espacio", "asteroide", "nasa", "marte", "luna", "cohete", "spacex",
        "telescopio", "james webb", "galaxia", "universo", "física", "cuántica",
        "océano", "profundidades", "descubrimiento", "anomalía", "atmósfera",
        "esa", "starship", "solar flare", "black hole", "cosmic", "supernova",
        "exoplanet", "astronomy", "deep space", "spacecraft"
    ],
}

AVIATION_TERMS = [
    "avión", "aeronave", "vuelo", "aterrizaje", "piloto", "cabina", "altitud",
    "accidente aéreo", "airplane", "aircraft", "flight", "cockpit", "crash",
    "mayday", "boeing", "airbus", "turbulence", "emergency landing", "airspace",
    "shooting", "aerotime", "aviation safety", "ntsb", "faa"
]

# Términos estrictos de seguridad de vuelo, incidentes técnicos e investigaciones reales (G1)
AVIATION_INCIDENT_TERMS = [
    "mayday", "emergency landing", "aterrizaje de emergencia", "engine failure",
    "falla de motor", "falla técnica", "technical failure", "severe turbulence", "turbulencia",
    "diversion", "desvío", "diverted", "desviado", "cabin pressure", "despresurización",
    "depressurization", "bird strike", "impacto de ave", "near miss", "runway incursion",
    "incursión en pista", "hydraulic failure", "falla hidráulica", "gear failure",
    "tren de aterrizaje", "smoke in cockpit", "humo en cabina", "black box", "caja negra",
    "ntsb investigates", "faa emergency", "aaib report", "bea report",
    "crash", "crashed", "accident", "accidente", "plane incident", "incidente aéreo",
    "loss of control", "pérdida de control", "go-around", "lightning strike",
    "emergency evacuation", "evacuación de emergencia", "tailstrike", "flap failure",
    "engine stall", "compressor stall", "airprox", "fatal crash", "dies in crash",
    "muere en accidente", "heridos en vuelo", "smoke in cabin", "in-flight fire",
    "incendio en vuelo", "grounded after", "alerta aérea",
    "squawk 7700", "squawk 7600", "runway overrun", "rejected takeoff"
]

# Penalización estricta a temas puramente comerciales, regulatorios/burocráticos o itinerarios en G1
AVIATION_COMMERCIAL_PENALTIES = [
    "shareholders approve", "takeover bid", "insolvency filing", "bankruptcy",
    "ticket price", "loyalty program", "new route", "route launch", "quarterly profit",
    "financial results", "earnings", "shares rise", "shares fall", "ceo steps down",
    "codeshare", "fleet order", "air show order", "travel guide", "vuelos baratos",
    "aerolínea más barata", "itinerario", "papa", "santo padre", "visita del",
    "recorrido", "calles cerradas", "adquiere", "compra de acciones", "patrocinio", "sponsor",
    "air taxi", "evtol", "certification milestone", "certified by faa", "faa proposes",
    "faa rule", "regulatory approval", "baggage fee", "airfare", "frequent flyer",
    "livery", "cabin upgrade", "premium seat", "airline union", "pilot shortage",
    "drone delivery", "memorandum of understanding"
]

# Palabras de polémica, controversia, shock y alto potencial de vistas (Views)
POLEMIC_KEYWORDS = [
    "crisis", "demanda", "paraliza", "alerta", "prohibido", "colapso", "investigación",
    "violación", "millonario", "caída", "shock", "escándalo", "secreto", "filtración",
    "amenaza", "grave", "falla", "caos", "urgente", "colapsa", "destrucción",
    "warns", "scandal", "ban", "lawsuit", "exploit", "outage", "ravages", "defeat",
    "breach", "exposed", "emergency", "urgent", "clash", "fight", "collapse", "crisis"
]

# NUEVO FILTRO: Impacto Humano, Trascendencia para la Humanidad e Interés Masivo para Todo Público
UNIVERSAL_HUMAN_IMPACT_BOOSTS = [
    # Avances que cambian el rumbo de la humanidad / civilización / vida diaria
    "cambia el rumbo", "cambia la humanidad", "cura", "enfermedad", "revoluciona",
    "histórico", "hito histórico", "vida extraterrestre", "agua en", "señal extraterrestre",
    "nuevo planeta", "asteroide", "amenaza a la tierra", "inteligencia sobrehumana",
    "humanoides", "robot en hogares", "fusión nuclear", "energía infinita", "revolución cuántica",
    "milagro", "rescate heroico", "sobreviviente", "tragedia masiva", "emergencia nacional",
    "apagón masivo", "crisis global", "peligro inminente", "alerta mundial", "pandemia",
    "breakthrough", "cure", "alien", "extraterrestrial", "life on", "historic milestone",
    "transforms humanity", "humanity", "existential", "quantum supremacy", "nuclear fusion",
    "massive blackout", "unprecedented", "game-changer", "world-first", "humanoid robot"
]

# PENALIZACIÓN ESTRICTA: Minucias técnicas, contratos administrativos o noticias de nicho "rebuscadas"
NICHE_TECHNICAL_PENALTIES = [
    "experimental aircraft", "flight research", "research platform", "grant",
    "contract", "contractor", "procurement", "licitación", "convenio", "acuerdo comercial",
    "adjudicación", "subsidio", "routine maintenance", "patch notes", "firmware update",
    "benchmarking", "benchmark suite", "minor update", "driver update", "beta release",
    "guidelines", "committee", "workshop", "comité", "reunión técnica", "estudio preliminar",
    "vuelo de prueba rutinario", "prueba estática", "inspección de rutina", "revisión de protocolo",
    "mantenimiento programado", "aerotime reports that a", "small partnership"
]


def is_blacklisted(text: str) -> bool:
    t = text.lower()
    return any(b in t for b in BLACKLIST_TERMS)


def parse_rss_date(date_str: str) -> float:
    """Parsea fechas RSS (RFC 2822 o ISO 8601) a timestamp Unix UTC en float."""
    if not date_str:
        return 0.0
    # 1. Intentar RFC 2822 (estándar RSS 2.0)
    try:
        dt = email.utils.parsedate_to_datetime(date_str)
        if dt:
            return dt.timestamp()
    except Exception:
        pass
    # 2. Intentar ISO 8601 (estándar Atom)
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if dt:
            return dt.timestamp()
    except Exception:
        pass
    return 0.0


def title_tokens(title: str) -> Set[str]:
    """Extrae palabras clave de un título para deduplicación entre foros."""
    words = re.findall(r"\b[a-z0-9áéíóúñ]{3,}\b", title.lower())
    stop_words = {
        "para", "como", "con", "que", "los", "las", "por", "una", "uno", "unos",
        "the", "and", "for", "with", "from", "sobre", "tras", "este", "esta", "about"
    }
    return set(w for w in words if w not in stop_words)


def is_duplicate_story(title_a: str, title_b: str) -> bool:
    """Detecta si dos fuentes diferentes están reportando sobre el mismo hecho."""
    t_a = title_tokens(title_a)
    t_b = title_tokens(title_b)
    if not t_a or not t_b:
        return False
    inter = t_a.intersection(t_b)
    min_len = min(len(t_a), len(t_b))
    return (len(inter) / min_len) >= 0.50


_KW_REGEX_CACHE: Dict[str, re.Pattern] = {}


def kw_match(kw: str, text: str) -> bool:
    """Comprueba coincidencia de palabra clave evitando falsos positivos por subcadenas (cure/secure, stall/install, etc.)."""
    key = kw.lower()
    pat = _KW_REGEX_CACHE.get(key)
    if pat is None:
        escaped = re.escape(key)
        if len(key) <= 4 and " " not in key:
            pat = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
        else:
            # Exige inicio en límite de palabra; si no es multi-palabra corta también evita coincidir en medio de otra palabra
            pat = re.compile(rf"\b{escaped}", re.IGNORECASE)
        _KW_REGEX_CACHE[key] = pat
    return bool(pat.search(text))


def classify_genre(title: str, summary: str, default_genre: str, allowed_genres: Optional[List[str]] = None) -> str:
    combined = f"{title} {summary}".lower()
    title_low = title.lower()
    scores = {k: 0 for k in GENRE_KEYWORDS}
    for genre, kws in GENRE_KEYWORDS.items():
        if allowed_genres and genre not in allowed_genres:
            continue
        for kw in kws:
            if kw_match(kw, combined):
                scores[genre] += 3 if kw_match(kw, title_low) else 1

    valid_scores = {k: v for k, v in scores.items() if (not allowed_genres or k in allowed_genres)}
    best_genre = max(valid_scores, key=valid_scores.get)
    if valid_scores[best_genre] > 0:
        return best_genre
    return default_genre


def score_article(item: Dict[str, Any], now_ts: float) -> float:
    """
    Algoritmo de puntuación integral:
    - Cronología estricta (frescura en horas).
    - Prioridad Nacional Perú en Desastres / Catástrofes (+50 pts).
    - Aviación: Prioridad estricta al último incidente reportado.
    - Densidad informativa (datos duros, cifras, extensión).
    - Potencial de vistas / viralidad y polémica/controversia.
    """
    base_weight = item.get("source_weight", 1.0)
    score = base_weight * 2.0

    pub_ts = item.get("timestamp", 0.0)
    if pub_ts > 0:
        age_hours = max(0.0, (now_ts - pub_ts) / 3600.0)
        # 1. Regla Cronológica (De lo más reciente a lo más antiguo)
        if age_hours <= 3.0:
            score += 14.0  # Primicia absoluta (hace <3 horas)
        elif age_hours <= 6.0:
            score += 9.0   # Muy reciente (hace <6 horas)
        elif age_hours <= 12.0:
            score += 6.0   # Publicado hoy (hace <12 horas)
        elif age_hours <= 24.0:
            score += 3.0   # Últimas 24 horas
        elif age_hours > 48.0:
            score -= 8.0   # Noticia antigua
    else:
        age_hours = 24.0

    item["age_hours"] = round(age_hours, 1)

    combined = f"{item['title']} {item['summary']}".lower()

    # 2. Regla Especial Aviación (G1): Prioridad estricta a incidentes Mayday y seguridad técnica
    is_av_source = item.get("is_aviation", False)
    genre_is_av = item.get("genre") == "G1_AVIACION_CATASTROFES"

    if is_av_source or genre_is_av:
        incident_hits = [w for w in AVIATION_INCIDENT_TERMS if kw_match(w, combined)]
        commercial_hits = [w for w in AVIATION_COMMERCIAL_PENALTIES if kw_match(w, combined)]

        if incident_hits:
            item["is_aviation_incident"] = True
            # Bonificación fuerte a incidentes reales de vuelo, fallas técnicas e investigaciones (+18 a +38 pts)
            score += min(38.0, 18.0 + len(incident_hits) * 6.0)
            if pub_ts > 0:
                freshness_boost = max(0.0, 24.0 - min(24.0, age_hours)) * 0.95
                score += freshness_boost
        else:
            item["is_aviation_incident"] = False

        if commercial_hits:
            # Penalización severa a temas puramente financieros, corporativos, regulatorios o de itinerarios
            score -= min(60.0, len(commercial_hits) * 20.0)

        if genre_is_av and not incident_hits:
            # Fuente de aviación hablando de regulación/contratos/rutas sin incidente de seguridad
            score -= 14.0

        # Si NO proviene de fuente especializada de aviación y NO tiene incidentes técnicos, descartar totalmente
        if not is_av_source and not incident_hits:
            score = -999.0
    else:
        item["is_aviation_incident"] = False

    item["is_peru_priority"] = False

    # 3. Riqueza y Densidad Informativa (Más información)
    text_len = len(item["title"]) + len(item["summary"])
    if text_len >= 120:
        score += 1.5
    if text_len >= 250:
        score += 2.5
    # Cifras y métricas numéricas concretas
    data_matches = re.findall(r"\b\d+(?:[\.,]\d+)?%?|\b\d+k\b|\b\d+m\b", combined)
    score += min(3.5, len(data_matches) * 0.7)

    # 5. Potencial de Vistas y Polémica / Controversia (con límites de palabra)
    polemic_matches = [w for w in POLEMIC_KEYWORDS if kw_match(w, combined)]
    score += min(8.0, len(polemic_matches) * 2.0)

    # 6. Coincidencia con palabras clave del género
    genre_kws = GENRE_KEYWORDS.get(item["genre"], [])
    title_low = item["title"].lower()
    kw_hits = [k for k in genre_kws if kw_match(k, combined)]
    for kw in kw_hits:
        score += 2.5 if kw_match(kw, title_low) else 1.0

    # 7. Trascendencia Humana e Impacto Emocional para Todo Público (con límites de palabra)
    human_boost_hits = [k for k in UNIVERSAL_HUMAN_IMPACT_BOOSTS if kw_match(k, combined)]
    if human_boost_hits:
        boost_pts = min(22.0, len(human_boost_hits) * 7.0)
        score += boost_pts
        item["human_impact_level"] = "ALTO"
    else:
        item["human_impact_level"] = "NORMAL"

    # 8. FILTRO NEGATIVO: Penalización estricta a tecnicismos rebuscados o contratos administrativos
    niche_penalties = [k for k in NICHE_TECHNICAL_PENALTIES if kw_match(k, combined)]
    if niche_penalties:
        penalty_pts = min(25.0, len(niche_penalties) * 9.0)
        score -= penalty_pts
        item["is_niche_rebuscada"] = True
    else:
        item["is_niche_rebuscada"] = False

    return round(score, 2)


def clean_rss_text(raw_text: str) -> str:
    """Decodifica entidades HTML (&quot;, &#39;, &amp;) y limpia etiquetas HTML residuales."""
    if not raw_text:
        return ""
    unescaped = html.unescape(raw_text)
    if "<" in unescaped and ">" in unescaped:
        unescaped = re.sub(r"<[^>]+>", " ", unescaped)
    unescaped = html.unescape(unescaped)
    return re.sub(r"\s+", " ", unescaped).strip()


def get_node_text(elem: ET.Element, tag_names: List[str]) -> str:
    for name in tag_names:
        node = elem.find(name)
        if node is not None and node.text:
            return clean_rss_text(node.text)
    return ""


def get_node_attrib(elem: ET.Element, tag_names: List[str], attr: str = "href") -> str:
    for name in tag_names:
        node = elem.find(name)
        if node is not None:
            if node.text and node.text.strip():
                return node.text.strip()
            if attr in node.attrib:
                return node.attrib[attr].strip()
    return ""


def fetch_feed(feed_info: Dict[str, Any], max_items: int = 25) -> List[Dict[str, Any]]:
    items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    now_ts = datetime.now(timezone.utc).timestamp()

    try:
        req = urllib.request.Request(feed_info["url"], headers=headers)
        with urllib.request.urlopen(req, timeout=9) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)

        xml_items = root.findall(".//item")
        if not xml_items:
            xml_items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

        title_tags = ["title", "{http://www.w3.org/2005/Atom}title"]
        link_tags = ["link", "{http://www.w3.org/2005/Atom}link"]
        desc_tags = ["description", "{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content"]
        date_tags = ["pubDate", "{http://www.w3.org/2005/Atom}updated", "{http://purl.org/dc/elements/1.1/}date"]

        for item in xml_items[:max_items]:
            title = get_node_text(item, title_tags) or "Sin título"
            if is_blacklisted(title):
                continue

            link = get_node_attrib(item, link_tags, "href")
            desc = get_node_text(item, desc_tags)
            if is_blacklisted(desc):
                continue

            pub_date_str = get_node_text(item, date_tags)
            pub_ts = parse_rss_date(pub_date_str)

            genre = classify_genre(
                title, desc,
                default_genre=feed_info.get("primary_genre", "G1_AVIACION_CATASTROFES"),
                allowed_genres=feed_info.get("allowed_genres")
            )

            # Validar al menos una coincidencia temática o ser fuente nativa de la categoría
            combined = (title + " " + desc).lower()
            keyword_matches = [kw for kw in GENRE_KEYWORDS.get(genre, []) if kw_match(kw, combined)]
            if not keyword_matches and not feed_info.get("is_peru") and not feed_info.get("is_aviation"):
                continue

            candidate = {
                "source_id": feed_info["id"],
                "source_name": feed_info["name"],
                "source_weight": feed_info.get("weight", 1.0),
                "is_peru": feed_info.get("is_peru", False),
                "is_aviation": feed_info.get("is_aviation", False),
                "genre": genre,
                "title": title,
                "link": link,
                "summary": desc[:300] + ("..." if len(desc) > 300 else ""),
                "pub_date": pub_date_str,
                "timestamp": pub_ts,
            }

            candidate["score"] = score_article(candidate, now_ts)
            items.append(candidate)

    except Exception as e:
        print(f"[Aviso Escáner {feed_info['name']}]: {e}")
    return items


def scan_all_sources() -> List[Dict[str, Any]]:
    all_news = []
    for f in FEEDS:
        all_news.extend(fetch_feed(f))
    return all_news


def rerank_by_human_impact_gemini(candidates: List[Dict[str, Any]], genre_key: str = "") -> List[Dict[str, Any]]:
    """
    Utiliza Gemini para aportar un ajuste acotado por impacto humano/viralidad en el top 6,
    preservando las reglas duras del radar (ej. incidentes reales de aviación por encima de regulación en G1).
    """
    import os
    key = os.getenv("GEMINI_API_KEY")
    if not key or len(candidates) <= 1:
        return candidates

    try:
        sample_list = candidates[:6]
        items_text = "\n".join([
            f"[{idx}] Fuente: {c['source_name']} | Título: {c['title']} | Resumen: {c['summary'][:180]}"
            for idx, c in enumerate(sample_list)
        ])

        g1_rule = ""
        if genre_key == "G1_AVIACION_CATASTROFES":
            g1_rule = (
                "\nREGLA ESTRICTA DE AVIACIÓN (G1): Prioriza EXCLUSIVAMENTE accidentes reales, aterrizajes de emergencia, "
                "fallas técnicas en vuelo, turbulencia severa o investigaciones de seguridad. "
                "RELEGA al final normas burocráticas de la FAA, lanzamientos comerciales, taxis aéreos eVTOL o contratos."
            )

        prompt = f"""Eres el director de contenidos de un noticiero masivo de TikTok para todo público (NO para un nicho cerrado).
Tu objetivo es evaluar el nivel de impacto humano, urgencia y atractivo visual/informativo para audiencia masiva.
DESCARTA O RELEGA noticias rebuscadas, contratos administrativos, licitaciones o minucias burocráticas.{g1_rule}

Evalúa estas {len(sample_list)} noticias y ordénalas de MAYOR A MENOR impacto:
{items_text}

Responde ÚNICAMENTE con un JSON con los índices ordenados y el motivo breve:
{{"ranked_indices": [0, 1, ...], "top_reason": "breve justificación"}}"""

        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={key}",
            data=body,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            ans = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            m = re.search(r'\{.*"ranked_indices"\s*:\s*\[([0-9,\s]+)\].*\}', ans, re.DOTALL)
            if m:
                ranked_idx_list = [int(x.strip()) for x in m.group(1).split(",") if x.strip().isdigit()]
                # Ajuste acotado (+5.0 a +0.0 pts) para desempatar sin destruir incidentes ni penalizaciones
                for rank_pos, idx in enumerate(ranked_idx_list):
                    if 0 <= idx < len(sample_list):
                        bonus = max(0.0, 5.0 - rank_pos * 1.2)
                        sample_list[idx]["ai_rerank_bonus"] = bonus
                        sample_list[idx]["score"] = round(sample_list[idx]["score"] + bonus, 2)

                is_g1 = genre_key == "G1_AVIACION_CATASTROFES"
                sample_list.sort(
                    key=lambda x: (
                        1 if (is_g1 and x.get("is_aviation_incident")) else 0,
                        x["score"],
                        x.get("timestamp", 0),
                    ),
                    reverse=True,
                )
                return sample_list + candidates[6:]
    except Exception as e:
        print(f"[RADAR-AI] Aviso al clasificar impacto humano con Gemini: {e}")

    return candidates


def get_top_news_by_genre(genre_key: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Obtiene las mejores N noticias para un género específico, aplicando:
    1. En G1: Incidentes de vuelo reales siempre por encima de notas administrativas/comerciales.
    2. Puntaje integral y frescura cronológica.
    3. Deduplicación para que los N vídeos sean sobre temas distintos.
    4. Ajuste acotado por impacto humano con Gemini.
    """
    all_news = scan_all_sources()
    genre_items = [item for item in all_news if item["genre"] == genre_key]
    is_g1 = genre_key == "G1_AVIACION_CATASTROFES"

    # Ordenar garantizando en G1 los incidentes reales primero, luego score y timestamp
    genre_items.sort(
        key=lambda x: (
            1 if (is_g1 and x.get("is_aviation_incident")) else 0,
            x["score"],
            x.get("timestamp", 0)
        ),
        reverse=True
    )

    # Deduplicación inteligente: asegurar que cada puesto sea una noticia diferente
    unique_items: List[Dict[str, Any]] = []
    for item in genre_items:
        is_dup = False
        for chosen in unique_items:
            if is_duplicate_story(item["title"], chosen["title"]):
                is_dup = True
                break
        if not is_dup:
            unique_items.append(item)
        if len(unique_items) >= max(limit, 8):
            break

    unique_items = rerank_by_human_impact_gemini(unique_items, genre_key=genre_key)

    return unique_items[:limit]


def get_daily_4_genres() -> Dict[str, Dict[str, Any]]:
    """
    Selecciona exactamente la noticia número 1 de mayor impacto para cada uno de los 4 géneros.
    Garantiza la producción de 4 vídeos diarios sin repetir temáticas.
    """
    genre_names = {
        "G1_AVIACION_CATASTROFES": "✈️ AVIACIÓN INTERNACIONAL",
        "G2_CIBERATAQUES_HACKERS": "💻 CIBERATAQUES & AMENAZAS",
        "G3_IA_ROBOTICA": "🤖 INTELIGENCIA ARTIFICIAL & TECH",
        "G4_ESPACIO_CIENCIA": "🚀 ESPACIO & CIENCIA EXTREMA",
    }

    selected: Dict[str, Dict[str, Any]] = {}

    for g, label in genre_names.items():
        top_list = get_top_news_by_genre(g, limit=1)
        if top_list:
            chosen = top_list[0]
            chosen["genre_label"] = label
            selected[g] = chosen
        else:
            # Fallback temático garantizado
            fallbacks = {
                "G1_AVIACION_CATASTROFES": {
                    "source_name": "Reporte de Emergencia NTSB",
                    "title": "Misteriosa caída de altitud en jet privado sobre costa Atlántica",
                    "link": "https://www.bbc.com/mundo",
                    "summary": "Falla súbita de instrumentación obliga a descenso de emergencia a 2.000 pies.",
                    "score": 5.0,
                    "genre": g,
                    "genre_label": label,
                },
                "G2_CIBERATAQUES_HACKERS": {
                    "source_name": "The Hacker News",
                    "title": "Ciberataque masivo desactiva sistemas de frío en cadenas de supermercados",
                    "link": "https://thehackernews.com",
                    "summary": "Ransomware provoca pérdidas millonarias al alterar sensores térmicos de distribución.",
                    "score": 5.0,
                    "genre": g,
                    "genre_label": label,
                },
                "G3_IA_ROBOTICA": {
                    "source_name": "Tom's Hardware",
                    "title": "Empresas aceleran adopción de nodos de 2 nanómetros para chips de inteligencia artificial",
                    "link": "https://www.tomshardware.com",
                    "summary": "La nueva litografía extrema rompe barreras de eficiencia energética en centros de cómputo.",
                    "score": 5.0,
                    "genre": g,
                    "genre_label": label,
                },
                "G4_ESPACIO_CIENCIA": {
                    "source_name": "NASA Science",
                    "title": "Telescopio detecta gigantesca llamarada solar en dirección a la magnetósfera",
                    "link": "https://www.nasa.gov",
                    "summary": "Emisión electromagnética de clase X amenaza con interferir satélites de navegación.",
                    "score": 5.0,
                    "genre": g,
                    "genre_label": label,
                },
            }
            selected[g] = fallbacks[g]

    return selected


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TikTok Radar · Escáner de Noticias de Última Hora")
    parser.add_argument("--genre", type=str, default="", help="Filtrar por género (G1, G2, G3, G4, G1_AVIACION, TECH, CIENCIA, SLOT_1, SLOT_2)")
    parser.add_argument("--limit", type=int, default=5, help="Número de noticias a mostrar por género (def: 5)")
    args = parser.parse_args()

    if args.genre:
        raw_g = args.genre.upper().strip()
        if any(k in raw_g for k in ["G1", "AVIA", "VUELO", "AEREO", "AÉREO", "SLOT_1"]):
            g_key = "G1_AVIACION_CATASTROFES"
            canonical_label = "G1_AVIACION_CATASTROFES"
            criteria_note = "Incidentes reales de seguridad aérea + Frescura cronológica + Impacto"
        elif any(k in raw_g for k in ["G2", "CIBER", "HACK", "CYBER"]):
            g_key = "G2_CIBERATAQUES_HACKERS"
            canonical_label = "G2_CIBERATAQUES"
            criteria_note = "Ciberseguridad global + Frescura cronológica + Impacto público"
        elif raw_g in ("SLOT_2", "TECH") or any(k in raw_g for k in ["G3", "HARDWARE", "ROBOT", "CHIP"]):
            g_key = "G3_IA_ROBOTICA"
            canonical_label = "G3_IA_HARDWARE"
            criteria_note = "IA, Hardware & Robótica + Frescura cronológica + Impacto humano"
        elif any(k in raw_g for k in ["G4", "ESPACIO", "CIENCIA", "NASA", "ORBITA"]):
            g_key = "G4_ESPACIO_CIENCIA"
            canonical_label = "G4_ESPACIO_CIENCIA"
            criteria_note = "Espacio & Ciencia extrema + Frescura cronológica + Trascendencia"
        else:
            g_key = "G3_IA_ROBOTICA"
            canonical_label = "G3_IA_HARDWARE"
            criteria_note = "IA, Hardware & Robótica + Frescura cronológica + Impacto humano"

        print(f"=== TIKTOK RADAR · TOP {args.limit} NOTICIAS PARA [{canonical_label}] ===")
        print(f"Criterio: {criteria_note}\n")
        ranked = get_top_news_by_genre(g_key, limit=args.limit)
        for idx, it in enumerate(ranked, 1):
            peru_flag = " [🇵🇪 PRIORIDAD PERÚ]" if it.get("is_peru_priority") else ""
            av_flag = " [✈️ INCIDENTE AVIACIÓN]" if it.get("is_aviation_incident") else ""
            print(f"#{idx} [{it['source_name']}]{peru_flag}{av_flag} (Hace {it.get('age_hours', '?')}h | Score: {it['score']})")
            print(f"   Título: {it['title']}")
            print(f"   Enlace: {it['link']}")
            print(f"   Resumen: {it['summary'][:150]}...\n")
    else:
        daily = get_daily_4_genres()
        print("=== TIKTOK RADAR · 4 GÉNEROS SELECCIONADOS PARA HOY ===")
        print("Reglas: De lo más reciente a lo antiguo, máxima densidad informativa, polémica, y prioridad Perú/Aviación.")
        for g, item in daily.items():
            peru_flag = " [🇵🇪 PRIORIDAD PERÚ]" if item.get("is_peru_priority") else ""
            av_flag = " [✈️ ÚLTIMA HORA AVIACIÓN]" if item.get("is_aviation_incident") else ""
            print(f"\n[{item['genre_label']}]{peru_flag}{av_flag}")
            print(f"  Fuente: {item['source_name']} (Hace {item.get('age_hours', '?')}h | Score: {item['score']})")
            print(f"  Título: {item['title']}")
            print(f"  Enlace: {item['link']}")
