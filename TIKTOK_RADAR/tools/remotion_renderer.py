#!/usr/bin/env python3
"""
TIKTOK RADAR · Remotion Motion Graphic Renderer (Puente Python -> React/Chromium Headless)
Renderiza animaciones editoriales 2.5D táctiles (cartografía real, diagramas progresivos,
fichas de evidencia y cierres documentales) a 1080x1920 (9:16 vertical) a 24 fps.

Composiciones Principales (Estilo Editorial 2.5D):
  - Editorial25DMap: Cartografía vectorial real (d3-geo + world-atlas) en perspectiva 2.5D,
    rutas/desvíos/epicentros animados y ficha de papel archival en paralaje.
  - Editorial25DDiagram: Croquis técnico progresivo sobre papel archival (avión, chip, red,
    nave espacial o impacto sísmico) con cotas animadas y conclusión legible en móvil.
  - Editorial25DFactSheet: Lámina editorial de magnitud verificada o contraste factual sin cajas UI.
  - Editorial25DOutro: Cierre documental en papel archival y tinta editorial por primeros principios.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

TOOLS_DIR = Path(__file__).resolve().parent
ROOT_DIR = TOOLS_DIR.parent
MOTION_ENGINE_DIR = ROOT_DIR / "motion_engine"
BATCH_WORKER_JS = MOTION_ENGINE_DIR / "render_batch.mjs"

THEME_VISUALS: Dict[str, Dict[str, str]] = {
    "aviation": {
        "accentColor": "#E5A93C",
        "alertColor": "#E63946",
        "diagramKind": "aircraft",
        "markerIcon": "plane",
    },
    "cyber": {
        "accentColor": "#F4A261",
        "alertColor": "#E63946",
        "diagramKind": "network",
        "markerIcon": "pulse",
    },
    "hardware": {
        "accentColor": "#38BDF8",
        "alertColor": "#F59E0B",
        "diagramKind": "chip",
        "markerIcon": "chip",
    },
    "space": {
        "accentColor": "#FFB703",
        "alertColor": "#A855F7",
        "diagramKind": "spacecraft",
        "markerIcon": "rocket",
    },
    "universal": {
        "accentColor": "#E5A93C",
        "alertColor": "#E63946",
        "diagramKind": "seismic",
        "markerIcon": "pulse",
    },
}


def is_remotion_available() -> bool:
    """Verifica si Node.js, npm y los paquetes de Remotion están instalados."""
    if not (MOTION_ENGINE_DIR / "node_modules" / ".bin" / "remotion").exists() and not shutil.which("npx"):
        return False
    return (MOTION_ENGINE_DIR / "package.json").exists()


def truncate_clean(text: str, max_len: int) -> str:
    """Recorta texto respetando límites de palabra sin cortar palabras a la mitad."""
    clean = " ".join((text or "").split()).strip()
    if len(clean) <= max_len:
        return clean
    cut = clean[:max_len].rsplit(" ", 1)[0].strip()
    return cut if len(cut) >= int(max_len * 0.55) else clean[:max_len].strip()


def _resolve_genre_theme(genre: str) -> str:
    """Mapea la categoría editorial a un tema visual sin falsos positivos por subcadena."""
    g = (genre or "").upper()
    tokens = set("".join(ch if ch.isalnum() else " " for ch in g).split())
    if "G1" == g or any(k in g for k in ("AVIACION", "VUELO", "ACCIDENTE", "MAYDAY", "AERO")):
        return "aviation"
    if "CATASTROF" in g or "SISMO" in g or "TERREMOTO" in g or "LLUVIA" in g or "DESASTRE" in g:
        return "universal"
    if "G2" in tokens or any(k in g for k in ("CIBER", "CYBER", "HACK", "SECURITY")):
        return "cyber"
    if "G4" in tokens or any(k in g for k in ("ESPACIO", "SPACE", "CIENCIA", "ASTRONOM")):
        return "space"
    if "G3" in tokens or "IA" in tokens or "AI" in tokens or any(k in g for k in ("HARDWARE", "CHIP", "TECH", "ROBOTIC")):
        return "hardware"
    return "universal"


def get_composition_for_genre(genre: str) -> str:
    """Mapea la categoría editorial al componente Remotion 2.5D óptimo."""
    theme = _resolve_genre_theme(genre)
    theme_to_comp = {
        "aviation": "Editorial25DMap",
        "cyber": "Editorial25DDiagram",
        "hardware": "Editorial25DDiagram",
        "space": "Editorial25DMap",
        "universal": "Editorial25DFactSheet",
    }
    return theme_to_comp.get(theme, "Editorial25DFactSheet")


def get_composition_for_shot(
    genre: str,
    shot_id: str = "",
    shot_type: str = "",
    has_geo: bool = True,
    has_receipt: bool = False,
) -> str:
    """
    Selecciona la composición Editorial 2.5D especializada según el plano y su función narrativa:
    - SH13 / Cierre: Editorial25DOutro (conclusión documental en papel archival).
    - SH10 / Diagrama / Esquema: Editorial25DDiagram (croquis técnico progresivo).
    - SH11 / Evidencia / Comparativa: Editorial25DFactSheet (contraste o cifra verificada).
    - SH01 / Contexto: Editorial25DMap si existe ancla geográfica real, o Editorial25DFactSheet.
    - SH03 / Recibo: Editorial25DReceipt si es Recibo Documental / `has_receipt=True`, sino FactSheet/Diagram.
    """
    s_id = (shot_id or "").upper().strip()
    s_type = (shot_type or "").upper().strip()

    if s_id == "SH13":
        return "Editorial25DOutro"
    if s_id == "SH10":
        return "Editorial25DDiagram"
    if has_receipt or any(k in s_type for k in ["RECIBO", "RECEIPT", "PRUEBA DOCUMENTAL"]):
        return "Editorial25DReceipt"
    if s_id == "SH11":
        return "Editorial25DFactSheet"
    if s_id == "SH01":
        if has_geo:
            return "Editorial25DMap"
        return "Editorial25DFactSheet"
    if s_id == "SH03":
        if any(k in s_type for k in ["BLUEPRINT", "ARQUITECTURA", "TOPOLOGÍA", "TOPOLOGIA", "ESQUEMA", "DIAGRAMA"]):
            return "Editorial25DDiagram"
        if not has_geo:
            return "Editorial25DDiagram"
        return "Editorial25DFactSheet"

    if any(k in s_type for k in ["CIERRE", "OUTRO", "CIERRE DOCUMENTAL"]):
        return "Editorial25DOutro"

    if any(k in s_type for k in ["MAPA", "RUTA", "CORREDOR", "EPICENTRO"]):
        return "Editorial25DMap" if has_geo else "Editorial25DFactSheet"
    if any(k in s_type for k in ["BLUEPRINT", "ARQUITECTURA", "TOPOLOGÍA", "TOPOLOGIA", "ESQUEMA", "DIAGRAMA"]):
        return "Editorial25DDiagram"
    if any(k in s_type for k in ["EVIDENCIA", "ESTADISTICA", "DATOS", "COMPARATIVA", "FORENSE", "BENCHMARK"]):
        return "Editorial25DFactSheet"
    return get_composition_for_genre(genre)


def build_category_props(
    genre: str,
    title: str = "",
    subtitle: str = "",
    duration_frames: int = 120,
    composition_id: Optional[str] = None,
    extra_props: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Genera propiedades editoriales 2.5D contextualizadas a la categoría y noticia real.
    Nunca inventa cifras técnicas ni imprime marcas ajenas.
    """
    theme = _resolve_genre_theme(genre)
    vis = THEME_VISUALS.get(theme, THEME_VISUALS["universal"])
    comp_id = composition_id or get_composition_for_genre(genre)
    clean_title = truncate_clean(title or "ANÁLISIS DEL REPORTE", 58).upper()
    clean_sub = truncate_clean(subtitle or "CONTEXTO TÉCNICO Y PRIMEROS PRINCIPIOS", 84).upper()
    ex = dict(extra_props or {})

    if comp_id == "Editorial25DMap":
        kicker_map = {
            "aviation": "CORREDOR AÉREO",
            "cyber": "INFRAESTRUCTURA GLOBAL",
            "hardware": "CADENA DE SILICIO",
            "space": "TRAYECTORIA DE MISIÓN",
            "universal": "LOCALIZACIÓN DEL REPORTE",
        }
        props: Dict[str, Any] = {
            "durationInFrames": duration_frames,
            "kicker": kicker_map.get(theme, "LOCALIZACIÓN DEL REPORTE"),
            "headline": clean_title,
            "markerIcon": vis["markerIcon"],
            "accentColor": vis["accentColor"],
            "alertColor": vis["alertColor"],
            "stampText": "REPORTE ACTIVO",
            "cardKicker": "REGISTRO GEOGRÁFICO",
            "cardHeadline": truncate_clean(ex.get("flightNumber") or ex.get("sourceTag") or clean_title, 34).upper(),
            "cardLines": [
                truncate_clean(subtitle or clean_title, 44).upper(),
                "UBICACIÓN CONTRASTADA EN PRENSA OFICIAL",
            ],
        }
        allowed = {
            "durationInFrames", "kicker", "headline", "mapMode", "markerIcon",
            "origin", "plannedDest", "diversionDest", "diversionRatio",
            "highlightCountries", "stampText", "cardKicker", "cardHeadline",
            "cardLines", "accentColor", "alertColor",
        }
    elif comp_id == "Editorial25DDiagram":
        diag_defaults = {
            "aviation": {
                "kicker": "DECONSTRUCCIÓN TÉCNICA",
                "calloutTitle": "SISTEMA CRÍTICO",
                "calloutDetail": "ALERTA PREVENTIVA",
                "secondaryLabel": "RESPUESTA EN VUELO",
                "secondaryCallout": "PROTOCOLO DE SEGURIDAD",
                "bottomStamp": "CLAVE OPERATIVA",
                "bottomTakeaway": "ACTUAR ANTES DE PERDER EL MARGEN",
            },
            "cyber": {
                "kicker": "ANATOMÍA DEL INCIDENTE",
                "calloutTitle": "VECTOR DE ENTRADA",
                "calloutDetail": "NODO EXPUESTO",
                "secondaryLabel": "CONTENCIÓN",
                "secondaryCallout": "AISLAMIENTO DE RED",
                "bottomStamp": "LECCIÓN DIGITAL",
                "bottomTakeaway": "UN SOLO ESLABÓN EXPONE TODA LA RED",
            },
            "hardware": {
                "kicker": "ARQUITECTURA INTERNA",
                "calloutTitle": "NÚCLEO DE CÓMPUTO",
                "calloutDetail": "LÍMITE FÍSICO",
                "secondaryLabel": "ESCALA Y DISEÑO",
                "secondaryCallout": "EFICIENCIA TÉRMICA",
                "bottomStamp": "CLAVE DE INGENIERÍA",
                "bottomTakeaway": "MÁS DENSIDAD EXIGE NUEVA ARQUITECTURA",
            },
            "space": {
                "kicker": "MECÁNICA DE MISIÓN",
                "calloutTitle": "FASE CRÍTICA",
                "calloutDetail": "VENTANA ORBITAL",
                "secondaryLabel": "CONTROL DE NAVE",
                "secondaryCallout": "CORRECCIÓN EN RUTA",
                "bottomStamp": "CLAVE DE MISIÓN",
                "bottomTakeaway": "PRECISIÓN MILIMÉTRICA EN EL VACÍO",
            },
            "universal": {
                "kicker": "DECONSTRUCCIÓN DEL CASO",
                "calloutTitle": "PUNTO DE TENSIÓN",
                "calloutDetail": "FACTOR DETONANTE",
                "secondaryLabel": "RESPUESTA",
                "secondaryCallout": "MEDIDA PREVENTIVA",
                "bottomStamp": "CLAVE DEL REPORTE",
                "bottomTakeaway": "ENTENDER LA CAUSA EVITA EL COLAPSO",
            },
        }
        props = {
            "durationInFrames": duration_frames,
            "headline": clean_title,
            "diagramKind": vis["diagramKind"],
            "accentColor": vis["accentColor"],
            "alertColor": vis["alertColor"],
            **diag_defaults.get(theme, diag_defaults["universal"]),
        }
        allowed = {
            "durationInFrames", "kicker", "headline", "diagramKind",
            "calloutTitle", "calloutDetail", "secondaryLabel", "secondaryCallout",
            "bottomStamp", "bottomTakeaway", "accentColor", "alertColor",
        }
    elif comp_id == "Editorial25DReceipt":
        raw_quote = str(ex.get("receiptQuote") or clean_sub or clean_title).strip()
        raw_hl = str(ex.get("highlightPhrase") or "").strip()
        if not raw_hl or raw_hl.lower() not in raw_quote.lower():
            rw = raw_quote.split()
            raw_hl = " ".join(rw[:min(5, len(rw))]).strip(".,;:")
        props = {
            "durationInFrames": duration_frames,
            "kicker": "EVIDENCIA DOCUMENTAL",
            "headline": truncate_clean(ex.get("headline") or clean_title, 54).upper(),
            "sourceName": truncate_clean(str(ex.get("sourceName") or ex.get("sourceTag") or "PRENSA OFICIAL").replace("FUENTE:", "").strip(), 28).upper(),
            "publicationDate": truncate_clean(str(ex.get("publicationDate") or "REGISTRO CONTRASTADO"), 24).upper(),
            "articleTitle": truncate_clean(str(ex.get("articleTitle") or title or clean_title), 84),
            "receiptQuote": truncate_clean(raw_quote, 168),
            "highlightPhrase": raw_hl,
            "keyMetricBadge": str(ex.get("keyMetricBadge") or "").upper()[:20],
            "bottomTakeaway": truncate_clean(str(ex.get("bottomTakeaway") or clean_sub), 58).upper(),
            "accentColor": vis["accentColor"],
            "alertColor": vis["alertColor"],
        }
        allowed = {
            "durationInFrames", "kicker", "headline", "sourceName", "publicationDate",
            "articleTitle", "receiptQuote", "highlightPhrase", "keyMetricBadge",
            "bottomTakeaway", "accentColor", "alertColor",
        }
    elif comp_id == "Editorial25DFactSheet":
        # Promover un identificador o cifra real si existe en extra_props sin inventar datos
        real_hero = ex.get("heroValue") or ex.get("nodeSize") or ex.get("cveSeverity") or ex.get("flightNumber")
        fact_mode = ex.get("mode") or ("metric" if real_hero and not ex.get("leftValue") else "comparison")
        fact_defaults = {
            "aviation": {
                "leftLabel": "OPERACIÓN ESTÁNDAR",
                "leftValue": "RUTA PLANIFICADA",
                "rightLabel": "DECISIÓN REPORTADA",
                "rightValue": "MANIOBRA PREVENTIVA",
                "bottomTakeaway": "EL MARGEN DE SEGURIDAD DEFINE LA MANIOBRA",
            },
            "cyber": {
                "leftLabel": "SUPERFICIE EXPUESTA",
                "leftValue": "BRECHA REPORTADA",
                "rightLabel": "RESPUESTA ACTIVA",
                "rightValue": "AISLAMIENTO Y PARCHE",
                "bottomTakeaway": "CONTENER A TIEMPO FRENA LA PROPAGACIÓN",
            },
            "hardware": {
                "leftLabel": "ARQUITECTURA PREVIA",
                "leftValue": "GENERACIÓN ANTERIOR",
                "rightLabel": "NUEVO ESTÁNDAR",
                "rightValue": "SALTO EN CÓMPUTO",
                "bottomTakeaway": "EL REDISEÑO CAMBIA EL TECHO DE RENDIMIENTO",
            },
            "space": {
                "leftLabel": "MARGEN PREVISTO",
                "leftValue": "VENTANA NOMINAL",
                "rightLabel": "HITO REPORTADO",
                "rightValue": "FASE COMPLETADA",
                "bottomTakeaway": "CADA FASE DEPENDE DE CÁLCULO EXACTO",
            },
            "universal": {
                "leftLabel": "CONDICIÓN INICIAL",
                "leftValue": "ESTADO PREVIO",
                "rightLabel": "HECHO CONFIRMADO",
                "rightValue": "IMPACTO REPORTADO",
                "bottomTakeaway": "LOS DATOS CONFIRMAN EL GIRO DEL CASO",
            },
        }.get(theme, {})

        props = {
            "durationInFrames": duration_frames,
            "kicker": "EVIDENCIA VERIFICADA",
            "headline": clean_title,
            "mode": fact_mode,
            "heroValue": str(real_hero or "HECHO CLAVE").upper()[:24],
            "heroUnit": str(ex.get("heroUnit") or "DATO CONTRASTADO EN EL REPORTE").upper()[:40],
            "heroCaption": truncate_clean(ex.get("heroCaption") or clean_sub, 86).upper(),
            "sourceStamp": truncate_clean(ex.get("sourceTag") or "FUENTE OFICIAL VERIFICADA", 36).upper(),
            "accentColor": vis["accentColor"],
            "alertColor": vis["alertColor"],
            **fact_defaults,
        }
        allowed = {
            "durationInFrames", "kicker", "headline", "mode",
            "heroValue", "heroUnit", "heroCaption",
            "leftLabel", "leftValue", "leftRatio",
            "rightLabel", "rightValue", "rightRatio",
            "sourceStamp", "bottomTakeaway", "accentColor", "alertColor",
        }
    elif comp_id == "Editorial25DOutro":
        props = {
            "durationInFrames": duration_frames,
            "kicker": "PRIMEROS PRINCIPIOS",
            "headline": truncate_clean(ex.get("headline") or "LO QUE DEJA ESTE CASO", 46).upper(),
            "quote": (
                "Los sistemas modernos no buscan eliminar toda incertidumbre, "
                "sino detectar las señales a tiempo para conservar el margen de seguridad."
            ),
            "takeaway": "CRITERIO PREVENTIVO ANTE LO IMPREVISTO",
            "sourceTag": truncate_clean(ex.get("sourceTag") or "PRENSA OFICIAL VERIFICADA", 38).upper(),
            "accentColor": vis["accentColor"],
            "alertColor": vis["alertColor"],
        }
        allowed = {
            "durationInFrames", "kicker", "headline", "quote",
            "takeaway", "sourceTag", "accentColor", "alertColor",
        }
    else:
        # Fallback limpio para composiciones legadas si se invocan explícitamente por ID
        props = {
            "durationInFrames": duration_frames,
            "title": clean_title,
            "subtitle": clean_sub,
            "theme": theme,
        }
        allowed = {
            "title", "subtitle", "durationInFrames", "theme",
            "initialAlt", "finalAlt", "flightNumber", "warningText", "descentRate",
            "nodeSize", "transistorCount", "efficiencyGain", "architectureTag",
            "packetRate", "cveSeverity", "threatVector", "targetCount",
            "labelA", "valA", "percentA", "labelB", "valB", "percentB", "multiplierTag", "sourceTag",
            "componentA", "statusA", "metricA", "componentB", "statusB", "metricB",
            "componentC", "statusC", "metricC", "blueprintTag",
            "quote", "takeaway",
        }

    for k, v in ex.items():
        if v not in (None, "", [], {}) and k in allowed:
            props[k] = v

    return props


def render_remotion_batch(
    jobs: List[Dict[str, Any]],
    concurrency: int = 2,
    crf: int = 14,
    gl: str = "angle",
    timeout_sec: int = 360,
) -> Dict[str, Optional[Path]]:
    """
    Renderiza múltiples composiciones en una sola sesión de navegador y bundle cacheado
    mediante `render_batch.mjs` (@remotion/bundler + @remotion/renderer).
    """
    results: Dict[str, Optional[Path]] = {str(j["outputLocation"]): None for j in jobs}
    if not jobs or not is_remotion_available() or not BATCH_WORKER_JS.exists():
        return results

    payload = {
        "concurrency": concurrency,
        "gl": gl,
        "jobs": [
            {
                "compositionId": j["compositionId"],
                "outputLocation": str(j["outputLocation"]),
                "inputProps": j.get("inputProps") or {},
                "transparent": bool(j.get("transparent", False)),
                "crf": int(j.get("crf", crf)),
                "concurrency": int(j.get("concurrency", concurrency)),
            }
            for j in jobs
        ],
    }

    batch_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
    try:
        json.dump(payload, batch_file, ensure_ascii=False)
        batch_file.close()
        res = subprocess.run(
            ["node", str(BATCH_WORKER_JS), batch_file.name],
            cwd=str(MOTION_ENGINE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_sec,
        )
        for line in (res.stdout or "").splitlines():
            if line.strip():
                print(line, flush=True)
        for j in jobs:
            out_p = Path(str(j["outputLocation"]))
            if out_p.exists() and out_p.stat().st_size > 10_000:
                results[str(out_p)] = out_p
        return results
    except Exception as e:
        print(f"[REMOTION-BATCH] ⚠️ Excepción ejecutando lote: {e}", file=sys.stderr)
        return results
    finally:
        if os.path.exists(batch_file.name):
            try:
                os.remove(batch_file.name)
            except OSError:
                pass


def render_remotion_scene(
    composition_id: str = "Editorial25DMap",
    output_path: Optional[Path] = None,
    props: Optional[Dict[str, Any]] = None,
    concurrency: int = 2,
    transparent: bool = False,
    crf: int = 14,
    timeout_sec: int = 180,
) -> Optional[Path]:
    """
    Renderiza una composición de Remotion a MP4 (o WebM con alfa si transparent=True),
    priorizando el worker por lotes con bundle en caché y con fallback directo a CLI.
    """
    if not is_remotion_available():
        print("[REMOTION] ⚠️ Remotion no está configurado en motion_engine.", file=sys.stderr)
        return None

    out_file = output_path or (ROOT_DIR / "entregas" / f"{composition_id}.mp4")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if BATCH_WORKER_JS.exists():
        print(f"[REMOTION] 🚀 Renderizando composición '{composition_id}' (worker cacheado) hacia {out_file.name}...", flush=True)
        batch_res = render_remotion_batch(
            jobs=[{
                "compositionId": composition_id,
                "outputLocation": str(out_file),
                "inputProps": props or {},
                "transparent": transparent,
                "crf": crf,
                "concurrency": concurrency,
            }],
            concurrency=concurrency,
            crf=crf,
            timeout_sec=timeout_sec,
        )
        hit = batch_res.get(str(out_file))
        if hit and hit.exists():
            return hit

    cmd = [
        "npx", "remotion", "render",
        "src/index.ts",
        composition_id,
        str(out_file),
        f"--concurrency={concurrency}",
        "--gl=angle",
    ]

    if transparent:
        cmd.extend(["--transparent", "--codec=vp8"])
    else:
        cmd.append(f"--crf={crf}")

    props_temp_file = None
    if props:
        props_temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(props, props_temp_file, ensure_ascii=False)
        props_temp_file.close()
        cmd.append(f"--props={props_temp_file.name}")

    try:
        print(f"[REMOTION] 🚀 Renderizando composición '{composition_id}' hacia {out_file.name}...", flush=True)
        res = subprocess.run(
            cmd,
            cwd=str(MOTION_ENGINE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_sec,
        )
        if res.returncode == 0 and out_file.exists() and out_file.stat().st_size > 10_000:
            print(f"[REMOTION] ✅ Renderizado completado: {out_file.name} ({out_file.stat().st_size / 1024:.1f} KB)", flush=True)
            return out_file
        print(f"[REMOTION] ❌ Error en renderizado (code {res.returncode}):\n{res.stdout[-1200:]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[REMOTION] ❌ Excepción al renderizar: {e}", file=sys.stderr)
        return None
    finally:
        if props_temp_file and os.path.exists(props_temp_file.name):
            try:
                os.remove(props_temp_file.name)
            except OSError:
                pass


def render_remotion_still(
    composition_id: str = "Editorial25DMap",
    output_path: Optional[Path] = None,
    frame_number: int = 60,
    props: Optional[Dict[str, Any]] = None,
    timeout_sec: int = 60,
) -> Optional[Path]:
    """
    Renderiza un único fotograma de la composición a JPG/PNG para inspección visual o portadas.
    """
    if not is_remotion_available():
        return None

    out_file = output_path or (ROOT_DIR / "entregas" / f"{composition_id}_frame{frame_number}.jpg")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "npx", "remotion", "still",
        "src/index.ts",
        composition_id,
        str(out_file),
        f"--frame={frame_number}",
        "--gl=angle",
        "--jpeg-quality=95",
        "--overwrite",
    ]

    props_temp_file = None
    if props:
        props_temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(props, props_temp_file, ensure_ascii=False)
        props_temp_file.close()
        cmd.append(f"--props={props_temp_file.name}")

    try:
        res = subprocess.run(
            cmd,
            cwd=str(MOTION_ENGINE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_sec,
        )
        if res.returncode == 0 and out_file.exists():
            return out_file
        return None
    except Exception as e:
        print(f"[REMOTION] ❌ Excepción al renderizar still: {e}", file=sys.stderr)
        return None
    finally:
        if props_temp_file and os.path.exists(props_temp_file.name):
            try:
                os.remove(props_temp_file.name)
            except OSError:
                pass


def render_category_motion_graphic(
    genre: str,
    output_path: Path,
    title: str = "",
    subtitle: str = "",
    target_duration_sec: float = 5.0,
    fps: int = 24,
    shot_id: str = "",
    shot_type: str = "",
    composition_id: Optional[str] = None,
    extra_props: Optional[Dict[str, Any]] = None,
) -> Optional[Path]:
    """
    Selecciona la composición Editorial 2.5D adecuada según género y plano y compila el vídeo vertical 9:16.
    """
    has_geo = bool(
        extra_props and (
            extra_props.get("origin")
            or extra_props.get("has_geo")
        )
    )
    comp_id = composition_id or get_composition_for_shot(
        genre,
        shot_id=shot_id,
        shot_type=shot_type,
        has_geo=has_geo if (extra_props and "has_geo" in extra_props) else True,
        has_receipt=bool(extra_props and extra_props.get("has_receipt")),
    )
    frames = max(24, int(target_duration_sec * fps))
    props = build_category_props(
        genre=genre,
        title=title,
        subtitle=subtitle,
        duration_frames=frames,
        composition_id=comp_id,
        extra_props=extra_props,
    )
    return render_remotion_scene(
        composition_id=comp_id,
        output_path=output_path,
        props=props,
        concurrency=2,
    )


if __name__ == "__main__":
    print("Probando renderizado still para las 5 composiciones Editorial 2.5D...")
    all_comps = [
        "Editorial25DMap",
        "Editorial25DReceipt",
        "Editorial25DDiagram",
        "Editorial25DFactSheet",
        "Editorial25DOutro",
    ]
    for comp in all_comps:
        out = Path(f"/tmp/test_{comp}.jpg")
        r = render_remotion_still(comp, output_path=out, frame_number=72)
        print(f" Still {comp}: {'✅' if r and out.exists() else '❌'} -> {out}")
