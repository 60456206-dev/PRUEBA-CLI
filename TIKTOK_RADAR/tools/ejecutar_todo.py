#!/usr/bin/env python3
"""
TIKTOK RADAR · Orquestador Maestro de Producción Autónoma Híbrida (1-Click / Cron)
Ejecuta de principio a fin las 3 fases en el servidor AWS:
  Fase 1 (`pipeline_autonomo.py`): Escaneo de noticias en vivo, guion monetizable (>60s),
                                   13 prompts con render_mode híbrido y síntesis de voz Gemini TTS.
  Fase 2 (`flow_generator.py`):    Inyección autónoma en Google Flow Modo Híbrido (8 planos cinematográficos,
                                   ahorrando créditos al omitir los 5 planos infográficos).
  Fase 3 (`ensamblador_final.py`): Edición algorítmica profesional (5 infografías vectoriales HUD FFmpeg
                                   + transiciones `xfade` + cámara dinámica + subtítulos Kinetic ASS + audio -14.8 LUFS).
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(__file__).parent))
from pipeline_autonomo import run_pipeline
from ensamblador_final import assemble_final_video, get_latest_delivery_dir


def _read_qc_summary(qc_path: Path) -> dict:
    """Lee QC_AUDIT_REPORT.json soportando el esquema actual y campos heredados."""
    if not qc_path.exists():
        return {"present": False, "verdict": "DESCONOCIDO", "score": 0, "errors": [], "failed": False}
    qc_data = json.loads(qc_path.read_text(encoding="utf-8"))
    verdict = str(qc_data.get("verdict", "DESCONOCIDO")).upper()
    score = qc_data.get("score", qc_data.get("overall_score", 0))
    errors = qc_data.get("errors")
    if not isinstance(errors, list):
        crit = qc_data.get("critical_failures", 0)
        errors = [f"critical_failure_{i + 1}" for i in range(int(crit or 0))]
    failed = verdict == "FAIL" or len(errors) > 0
    return {
        "present": True,
        "verdict": verdict,
        "score": score,
        "errors": errors,
        "failed": failed,
    }


def _dispatch_whatsapp_outcome(delivery_dir: Path, send_whatsapp_flag: bool, qc_summary: dict) -> None:
    """Envía la entrega final a WhatsApp o bloquea con alerta si QC marcó FAIL."""
    if not send_whatsapp_flag:
        print("[WHATSAPP] Envío automático omitido por bandera --no-whatsapp.")
        return
    try:
        from whatsapp_monitor import send_whatsapp as notify_whatsapp_text, send_whatsapp_delivery

        if qc_summary.get("failed"):
            errors = qc_summary.get("errors") or []
            err_preview = "; ".join(str(e) for e in errors[:3]) or "Revisa QC_AUDIT_REPORT.json"
            alert_msg = (
                f"⚠️ *BLOQUEO QC EN ENTREGA* ({delivery_dir.name})\n"
                f"Veredicto: *{qc_summary.get('verdict', 'FAIL')}* | Score: {qc_summary.get('score', 0)}/100\n"
                f"Errores críticos ({len(errors)}): {err_preview}\n"
                f"El vídeo no se envió automáticamente como listo para publicar."
            )
            print("[WHATSAPP] QC en FAIL: enviando alerta de bloqueo en lugar del paquete final...")
            notify_whatsapp_text(alert_msg)
            return

        print("[WHATSAPP] Enviando paquete completo a WhatsApp (Portada 9:16 + Vídeo + Hashtags)...")
        send_whatsapp_delivery(delivery_dir)
    except Exception as e:
        print(f"[WHATSAPP] Aviso al enviar entrega a WhatsApp: {e}")


def produce_single_genre(
    genre_key: Optional[str] = None,
    skip_flow: bool = False,
    custom_dir: Optional[str] = None,
    rank_index: int = 0,
    send_whatsapp: bool = True,
) -> Path:
    if custom_dir:
        delivery_dir = get_latest_delivery_dir(custom_dir)
        print(f"[FASE 1] Reutilizando paquete existente en: {delivery_dir}\n")
    else:
        print(f"[FASE 1] Ejecutando Radar de Noticias + Guión + Voz Gemini TTS ({genre_key or 'AUTOMÁTICO'} | Rank {rank_index})...")
        delivery_dir = run_pipeline(genre_key, rank_index=rank_index)
        print("")

    if not skip_flow:
        print("[FASE 2] Iniciando Inyector Autónomo Google Flow Modo Híbrido (8 Planos Flow + 5 Remotion/HUD)...")
        from flow_generator import run_flow_generator
        flow_ok = asyncio.run(run_flow_generator(delivery_dir))
        if not flow_ok:
            print(
                "\n⚠️ [AVISO FASE 2] Algunos planos no se pudieron descargar de Flow en esta tanda. "
                "El Ensamblador NLE completará automáticamente los planos faltantes con placas Remotion/HUD 3D.\n"
            )
    else:
        print("[FASE 2] Omitida por bandera --skip-flow.\n")

    print("[FASE 3] Ejecutando Ensamblador Algorítmico NLE (Remotion + Vector HUD + Transiciones + Subtítulos Kinetic + Audio -14.0 LUFS)...")
    final_mp4 = assemble_final_video(delivery_dir)
    print(f"✅ VÍDEO COMPLETADO: {final_mp4}\n")

    qc_path = delivery_dir / "QC_AUDIT_REPORT.json"
    qc_summary = {"present": False, "verdict": "DESCONOCIDO", "score": 0, "errors": [], "failed": False}
    if qc_path.exists():
        try:
            qc_summary = _read_qc_summary(qc_path)
            if qc_summary["failed"]:
                print(
                    f"⚠️ [QC ALERTA] Auditoría final: {qc_summary['verdict']} "
                    f"(Score: {qc_summary['score']}/100 | Fallos críticos: {len(qc_summary['errors'])}). "
                    f"Revisa {qc_path} antes de publicar."
                )
            else:
                print(f"✅ [QC] Auditoría final: {qc_summary['verdict']} (Score: {qc_summary['score']}/100)")
        except Exception as e:
            print(f"[QC] Aviso leyendo QC_AUDIT_REPORT.json: {e}")

    # Notificar y enviar a WhatsApp automáticamente (Portada 9:16 + Vídeo + Hashtags) o bloquear si QC falló
    _dispatch_whatsapp_outcome(delivery_dir, send_whatsapp, qc_summary)

    return final_mp4


def main():
    parser = argparse.ArgumentParser(description="Orquestador Maestro TikTok Radar 24/7")
    parser.add_argument("--skip-flow", action="store_true", help="Omitir generación en Flow y ensamblar directamente")
    parser.add_argument("--no-whatsapp", action="store_true", help="Omitir envío automático de paquete por WhatsApp")
    parser.add_argument("--dir", type=str, default=None, help="Usar carpeta de entrega existente en vez de crear nueva")
    parser.add_argument("--genre", type=str, default=None, choices=[
        "G1_AVIACION_CATASTROFES", "G2_CIBERATAQUES_HACKERS",
        "G3_IA_ROBOTICA", "G4_ESPACIO_CIENCIA",
        "G1_AVIACION",
        "G1", "G2", "G3", "G4", "AUTO",
        "SLOT_1", "SLOT_2", "TECH", "CIENCIA"
    ], help="Producir un género específico, slot diario o AUTO para radar dinámico")
    parser.add_argument("--rank", type=int, default=0, help="Posición de noticia ordenada (0 = más reciente / mayor score)")
    parser.add_argument("--count", type=int, default=1, help="Número de vídeos a producir en serie para el género (ej: 5)")
    parser.add_argument("--all", action="store_true", help="Producir los 4 géneros automáticamente en lote")
    args = parser.parse_args()

    print("======================================================================")
    print("🚀 INICIANDO FÁBRICA AUTÓNOMA DE NOTICIERO EXPLAINER (TIKTOK RADAR >60s)")
    print("======================================================================\n")

    genre_map = {
        "G1": "G1_AVIACION_CATASTROFES",
        "G2": "G2_CIBERATAQUES_HACKERS",
        "G3": "G3_IA_ROBOTICA",
        "G4": "G4_ESPACIO_CIENCIA",
        "SLOT_1": "SLOT_1",
        "SLOT_2": "SLOT_2",
        "TECH": "SLOT_2",
        "CIENCIA": "SLOT_2",
        "AUTO": None,
    }

    if args.all:
        genres = ["G1_AVIACION_CATASTROFES", "G2_CIBERATAQUES_HACKERS", "G3_IA_ROBOTICA", "G4_ESPACIO_CIENCIA"]
        completed = []
        for g in genres:
            print(f"======================================================================")
            print(f"🎬 PRODUCIENDO GÉNERO DIARIO: {g}")
            print(f"======================================================================\n")
            mp4 = produce_single_genre(g, skip_flow=args.skip_flow, send_whatsapp=not args.no_whatsapp)
            completed.append(mp4)
        print("======================================================================")
        print(f"🎉 LOS 4 VÍDEOS DIARIOS HAN SIDO COMPLETADOS:")
        for c in completed:
            print(f"  • {c}")
        print("======================================================================")
    elif args.count > 1 and args.genre:
        target_genre = genre_map.get(args.genre, args.genre)
        print(f"🎬 PRODUCIENDO SERIE DE {args.count} VÍDEOS PARA {target_genre} (CRONOLOGÍA + INFORMACIÓN + POLÉMICA)")
        completed = []
        for r in range(args.count):
            print(f"\n>>> INICIANDO VÍDEO #{r+1} (RANK {r}) <<<")
            mp4 = produce_single_genre(target_genre, skip_flow=args.skip_flow, rank_index=r, send_whatsapp=not args.no_whatsapp)
            completed.append(mp4)
        print("======================================================================")
        print(f"🎉 SERIE DE {args.count} VÍDEOS COMPLETADA CON ÉXITO:")
        for c in completed:
            print(f"  • {c}")
        print("======================================================================")
    else:
        target_genre = genre_map.get(args.genre, args.genre)
        final_mp4 = produce_single_genre(
            target_genre,
            skip_flow=args.skip_flow,
            custom_dir=args.dir,
            rank_index=args.rank,
            send_whatsapp=not args.no_whatsapp,
        )
        print("======================================================================")
        print(f"🎉 PRODUCCIÓN FINALIZADA CON ÉXITO: {final_mp4}")
        print("======================================================================")


if __name__ == "__main__":
    main()
