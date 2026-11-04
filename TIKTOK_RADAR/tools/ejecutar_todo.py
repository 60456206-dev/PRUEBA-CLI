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
import sys
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(__file__).parent))
from pipeline_autonomo import run_pipeline
from ensamblador_final import assemble_final_video, get_latest_delivery_dir


def produce_single_genre(genre_key: Optional[str] = None, skip_flow: bool = False, custom_dir: Optional[str] = None, rank_index: int = 0) -> Path:
    if custom_dir:
        delivery_dir = get_latest_delivery_dir(custom_dir)
        print(f"[FASE 1] Reutilizando paquete existente en: {delivery_dir}\n")
    else:
        print(f"[FASE 1] Ejecutando Radar de Noticias + Guión + Voz Gemini TTS ({genre_key or 'AUTOMÁTICO'} | Rank {rank_index})...")
        delivery_dir = run_pipeline(genre_key, rank_index=rank_index)
        print("")

    if not skip_flow:
        print("[FASE 2] Iniciando Inyector Autónomo Google Flow Modo Híbrido (8 Planos Flow + 5 FFmpeg HUD)...")
        from flow_generator import run_flow_generator
        flow_ok = asyncio.run(run_flow_generator(delivery_dir))
        if not flow_ok:
            print(
                "\n⚠️ [AVISO FASE 2] Algunos planos no se pudieron descargar de Flow en esta tanda. "
                "El Ensamblador NLE completará automáticamente los planos faltantes con placas tácticas HUD 3D.\n"
            )
    else:
        print("[FASE 2] Omitida por bandera --skip-flow.\n")

    print("[FASE 3] Ejecutando Ensamblador Algorítmico CapCut NLE (Transiciones + Subtítulos Kinetic + Audio -14.8 LUFS)...")
    final_mp4 = assemble_final_video(delivery_dir)
    print(f"✅ VÍDEO COMPLETADO: {final_mp4}\n")

    # Notificar y enviar a WhatsApp automáticamente (Portada 9:16 + Vídeo + Hashtags)
    try:
        from whatsapp_monitor import send_whatsapp_delivery
        print(f"[WHATSAPP] Enviando paquete completo a WhatsApp (Portada 9:16 + Vídeo + Hashtags)...")
        send_whatsapp_delivery(delivery_dir)
    except Exception as e:
        print(f"[WHATSAPP] Aviso al enviar entrega a WhatsApp: {e}")

    return final_mp4


def main():
    parser = argparse.ArgumentParser(description="Orquestador Maestro TikTok Radar 24/7")
    parser.add_argument("--skip-flow", action="store_true", help="Omitir generación en Flow y ensamblar directamente")
    parser.add_argument("--dir", type=str, default=None, help="Usar carpeta de entrega existente en vez de crear nueva")
    parser.add_argument("--genre", type=str, default=None, choices=[
        "G1_AVIACION_CATASTROFES", "G2_CIBERATAQUES_HACKERS",
        "G3_IA_ROBOTICA", "G4_ESPACIO_CIENCIA",
        "G1", "G2", "G3", "G4"
    ], help="Producir un género específico")
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
    }

    if args.all:
        genres = ["G1_AVIACION_CATASTROFES", "G2_CIBERATAQUES_HACKERS", "G3_IA_ROBOTICA", "G4_ESPACIO_CIENCIA"]
        completed = []
        for g in genres:
            print(f"======================================================================")
            print(f"🎬 PRODUCIENDO GÉNERO DIARIO: {g}")
            print(f"======================================================================\n")
            mp4 = produce_single_genre(g, skip_flow=args.skip_flow)
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
            mp4 = produce_single_genre(target_genre, skip_flow=args.skip_flow, rank_index=r)
            completed.append(mp4)
        print("======================================================================")
        print(f"🎉 SERIE DE {args.count} VÍDEOS COMPLETADA CON ÉXITO:")
        for c in completed:
            print(f"  • {c}")
        print("======================================================================")
    else:
        target_genre = genre_map.get(args.genre, args.genre)
        final_mp4 = produce_single_genre(target_genre, skip_flow=args.skip_flow, custom_dir=args.dir, rank_index=args.rank)
        print("======================================================================")
        print(f"🎉 PRODUCCIÓN FINALIZADA CON ÉXITO: {final_mp4}")
        print("======================================================================")


if __name__ == "__main__":
    main()
