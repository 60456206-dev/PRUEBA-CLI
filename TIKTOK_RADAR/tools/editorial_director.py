#!/usr/bin/env python3
"""
TIKTOK RADAR · Director Editorial 2.5D y Extractor de Contexto Visual por Noticia
1. Resuelve anclas geográficas reales (ciudades, aeropuertos, países) sin inventar rutas.
2. Extrae métricas e identificadores verificables desde titular y guión.
3. Genera prompts dinámicos para Google Flow (fieles al hecho real, estética editorial 2.5D)
   y props estructurados en español para las 4 composiciones Remotion (`Editorial25D*`).
"""

import json
import os
import re
import time
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


# (display_name_es, code, lon, lat, world_atlas_country_name)
_GEO_GAZETTEER: Dict[str, Tuple[str, str, float, float, str]] = {
    "munich": ("MÚNICH", "MUC", 11.582, 48.135, "Germany"),
    "múnich": ("MÚNICH", "MUC", 11.582, 48.135, "Germany"),
    "frankfurt": ("FRÁNCFORT", "FRA", 8.682, 50.110, "Germany"),
    "berlin": ("BERLÍN", "BER", 13.405, 52.520, "Germany"),
    "berlín": ("BERLÍN", "BER", 13.405, 52.520, "Germany"),
    "alemania": ("ALEMANIA", "DE", 10.451, 51.165, "Germany"),
    "germany": ("ALEMANIA", "DE", 10.451, 51.165, "Germany"),
    "bangkok": ("BANGKOK", "BKK", 100.502, 13.756, "Thailand"),
    "tailandia": ("TAILANDIA", "TH", 100.992, 15.870, "Thailand"),
    "thailand": ("TAILANDIA", "TH", 100.992, 15.870, "Thailand"),
    "nueva delhi": ("NUEVA DELHI", "DEL", 77.209, 28.614, "India"),
    "new delhi": ("NUEVA DELHI", "DEL", 77.209, 28.614, "India"),
    "delhi": ("NUEVA DELHI", "DEL", 77.209, 28.614, "India"),
    "mumbai": ("BOMBAY", "BOM", 72.877, 19.076, "India"),
    "india": ("INDIA", "IN", 78.962, 20.593, "India"),
    "heathrow": ("LONDRES", "LHR", -0.454, 51.470, "United Kingdom"),
    "gatwick": ("LONDRES", "LGW", -0.182, 51.153, "United Kingdom"),
    "londres": ("LONDRES", "LHR", -0.127, 51.507, "United Kingdom"),
    "london": ("LONDRES", "LHR", -0.127, 51.507, "United Kingdom"),
    "reino unido": ("REINO UNIDO", "UK", -1.174, 52.355, "United Kingdom"),
    "paris": ("PARÍS", "CDG", 2.352, 48.856, "France"),
    "parís": ("PARÍS", "CDG", 2.352, 48.856, "France"),
    "francia": ("FRANCIA", "FR", 2.213, 46.227, "France"),
    "france": ("FRANCIA", "FR", 2.213, 46.227, "France"),
    "madrid": ("MADRID", "MAD", -3.703, 40.416, "Spain"),
    "barcelona": ("BARCELONA", "BCN", 2.173, 41.385, "Spain"),
    "españa": ("ESPAÑA", "ES", -3.749, 40.463, "Spain"),
    "spain": ("ESPAÑA", "ES", -3.749, 40.463, "Spain"),
    "roma": ("ROMA", "FCO", 12.496, 41.902, "Italy"),
    "rome": ("ROMA", "FCO", 12.496, 41.902, "Italy"),
    "amsterdam": ("ÁMSTERDAM", "AMS", 4.904, 52.367, "Netherlands"),
    "ámsterdam": ("ÁMSTERDAM", "AMS", 4.904, 52.367, "Netherlands"),
    "eindhoven": ("EINDHOVEN", "EIN", 5.469, 51.441, "Netherlands"),
    "países bajos": ("PAÍSES BAJOS", "NL", 5.291, 52.132, "Netherlands"),
    "netherlands": ("PAÍSES BAJOS", "NL", 5.291, 52.132, "Netherlands"),
    "estambul": ("ESTAMBUL", "IST", 28.978, 41.008, "Turkey"),
    "istanbul": ("ESTAMBUL", "IST", 28.978, 41.008, "Turkey"),
    "dubai": ("DUBÁI", "DXB", 55.270, 25.204, "United Arab Emirates"),
    "dubái": ("DUBÁI", "DXB", 55.270, 25.204, "United Arab Emirates"),
    "doha": ("DOHA", "DOH", 51.531, 25.285, "Qatar"),
    "tokio": ("TOKIO", "HND", 139.691, 35.689, "Japan"),
    "tokyo": ("TOKIO", "HND", 139.691, 35.689, "Japan"),
    "japón": ("JAPÓN", "JP", 138.252, 36.204, "Japan"),
    "japan": ("JAPÓN", "JP", 138.252, 36.204, "Japan"),
    "seúl": ("SEÚL", "ICN", 126.978, 37.566, "South Korea"),
    "seoul": ("SEÚL", "ICN", 126.978, 37.566, "South Korea"),
    "corea del sur": ("COREA DEL SUR", "KR", 127.766, 35.907, "South Korea"),
    "south korea": ("COREA DEL SUR", "KR", 127.766, 35.907, "South Korea"),
    "hsinchu": ("HSINCHU", "TWN", 120.967, 24.813, "Taiwan"),
    "taipei": ("TAIPÉI", "TPE", 121.565, 25.033, "Taiwan"),
    "taipéi": ("TAIPÉI", "TPE", 121.565, 25.033, "Taiwan"),
    "taiwán": ("TAIWÁN", "TW", 120.960, 23.697, "Taiwan"),
    "taiwan": ("TAIWÁN", "TW", 120.960, 23.697, "Taiwan"),
    "pekín": ("PEKÍN", "PEK", 116.407, 39.904, "China"),
    "beijing": ("PEKÍN", "PEK", 116.407, 39.904, "China"),
    "shanghái": ("SHANGHÁI", "PVG", 121.473, 31.230, "China"),
    "shanghai": ("SHANGHÁI", "PVG", 121.473, 31.230, "China"),
    "china": ("CHINA", "CN", 104.195, 35.861, "China"),
    "singapur": ("SINGAPUR", "SIN", 103.819, 1.352, "Malaysia"),
    "singapore": ("SINGAPUR", "SIN", 103.819, 1.352, "Malaysia"),
    "hong kong": ("HONG KONG", "HKG", 114.169, 22.319, "China"),
    "sídney": ("SÍDNEY", "SYD", 151.209, -33.868, "Australia"),
    "sydney": ("SÍDNEY", "SYD", 151.209, -33.868, "Australia"),
    "nueva york": ("NUEVA YORK", "JFK", -74.006, 40.712, "United States of America"),
    "new york": ("NUEVA YORK", "JFK", -74.006, 40.712, "United States of America"),
    "washington": ("WASHINGTON", "IAD", -77.036, 38.907, "United States of America"),
    "miami": ("MIAMI", "MIA", -80.191, 25.761, "United States of America"),
    "florida": ("FLORIDA", "FL", -81.515, 27.664, "United States of America"),
    "cabo cañaveral": ("CABO CAÑAVERAL", "KSC", -80.607, 28.392, "United States of America"),
    "cape canaveral": ("CABO CAÑAVERAL", "KSC", -80.607, 28.392, "United States of America"),
    "boca chica": ("STARBASE", "TX", -97.156, 25.997, "United States of America"),
    "houston": ("HOUSTON", "IAH", -95.369, 29.760, "United States of America"),
    "san francisco": ("SAN FRANCISCO", "SFO", -122.419, 37.774, "United States of America"),
    "silicon valley": ("SILICON VALLEY", "SJC", -121.886, 37.338, "United States of America"),
    "california": ("CALIFORNIA", "CA", -119.417, 36.778, "United States of America"),
    "los angeles": ("LOS ÁNGELES", "LAX", -118.243, 34.052, "United States of America"),
    "seattle": ("SEATTLE", "SEA", -122.332, 47.606, "United States of America"),
    "estados unidos": ("EE. UU.", "USA", -98.579, 39.828, "United States of America"),
    "united states": ("EE. UU.", "USA", -98.579, 39.828, "United States of America"),
    "toronto": ("TORONTO", "YYZ", -79.383, 43.653, "Canada"),
    "canadá": ("CANADÁ", "CA", -106.346, 56.130, "Canada"),
    "canada": ("CANADÁ", "CA", -106.346, 56.130, "Canada"),
    "ciudad de méxico": ("CDMX", "MEX", -99.133, 19.432, "Mexico"),
    "mexico city": ("CDMX", "MEX", -99.133, 19.432, "Mexico"),
    "méxico": ("MÉXICO", "MX", -102.552, 23.634, "Mexico"),
    "lima": ("LIMA", "LIM", -77.042, -12.046, "Peru"),
    "perú": ("PERÚ", "PE", -75.015, -9.189, "Peru"),
    "peru": ("PERÚ", "PE", -75.015, -9.189, "Peru"),
    "bogotá": ("BOGOTÁ", "BOG", -74.072, 4.711, "Colombia"),
    "santiago": ("SANTIAGO", "SCL", -70.669, -33.448, "Chile"),
    "buenos aires": ("BUENOS AIRES", "EZE", -58.381, -34.603, "Argentina"),
    "moscú": ("MOSCÚ", "SVO", 37.617, 55.755, "Russia"),
    "moscow": ("MOSCÚ", "SVO", 37.617, 55.755, "Russia"),
    "rusia": ("RUSIA", "RU", 105.318, 61.524, "Russia"),
    "russia": ("RUSIA", "RU", 105.318, 61.524, "Russia"),
    "kiev": ("KIEV", "KBP", 30.523, 50.450, "Ukraine"),
    "kyiv": ("KIEV", "KBP", 30.523, 50.450, "Ukraine"),
    "ucrania": ("UCRANIA", "UA", 31.165, 48.379, "Ukraine"),
    "ukraine": ("UCRANIA", "UA", 31.165, 48.379, "Ukraine"),
    "bruselas": ("BRUSELAS", "BRU", 4.351, 50.850, "Belgium"),
    "brussels": ("BRUSELAS", "BRU", 4.351, 50.850, "Belgium"),
    "israel": ("ISRAEL", "IL", 34.851, 31.046, "Israel"),
    "irán": ("IRÁN", "IR", 53.688, 32.427, "Iran"),
    "iran": ("IRÁN", "IR", 53.688, 32.427, "Iran"),
}


def _clean_short(text: str, limit: int) -> str:
    clean = " ".join((text or "").split()).strip()
    if len(clean) <= limit:
        return clean
    cut = clean[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return cut if len(cut) >= int(limit * 0.5) else clean[:limit].strip()


def resolve_geo_context(text: str, genre_label: str = "") -> Dict[str, Any]:
    """
    Detecta ubicaciones reales en titular/resumen/guión ordenadas por aparición.
    Nunca inventa ciudades ni rutas si no aparecen en la noticia.
    """
    low = (text or "").lower()
    hits: List[Tuple[int, str, Tuple[str, str, float, float, str]]] = []
    seen_display = set()

    for key in sorted(_GEO_GAZETTEER.keys(), key=len, reverse=True):
        m = re.search(rf"\b{re.escape(key)}\b", low)
        if not m:
            continue
        entry = _GEO_GAZETTEER[key]
        if entry[0] in seen_display:
            continue
        seen_display.add(entry[0])
        hits.append((m.start(), key, entry))

    hits.sort(key=lambda x: x[0])
    places = [
        {
            "name": entry[0],
            "code": entry[1],
            "lon": entry[2],
            "lat": entry[3],
            "country": entry[4],
        }
        for _, _, entry in hits
    ]

    if not places:
        return {"has_geo": False}

    # Filtrar país redundante si ya tenemos ciudad de ese país y hay más lugares
    if len(places) >= 3:
        cities = [p for p in places if len(p["code"]) == 3]
        if len(cities) >= 2:
            places = cities + [p for p in places if p not in cities and p["country"] not in {c["country"] for c in cities}]

    highlight = list(dict.fromkeys(p["country"] for p in places[:3]))
    is_diversion_story = any(
        w in low for w in ("desvía", "desvia", "desvío", "desvio", "divert", "diversion", "emergencia a", "alternate")
    )

    if len(places) >= 3 and is_diversion_story:
        return {
            "has_geo": True,
            "mapMode": "diversion",
            "origin": {"name": places[0]["name"], "code": places[0]["code"], "lon": places[0]["lon"], "lat": places[0]["lat"]},
            "plannedDest": {"name": places[1]["name"], "code": places[1]["code"], "lon": places[1]["lon"], "lat": places[1]["lat"]},
            "diversionDest": {"name": places[2]["name"], "code": places[2]["code"], "lon": places[2]["lon"], "lat": places[2]["lat"]},
            "highlightCountries": highlight,
        }
    if len(places) >= 2:
        return {
            "has_geo": True,
            "mapMode": "route",
            "origin": {"name": places[0]["name"], "code": places[0]["code"], "lon": places[0]["lon"], "lat": places[0]["lat"]},
            "plannedDest": {"name": places[1]["name"], "code": places[1]["code"], "lon": places[1]["lon"], "lat": places[1]["lat"]},
            "highlightCountries": highlight,
        }
    return {
        "has_geo": True,
        "mapMode": "epicenter",
        "origin": {"name": places[0]["name"], "code": places[0]["code"], "lon": places[0]["lon"], "lat": places[0]["lat"]},
        "highlightCountries": highlight[:1],
    }


def extract_story_metrics(
    title: str,
    script: str,
    source: str,
    genre_label: str,
    article_text: str = "",
    receipt_facts: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Extrae métricas, identificadores y anclas geográficas reales directamente desde el titular,
    guión y artículo completo (nunca inventa cifras falsas) para contextualizar Remotion.
    """
    combined_metrics = f"{title}. {script}. {article_text}".strip()
    combined_geo = f"{title}. {script}".strip()
    metrics: Dict[str, Any] = {
        "sourceTag": f"FUENTE: {(source or 'PRENSA OFICIAL').upper()[:28]}",
    }

    flight_m = re.search(
        r"\b(?!(?:EN|DE|EL|LA|AL|UN|IN|ON|AT|TO|BY|OF|AS|OR|NO|SI|SE|ES|SU|LO|DEL|LOS|LAS|CON|POR|SIN|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b)"
        r"(?:[A-Z]{2,3}[-\s]?\d{2,4}|(?i:Flight\s+\d{1,4}|Vuelo\s+\d{1,4}|Boeing\s+7\d{2}[A-Z0-9-]*|Airbus\s+A3\d{2}[A-Za-z0-9-]*|A3\d{2}neo|Sikorsky\s+S-?\d{2}))\b",
        combined_metrics,
    )
    if flight_m:
        metrics["flightNumber"] = flight_m.group(0).upper()[:22]

    alt_vals: List[int] = []
    for raw_num in re.findall(r"\b(\d{1,2}[.,]\d{3}|\d{3,5})\s*(?:ft|pies|feet)\b", combined_metrics, re.IGNORECASE):
        try:
            alt_vals.append(int(raw_num.replace(".", "").replace(",", "")))
        except ValueError:
            pass
    if len(alt_vals) >= 2:
        metrics["initialAlt"] = alt_vals[0]
        metrics["finalAlt"] = alt_vals[1]
    elif len(alt_vals) == 1:
        metrics["initialAlt"] = alt_vals[0]

    nm_m = re.search(r"\b(\d+(?:\.\d+)?)\s*nm\b", combined_metrics, re.IGNORECASE)
    if nm_m:
        metrics["nodeSize"] = f"{nm_m.group(1)} NM"

    cve_m = re.search(r"\b(CVE-\d{4}-\d{4,7})\b", combined_metrics, re.IGNORECASE)
    if cve_m:
        metrics["cveSeverity"] = cve_m.group(1).upper()

    quant_matches = re.findall(
        r"\b(\d+(?:[.,]\d+)?\s*(?:%|km/h|mph|nm|GHz|TFLOPS|TOPS|GB|TB|GW|MW|Gbps|Mbps|pisos|millones|billones|personas|pasajeros|satélites|vuelos|días|horas|minutos|segundos|ft|pies)|(?:Flight|Vuelo)\s+\d{1,4})\b",
        combined_metrics,
        re.IGNORECASE,
    )
    if quant_matches:
        first_q = re.sub(r"\s+", " ", quant_matches[0]).strip()
        metrics["multiplierTag"] = f"DATO DETECTADO: {first_q.upper()[:24]}"
        metrics["heroValue"] = first_q.upper()[:20]

    rf = dict(receipt_facts or {})
    extracted_nums = list(rf.get("numbers") or [])
    for q in quant_matches:
        q_clean = re.sub(r"\s+", " ", q).strip()
        if q_clean and q_clean.lower() not in {x.lower() for x in extracted_nums}:
            extracted_nums.append(q_clean)
        if len(extracted_nums) >= 6:
            break

    metrics["extractedNumbers"] = extracted_nums[:6]
    numeric_only = [n for n in extracted_nums if re.search(r"\d", n) and not re.match(r"^(?:TG|BA|AA|DL|UA|LH|AF|IB)\d+", n, re.IGNORECASE)]
    metrics["hasQuantitativePair"] = len(numeric_only) >= 2 or len(alt_vals) >= 2

    if rf.get("receipt_quote"):
        metrics["receiptQuote"] = str(rf["receipt_quote"])
    if rf.get("highlight_phrase"):
        metrics["highlightPhrase"] = str(rf["highlight_phrase"])

    if "AVIACION" in (genre_label or "").upper() and title:
        metrics["warningText"] = f"ALERTA: {title[:34].upper()}"

    geo = resolve_geo_context(combined_geo, genre_label)
    if not geo.get("has_geo") and article_text:
        geo = resolve_geo_context(f"{title}. {article_text[:1000]}", genre_label)
    metrics["has_geo"] = bool(geo.get("has_geo"))
    if geo.get("has_geo"):
        for k in ("mapMode", "origin", "plannedDest", "diversionDest", "highlightCountries"):
            if k in geo:
                metrics[k] = geo[k]

    return metrics


def _detect_story_subject(title: str, genre_label: str) -> Dict[str, str]:
    """Detecta modelo de aeronave, entidad o contexto real para prompts offline fieles a la noticia."""
    low = (title or "").lower()
    aircraft = "commercial widebody jetliner"
    for pat, label in [
        (r"a350", "Airbus A350 widebody commercial airliner"),
        (r"a380", "Airbus A380 double-deck commercial airliner"),
        (r"a32[01](?:neo)?", "Airbus A320 narrowbody commercial jetliner"),
        (r"787", "Boeing 787 Dreamliner widebody commercial airliner"),
        (r"777", "Boeing 777 widebody commercial airliner"),
        (r"747", "Boeing 747 commercial airliner"),
        (r"737", "Boeing 737 commercial airliner"),
        (r"helic[oó]ptero|sikorsky|chopper", "twin-turbine utility helicopter"),
        (r"carguero|cargo", "heavy commercial cargo freighter aircraft"),
    ]:
        if re.search(pat, low):
            aircraft = label
            break

    has_crash_or_sea = any(w in low for w in ("mar", "océano", "ocean", "sea", "rescate", "rescue", "crash", "estrell", "fuego", "fire", "incendio"))
    is_diversion = any(w in low for w in ("desvía", "desvia", "desvío", "divert", "emergencia", "aterrizaje"))

    return {
        "aircraft": aircraft,
        "has_crash_or_sea": "1" if has_crash_or_sea else "",
        "is_diversion": "1" if is_diversion else "",
        "genre": (genre_label or "").upper(),
    }


def build_default_editorial_graphics(
    title: str,
    script: str,
    source: str,
    genre_label: str,
    story_metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Construye props editoriales 2.5D en español para SH01, SH03, SH10, SH11 y SH13
    partiendo únicamente de hechos reales del titular/guión.
    """
    metrics = dict(story_metrics or extract_story_metrics(title, script, source, genre_label))
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script or "") if s.strip()]
    first_sent = _clean_short(sentences[0] if sentences else title, 92)
    mid_sent = _clean_short(sentences[min(len(sentences) - 1, max(0, len(sentences) // 2))] if sentences else title, 92)
    last_sent = _clean_short(sentences[-1] if sentences else title, 140)

    g = (genre_label or "").upper()
    headline_short = _clean_short(title or "REPORTE DE ACTUALIDAD", 54).upper()
    source_upper = (source or "PRENSA OFICIAL").upper()[:28]

    geo_lines = []
    if metrics.get("origin"):
        o_name = metrics["origin"]["name"]
        if metrics.get("diversionDest"):
            geo_lines = [
                f"RUTA ORIGINAL: {o_name} → {metrics['plannedDest']['name']}",
                f"DESVÍO REGISTRADO HACIA {metrics['diversionDest']['name']}",
            ]
        elif metrics.get("plannedDest"):
            geo_lines = [
                f"CONEXIÓN: {o_name} → {metrics['plannedDest']['name']}",
                f"FUENTE: {source_upper}",
            ]
        else:
            geo_lines = [
                f"UBICACIÓN REPORTADA: {o_name}",
                f"FUENTE DIRECTA: {source_upper}",
            ]

    sh01_props: Dict[str, Any] = {
        "kicker": "CORREDOR AÉREO" if "AVIACION" in g else "UBICACIÓN DEL REPORTE",
        "headline": headline_short,
        "stampText": "DESVÍO EN RUTA" if metrics.get("diversionDest") else "REPORTE ACTIVO",
        "cardKicker": metrics.get("flightNumber") or "REGISTRO GEOGRÁFICO",
        "cardHeadline": _clean_short(metrics.get("flightNumber") or headline_short, 32).upper(),
        "cardLines": geo_lines or [_clean_short(first_sent, 44).upper(), f"FUENTE: {source_upper}"],
    }
    for gk in ("has_geo", "mapMode", "origin", "plannedDest", "diversionDest", "highlightCountries"):
        if gk in metrics:
            sh01_props[gk] = metrics[gk]

    hero_val = metrics.get("heroValue") or metrics.get("nodeSize") or metrics.get("cveSeverity") or metrics.get("flightNumber")
    raw_receipt = str(metrics.get("receiptQuote") or first_sent or headline_short).strip()
    raw_highlight = str(metrics.get("highlightPhrase") or "").strip()
    if not raw_highlight or raw_highlight.lower() not in raw_receipt.lower():
        r_words = raw_receipt.split()
        raw_highlight = " ".join(r_words[:min(5, len(r_words))]).strip(".,;:")

    sh03_props: Dict[str, Any] = {
        "has_receipt": True,
        "kicker": "EVIDENCIA DOCUMENTAL",
        "headline": _clean_short(headline_short, 54).upper(),
        "sourceName": source_upper,
        "publicationDate": "REGISTRO CONTRASTADO",
        "articleTitle": _clean_short(title or headline_short, 84),
        "receiptQuote": _clean_short(raw_receipt, 168),
        "highlightPhrase": raw_highlight,
        "keyMetricBadge": str(hero_val).upper()[:20] if hero_val else "",
        "bottomTakeaway": _clean_short(mid_sent or headline_short, 58).upper(),
    }

    if "CIBER" in g:
        diag_kind, c1t, c1d, s_lbl, s_cal, b_st = ("network", "VECTOR DE FALLO", "NODO VULNERABLE", "DEFENSA", "AISLAMIENTO DE RED", "CLAVE DIGITAL")
    elif "HARDWARE" in g or "IA" in g:
        diag_kind, c1t, c1d, s_lbl, s_cal, b_st = ("chip", "NÚCLEO DE SILICIO", "LÍMITE FÍSICO", "ARQUITECTURA", "OPTIMIZACIÓN DE FLUJO", "CLAVE TÉCNICA")
    elif "ESPACIO" in g:
        diag_kind, c1t, c1d, s_lbl, s_cal, b_st = ("spacecraft", "FASE CRÍTICA", "VENTANA ORBITAL", "CONTROL", "AJUSTE DE TRAYECTORIA", "CLAVE DE MISIÓN")
    elif "CATASTROF" in g:
        diag_kind, c1t, c1d, s_lbl, s_cal, b_st = ("seismic", "ZONA DE IMPACTO", "FENÓMENO ACTIVO", "RESPUESTA", "MEDIDA PREVENTIVA", "CLAVE DE PREVENCIÓN")
    else:
        diag_kind, c1t, c1d, s_lbl, s_cal, b_st = ("aircraft", "SISTEMA DE CABINA", "ALERTA PREVENTIVA", "RESPUESTA EN VUELO", "PROTOCOLO DE SEGURIDAD", "CLAVE OPERATIVA")

    sh10_props: Dict[str, Any] = {
        "kicker": "DECONSTRUCCIÓN TÉCNICA",
        "headline": "¿CÓMO SE PRODUCE ESTE MECANISMO?",
        "diagramKind": diag_kind,
        "calloutTitle": c1t,
        "calloutDetail": c1d,
        "secondaryLabel": s_lbl,
        "secondaryCallout": s_cal,
        "bottomStamp": b_st,
        "bottomTakeaway": _clean_short(mid_sent or "ACTUAR ANTES DE PERDER EL MARGEN", 54).upper(),
    }

    extracted_nums = metrics.get("extractedNumbers") or []
    has_quant = bool(metrics.get("hasQuantitativePair")) and len(extracted_nums) >= 2
    if has_quant:
        left_val = str(extracted_nums[0]).upper()[:24]
        right_val = str(extracted_nums[1]).upper()[:24]
        sh11_props: Dict[str, Any] = {
            "kicker": "CONTRASTE FÁCTICO",
            "headline": "DATOS VERIFICADOS DEL REPORTE",
            "mode": "comparison",
            "leftLabel": "PARÁMETRO BASE",
            "leftValue": left_val,
            "leftRatio": 44,
            "rightLabel": "MAGNITUD REPORTADA",
            "rightValue": right_val,
            "rightRatio": 88,
            "sourceStamp": f"VERIFICADO · {source_upper}",
            "bottomTakeaway": _clean_short(mid_sent or headline_short, 56).upper(),
        }
    else:
        sh11_props = {
            "kicker": "CONTRASTE FÁCTICO",
            "headline": "ESCENARIO PREVISTO VS. DECISIÓN REAL",
            "mode": "comparison",
            "leftLabel": "CONDICIÓN PREVISTA",
            "leftValue": _clean_short(metrics.get("plannedDest", {}).get("name") or "OPERACIÓN ESTÁNDAR", 24).upper(),
            "rightLabel": "HECHO REPORTADO",
            "rightValue": _clean_short(metrics.get("diversionDest", {}).get("name") or hero_val or "MANIOBRA CORRECTIVA", 24).upper(),
            "sourceStamp": f"VERIFICADO · {source_upper}",
            "bottomTakeaway": _clean_short(mid_sent or headline_short, 56).upper(),
        }

    sh13_props: Dict[str, Any] = {
        "kicker": "PRIMEROS PRINCIPIOS",
        "headline": "LO QUE DEJA ESTE CASO",
        "quote": last_sent if len(last_sent) >= 28 else "Cuando la complejidad sube, el verdadero margen de seguridad está en anticiparse al fallo.",
        "takeaway": "CRITERIO Y PREVENCIÓN ANTE LO IMPREVISTO",
        "sourceTag": source_upper,
    }

    return {
        "SH01": sh01_props,
        "SH03": sh03_props,
        "SH10": sh10_props,
        "SH11": sh11_props,
        "SH13": sh13_props,
    }


def build_story_aware_shots(
    style_prefix: str,
    is_aviation: bool = False,
    is_cyber: bool = False,
    is_ai: bool = False,
    is_space: bool = False,
    title: str = "",
    summary: str = "",
    script: str = "",
    genre_label: str = "",
    active_mode: str = "flow_primario",
    dynamic_visuals: Optional[Dict[str, Any]] = None,
    story_metrics: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Construye los 13 planos del storyboard anclados a la noticia real.
    Prioriza los prompts y gráficos generados por Gemini (`dynamic_visuals`) y usa
    respaldo determinista fiel a la historia (sin escenas recicladas de Florida/barcos).
    """
    is_full_flow = (active_mode == "flow_puro")
    ctx_text = f"{title}. {summary}"
    subj = _detect_story_subject(ctx_text, genre_label)
    title_clean = _clean_short(title or "actualidad técnica", 70)

    if is_aviation:
        aircraft = subj["aircraft"]
        calm_finale = (
            "Wide editorial chiaroscuro shot of coastal emergency rescue spotlights illuminating dark waves at dusk"
            if subj["has_crash_or_sea"]
            else f"Wide editorial chiaroscuro shot of {aircraft} taxiing calmly along an illuminated international airport runway at dusk after a safe landing"
        )
        climb_or_turn = (
            f"Dynamic editorial chiaroscuro tracking shot of {aircraft} banking smoothly through high-altitude clouds on a preventive diversion course, warm sunset rim light"
            if subj["is_diversion"] or not subj["has_crash_or_sea"]
            else f"Dynamic editorial chiaroscuro tracking shot of {aircraft} descending through dark storm clouds with bright wingtip beacons"
        )
        base_raw = [
            {"id": "SH01", "sec": "0-4s", "dur": 4.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Mapa Editorial 2.5D",
             "action": f"Mapa editorial 2.5D contextualizando el evento: {title_clean}.",
             "visual_en": f"Editorial 2.5D cartographic illustration highlighting the region and route of {title_clean}.",
             "fallback_en": "Editorial 2.5D dark archival world map with warm amber trajectory line."},
            {"id": "SH02", "sec": "4-9s", "dur": 5.0, "ia_dur": "5s", "render_mode": "flow", "type": "Entorno Inicial",
             "action": f"Vuelo de crucero inicial del {aircraft} relacionado con {title_clean}.",
             "visual_en": f"Tactile editorial documentary illustration of a {aircraft} cruising smoothly high above layered dusk clouds, warm amber directional light on fuselage, slow camera push-in.",
             "fallback_en": f"Editorial documentary view of a {aircraft} cruising smoothly above clouds at twilight."},
            {"id": "SH03", "sec": "9-14s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Recibo Documental 2.5D",
             "action": "Recorte editorial de la fuente oficial con resaltado de la prueba verificada.",
             "visual_en": f"Editorial 2.5D archival press receipt clipping highlighting verified evidence of {title_clean}.",
             "fallback_en": "Clean editorial archival document sheet with highlighted evidence quote."},
            {"id": "SH04", "sec": "14-18s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Tripulación en Cabina",
             "action": "Primer plano al comandante en cabina evaluando la situación con calma y foco.",
             "visual_en": f"Close-up editorial chiaroscuro illustration inside the flight deck of {aircraft}, commercial airline captain wearing aviation headset, warm amber panel glow on focused face, calm concentration.",
             "fallback_en": "Close-up editorial illustration of a commercial airline pilot focused inside an illuminated cockpit."},
            {"id": "SH05", "sec": "18-22s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Acción en Cabina",
             "action": "Manos ejecutando listas de verificación y ajustes en consola de vuelo.",
             "visual_en": "Close-up editorial illustration of pilot hands adjusting flight management switches and thrust levers on a dark matte aircraft pedestal under warm amber studio rim light.",
             "fallback_en": "Close-up editorial illustration of pilot hands adjusting cockpit flight controls."},
            {"id": "SH06", "sec": "22-26s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Macro Instrumentación",
             "action": "Macro a pantallas de cabina mostrando ruta y alerta preventiva.",
             "visual_en": "Extreme macro chiaroscuro shot of modern glass cockpit navigation displays showing subtle amber route deviation arcs and crisp instrument needles, shallow depth of field.",
             "fallback_en": "Macro shot of illuminated aircraft cockpit navigation instruments in dark chiaroscuro."},
            {"id": "SH07", "sec": "26-30s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Maniobra en Ruta",
             "action": "Aeronave cambiando de rumbo entre capas atmosféricas al atardecer.",
             "visual_en": climb_or_turn,
             "fallback_en": f"Editorial documentary tracking shot of a {aircraft} turning smoothly over twilight clouds."},
            {"id": "SH08", "sec": "30-34s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Detalle Estructural",
             "action": "Plano cercano al ala y motor en aproximación controlada.",
             "visual_en": f"Tight tracking illustration along the swept wing and turbofan engine of a {aircraft} slicing through golden dusk haze, subtle airframe texture, shallow depth of field.",
             "fallback_en": "Close-up editorial shot along a commercial airliner wing and engine above evening clouds."},
            {"id": "SH09", "sec": "34-38s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Control de Aproximación",
             "action": "Alineación final hacia aeropuerto alterno bajo luces de pista.",
             "visual_en": "Editorial chiaroscuro cockpit perspective over the pilot shoulder looking down at illuminated airport runway approach lights glowing warmly through evening mist.",
             "fallback_en": "Editorial view from cockpit looking toward illuminated runway lights at dusk."},
            {"id": "SH10", "sec": "38-44s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Diagrama Progresivo 2.5D",
             "action": "Croquis técnico 2.5D explicando el principio de seguridad detrás de la decisión.",
             "visual_en": "Editorial 2.5D progressive architectural sketch of an aircraft showing safety protocol.",
             "fallback_en": "Minimal dark archival technical sketch of an aircraft on paper cutout."},
            {"id": "SH11", "sec": "44-50s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Evidencia Documental 2.5D",
             "action": "Comparativa editorial entre el plan original y la resolución segura.",
             "visual_en": "Editorial 2.5D torn-paper evidence comparison sheet showing verified flight outcome.",
             "fallback_en": "Clean editorial torn-paper archival comparison note."},
            {"id": "SH12", "sec": "50-56s", "dur": 5.5, "ia_dur": "5s", "render_mode": "flow", "type": "Resolución en Tierra",
             "action": "Aterrizaje seguro y supervisión técnica en aeropuerto de destino.",
             "visual_en": calm_finale,
             "fallback_en": f"Wide editorial shot of a {aircraft} parked safely on an illuminated airport tarmac at dusk."},
            {"id": "SH13", "sec": "56-62.5s", "dur": 6.2, "ia_dur": "5s", "render_mode": "infographic", "type": "Cierre Documental 2.5D",
             "action": "Nota final de primeros principios sobre seguridad y criterio operativo.",
             "visual_en": "Editorial 2.5D documentary paper note summarizing the core safety lesson.",
             "fallback_en": "Minimal dark study desk lighting over archival paper note."},
        ]
    elif is_cyber:
        base_raw = [
            {"id": "SH01", "sec": "0-4s", "dur": 4.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Mapa Editorial 2.5D",
             "action": f"Mapa contextual de infraestructura digital afectada: {title_clean}.",
             "visual_en": "Editorial 2.5D dark cartographic map showing affected network regions.", "fallback_en": "Editorial 2.5D network map."},
            {"id": "SH02", "sec": "4-9s", "dur": 5.0, "ia_dur": "5s", "render_mode": "flow", "type": "Centro de Operaciones",
             "action": "Sala de servidores en penumbra con iluminación direccional ámbar y roja.",
             "visual_en": f"Tactile editorial illustration of a quiet high-density data center corridor related to {title_clean}, brushed dark steel racks, warm amber and subtle crimson LED reflections.",
             "fallback_en": "Editorial dark server room corridor with subtle warm and crimson indicator lights."},
            {"id": "SH03", "sec": "9-14s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Recibo Documental 2.5D",
             "action": "Recorte editorial de la fuente oficial con el vector o métrica verificada.",
             "visual_en": "Editorial 2.5D archival press receipt highlighting verified cyber evidence.", "fallback_en": "Clean editorial archival press receipt."},
            {"id": "SH04", "sec": "14-18s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Especialista Digital",
             "action": "Analista revisando registros de acceso bajo luz de escritorio.",
             "visual_en": "Close-up editorial illustration of a cybersecurity analyst in a dim studio, dark-framed glasses reflecting warm terminal traces, focused concentration.",
             "fallback_en": "Close-up editorial illustration of a security analyst reading monitor logs."},
            {"id": "SH05", "sec": "18-22s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Inspección de Código",
             "action": "Manos auditando paquetes y comandos de mitigación en consola.",
             "visual_en": "Close-up chiaroscuro shot of specialist hands inspecting network logs on a matte dark workstation keyboard under directional desk lamp.",
             "fallback_en": "Close-up of hands typing security commands on illuminated keyboard."},
            {"id": "SH06", "sec": "22-26s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Macro Conectores",
             "action": "Macro a enlaces de fibra óptica y puertos troncales.",
             "visual_en": "Extreme macro editorial shot of dark fiber-optic patch cables and brushed metal server ports catching a single warm spotlight.",
             "fallback_en": "Macro shot of fiber-optic server connectors under moody lighting."},
            {"id": "SH07", "sec": "26-30s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Alerta en Infraestructura",
             "action": "Pasillo de racks registrando anomalía de tráfico.",
             "visual_en": "Slow atmospheric tracking shot down a matte black server aisle as warm amber diagnostic lights pulse along rack blades.",
             "fallback_en": "Tracking shot down a dim server corridor with amber warning lights."},
            {"id": "SH08", "sec": "30-34s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Flujo Térmico y Cómputo",
             "action": "Detalle de turbinas de refrigeración y carga de procesamiento.",
             "visual_en": "Close-up chiaroscuro shot of matte aluminum server cooling fans spinning smoothly inside a dark data center bay.",
             "fallback_en": "Close-up of industrial server cooling fans under moody chiaroscuro lighting."},
            {"id": "SH09", "sec": "34-38s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Aislamiento Preventivo",
             "action": "Conmutación física de enlace para aislar el segmento comprometido.",
             "visual_en": "Close-up editorial shot of an engineer hand toggling a physical hardware isolation switch on a dark network rack.",
             "fallback_en": "Close-up of a hand switching a dark hardware control toggle."},
            {"id": "SH10", "sec": "38-44s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Diagrama Progresivo 2.5D",
             "action": "Esquema de topología de red mostrando el eslabón aislado.",
             "visual_en": "Editorial 2.5D network topology sketch on dark archival paper.", "fallback_en": "Editorial 2.5D network diagram."},
            {"id": "SH11", "sec": "44-50s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Evidencia Documental 2.5D",
             "action": "Contraste entre exposición inicial y protocolo de contención.",
             "visual_en": "Editorial 2.5D torn-paper contrast sheet.", "fallback_en": "Editorial archival contrast card."},
            {"id": "SH12", "sec": "50-56s", "dur": 5.5, "ia_dur": "5s", "render_mode": "flow", "type": "Estabilización",
             "action": "Centro de monitoreo retomando operación estable.",
             "visual_en": "Wide editorial chiaroscuro shot of a quiet network operations center returning to calm steady lighting after containment.",
             "fallback_en": "Wide editorial view of calm network operations room at night."},
            {"id": "SH13", "sec": "56-62.5s", "dur": 6.2, "ia_dur": "5s", "render_mode": "infographic", "type": "Cierre Documental 2.5D",
             "action": "Reflexión final sobre resiliencia digital.",
             "visual_en": "Editorial 2.5D closing paper note.", "fallback_en": "Minimal dark editorial desk with paper note."},
        ]
    elif is_ai:
        base_raw = [
            {"id": "SH01", "sec": "0-4s", "dur": 4.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Mapa Editorial 2.5D",
             "action": f"Contexto global de semiconductores e IA para: {title_clean}.",
             "visual_en": "Editorial 2.5D map of global silicon supply hubs.", "fallback_en": "Editorial 2.5D map."},
            {"id": "SH02", "sec": "4-9s", "dur": 5.0, "ia_dur": "5s", "render_mode": "flow", "type": "Laboratorio de Silicio",
             "action": "Sala limpia con luz dorada direccional y maquinaria de precisión.",
             "visual_en": f"Tactile editorial illustration of a semiconductor cleanroom and precision optical lithography chamber relevant to {title_clean}, warm golden rim light in deep shadow.",
             "fallback_en": "Editorial documentary illustration of a cleanroom laboratory with warm golden lighting."},
            {"id": "SH03", "sec": "9-14s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Recibo Documental 2.5D",
             "action": "Recorte editorial de la fuente oficial con el dato o cifra real del avance.",
             "visual_en": "Editorial 2.5D press receipt showing verified hardware evidence.", "fallback_en": "Clean editorial archival press receipt."},
            {"id": "SH04", "sec": "14-18s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Investigador",
             "action": "Ingeniero inspeccionando oblea de silicio con gafas protectoras claras.",
             "visual_en": "Close-up editorial illustration of a semiconductor researcher wearing crisp white lab coat and clear safety goggles, no face mask, focused eyes lit by warm instrument glow.",
             "fallback_en": "Close-up editorial illustration of hardware engineer with clear glasses inspecting silicon."},
            {"id": "SH05", "sec": "18-22s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Manejo de Precisión",
             "action": "Brazo mecánico transfiriendo oblea de silicio en cámara limpia.",
             "visual_en": "Close-up chiaroscuro shot of a precision robotic wafer handler delicately holding a reflective silicon disc under warm studio directional light.",
             "fallback_en": "Close-up editorial shot of precision robotic arm holding a silicon wafer."},
            {"id": "SH06", "sec": "22-26s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Macro Microarquitectura",
             "action": "Macro a circuitos grabados sobre silicio con reflejos cálidos.",
             "visual_en": "Extreme macro editorial illustration of intricate nanometer silicon circuit pathways catching warm amber and slate directional reflections.",
             "fallback_en": "Extreme macro shot of detailed microchip circuitry under directional studio light."},
            {"id": "SH07", "sec": "26-30s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Grabado Óptico",
             "action": "Óptica de precisión enfocando haz sobre sustrato.",
             "visual_en": "Atmospheric editorial close-up of high-precision optical mirrors inside an EUV lithography chamber projecting a subtle warm focal beam onto silicon.",
             "fallback_en": "Close-up editorial shot of precision optical mirrors in dark laboratory."},
            {"id": "SH08", "sec": "30-34s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Ensamblaje de Procesadores",
             "action": "Línea automatizada de empaquetado de chips.",
             "visual_en": "Slow tracking chiaroscuro shot along dark precision trays carrying finished microprocessor dies in an automated clean facility.",
             "fallback_en": "Tracking shot of precision microchips arranged on dark factory trays."},
            {"id": "SH09", "sec": "34-38s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Prueba en Banco",
             "action": "Mano conectando módulo de cómputo en banco de pruebas.",
             "visual_en": "Close-up editorial shot of an engineer hand seating a matte black processor module onto a test motherboard under warm desk lamp light.",
             "fallback_en": "Close-up of engineer hands placing a processor module on a test board."},
            {"id": "SH10", "sec": "38-44s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Diagrama Progresivo 2.5D",
             "action": "Croquis técnico de la arquitectura de silicio.",
             "visual_en": "Editorial 2.5D chip architecture sketch.", "fallback_en": "Editorial 2.5D technical chip diagram."},
            {"id": "SH11", "sec": "44-50s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Evidencia Documental 2.5D",
             "action": "Contraste editorial frente a la generación anterior.",
             "visual_en": "Editorial 2.5D comparison note.", "fallback_en": "Editorial archival contrast note."},
            {"id": "SH12", "sec": "50-56s", "dur": 5.5, "ia_dur": "5s", "render_mode": "flow", "type": "Escala Industrial",
             "action": "Vista abierta de centro de cómputo moderno en penumbra.",
             "visual_en": "Wide editorial chiaroscuro illustration of a sleek modern AI compute hall with warm directional architectural lighting and deep slate shadows.",
             "fallback_en": "Wide editorial view of modern high-tech compute hall in dim chiaroscuro."},
            {"id": "SH13", "sec": "56-62.5s", "dur": 6.2, "ia_dur": "5s", "render_mode": "infographic", "type": "Cierre Documental 2.5D",
             "action": "Reflexión final sobre el avance tecnológico.",
             "visual_en": "Editorial 2.5D closing paper note.", "fallback_en": "Minimal dark editorial paper note."},
        ]
    elif is_space:
        base_raw = [
            {"id": "SH01", "sec": "0-4s", "dur": 4.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Mapa Editorial 2.5D",
             "action": f"Ubicación y contexto de misión espacial: {title_clean}.",
             "visual_en": "Editorial 2.5D space launch site cartographic view.", "fallback_en": "Editorial 2.5D map."},
            {"id": "SH02", "sec": "4-9s", "dur": 5.0, "ia_dur": "5s", "render_mode": "flow", "type": "Vehículo en Órbita",
             "action": "Nave o módulo espacial sobre el horizonte terrestre.",
             "visual_en": f"Tactile editorial illustration of a metallic spacecraft orbiting softly above Earth's curved twilight horizon related to {title_clean}, warm golden rim light on solar foil.",
             "fallback_en": "Editorial documentary illustration of a spacecraft above Earth's horizon."},
            {"id": "SH03", "sec": "9-14s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Recibo Documental 2.5D",
             "action": "Recorte editorial de la fuente oficial con el hito verificado de la misión.",
             "visual_en": "Editorial 2.5D press receipt showing verified space telemetry.", "fallback_en": "Clean editorial archival press receipt."},
            {"id": "SH04", "sec": "14-18s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Control de Misión",
             "action": "Primer plano a director de vuelo observando trayectoria.",
             "visual_en": "Close-up editorial illustration of a space mission flight director wearing lightweight comms headset in a dim room, warm screen light on focused eyes.",
             "fallback_en": "Close-up editorial illustration of mission controller in dim control room."},
            {"id": "SH05", "sec": "18-22s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Secuencia de Mando",
             "action": "Manos operando consola de seguimiento orbital.",
             "visual_en": "Close-up chiaroscuro shot of operator hands adjusting precision switches on a matte aerospace telemetry console under warm desk illumination.",
             "fallback_en": "Close-up of hands operating aerospace telemetry console."},
            {"id": "SH06", "sec": "22-26s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Macro Instrumento",
             "action": "Macro a sensor óptico o tobera de maniobra en vacío.",
             "visual_en": "Extreme macro editorial shot of brushed titanium spacecraft attitude thrusters and golden thermal foil catching warm solar light in deep space.",
             "fallback_en": "Macro shot of metallic spacecraft thruster against deep dark space."},
            {"id": "SH07", "sec": "26-30s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Maniobra Orbital",
             "action": "Impulso controlado iluminando el casco metálico.",
             "visual_en": "Dynamic editorial chiaroscuro shot of spacecraft thrusters firing a soft luminous exhaust plume in cosmic darkness, slow camera drift.",
             "fallback_en": "Editorial shot of rocket stage firing gently in dark orbital space."},
            {"id": "SH08", "sec": "30-34s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Despliegue Estructural",
             "action": "Paneles solares o instrumentos desplegándose con precisión.",
             "visual_en": "Close-up editorial illustration of golden multi-junction solar panels unfolding calmly against a subtle starry velvet backdrop.",
             "fallback_en": "Close-up of satellite golden solar panels unfolding in space."},
            {"id": "SH09", "sec": "34-38s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Confirmación en Tierra",
             "action": "Antenas de espacio profundo captando la señal.",
             "visual_en": "Editorial twilight illustration of a large deep-space radio dish antenna pointing skyward under dusk clouds with warm ground spotlights.",
             "fallback_en": "Editorial shot of large radio telescope dish at twilight."},
            {"id": "SH10", "sec": "38-44s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Diagrama Progresivo 2.5D",
             "action": "Croquis técnico 2.5D del vehículo o instrumento.",
             "visual_en": "Editorial 2.5D spacecraft blueprint sketch.", "fallback_en": "Editorial 2.5D spacecraft technical diagram."},
            {"id": "SH11", "sec": "44-50s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Evidencia Documental 2.5D",
             "action": "Contraste factual de la misión reportada.",
             "visual_en": "Editorial 2.5D comparison sheet.", "fallback_en": "Editorial archival comparison sheet."},
            {"id": "SH12", "sec": "50-56s", "dur": 5.5, "ia_dur": "5s", "render_mode": "flow", "type": "Horizonte Cósmico",
             "action": "Vista amplia de la nave en ruta estable.",
             "visual_en": "Wide tactile editorial illustration of the spacecraft gliding steadily across deep slate cosmos toward a softly lit planetary limb.",
             "fallback_en": "Wide editorial view of spacecraft gliding smoothly in deep space."},
            {"id": "SH13", "sec": "56-62.5s", "dur": 6.2, "ia_dur": "5s", "render_mode": "infographic", "type": "Cierre Documental 2.5D",
             "action": "Reflexión final de primeros principios.",
             "visual_en": "Editorial 2.5D closing paper note.", "fallback_en": "Minimal dark editorial paper note."},
        ]
    else:
        base_raw = [
            {"id": "SH01", "sec": "0-4s", "dur": 4.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Mapa Editorial 2.5D",
             "action": f"Contexto y ubicación del evento: {title_clean}.",
             "visual_en": "Editorial 2.5D regional map highlighting the event.", "fallback_en": "Editorial 2.5D map."},
            {"id": "SH02", "sec": "4-9s", "dur": 5.0, "ia_dur": "5s", "render_mode": "flow", "type": "Escena de Apertura",
             "action": f"Plano atmosférico del entorno de la noticia: {title_clean}.",
             "visual_en": f"Tactile editorial documentary illustration establishing the real setting of '{title_clean}', directional warm twilight rim light and deep carbon shadows.",
             "fallback_en": "Editorial chiaroscuro establishing shot of modern infrastructure at dusk."},
            {"id": "SH03", "sec": "9-14s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Recibo Documental 2.5D",
             "action": "Recorte editorial de la fuente oficial con la prueba verificada del reporte.",
             "visual_en": "Editorial 2.5D archival press receipt.", "fallback_en": "Clean editorial archival press receipt."},
            {"id": "SH04", "sec": "14-18s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Especialista",
             "action": "Primer plano sobrio a especialista evaluando reportes.",
             "visual_en": "Close-up editorial illustration of a technical specialist studying printed charts and instruments under warm desk lamp light in deep shadow.",
             "fallback_en": "Close-up editorial illustration of a specialist reading technical instruments."},
            {"id": "SH05", "sec": "18-22s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Acción de Control",
             "action": "Manos operando instrumentos de medición y registro.",
             "visual_en": "Close-up chiaroscuro shot of hands adjusting precision instruments on a matte technical console under directional studio lighting.",
             "fallback_en": "Close-up of hands adjusting precision instruments on a console."},
            {"id": "SH06", "sec": "22-26s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Macro Evidencia",
             "action": "Detalle macro al indicador o mecanismo físico clave.",
             "visual_en": "Extreme macro editorial shot of brushed steel measurement dials and warning markers illuminated by a single warm amber rim light.",
             "fallback_en": "Macro shot of precision mechanical dials under warm directional light."},
            {"id": "SH07", "sec": "26-30s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Escena Central",
             "action": "Visualización atmosférica del fenómeno principal.",
             "visual_en": f"Dynamic editorial documentary illustration depicting the central event of '{title_clean}', moody volumetric haze and crisp directional rim light.",
             "fallback_en": "Dynamic editorial chiaroscuro scene with atmospheric lighting."},
            {"id": "SH08", "sec": "30-34s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Dinámica Física",
             "action": "Detalle de fuerzas físicas o respuesta en terreno.",
             "visual_en": "Close-up editorial illustration capturing subtle physical motion, layered matte textures and dramatic shadow depth.",
             "fallback_en": "Editorial physical detail shot with textured chiaroscuro lighting."},
            {"id": "SH09", "sec": "34-38s", "dur": 4.0, "ia_dur": "5s", "render_mode": "flow", "type": "Respuesta Técnica",
             "action": "Activación de protocolo preventivo o monitoreo.",
             "visual_en": "Close-up editorial shot inside a calm operations room as an operator logs a safety protocol check on a matte console.",
             "fallback_en": "Close-up of operator activating safety protocol on console."},
            {"id": "SH10", "sec": "38-44s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Diagrama Progresivo 2.5D",
             "action": "Esquema técnico 2.5D explicando la causa del suceso.",
             "visual_en": "Editorial 2.5D progressive mechanism sketch.", "fallback_en": "Editorial 2.5D diagram."},
            {"id": "SH11", "sec": "44-50s", "dur": 5.0, "ia_dur": "5s", "render_mode": "infographic", "type": "Evidencia Documental 2.5D",
             "action": "Contraste factual entre condiciones y desenlace.",
             "visual_en": "Editorial 2.5D contrast sheet.", "fallback_en": "Editorial archival contrast sheet."},
            {"id": "SH12", "sec": "50-56s", "dur": 5.5, "ia_dur": "5s", "render_mode": "flow", "type": "Panorama Posterior",
             "action": "Vista general serena verificando estabilización.",
             "visual_en": "Wide editorial chiaroscuro establishing view of calm city infrastructure under soft twilight haze.",
             "fallback_en": "Wide editorial view of quiet modern infrastructure at twilight."},
            {"id": "SH13", "sec": "56-62.5s", "dur": 6.2, "ia_dur": "5s", "render_mode": "infographic", "type": "Cierre Documental 2.5D",
             "action": "Nota final documental por primeros principios.",
             "visual_en": "Editorial 2.5D closing paper note.", "fallback_en": "Minimal dark editorial paper note."},
        ]

    # Mezclar mejoras dinámicas generadas por Gemini cuando estén disponibles
    dyn_flow = (dynamic_visuals or {}).get("flow_shots") or {}
    dyn_ed = (dynamic_visuals or {}).get("editorial_graphics") or {}
    default_ed = build_default_editorial_graphics(
        title=title,
        script=script,
        source=(story_metrics or {}).get("sourceTag", "").replace("FUENTE:", "").strip() or "PRENSA OFICIAL",
        genre_label=genre_label,
        story_metrics=story_metrics,
    )

    shots: List[Dict[str, Any]] = []
    for s in base_raw:
        sid = s["id"]
        mode = "flow" if is_full_flow else s.get("render_mode", "flow")
        action = s["action"]
        visual_en = s["visual_en"]
        fallback_en = s["fallback_en"]

        if sid in dyn_flow and isinstance(dyn_flow[sid], dict):
            ov = dyn_flow[sid]
            action = str(ov.get("action") or action).strip()
            visual_en = str(ov.get("visual_en") or visual_en).strip()
            fallback_en = str(ov.get("fallback_en") or fallback_en).strip()

        item: Dict[str, Any] = {
            "id": sid,
            "sec": s["sec"],
            "dur": s["dur"],
            "ia_dur": s["ia_dur"],
            "render_mode": mode,
            "type": s["type"],
            "action": action,
            "prompt": style_prefix + visual_en,
            "fallback_prompt": style_prefix + fallback_en,
        }
        if mode == "infographic":
            merged_props = dict(story_metrics or {})
            merged_props.update(default_ed.get(sid, {}))
            if sid in dyn_ed and isinstance(dyn_ed[sid], dict):
                for k, v in dyn_ed[sid].items():
                    if v not in (None, "", [], {}):
                        merged_props[k] = v
            item["remotion_props"] = merged_props

        shots.append(item)
    return shots


def _call_gemini_json(prompt_text: str, timeout_sec: int = 22) -> Optional[Dict[str, Any]]:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    for model in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-lite-latest", "gemini-2.5-flash"]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            body = {
                "contents": [{"parts": [{"text": prompt_text}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                data = json.load(resp)
            raw_txt = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            raw_txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_txt, flags=re.DOTALL).strip()
            parsed = json.loads(raw_txt)
            if isinstance(parsed, dict):
                return parsed
        except Exception as e:
            print(f"[DIRECTOR-AI] ⚠️ Aviso {model}: {e}", flush=True)
            time.sleep(0.4)
    return None


def build_dynamic_story_visuals(
    news: Dict[str, Any],
    script: str,
    genre_label: str,
    story_metrics: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Usa Gemini para diseñar los 8 prompts de Google Flow (en inglés, estética 2.5D editorial)
    y los 5 gráficos editoriales en español estrictamente fieles a la noticia real.
    """
    if not os.getenv("GEMINI_API_KEY", "").strip():
        return None

    title = news.get("title", "")
    summary = news.get("summary_full") or news.get("summary", "")
    source = news.get("source_name") or news.get("source", "Prensa Oficial")
    article_excerpt = str(news.get("article_text") or summary)[:1600]
    receipt_hint = str(news.get("receipt_quote") or (story_metrics or {}).get("receiptQuote") or "")
    highlight_hint = str(news.get("highlight_phrase") or (story_metrics or {}).get("highlightPhrase") or "")

    prompt = f"""Eres el director de arte de un documental editorial 2.5D (estilo Vox / Johnny Harris / Veritasium: animación táctil en papel y claroscuro).
Debes diseñar el paquete visual completo para ESTA noticia exacta, sin reciclar escenas viejas ni inventar hechos no reportados.

NOTICIA: {title}
FUENTE: {source}
CATEGORÍA: {genre_label}
RESUMEN / EXTRACTO DEL ARTÍCULO: {article_excerpt}
CITA VERIFICABLE BASE: {receipt_hint}
GUIÓN DE LOCUCIÓN:
{script}

REGLAS ESTRICTAS DE RIGOR FÁCTUAL:
1. PROHIBIDO inventar fuego, explosiones, accidentes en el mar, barcos de rescate, caída de altitud o víctimas si la noticia NO los menciona.
2. Si la noticia trata de un modelo concreto (ej. Airbus A350 de Thai Airways, chip de 2nm, fallo específico), TODOS los prompts de Flow deben describir ese modelo/escenario exacto.
3. Estética de los 8 prompts Flow (`SH02, SH04, SH05, SH06, SH07, SH08, SH09, SH12`): en INGLÉS, sin texto en pantalla, sin palabras como "Veritasium" ni "Stylized 3D plastic", pidiendo iluminación editorial claroscuro, textura mate táctil y profundidad 2.5D.
4. Gráficos editoriales Remotion (`SH01, SH03, SH10, SH11, SH13`): en ESPAÑOL claro, legible en teléfono móvil, pocas palabras por campo. NUNCA inventes números que no aparezcan en el artículo, titular o guión.
5. Para `SH01` (Mapa 2.5D): incluye coordenadas reales (`lon`, `lat`) SOLO si la noticia tiene ubicaciones geográficas claras (`has_geo: true`). Si es un tema puramente conceptual sin ubicación relevante, pon `"has_geo": false`.
6. Para `SH03` (Recibo Documental 2.5D): usa una cita real y verificable (`receiptQuote`, máx 160 caracteres) basada en la noticia/artículo, y pon en `highlightPhrase` 3 a 7 palabras EXACTAS contenidas dentro de `receiptQuote`.
7. Para `SH10` (Diagrama 2.5D): elige `diagramKind` entre `"aircraft"`, `"chip"`, `"network"`, `"spacecraft"`, `"seismic"`.
8. Para `SH11` (Evidencia / Contraste): NUNCA inventes porcentajes ni ratios si no existen 2 cifras reales comparables; si el contraste es cualitativo, deja `leftRatio` y `rightRatio` omitidos o en `null`.

Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta:
{{
  "flow_shots": {{
    "SH02": {{"action": "descripción breve en español", "visual_en": "scene prompt in English", "fallback_en": "simpler safe prompt in English"}},
    "SH04": {{"action": "...", "visual_en": "...", "fallback_en": "..."}},
    "SH05": {{"action": "...", "visual_en": "...", "fallback_en": "..."}},
    "SH06": {{"action": "...", "visual_en": "...", "fallback_en": "..."}},
    "SH07": {{"action": "...", "visual_en": "...", "fallback_en": "..."}},
    "SH08": {{"action": "...", "visual_en": "...", "fallback_en": "..."}},
    "SH09": {{"action": "...", "visual_en": "...", "fallback_en": "..."}},
    "SH12": {{"action": "...", "visual_en": "...", "fallback_en": "..."}}
  }},
  "editorial_graphics": {{
    "SH01": {{
      "has_geo": true,
      "mapMode": "diversion | route | epicenter",
      "kicker": "MÁX 3 PALABRAS",
      "headline": "TITULAR CORTO EN ESPAÑOL (MÁX 50 CARACTERES)",
      "origin": {{"name": "CIUDAD", "code": "COD", "lon": 0.0, "lat": 0.0}},
      "plannedDest": {{"name": "CIUDAD", "code": "COD", "lon": 0.0, "lat": 0.0}},
      "diversionDest": {{"name": "CIUDAD", "code": "COD", "lon": 0.0, "lat": 0.0}},
      "highlightCountries": ["CountryNameInEnglish"],
      "stampText": "ESTADO CORTO (EJ. DESVÍO EN VUELO, ALERTA ACTIVA; NO PONGAS EL NOMBRE DEL MEDIO)",
      "cardKicker": "SUBTÍTULO FICHA (MÁX 24 CARACTERES)",
      "cardHeadline": "DATO PRINCIPAL FICHA (MÁX 22 CARACTERES)",
      "cardLines": ["LÍNEA 1 CORTA (MÁX 38 CARACTERES)", "LÍNEA 2 CORTA (MÁX 38 CARACTERES)"]
    }},
    "SH03": {{
      "has_receipt": true,
      "kicker": "EVIDENCIA DOCUMENTAL",
      "headline": "LO QUE CONFIRMA EL REPORTE",
      "sourceName": "{source.upper()[:28]}",
      "publicationDate": "REGISTRO OFICIAL",
      "articleTitle": "TITULAR DEL ARTÍCULO EN ESPAÑOL (MÁX 78 CARACTERES)",
      "receiptQuote": "CITA FACTUAL VERIFICABLE EN ESPAÑOL (MÁX 160 CARACTERES)",
      "highlightPhrase": "3 A 7 PALABRAS EXACTAS DENTRO DE receiptQuote",
      "keyMetricBadge": "DATO NUMÉRICO O CÓDIGO REAL (O CADENA VACÍA SI NO HAY)",
      "bottomTakeaway": "CONCLUSIÓN CORTA LEGIBLE EN MÓVIL"
    }},
    "SH10": {{
      "kicker": "DECONSTRUCCIÓN TÉCNICA",
      "headline": "¿PREGUNTA O IDEA CENTRAL DEL MECANISMO?",
      "diagramKind": "aircraft | chip | network | spacecraft | seismic",
      "calloutTitle": "ETIQUETA 1",
      "calloutDetail": "DETALLE CORTO 1",
      "secondaryLabel": "ETIQUETA 2",
      "secondaryCallout": "DETALLE CORTO 2",
      "bottomStamp": "CLAVE OPERATIVA",
      "bottomTakeaway": "CONCLUSIÓN BREVE Y CLARA"
    }},
    "SH11": {{
      "kicker": "EVIDENCIA DEL CASO",
      "headline": "TITULAR DE CONTRASTE REAL",
      "mode": "comparison",
      "leftLabel": "ESCENARIO BASE",
      "leftValue": "DATO O HECHO A",
      "rightLabel": "DESENLACE REAL",
      "rightValue": "DATO O HECHO B",
      "sourceStamp": "FUENTE · {source.upper()[:24]}",
      "bottomTakeaway": "CONCLUSIÓN FÁCTICA EN ESPAÑOL"
    }},
    "SH13": {{
      "kicker": "PRIMEROS PRINCIPIOS",
      "headline": "LO QUE DEJA ESTE CASO",
      "quote": "Reflexión final concisa en español (máx 125 caracteres)",
      "takeaway": "FRASE DE CIERRE CORTA",
      "sourceTag": "{source.upper()[:28]}"
    }}
  }}
}}"""

    parsed = _call_gemini_json(prompt, timeout_sec=24)
    if not parsed:
        return None

    # Limpiar posibles campos nulos o coordenadas inválidas en SH01 y asegurar rigor en SH03/SH11
    ed = parsed.get("editorial_graphics")
    if isinstance(ed, dict):
        if isinstance(ed.get("SH01"), dict):
            s1 = ed["SH01"]
            if not s1.get("has_geo"):
                s1["has_geo"] = False
                for k in ("origin", "plannedDest", "diversionDest"):
                    s1.pop(k, None)
            else:
                for k in ("origin", "plannedDest", "diversionDest"):
                    place = s1.get(k)
                    if isinstance(place, dict):
                        try:
                            lon = float(place["lon"])
                            lat = float(place["lat"])
                            if abs(lon) < 0.001 and abs(lat) < 0.001:
                                s1.pop(k, None)
                            else:
                                place["lon"] = lon
                                place["lat"] = lat
                        except Exception:
                            s1.pop(k, None)
                    elif place is None:
                        s1.pop(k, None)
                if not isinstance(s1.get("origin"), dict):
                    if story_metrics and story_metrics.get("has_geo") and story_metrics.get("origin"):
                        for gk in ("has_geo", "mapMode", "origin", "plannedDest", "diversionDest", "highlightCountries"):
                            if gk in story_metrics:
                                s1[gk] = story_metrics[gk]
                    else:
                        s1["has_geo"] = False

        if isinstance(ed.get("SH03"), dict):
            s3 = ed["SH03"]
            s3["has_receipt"] = True
            rq = str(s3.get("receiptQuote") or receipt_hint or "").strip()
            hp = str(s3.get("highlightPhrase") or highlight_hint or "").strip()
            if rq and (not hp or hp.lower() not in rq.lower()):
                rw = rq.split()
                s3["highlightPhrase"] = " ".join(rw[:min(5, len(rw))]).strip(".,;:")

        if isinstance(ed.get("SH11"), dict):
            s11 = ed["SH11"]
            lv = str(s11.get("leftValue") or "")
            rv = str(s11.get("rightValue") or "")
            if not (re.search(r"\d", lv) and re.search(r"\d", rv)):
                s11.pop("leftRatio", None)
                s11.pop("rightRatio", None)

    print("[DIRECTOR-AI] ✅ Visuales y prompts dinámicos 2.5D generados para la noticia.", flush=True)
    return parsed


def _split_script_into_semantic_beats(script: str, target_beats: int = 17) -> List[Dict[str, Any]]:
    """
    Divide `script.split()` en ~16-18 beats semánticos respetando pausas de puntuación/cláusulas,
    garantizando partición exacta 1:1 de índices de palabra sin omitir ni duplicar palabras.
    """
    words = (script or "").split()
    n_words = len(words)
    if n_words == 0:
        return []

    # 1. Cortes primarios por puntuación fuerte o pausa de cláusula
    spans: List[Tuple[int, int]] = []
    cur_start = 0
    for idx, w in enumerate(words):
        at_punct = w.endswith((".", "?", "!", ";", ":"))
        at_comma = w.endswith(",") and (idx - cur_start + 1) >= 5
        if at_punct or at_comma:
            spans.append((cur_start, idx))
            cur_start = idx + 1
    if cur_start < n_words:
        spans.append((cur_start, n_words - 1))

    # 2. Subdividir segmentos largos (> 11 palabras) en pausas naturales o punto medio
    conj_words = {"pero", "porque", "donde", "cuando", "mientras", "aunque", "para", "como", "y"}
    refined: List[Tuple[int, int]] = []
    for s_idx, e_idx in spans:
        stack = [(s_idx, e_idx)]
        while stack:
            a, b = stack.pop(0)
            length = b - a + 1
            if length <= 11 or n_words < 24:
                refined.append((a, b))
                continue
            mid = a + length // 2
            split_pos = mid
            best_dist = length
            for k in range(a + 4, b - 3):
                tok_clean = re.sub(r"[^\wáéíóúñü]", "", words[k].lower())
                if tok_clean in conj_words or words[k - 1].endswith(","):
                    if abs(k - mid) < best_dist:
                        best_dist = abs(k - mid)
                        split_pos = k
            if split_pos <= a + 2 or split_pos > b - 2:
                split_pos = mid
            stack.insert(0, (split_pos, b))
            stack.insert(0, (a, split_pos - 1))

    # 3. Fusionar fragmentos diminutos (< 5 palabras) si el guión es largo y excede target_beats + 1
    merged: List[Tuple[int, int]] = []
    for a, b in refined:
        if merged and ((b - a + 1) < 5 or len(merged) >= target_beats) and (merged[-1][1] - merged[-1][0] + 1) <= 7:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))

    # 4. Si aún estamos muy por debajo de 16 beats en un guión largo (>= 95 palabras), dividir los bloques más largos
    if n_words >= 95:
        while len(merged) < 16:
            longest_i = max(range(len(merged)), key=lambda i: merged[i][1] - merged[i][0])
            a, b = merged[longest_i]
            length = b - a + 1
            if length < 8:
                break
            mid = a + length // 2
            merged = merged[:longest_i] + [(a, mid - 1), (mid, b)] + merged[longest_i + 1:]

    # 5. Si excede 18 beats, fusionar los dos bloques consecutivos más cortos
    while len(merged) > 18 and len(merged) >= 2:
        pair_i = min(
            range(len(merged) - 1),
            key=lambda i: (merged[i][1] - merged[i][0] + 1) + (merged[i + 1][1] - merged[i + 1][0] + 1),
        )
        merged = merged[:pair_i] + [(merged[pair_i][0], merged[pair_i + 1][1])] + merged[pair_i + 2:]

    return [
        {
            "word_start_idx": a,
            "word_end_idx": b,
            "text": " ".join(words[a:b + 1]),
        }
        for a, b in merged
    ]


def build_narrative_beat_sheet(
    script: str,
    shots: List[Dict[str, Any]],
    news: Optional[Dict[str, Any]] = None,
    genre_label: str = "",
) -> List[Dict[str, Any]]:
    """
    Construye un Beat Sheet narrativo (16-18 beats en guiones completos) con:
    - Roles estilo Veritasium/Vox (Hook Paradoja, Mapa, Receipt, Escalada, Mecanismo, Diagrama, Music Drop Reveal, Evidencia, Resolución, Cierre).
    - >75-80% hard cuts ('cut') y 'dissolve' exclusivamente al cambiar de Acto (1->2, 2->3, 3->4).
    - Reencuadres punch-in (variant='punch_in', start_trim=1.8) de planos Flow existentes sin consumir créditos extra.
    - 1 único music_drop en la revelación y SFX diegéticos mapeados por beat.
    """
    raw_beats = _split_script_into_semantic_beats(script, target_beats=17)
    n = len(raw_beats)
    if n == 0:
        return []

    available_ids = [s.get("id") for s in (shots or []) if s.get("id")]
    valid_set = set(available_ids)

    def _pick_shot(preferred: str, fallback: str = "SH02") -> str:
        if preferred in valid_set:
            return preferred
        if fallback in valid_set:
            return fallback
        return available_ids[0] if available_ids else preferred

    # Asignar actos, roles, planos, variantes, transiciones y cues SFX según n
    if n >= 12:
        act2_start = 3
        drop_idx = max(act2_start + 3, min(n - 4, int(round(n * 0.65))))
        act4_start = max(drop_idx + 2, n - 2)
        diag_idx = act2_start + max(2, (drop_idx - act2_start) // 2)
        evid_idx = min(act4_start - 1, drop_idx + 2) if (act4_start - drop_idx) >= 3 else -1

        act2_flow_cycle = [
            ("ESCALADA", "SH04", "primary", "none"),
            ("ESCALADA", "SH05", "primary", "none"),
            ("MECANISMO", "SH06", "primary", "click"),
            ("ANALOGIA", "SH07", "primary", "none"),
            ("MECANISMO", "SH04", "punch_in", "none"),
            ("ANALOGIA", "SH08", "primary", "none"),
            ("MECANISMO", "SH05", "punch_in", "none"),
            ("ESCALADA", "SH09", "primary", "none"),
        ]
        act3_cycle = [
            ("GIRO_TECNICO", "SH08", "punch_in"),
            ("GIRO_TECNICO", "SH07", "punch_in"),
            ("GIRO_TECNICO", "SH06", "punch_in"),
        ]

        beats: List[Dict[str, Any]] = []
        a2_cursor = 0
        a3_cursor = 0
        for i, rb in enumerate(raw_beats):
            variant = "primary"
            start_trim = 0.0
            music_drop = False
            sfx_cue = "none"

            if i == 0:
                act, role, shot_id, sfx_cue = 1, "HOOK_PARADOJA", _pick_shot("SH02"), "boom"
            elif i == 1:
                act, role, shot_id, sfx_cue = 1, "CONTEXTO_MAPA", _pick_shot("SH01", "SH02"), "paper"
            elif i == 2:
                act, role, shot_id, sfx_cue = 1, "RECEIPT", _pick_shot("SH03", "SH02"), "highlighter"
            elif i < drop_idx:
                act = 2
                if i == diag_idx:
                    role, shot_id, sfx_cue = "DIAGRAMA", _pick_shot("SH10", "SH06"), "click"
                else:
                    role, pref_sh, variant, sfx_cue = act2_flow_cycle[a2_cursor % len(act2_flow_cycle)]
                    shot_id = _pick_shot(pref_sh)
                    a2_cursor += 1
                    if variant == "punch_in":
                        start_trim = 1.8
                if i == drop_idx - 1:
                    sfx_cue = "riser"
            elif i == drop_idx:
                act = 3
                role = "MUSIC_DROP_REVEAL"
                shot_id = _pick_shot("SH09", "SH07")
                music_drop = True
                sfx_cue = "boom"
            elif i < act4_start:
                act = 3
                if i == evid_idx:
                    role, shot_id, sfx_cue = "EVIDENCIA", _pick_shot("SH11", "SH08"), "paper"
                else:
                    role, pref_sh, variant = act3_cycle[a3_cursor % len(act3_cycle)]
                    shot_id = _pick_shot(pref_sh)
                    start_trim = 1.8 if variant == "punch_in" else 0.0
                    a3_cursor += 1
            elif i == n - 2:
                act, role, shot_id = 4, "RESOLUCION", _pick_shot("SH12", "SH09")
            else:
                act, role, shot_id, sfx_cue = 4, "CIERRE", _pick_shot("SH13", "SH12"), "paper"

            prev_act = beats[-1]["act"] if beats else act
            transition_in = "dissolve" if (beats and act != prev_act) else "cut"

            beats.append({
                "beat_id": f"B{i + 1:02d}",
                "role": role,
                "act": act,
                "text": rb["text"],
                "word_start_idx": rb["word_start_idx"],
                "word_end_idx": rb["word_end_idx"],
                "shot_id": shot_id,
                "variant": variant,
                "start_trim": start_trim,
                "transition_in": transition_in,
                "music_drop": music_drop,
                "sfx_cue": sfx_cue,
            })
        return beats

    # Caso compacto (< 12 beats, ej. scripts breves en tests)
    default_order = ["SH02", "SH01", "SH03", "SH04", "SH06", "SH10", "SH07", "SH09", "SH11", "SH12", "SH13"]
    drop_idx = max(1, min(n - 2, int(round(n * 0.65)))) if n >= 3 else -1
    beats = []
    for i, rb in enumerate(raw_beats):
        act = 1 if i == 0 else (4 if i == n - 1 else (3 if drop_idx >= 0 and i >= drop_idx else 2))
        prev_act = beats[-1]["act"] if beats else act
        shot_id = _pick_shot(default_order[min(i, len(default_order) - 1)])
        is_drop = (i == drop_idx)
        role = "HOOK_PARADOJA" if i == 0 else ("CIERRE" if i == n - 1 else ("MUSIC_DROP_REVEAL" if is_drop else "DESARROLLO"))
        beats.append({
            "beat_id": f"B{i + 1:02d}",
            "role": role,
            "act": act,
            "text": rb["text"],
            "word_start_idx": rb["word_start_idx"],
            "word_end_idx": rb["word_end_idx"],
            "shot_id": shot_id,
            "variant": "primary",
            "start_trim": 0.0,
            "transition_in": "dissolve" if (beats and act != prev_act) else "cut",
            "music_drop": is_drop,
            "sfx_cue": "boom" if (i == 0 or is_drop) else ("paper" if shot_id in ("SH01", "SH11", "SH13") else "none"),
        })
    return beats

