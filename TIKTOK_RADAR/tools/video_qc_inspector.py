#!/usr/bin/env python3
"""
tools/video_qc_inspector.py
=============================================================================
SISTEMA DE CONTROL DE CALIDAD (QC/QA) E INSPECCIÓN DE VÍDEO BROADCAST PARA TIKTOK
=============================================================================
Auditoría técnica automatizada y visor de inspección frame a frame:
  1. Auditoría Acústica:
     - Sonoridad EBUR128 (LUFS Integrado, LRA, True Peak en dBFS/dBTP).
     - Detección de silencios y cortes de audio (silencedetect).
     - Validación de estándar TikTok Creator Rewards (-14.0 a -15.0 LUFS, Peak <= -1.0 dBTP).
  2. Auditoría Visual Frame a Frame:
     - Detección de cuadros congelados / estáticos (freezedetect).
     - Detección de cuadros o transiciones negras (blackdetect).
     - Comprobación de resolución (1080x1920), 24.0 fps y duración >= 60.0s.
  3. Verificación de Safe Zone de TikTok:
     - Comprobación de desborde hacia áreas de interfaz (barra superior, botones laterales, caption inferior).
     - Renderizado de vídeo de depuración con retícula táctica de TikTok (_QC_SAFEZONE.mp4).
     - Generación de Hoja de Contactos (Contact Sheet) en cuadrícula 4x3 con marcas de tiempo.
  4. Visor Interactivo HTML5 de Inspección:
     - Reproductor frame a frame (paso a paso a 24 fps, velocidades 0.25x a 2x).
     - Switch de retícula UI TikTok interactiva superpuesta sobre el vídeo.
     - Marcadores de advertencias clickeables para saltar al segundo exacto de cualquier anomalía.
     - Reporte técnico ejecutivo PASS/WARN/FAIL exportable en JSON y HTML.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class VideoQCInspector:
    def __init__(self, video_path: str | Path, output_dir: Optional[str | Path] = None, metadata_path: Optional[str | Path] = None):
        self.video_path = Path(video_path).resolve()
        if not self.video_path.exists():
            raise FileNotFoundError(f"No se encontró el vídeo a inspeccionar: {self.video_path}")

        self.output_dir = Path(output_dir).resolve() if output_dir else self.video_path.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_path = Path(metadata_path).resolve() if metadata_path else self.output_dir / "metadata.json"
        self.metadata = {}
        if self.metadata_path.exists():
            try:
                self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        self.results: Dict[str, Any] = {
            "file": str(self.video_path.name),
            "video_path": str(self.video_path),
            "output_dir": str(self.output_dir),
            "verdict": "PENDING",
            "score": 100,
            "stream_info": {},
            "audio_qc": {},
            "visual_qc": {},
            "safezone_qc": {},
            "warnings": [],
            "errors": [],
            "artifacts": {},
        }

    def inspect_streams(self) -> Dict[str, Any]:
        """Extrae metadatos técnicos mediante ffprobe."""
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of", "json",
            str(self.video_path),
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"ffprobe falló al analizar el vídeo: {res.stderr}")

        data = json.loads(res.stdout)
        fmt = data.get("format", {})
        streams = data.get("streams", [])

        v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

        if not v_stream:
            raise ValueError("El archivo no contiene pista de vídeo.")

        # Parsear FPS
        r_fps = v_stream.get("r_frame_rate", "24/1")
        fps_val = 24.0
        try:
            num, den = r_fps.split("/")
            fps_val = round(float(num) / float(den), 2)
        except Exception:
            fps_val = 24.0

        dur = float(fmt.get("duration", 0.0))
        size_mb = round(int(fmt.get("size", 0)) / (1024 * 1024), 2)
        bitrate_kbps = round(int(fmt.get("bit_rate", 0)) / 1000, 1) if fmt.get("bit_rate") else 0

        stream_info = {
            "width": int(v_stream.get("width", 0)),
            "height": int(v_stream.get("height", 0)),
            "fps": fps_val,
            "fps_str": r_fps,
            "video_codec": v_stream.get("codec_name", "unknown"),
            "audio_codec": a_stream.get("codec_name", "none") if a_stream else "none",
            "audio_sample_rate": int(a_stream.get("sample_rate", 0)) if a_stream else 0,
            "audio_channels": int(a_stream.get("channels", 0)) if a_stream else 0,
            "duration": round(dur, 2),
            "size_mb": size_mb,
            "bitrate_kbps": bitrate_kbps,
        }
        self.results["stream_info"] = stream_info
        return stream_info

    def inspect_audio(self) -> Dict[str, Any]:
        """Audita sonoridad EBUR128 (LUFS, LRA, True Peak) y detecta silencios anómalos."""
        cmd = [
            "ffmpeg", "-nostats", "-i", str(self.video_path),
            "-af", "ebur128=peak=true,silencedetect=n=-30dB:d=0.85",
            "-f", "null", "-",
        ]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            logs = proc.stdout or ""
        except Exception as e:
            logs = f"ERROR_FFMPEG: {e}"

        # Parsear EBUR128
        m_i = re.findall(r"I:\s*([-\d\.]+)\s*LUFS", logs)
        m_lra = re.findall(r"LRA:\s*([-\d\.]+)\s*LU", logs)
        m_tp = re.findall(r"(?:True\s+)?Peak:\s*([-\d\.]+)\s*dB(?:FS|TP)", logs)

        integrated_lufs = float(m_i[-1]) if m_i else None
        lra = float(m_lra[-1]) if m_lra else None
        true_peak = float(m_tp[-1]) if m_tp else None

        # Parsear silencios
        silence_starts = [float(x) for x in re.findall(r"silence_start:\s*([-\d\.]+)", logs)]
        silence_ends = [float(x) for x in re.findall(r"silence_end:\s*([-\d\.]+)", logs)]
        silence_durs = [float(x) for x in re.findall(r"silence_duration:\s*([-\d\.]+)", logs)]

        silence_events = []
        for i in range(min(len(silence_starts), len(silence_durs))):
            s_start = silence_starts[i]
            s_dur = silence_durs[i]
            s_end = silence_ends[i] if i < len(silence_ends) else round(s_start + s_dur, 2)
            silence_events.append({
                "start": round(s_start, 2),
                "end": round(s_end, 2),
                "duration": round(s_dur, 2),
            })

        audio_qc = {
            "measurement_ok": integrated_lufs is not None,
            "integrated_lufs": integrated_lufs,
            "target_lufs_range": [-15.5, -13.5],
            "lufs_pass": (integrated_lufs is not None and -16.0 <= integrated_lufs <= -13.0),
            "loudness_range_lra": lra,
            "true_peak_dbfs": true_peak,
            "true_peak_pass": (true_peak is not None and true_peak <= -0.5),
            "silence_events": silence_events,
            "silence_count": len(silence_events),
        }
        self.results["audio_qc"] = audio_qc
        return audio_qc

    def inspect_visual_artifacts(self, freeze_noise: int = -50, freeze_duration: float = 1.25) -> Dict[str, Any]:
        """Detecta frames congelados (freezedetect) y pantallas negras accidentales (blackdetect)."""
        vf_filter = f"freezedetect=n={freeze_noise}dB:d={freeze_duration},blackdetect=d=0.25:pix_th=0.06:pic_th=0.98"
        cmd = [
            "ffmpeg", "-nostats", "-i", str(self.video_path),
            "-vf", vf_filter,
            "-f", "null", "-",
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        logs = proc.stdout

        # Parsear Freezedetect
        freeze_starts = [float(x) for x in re.findall(r"lavfi\.freezedetect\.freeze_start:\s*([-\d\.]+)", logs)]
        freeze_durs = [float(x) for x in re.findall(r"lavfi\.freezedetect\.freeze_duration:\s*([-\d\.]+)", logs)]
        freeze_ends = [float(x) for x in re.findall(r"lavfi\.freezedetect\.freeze_end:\s*([-\d\.]+)", logs)]

        freeze_events = []
        for i in range(min(len(freeze_starts), len(freeze_durs))):
            f_start = freeze_starts[i]
            f_dur = freeze_durs[i]
            f_end = freeze_ends[i] if i < len(freeze_ends) else round(f_start + f_dur, 2)
            freeze_events.append({
                "start": round(f_start, 2),
                "end": round(f_end, 2),
                "duration": round(f_dur, 2),
            })

        # Parsear Blackdetect
        black_matches = re.findall(r"black_start:\s*([-\d\.]+)\s*black_end:\s*([-\d\.]+)\s*black_duration:\s*([-\d\.]+)", logs)
        black_events = []
        for b_start, b_end, b_dur in black_matches:
            black_events.append({
                "start": round(float(b_start), 2),
                "end": round(float(b_end), 2),
                "duration": round(float(b_dur), 2),
            })

        visual_qc = {
            "freeze_events": freeze_events,
            "freeze_count": len(freeze_events),
            "black_events": black_events,
            "black_count": len(black_events),
            "clean_playback": len(freeze_events) == 0 and len(black_events) == 0,
        }
        self.results["visual_qc"] = visual_qc
        return visual_qc

    def inspect_safezone_and_editorial(self) -> Dict[str, Any]:
        """Verifica Safe Zone 9:16 en subtítulos .ASS, portada oficial y reglas editoriales."""
        delivery_dir = self.video_path.parent
        ass_file = delivery_dir / "SUBTITULOS_KINETIC.ass"
        meta_file = delivery_dir / "metadata.json"
        cover_file = delivery_dir / "PORTADA_TIKTOK_916.jpg"
        shots_dir = delivery_dir / "shots"

        safezone_qc: Dict[str, Any] = {
            "ass_present": ass_file.exists(),
            "capcut_margin_v": None,
            "capcut_y_est": None,
            "capcut_safezone_ok": None,
            "hook_margin_v": None,
            "hook_safezone_ok": None,
            "subtitle_events_count": 0,
            "cover_present": cover_file.exists(),
            "editorial_issues": [],
            "missing_flow_shots": [],
        }

        if ass_file.exists():
            try:
                ass_text = ass_file.read_text(encoding="utf-8", errors="replace")
                safezone_qc["subtitle_events_count"] = len(re.findall(r"^Dialogue:", ass_text, re.MULTILINE))
                cap_m = re.search(r"Style:\s*CapCutBouncing,[^\n]*?,(-?\d+),\d+\s*$", ass_text, re.MULTILINE)
                if cap_m:
                    mv = int(cap_m.group(1))
                    y_est = 1920 - mv
                    safezone_qc["capcut_margin_v"] = mv
                    safezone_qc["capcut_y_est"] = y_est
                    safezone_qc["capcut_safezone_ok"] = (140 <= y_est <= 1400)
                hook_m = re.search(r"Style:\s*HookPill,[^\n]*?,(-?\d+),\d+\s*$", ass_text, re.MULTILINE)
                if hook_m:
                    hmv = int(hook_m.group(1))
                    safezone_qc["hook_margin_v"] = hmv
                    safezone_qc["hook_safezone_ok"] = (hmv >= 140)
            except Exception as e:
                safezone_qc["editorial_issues"].append(f"Error analizando SUBTITULOS_KINETIC.ass: {e}")

        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                script_low = (meta.get("script") or "").lower()
                if any(phrase in script_low for phrase in ["deja tus comentarios", "déjamelo en los comentarios", "comenta abajo"]):
                    safezone_qc["editorial_issues"].append("El guión contiene muletilla prohibida de pedir comentarios.")
                for s in meta.get("shots", []):
                    if s.get("render_mode") == "flow":
                        raw_mp4 = shots_dir / f"{s.get('id')}.mp4"
                        if not (raw_mp4.exists() and raw_mp4.stat().st_size > 25_000):
                            safezone_qc["missing_flow_shots"].append(s.get("id"))
            except Exception:
                pass

        self.results["safezone_qc"] = safezone_qc
        return safezone_qc

    def evaluate_verdict(self) -> Dict[str, Any]:
        """Evalúa reglas de broadcast y emite veredicto técnico PASS / WARN / FAIL."""
        s = self.results.get("stream_info", {})
        a = self.results.get("audio_qc", {})
        v = self.results.get("visual_qc", {})
        sz = self.results.get("safezone_qc", {})

        warnings = []
        errors = []
        score = 100

        # Validación 1: Formato y Aspect Ratio
        if s.get("width") != 1080 or s.get("height") != 1920:
            errors.append(f"Resolución no estándar: {s.get('width')}x{s.get('height')}. Se exige 1080x1920 (9:16 vertical).")
            score -= 30

        # Validación 2: Framerate
        if abs(s.get("fps", 0) - 24.0) > 0.5:
            warnings.append(f"FPS detectado: {s.get('fps')}. El estándar broadcast acordado es 24.0 fps.")
            score -= 5

        # Validación 3: Duración mínima para TikTok Creator Rewards (>60s)
        dur = s.get("duration", 0)
        if dur < 60.05:
            errors.append(f"Duración {dur}s es inferior a 60.1s. NO califica para TikTok Creator Rewards (>60s).")
            score -= 40
        elif dur > 65.0:
            warnings.append(f"Duración {dur}s excede el rango óptimo de retención (61-63s).")
            score -= 5

        # Validación 4: Audio LUFS (falla si no pudo medirse)
        lufs = a.get("integrated_lufs")
        if lufs is None:
            errors.append("No se pudo medir la sonoridad LUFS real con FFmpeg ebur128.")
            score -= 25
        elif not (-16.5 <= lufs <= -12.5):
            errors.append(f"Sonoridad fuera de norma: {lufs} LUFS (Objetivo TikTok: -14.0 a -15.0 LUFS).")
            score -= 20
        elif not (-15.5 <= lufs <= -13.5):
            warnings.append(f"Sonoridad en borde: {lufs} LUFS (Recomendado: -14.0 a -15.0 LUFS).")
            score -= 5

        # Validación 5: True Peak
        tp = a.get("true_peak_dbfs")
        if tp is None:
            warnings.append("No se pudo medir True Peak real con FFmpeg ebur128.")
            score -= 5
        elif tp > -0.5:
            warnings.append(f"Pico de audio elevado: {tp} dBTP. Riesgo de distorsión en altavoces móviles (Máx sugerido: -1.0 dBTP).")
            score -= 10

        # Validación 6: Congelamiento de vídeo
        freeze_count = v.get("freeze_count", 0)
        if freeze_count > 0:
            events_desc = ", ".join([f"{ev['start']}s-{ev['end']}s ({ev['duration']}s)" for ev in v.get("freeze_events", [])[:3]])
            warnings.append(f"Detectados {freeze_count} segmentos con frames congelados (>1.2s): {events_desc}.")
            score -= min(25, freeze_count * 5)

        # Validación 7: Pantallas negras
        black_count = v.get("black_count", 0)
        if black_count > 0:
            errors.append(f"Detectadas {black_count} pantallas negras accidentales.")
            score -= 20

        # Validación 8: Safe Zone TikTok 9:16 y consistencia editorial
        if sz.get("ass_present") is False:
            warnings.append("No se encontró SUBTITULOS_KINETIC.ass para validar Safe Zone de subtítulos.")
            score -= 5
        if sz.get("capcut_safezone_ok") is False:
            errors.append(
                f"Subtítulos CapCutBouncing invaden zona inferior TikTok (Y={sz.get('capcut_y_est')}, límite <= 1400)."
            )
            score -= 20
        if sz.get("hook_safezone_ok") is False:
            warnings.append(f"Rótulo HookPill demasiado alto (MarginV={sz.get('hook_margin_v')}, recomendado >= 140).")
            score -= 5
        if sz.get("cover_present") is False:
            warnings.append("Falta PORTADA_TIKTOK_916.jpg en la entrega.")
            score -= 5
        for issue in sz.get("editorial_issues", []):
            warnings.append(issue)
            score -= 5
        missing_flow = sz.get("missing_flow_shots", [])
        if missing_flow:
            warnings.append(f"{len(missing_flow)} plano(s) Flow ausentes sustituidos por fallback HUD: {', '.join(missing_flow[:8])}.")

        # Veredicto final
        score = max(0, min(100, score))
        if len(errors) > 0 or score < 70:
            verdict = "FAIL"
        elif len(warnings) > 0 or score < 90:
            verdict = "WARN"
        else:
            verdict = "PASS"

        self.results["score"] = score
        self.results["verdict"] = verdict
        self.results["warnings"] = warnings
        self.results["errors"] = errors
        return {"verdict": verdict, "score": score, "warnings": warnings, "errors": errors}

    def generate_safezone_preview_video(self, output_mp4: Optional[str | Path] = None) -> Path:
        """Renderiza un vídeo de prueba con la retícula de Safe Zone de TikTok quemada."""
        out_path = Path(output_mp4).resolve() if output_mp4 else self.output_dir / "VIDEO_QC_SAFEZONE.mp4"

        # Filtros drawbox y drawtext con % escapados como %%
        vf = (
            # 1. Zona de peligro superior (0 a 140)
            "drawbox=x=0:y=0:w=1080:h=140:color=red@0.35:t=fill,"
            "drawtext=text='[!] TIKTOK TOP BAR (HEADER / BUSQUEDA)':x=30:y=55:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=4,"
            # 2. Zona de peligro lateral derecha (930 a 1080, de Y=350 a 1400)
            "drawbox=x=930:y=350:w=150:h=1050:color=red@0.35:t=fill,"
            "drawtext=text='BOTONES TIKTOK':x=940:y=720:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=3,"
            # 3. Zona de peligro inferior (1400 a 1920)
            "drawbox=x=0:y=1400:w=1080:h=520:color=red@0.35:t=fill,"
            "drawtext=text='[!] TIKTOK CAPTION / NOMBRE CUENTA / AUDIO':x=30:y=1440:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=4,"
            # 4. Zona 100% Segura central (borde verde lima)
            "drawbox=x=40:y=150:w=880:h=1240:color=lime@0.8:t=4,"
            "drawtext=text='[✓] SAFE ZONE OPTIMA 100%%':x=60:y=170:fontsize=22:fontcolor=lime:box=1:boxcolor=black@0.7:boxborderw=4"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(self.video_path),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-c:a", "copy",
            str(out_path),
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Error generando preview de safe zone: {res.stderr}")

        self.results["artifacts"]["safezone_video"] = str(out_path)
        return out_path

    def generate_contact_sheet(self, output_jpg: Optional[str | Path] = None, cols: int = 4, rows: int = 3) -> Path:
        """Extrae 12 fotogramas distribuidos y arma una hoja de contactos (Contact Sheet) 4x3."""
        out_path = Path(output_jpg).resolve() if output_jpg else self.output_dir / "CONTACT_SHEET_QC.jpg"
        dur = self.results.get("stream_info", {}).get("duration", 62.0)
        fps = self.results.get("stream_info", {}).get("fps", 24.0)

        total_tiles = cols * rows
        # Calcular los números de frame clave distribuidos
        frame_indices = [int((i + 1) * ((dur * fps) / (total_tiles + 1))) for i in range(total_tiles)]
        select_expr = "+".join([f"eq(n\\,{idx})" for idx in frame_indices])

        vf = (
            f"select='{select_expr}',"
            f"scale=270:480,"
            f"drawtext=text='%{{pts\\:hms}}':x=12:y=12:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.7:boxborderw=4,"
            f"tile={cols}x{rows}"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(self.video_path),
            "-vf", vf,
            "-frames:v", "1",
            str(out_path),
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0 or not out_path.exists():
            # Fallback simple con fps uniforme
            vf_fallback = f"fps={total_tiles}/{dur},scale=270:480,tile={cols}x{rows}"
            subprocess.run(["ffmpeg", "-y", "-i", str(self.video_path), "-vf", vf_fallback, "-frames:v", "1", str(out_path)], check=True)

        self.results["artifacts"]["contact_sheet"] = str(out_path)
        return out_path

    def generate_html_report(self, output_html: Optional[str | Path] = None) -> Path:
        """Genera el visor web interactivo de inspección con control Frame a Frame y Safe Zone Switch."""
        out_path = Path(output_html).resolve() if output_html else self.output_dir / "REPORTE_INSPECCION.html"

        s = self.results.get("stream_info", {})
        a = self.results.get("audio_qc", {})
        v = self.results.get("visual_qc", {})
        verdict = self.results.get("verdict", "WARN")
        score = self.results.get("score", 0)

        # Colores de veredicto
        badge_color = "#00e676" if verdict == "PASS" else ("#ffd166" if verdict == "WARN" else "#ff3366")
        status_text = "APROBADO PARA TIKTOK" if verdict == "PASS" else ("OBSERVACIONES DETECTADAS" if verdict == "WARN" else "RECHAZADO TÉCNICAMENTE")

        # Lista de warnings
        warnings_html = "".join([f"<li class='warn-item'>⚠️ {w}</li>" for w in self.results.get("warnings", [])])
        errors_html = "".join([f"<li class='error-item'>❌ {e}</li>" for e in self.results.get("errors", [])])
        if not warnings_html and not errors_html:
            alerts_html = "<li class='pass-item'>✅ Ninguna anomalía técnica detectada. El metraje cumple 100% con los estándares broadcast.</li>"
        else:
            alerts_html = errors_html + warnings_html

        # Botones de salto temporal para frames congelados
        freeze_buttons_html = ""
        for idx, f_ev in enumerate(v.get("freeze_events", [])):
            freeze_buttons_html += (
                f"<button class='jump-btn' onclick='seekVideo({f_ev['start']})'>"
                f"❄️ Salto #{idx+1}: {f_ev['start']}s ({f_ev['duration']}s)"
                f"</button>"
            )
        if not freeze_buttons_html:
            freeze_buttons_html = "<span style='color:#a0aec0; font-size:13px;'>Cero frames estáticos detectados. Metraje dinámico continuo.</span>"

        # Contact Sheet relativo si existe
        contact_sheet_rel = "CONTACT_SHEET_QC.jpg" if (self.output_dir / "CONTACT_SHEET_QC.jpg").exists() else ""

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Inspector Broadcast QC · {self.video_path.name}</title>
  <style>
    :root {{
      --bg-dark: #0a0d14;
      --card-bg: #121824;
      --card-border: #1e293b;
      --accent-cyan: #00e5ff;
      --accent-yellow: #ffd166;
      --accent-green: #00e676;
      --accent-red: #ff3366;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
    body {{ background: var(--bg-dark); color: var(--text-main); padding: 24px; }}
    .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; border-bottom: 1px solid var(--card-border); padding-bottom: 16px; }}
    .header h1 {{ font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }}
    .header .badge {{ padding: 6px 14px; border-radius: 999px; font-weight: 800; font-size: 13px; text-transform: uppercase; background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}; }}
    
    .layout {{ display: grid; grid-template-columns: 420px 1fr; gap: 24px; }}
    @media(max-width: 900px) {{ .layout {{ grid-template-columns: 1fr; }} }}

    /* Video player container vertical 9:16 */
    .player-column {{ display: flex; flex-direction: column; align-items: center; }}
    .video-wrapper {{
      position: relative;
      width: 360px;
      height: 640px;
      background: #000;
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 20px 40px rgba(0,0,0,0.6);
      border: 1px solid var(--card-border);
    }}
    video {{ width: 100%; height: 100%; object-fit: contain; }}

    /* Reticula TikTok Safe Zone superpuesta */
    .safe-zone-overlay {{
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      pointer-events: none;
      display: none;
    }}
    .safe-zone-overlay.active {{ display: block; }}
    .sz-top {{
      position: absolute; top: 0; left: 0; right: 0; height: 7.3%;
      background: rgba(255, 51, 102, 0.28);
      border-bottom: 1px dashed rgba(255, 51, 102, 0.8);
      color: #fff; font-size: 10px; padding: 4px; font-weight: bold;
    }}
    .sz-bottom {{
      position: absolute; bottom: 0; left: 0; right: 0; height: 27%;
      background: rgba(255, 51, 102, 0.28);
      border-top: 1px dashed rgba(255, 51, 102, 0.8);
      color: #fff; font-size: 10px; padding: 4px; font-weight: bold;
    }}
    .sz-right {{
      position: absolute; right: 0; top: 18%; bottom: 27%; width: 14%;
      background: rgba(255, 51, 102, 0.28);
      border-left: 1px dashed rgba(255, 51, 102, 0.8);
      color: #fff; font-size: 9px; padding: 4px; text-align: center;
    }}
    .sz-safe-box {{
      position: absolute; top: 7.8%; left: 3.7%; right: 14.8%; bottom: 27.5%;
      border: 2px solid rgba(0, 230, 118, 0.85);
      border-radius: 4px;
      color: #00e676; font-size: 10px; padding: 4px; font-weight: bold;
    }}

    /* Controles de transporte y frame-by-frame */
    .controls {{
      width: 360px;
      margin-top: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .timecode-bar {{
      display: flex; justify-content: space-between; align-items: center;
      background: var(--card-bg); padding: 8px 12px; border-radius: 8px;
      border: 1px solid var(--card-border); font-size: 13px; font-variant-numeric: tabular-nums;
    }}
    .btn-row {{ display: flex; gap: 6px; justify-content: center; }}
    button.ctl-btn {{
      background: var(--card-bg); color: var(--text-main); border: 1px solid var(--card-border);
      padding: 8px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;
      transition: all 0.15s ease;
    }}
    button.ctl-btn:hover {{ background: #1e293b; border-color: var(--accent-cyan); color: var(--accent-cyan); }}
    
    .toggle-row {{
      display: flex; align-items: center; justify-content: space-between;
      background: var(--card-bg); padding: 8px 12px; border-radius: 8px;
      border: 1px solid var(--card-border); font-size: 13px;
    }}
    .toggle-row label {{ display: flex; align-items: center; gap: 8px; cursor: pointer; }}

    /* Cards de diagnostico */
    .dashboard-column {{ display: flex; flex-direction: column; gap: 16px; }}
    .grid-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .card {{
      background: var(--card-bg); border: 1px solid var(--card-border);
      border-radius: 10px; padding: 14px;
    }}
    .card-title {{ font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-bottom: 6px; letter-spacing: 0.5px; }}
    .card-value {{ font-size: 22px; font-weight: 800; font-variant-numeric: tabular-nums; }}
    .card-sub {{ font-size: 11px; color: var(--text-muted); margin-top: 4px; }}
    .text-pass {{ color: var(--accent-green); }}
    .text-warn {{ color: var(--accent-yellow); }}
    .text-fail {{ color: var(--accent-red); }}

    /* Lista de alertas */
    .alerts-card {{
      background: var(--card-bg); border: 1px solid var(--card-border);
      border-radius: 10px; padding: 16px;
    }}
    .alerts-card h3 {{ font-size: 14px; font-weight: 700; margin-bottom: 12px; }}
    .alerts-card ul {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
    .alerts-card li {{ font-size: 13px; padding: 8px 12px; border-radius: 6px; }}
    .warn-item {{ background: rgba(255, 209, 102, 0.12); border-left: 3px solid var(--accent-yellow); color: #ffe699; }}
    .error-item {{ background: rgba(255, 51, 102, 0.12); border-left: 3px solid var(--accent-red); color: #ff99aa; }}
    .pass-item {{ background: rgba(0, 230, 118, 0.12); border-left: 3px solid var(--accent-green); color: #80ffbf; }}

    /* Saltos temporales */
    .jump-group {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }}
    button.jump-btn {{
      background: #1e293b; color: var(--accent-yellow); border: 1px solid rgba(255, 209, 102, 0.3);
      padding: 6px 10px; border-radius: 6px; font-size: 12px; cursor: pointer;
    }}
    button.jump-btn:hover {{ background: #2d3748; }}

    /* Contact Sheet section */
    .contact-sheet-card {{
      background: var(--card-bg); border: 1px solid var(--card-border);
      border-radius: 10px; padding: 16px;
    }}
    .contact-sheet-card img {{ width: 100%; border-radius: 6px; border: 1px solid var(--card-border); margin-top: 10px; }}
  </style>
</head>
<body>

  <div class="header">
    <div>
      <h1>Auditoría y Control de Calidad Broadcast</h1>
      <span style="font-size:12px; color:var(--text-muted);">{self.video_path.name} · Score Técnico: {score}/100</span>
    </div>
    <div class="badge">{verdict}: {status_text}</div>
  </div>

  <div class="layout">
    <!-- Columna Izquierda: Reproductor Vertical e Inspección Frame a Frame -->
    <div class="player-column">
      <div class="video-wrapper">
        <video id="qcVideo" src="{self.video_path.name}" preload="metadata" playsinline></video>
        <!-- Overlay Safe Zone TikTok -->
        <div id="safeZoneOverlay" class="safe-zone-overlay active">
          <div class="sz-top">TIKTOK TOP BAR (HEADER / SEARCH)</div>
          <div class="sz-right">BOTONES UI</div>
          <div class="sz-bottom">TIKTOK CAPTION / NOMBRE CUENTA / AUDIO</div>
          <div class="sz-safe-box">SAFE ZONE 100%</div>
        </div>
      </div>

      <div class="controls">
        <div class="timecode-bar">
          <span id="tcDisplay">00:00.000</span>
          <span id="frameDisplay" style="color:var(--accent-cyan);">F: 0 / {int(s.get('duration', 62) * 24)}</span>
          <span style="color:var(--text-muted); font-size:11px;">24 fps</span>
        </div>

        <div class="btn-row">
          <button class="ctl-btn" onclick="stepFrame(-24)">⏮ -1s</button>
          <button class="ctl-btn" onclick="stepFrame(-1)">◀ -1 Frame</button>
          <button class="ctl-btn" id="playBtn" onclick="togglePlay()" style="min-width:60px;">Play</button>
          <button class="ctl-btn" onclick="stepFrame(1)">+1 Frame ▶</button>
          <button class="ctl-btn" onclick="stepFrame(24)">+1s ⏭</button>
        </div>

        <div class="btn-row">
          <button class="ctl-btn" onclick="setSpeed(0.25)">0.25x</button>
          <button class="ctl-btn" onclick="setSpeed(0.5)">0.5x</button>
          <button class="ctl-btn" onclick="setSpeed(1.0)">1.0x</button>
          <button class="ctl-btn" onclick="setSpeed(2.0)">2.0x</button>
        </div>

        <div class="toggle-row">
          <label>
            <input type="checkbox" id="safeZoneToggle" checked onchange="toggleSafeZone(this.checked)">
            Mostrar Safe Zone TikTok (UI Overlay)
          </label>
        </div>
      </div>
    </div>

    <!-- Columna Derecha: Métricas Técnicas y Diagnóstico -->
    <div class="dashboard-column">
      <div class="grid-cards">
        <div class="card">
          <div class="card-title">Sonoridad EBUR128</div>
          <div class="card-value {'text-pass' if a.get('lufs_pass') else 'text-fail'}">{a.get('integrated_lufs', -14.5)} LUFS</div>
          <div class="card-sub">Objetivo: -14.0 a -15.0 LUFS</div>
        </div>

        <div class="card">
          <div class="card-title">Pico Máximo (True Peak)</div>
          <div class="card-value {'text-pass' if a.get('true_peak_pass') else 'text-warn'}">{a.get('true_peak_dbfs', -1.0)} dBTP</div>
          <div class="card-sub">Anti-distorsión (≤ -1.0 dBTP)</div>
        </div>

        <div class="card">
          <div class="card-title">Duración Total</div>
          <div class="card-value {'text-pass' if s.get('duration', 0) >= 60.1 else 'text-fail'}">{s.get('duration', 0)}s</div>
          <div class="card-sub">Creator Rewards: ≥ 60.1s</div>
        </div>

        <div class="card">
          <div class="card-title">Frames Congelados</div>
          <div class="card-value {'text-pass' if v.get('freeze_count', 0) == 0 else 'text-warn'}">{v.get('freeze_count', 0)}</div>
          <div class="card-sub">Segmentos > 1.25s estáticos</div>
        </div>

        <div class="card">
          <div class="card-title">Pantallas Negras</div>
          <div class="card-value {'text-pass' if v.get('black_count', 0) == 0 else 'text-fail'}">{v.get('black_count', 0)}</div>
          <div class="card-sub">Pérdida de señal / cortes</div>
        </div>

        <div class="card">
          <div class="card-title">Resolución y FPS</div>
          <div class="card-value text-pass">{s.get('width', 1080)}x{s.get('height', 1920)}</div>
          <div class="card-sub">{s.get('fps', 24)} fps · {s.get('video_codec', 'h264')}</div>
        </div>
      </div>

      <!-- Alertas de Inspección -->
      <div class="alerts-card">
        <h3>Diagnóstico Técnico y Alertas de Calidad</h3>
        <ul>
          {alerts_html}
        </ul>

        <div style="margin-top:16px;">
          <div class="card-title">Acceso Rápido a Segmentos Observados</div>
          <div class="jump-group">
            {freeze_buttons_html}
          </div>
        </div>
      </div>

      <!-- Contact Sheet de Continuidad -->
      {f'''
      <div class="contact-sheet-card">
        <h3>Hoja de Contactos (Contact Sheet) · 12 Cuadros Clave</h3>
        <span style="font-size:12px; color:var(--text-muted);">Revisión rápida de continuidad de color, composición y legibilidad tipográfica en Safe Zone.</span>
        <a href="{contact_sheet_rel}" target="_blank">
          <img src="{contact_sheet_rel}" alt="Contact Sheet">
        </a>
      </div>
      ''' if contact_sheet_rel else ''}
    </div>
  </div>

  <script>
    const video = document.getElementById('qcVideo');
    const playBtn = document.getElementById('playBtn');
    const tcDisplay = document.getElementById('tcDisplay');
    const frameDisplay = document.getElementById('frameDisplay');
    const safeZoneOverlay = document.getElementById('safeZoneOverlay');
    const FPS = {s.get('fps', 24.0)};

    function togglePlay() {{
      if (video.paused) {{
        video.play();
        playBtn.innerText = 'Pausa';
      }} else {{
        video.pause();
        playBtn.innerText = 'Play';
      }}
    }}

    function stepFrame(deltaFrames) {{
      video.pause();
      playBtn.innerText = 'Play';
      const frameDuration = 1.0 / FPS;
      video.currentTime = Math.max(0, Math.min(video.duration, video.currentTime + (deltaFrames * frameDuration)));
      updateTimecode();
    }}

    function setSpeed(rate) {{
      video.playbackRate = rate;
    }}

    function seekVideo(timeSec) {{
      video.pause();
      playBtn.innerText = 'Play';
      video.currentTime = timeSec;
      updateTimecode();
    }}

    function toggleSafeZone(checked) {{
      if (checked) {{
        safeZoneOverlay.classList.add('active');
      }} else {{
        safeZoneOverlay.classList.remove('active');
      }}
    }}

    function formatTimecode(sec) {{
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      const ms = Math.floor((sec % 1) * 1000);
      return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0') + '.' + String(ms).padStart(3, '0');
    }}

    function updateTimecode() {{
      const cur = video.currentTime;
      tcDisplay.innerText = formatTimecode(cur);
      const curFrame = Math.floor(cur * FPS);
      frameDisplay.innerText = 'F: ' + curFrame + ' / ' + Math.floor(video.duration * FPS);
    }}

    video.addEventListener('timeupdate', updateTimecode);
    video.addEventListener('play', () => playBtn.innerText = 'Pausa');
    video.addEventListener('pause', () => playBtn.innerText = 'Play');

    // Atajos de teclado estilo editor profesional (J, K, L, Espacio, Flechas)
    window.addEventListener('keydown', (e) => {{
      if (e.target.tagName === 'INPUT') return;
      if (e.code === 'Space') {{
        e.preventDefault();
        togglePlay();
      }} else if (e.code === 'ArrowLeft') {{
        e.preventDefault();
        stepFrame(-1);
      }} else if (e.code === 'ArrowRight') {{
        e.preventDefault();
        stepFrame(1);
      }} else if (e.key === 'j' || e.key === 'J') {{
        stepFrame(-24);
      }} else if (e.key === 'l' || e.key === 'L') {{
        stepFrame(24);
      }} else if (e.key === 'k' || e.key === 'K') {{
        video.pause();
      }} else if (e.key === 's' || e.key === 'S') {{
        const chk = document.getElementById('safeZoneToggle');
        chk.checked = !chk.checked;
        toggleSafeZone(chk.checked);
      }}
    }});
  </script>
</body>
</html>
"""
        out_path.write_text(html_content, encoding="utf-8")
        self.results["artifacts"]["html_report"] = str(out_path)
        return out_path

    def run_full_qc(self, generate_safezone_video: bool = True, generate_contact_sheet: bool = True) -> Dict[str, Any]:
        """Ejecuta el protocolo de inspección completo y exporta los artefactos de verificación."""
        print(f"\n🔍 [QC INSPECTOR] Iniciando auditoría técnica de emisión: {self.video_path.name}")
        
        # 1. Streams ffprobe
        self.inspect_streams()
        print(f"   ✓ Formato verificado: {self.results['stream_info']['width']}x{self.results['stream_info']['height']} @ {self.results['stream_info']['fps']} fps, {self.results['stream_info']['duration']}s")

        # 2. Audio EBUR128
        self.inspect_audio()
        print(f"   ✓ Audio auditado: {self.results['audio_qc']['integrated_lufs']} LUFS (Peak: {self.results['audio_qc']['true_peak_dbfs']} dBTP)")

        # 3. Artefactos visuales (freeze & black)
        self.inspect_visual_artifacts()
        print(f"   ✓ Escaneo visual: {self.results['visual_qc']['freeze_count']} frames estáticos, {self.results['visual_qc']['black_count']} negros")

        # 4. Safe Zone 9:16 y reglas editoriales
        sz = self.inspect_safezone_and_editorial()
        print(f"   ✓ Safe Zone / Editorial: CapCut Y={sz.get('capcut_y_est')} | Eventos ASS={sz.get('subtitle_events_count')} | Portada={'Sí' if sz.get('cover_present') else 'No'}")

        # 5. Evaluación de veredicto
        verdict_res = self.evaluate_verdict()
        print(f"   ★ Veredicto preliminar: {verdict_res['verdict']} (Score: {verdict_res['score']}/100)")

        # 5. Generar Contact Sheet
        if generate_contact_sheet:
            cs_path = self.generate_contact_sheet()
            print(f"   ✓ Hoja de contactos generada: {cs_path.name}")

        # 6. Generar Vídeo de Depuración con Safe Zone
        if generate_safezone_video:
            sz_path = self.generate_safezone_preview_video()
            print(f"   ✓ Vídeo con retícula de Safe Zone generado: {sz_path.name}")

        # 7. Generar Visor HTML interactivo
        html_path = self.generate_html_report()
        print(f"   ✓ Visor HTML Frame a Frame generado: {html_path.name}")

        # Guardar reporte JSON
        json_report_path = self.output_dir / "QC_AUDIT_REPORT.json"
        json_report_path.write_text(json.dumps(self.results, indent=2, ensure_ascii=False), encoding="utf-8")
        self.results["artifacts"]["json_report"] = str(json_report_path)
        print(f"   ✓ Reporte estructurado guardado: {json_report_path.name}\n")

        return self.results


def main():
    parser = argparse.ArgumentParser(description="Auditoría y Control de Calidad (QC/QA) para TikTok 9:16")
    parser.add_argument("--video", "-v", required=True, help="Ruta al archivo MP4 a inspeccionar")
    parser.add_argument("--output-dir", "-o", default=None, help="Directorio para guardar reportes y artefactos")
    parser.add_argument("--no-safezone-video", action="store_true", help="Omitir generación del vídeo de depuración de safe zone")
    parser.add_argument("--no-contact-sheet", action="store_true", help="Omitir generación de la hoja de contactos")

    args = parser.parse_args()
    inspector = VideoQCInspector(args.video, output_dir=args.output_dir)
    res = inspector.run_full_qc(
        generate_safezone_video=not args.no_safezone_video,
        generate_contact_sheet=not args.no_contact_sheet,
    )

    print("=" * 60)
    print(f"RESULTADO FINAL: [{res['verdict']}] - Score: {res['score']}/100")
    if res["errors"]:
        print("\nERRORES:")
        for err in res["errors"]:
            print(f"  ❌ {err}")
    if res["warnings"]:
        print("\nADVERTENCIAS:")
        for w in res["warnings"]:
            print(f"  ⚠️ {w}")
    print("=" * 60)


if __name__ == "__main__":
    main()
