#!/usr/bin/env python3
"""
TIKTOK RADAR · Remotion Motion Graphic Renderer (Puente Python -> React/Chromium Headless)
Permite renderizar animaciones vectoriales, gráficos y HUDs técnicos estilo Veritasium
usando componentes de React a 1080x1920 (9:16 vertical) a 24 fps.

Composiciones Disponibles:
  - VeritasiumAltimeter: Telemetría de aviación, altitud barométrica, PFD attitude, alerta pull-up.
  - VeritasiumTechChip: Arquitectura de silicio 2nm, transistores GAA nanosheet, fotones EUV.
  - VeritasiumCyberRadar: Radar de ciberataques, flujo de paquetes DDoS, mapa de nodos, CVE severidad.
  - VeritasiumStatComparison: Comparativa proporcional de inversión/impacto con multiplicador.
  - VeritasiumBlueprint: Desglose de arquitectura crítica, blueprint vectorial 3D y láser de escaneo.
  - VeritasiumDocumentaryOutro: Cierre documental solemne por primeros principios con cita y sello oficial.
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
    """Mapea la categoría editorial al componente Remotion óptimo."""
    theme = _resolve_genre_theme(genre)
    theme_to_comp = {
        "aviation": "VeritasiumAltimeter",
        "cyber": "VeritasiumCyberRadar",
        "hardware": "VeritasiumTechChip",
        "space": "VeritasiumStatComparison",
        "universal": "VeritasiumStatComparison",
    }
    return theme_to_comp.get(theme, "VeritasiumStatComparison")


def get_composition_for_shot(genre: str, shot_id: str = "", shot_type: str = "") -> str:
    """
    Selecciona la composición Remotion especializada según el plano y su función narrativa:
    - SH13 / Cierre: VeritasiumDocumentaryOutro (conclusión por primeros principios).
    - SH10 / Blueprint / Arquitectura: VeritasiumBlueprint.
    - SH11 / Evidencia / Comparativa: VeritasiumStatComparison.
    - SH01 / SH03 / Radar / Telemetría: Composición principal del género (o StatComparison en datos puros).
    """
    s_id = (shot_id or "").upper().strip()
    s_type = (shot_type or "").upper().strip()

    # 1. Prioridad por rol estructural del shot_id para evitar colisiones por etiquetas genéricas
    if s_id == "SH13" or any(k in s_type for k in ["CIERRE", "DOCUMENTAL", "OUTRO"]):
        return "VeritasiumDocumentaryOutro"
    if s_id == "SH10":
        return "VeritasiumBlueprint"
    if s_id == "SH11":
        return "VeritasiumStatComparison"
    if s_id == "SH01":
        return get_composition_for_genre(genre)
    if s_id == "SH03":
        hero = get_composition_for_genre(genre)
        if any(k in s_type for k in ["DATOS", "ESTADISTICA", "COMPARATIVA", "METRICAS", "MÉTRICAS"]):
            return "VeritasiumStatComparison" if hero != "VeritasiumStatComparison" else "VeritasiumBlueprint"
        if hero == "VeritasiumStatComparison":
            return "VeritasiumBlueprint"
        return hero

    # 2. Heurística secundaria por shot_type explícito (sin atrapar etiqueta genérica "INFOGRAFÍA")
    if any(k in s_type for k in ["BLUEPRINT", "ARQUITECTURA", "TOPOLOGÍA", "ESQUEMA", "DIAGRAMA"]):
        return "VeritasiumBlueprint"
    if any(k in s_type for k in ["EVIDENCIA", "ESTADISTICA", "DATOS", "COMPARATIVA", "FORENSE", "BENCHMARK"]):
        return "VeritasiumStatComparison"
    return get_composition_for_genre(genre)


def build_category_props(
    genre: str,
    title: str = "",
    subtitle: str = "",
    duration_frames: int = 120,
    composition_id: Optional[str] = None,
    extra_props: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Genera las propiedades de animación contextualizadas a la categoría y noticia."""
    theme = _resolve_genre_theme(genre)

    comp_id = composition_id or get_composition_for_genre(genre)
    base_props: Dict[str, Any] = {
        "durationInFrames": duration_frames,
        "title": truncate_clean(title or "ANÁLISIS TÉCNICO VERITASIUM", 60).upper(),
        "subtitle": truncate_clean(subtitle or "RECONSTRUCCIÓN POR PRIMEROS PRINCIPIOS", 82).upper(),
        "theme": theme,
    }

    if comp_id == "VeritasiumAltimeter":
        base_props.update({
            "initialAlt": 35000,
            "finalAlt": 3200,
            "flightNumber": "FLIGHT SAFETY DATA",
            "warningText": "ALERTA: TASA DE DESCENSO CRÍTICA",
            "descentRate": "-3,400 FPM",
        })
    elif comp_id == "VeritasiumTechChip":
        base_props.update({
            "nodeSize": "2 NM",
            "transistorCount": "33.7 BILLONES",
            "efficiencyGain": "+30% EFICIENCIA / +15% VELOCIDAD",
            "architectureTag": "GAA NANOSHEET 3D",
        })
    elif comp_id == "VeritasiumCyberRadar":
        base_props.update({
            "packetRate": "14.8 M PPS",
            "cveSeverity": "CVSS 9.8 · CRÍTICO",
            "threatVector": "ZERO-DAY EXPLOITATION",
            "targetCount": "184 NODOS COMPROMETIDOS",
        })
    elif comp_id == "VeritasiumStatComparison":
        stat_presets = {
            "space": {
                "labelA": "MISIÓN CONVENCIONAL",
                "valA": "1 USO",
                "percentA": 28,
                "labelB": "SISTEMA REUTILIZABLE",
                "valB": "CICLO CONTINUO",
                "percentB": 94,
                "multiplierTag": "EFICIENCIA DE ARQUITECTURA ESPACIAL",
                "sourceTag": "TELEMETRÍA DE MISIÓN · DEEP SPACE",
            },
            "aviation": {
                "labelA": "MARGEN NOMINAL",
                "valA": "ESTÁNDAR",
                "percentA": 88,
                "labelB": "EVENTO REPORTADO",
                "valB": "DESVIACIÓN",
                "percentB": 34,
                "multiplierTag": "AUDITORÍA DE SEGURIDAD AÉREA",
                "sourceTag": "REGISTRO AERONÁUTICO VERIFICADO",
            },
            "cyber": {
                "labelA": "EXPOSICIÓN INICIAL",
                "valA": "CRÍTICA",
                "percentA": 95,
                "labelB": "CON MITIGACIÓN",
                "valB": "CONTENIDO",
                "percentB": 22,
                "multiplierTag": "REDUCCIÓN DE SUPERFICIE DE ATAQUE",
                "sourceTag": "TELEMETRÍA SOC · THREAT INTEL",
            },
            "hardware": {
                "labelA": "ARQUITECTURA PREVIA",
                "valA": "1.0X BASE",
                "percentA": 45,
                "labelB": "NUEVA GENERACIÓN",
                "valB": "+40% EFIC.",
                "percentB": 92,
                "multiplierTag": "SALTO EN DENSIDAD Y EFICIENCIA",
                "sourceTag": "BENCHMARK TÉCNICO VERIFICADO",
            },
            "universal": {
                "labelA": "PARÁMETRO BASE",
                "valA": "FASE 01",
                "percentA": 35,
                "labelB": "UMBRAL REPORTADO",
                "valB": "FASE 02",
                "percentB": 92,
                "multiplierTag": "EVOLUCIÓN DEL EVENTO REPORTADO",
                "sourceTag": "REGISTRO DOCUMENTAL VERIFICADO",
            },
        }
        base_props.update(stat_presets.get(theme, stat_presets["universal"]))
    elif comp_id == "VeritasiumBlueprint":
        if theme == "cyber":
            base_props.update({
                "componentA": "GATEWAY DE ENRUTAMIENTO BGP",
                "statusA": "SATURACIÓN DDOS",
                "metricA": "14.8M PPS (ANOMALÍA)",
                "componentB": "INFRAESTRUCTURA DNS ROOT",
                "statusB": "TRÁFICO MALICIOSO",
                "metricB": "940 GBPS DE PICO",
                "componentC": "FIREWALL PERIMETRAL CORE",
                "statusC": "MITIGACIÓN DEFCON 2",
                "metricC": "FILTRADO ACTIVO",
                "blueprintTag": "TOPOLOGÍA DE RED · INTEL SOC",
            })
        elif theme == "hardware":
            base_props.update({
                "componentA": "CANALES GAA NANOSHEET 3D",
                "statusA": "CORRIENTE DE FUGA 0.02nA",
                "metricA": "ESCALA 2 NM",
                "componentB": "LÁSER EUV ALTA APERTURA NUMÉRICA",
                "statusB": "POTENCIA ÓPTIMA",
                "metricB": "LONGITUD 13.5 NM",
                "componentC": "INTERCONEXIÓN ÓPTICA CO-EMPAQUETADA",
                "statusC": "EFICIENCIA MÁXIMA",
                "metricC": "+30% ANCHO BANDA",
                "blueprintTag": "ARQUITECTURA DE SILICIO · SEMICONDUCTORES",
            })
        elif theme == "space":
            base_props.update({
                "componentA": "ESCUDO TÉRMICO ABLATIVO",
                "statusA": "RESISTENCIA TÉRMICA",
                "metricA": "TOLERANCIA 2800°C",
                "componentB": "CONTROL DE ACTITUD (RCS)",
                "statusB": "PROPULSIÓN FRÍA",
                "metricB": "IMPULSO 285s",
                "componentC": "ARRAY SOLAR MULTI-UNIÓN",
                "statusC": "DESPLIEGUE EXITOSO",
                "metricC": "POTENCIA 18.5 kW",
                "blueprintTag": "BLUEPRINT DE MISIÓN · DEEP SPACE",
            })
        elif theme == "aviation":
            base_props.update({
                "componentA": "SUPERFICIE DE CONTROL VERTICAL",
                "statusA": "DEFLEXIÓN NO COMANDADA",
                "metricA": "DESVIACIÓN 18.4°",
                "componentB": "SISTEMA HIDRÁULICO PRIMARIO",
                "statusB": "PÉRDIDA DE PRESIÓN",
                "metricB": "850 PSI (CRÍTICO)",
                "componentC": "COMPUTADORA DE GESTIÓN DE VUELO",
                "statusC": "ALERTA GPWS ACTIVA",
                "metricC": "LATENCIA 12ms",
                "blueprintTag": "BLUEPRINT AERONÁUTICO · NTSB/FAA",
            })
        else:
            base_props.update({
                "componentA": "EPICENTRO DE ANOMALÍA CRÍTICA",
                "statusA": "IMPACTO EN INFRAESTRUCTURA",
                "metricA": "ESCALA VERIFICADA",
                "componentB": "RED DE RESPUESTA Y SENSORES",
                "statusB": "MONITOREO CONTINUO",
                "metricB": "CANAL ACTIVO",
                "componentC": "PROTOCOLO DE CONTENCIÓN",
                "statusC": "MITIGACIÓN EN CURSO",
                "metricC": "RESPUESTA INMEDIATA",
                "blueprintTag": "ANÁLISIS ESTRUCTURAL · TIKTOK RADAR",
            })
    elif comp_id == "VeritasiumDocumentaryOutro":
        base_props.update({
            "quote": (
                "La tecnología avanzada no elimina el error humano ni la incertidumbre física: "
                "diseña sistemas capaces de sobrevivir a ambos."
            ),
            "takeaway": "INGENIO Y RESILIENCIA ANTE LO IMPREVISTO",
            "sourceTag": "AUDITORÍA TÉCNICA VERIFICADA · TIKTOK RADAR",
        })

    if extra_props:
        allowed_per_comp = {
            "VeritasiumAltimeter": {"initialAlt", "finalAlt", "flightNumber", "warningText", "descentRate"},
            "VeritasiumTechChip": {"nodeSize", "transistorCount", "efficiencyGain", "architectureTag"},
            "VeritasiumCyberRadar": {"packetRate", "cveSeverity", "threatVector", "targetCount"},
            "VeritasiumStatComparison": {"labelA", "valA", "percentA", "labelB", "valB", "percentB", "multiplierTag", "sourceTag"},
            "VeritasiumBlueprint": {"componentA", "statusA", "metricA", "componentB", "statusB", "metricB", "componentC", "statusC", "metricC", "blueprintTag"},
            "VeritasiumDocumentaryOutro": {"quote", "takeaway", "sourceTag"},
        }.get(comp_id, set()) | {"title", "subtitle", "durationInFrames", "theme"}
        for k, v in extra_props.items():
            if v not in (None, "") and k in allowed_per_comp:
                base_props[k] = v

    return base_props


def render_remotion_batch(
    jobs: List[Dict[str, Any]],
    concurrency: int = 2,
    crf: int = 14,
    gl: str = "angle",
    timeout_sec: int = 360,
) -> Dict[str, Optional[Path]]:
    """
    Renderiza múltiples composiciones en una sola sesión de navegador y bundle cacheado
    mediante `render_batch.mjs` (@remotion/bundler + @remotion/renderer), evitando recompilar
    Webpack 5 veces seguidas y reduciendo compresión intermedia con CRF configurable.
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
    composition_id: str = "VeritasiumAltimeter",
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
        else:
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
    composition_id: str = "VeritasiumAltimeter",
    output_path: Optional[Path] = None,
    frame_number: int = 45,
    props: Optional[Dict[str, Any]] = None,
    timeout_sec: int = 60,
) -> Optional[Path]:
    """
    Renderiza un único fotograma de la composición a JPG/PNG en ~1-2 segundos.
    Ideal para inspección visual instantánea, portadas o tarjetas de verificación.
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
    Función de alto nivel para invocar desde el ensamblador final o el pipeline.
    Selecciona la composición adecuada según el género y el plano, y compila el vídeo vertical 9:16.
    """
    comp_id = composition_id or get_composition_for_shot(genre, shot_id=shot_id, shot_type=shot_type)
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
    # Test directo CLI para las 6 composiciones
    print("Probando renderizado rápido still para las 6 composiciones...")
    all_comps = [
        "VeritasiumAltimeter",
        "VeritasiumTechChip",
        "VeritasiumCyberRadar",
        "VeritasiumStatComparison",
        "VeritasiumBlueprint",
        "VeritasiumDocumentaryOutro",
    ]
    for comp in all_comps:
        out = Path(f"/tmp/test_{comp}.jpg")
        r = render_remotion_still(comp, output_path=out, frame_number=45)
        print(f" Still {comp}: {'✅' if r and out.exists() else '❌'} -> {out}")
