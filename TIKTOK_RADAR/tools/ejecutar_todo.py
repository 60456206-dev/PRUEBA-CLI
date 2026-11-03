#!/usr/bin/env python3
"""
TIKTOK RADAR · Orquestador Maestro de Producción Autónoma (1-Click / Cron)
Ejecuta de principio a fin las 3 fases en el servidor AWS:
  Fase 1 (`pipeline_autonomo.py`): Escaneo de noticias en vivo, guion monetizable (>60s),
                                   13 prompts 3D con fallback y síntesis de voz Edge-TTS.
  Fase 2 (`flow_generator.py`):    Inyección autónoma en Google Flow (Veo) con auto-curación,
                                   checkpointing y descarga de los 13 clips (SH01..SH13).
  Fase 3 (`ensamblador_final.py`): Edición algorítmica profesional (transiciones `xfade`,
                                   cámara dinámica, subtítulos Kinetic ASS y audio -14.8 LUFS).
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from pipeline_autonomo import run_pipeline
from ensamblador_final import assemble_final_video, get_latest_delivery_dir


def main():
    parser = argparse.ArgumentParser(description="Orquestador Maestro TikTok Radar 24/7")
    parser.add_argument("--skip-flow", action="store_true", help="Omitir generación en Flow y ensamblar directamente")
    parser.add_argument("--dir", type=str, default=None, help="Usar carpeta de entrega existente en vez de crear nueva")
    args = parser.parse_args()

    print("======================================================================")
    print("🚀 INICIANDO FÁBRICA AUTÓNOMA DE NOTICIERO 3D (TIKTOK RADAR >60s)")
    print("======================================================================\n")

    if args.dir:
        delivery_dir = get_latest_delivery_dir(args.dir)
        print(f"[FASE 1] Reutilizando paquete existente en: {delivery_dir}\n")
    else:
        print("[FASE 1] Ejecutando Radar de Noticias + Guión + Voz Edge-TTS...")
        delivery_dir = run_pipeline()
        print("")

    if not args.skip_flow:
        print("[FASE 2] Iniciando Inyector Autónomo de Google Flow (Self-Healing)...")
        from flow_generator import run_flow_generator
        flow_ok = asyncio.run(run_flow_generator(delivery_dir))
        if not flow_ok:
            print(
                "\n⚠️ [AVISO FASE 2] Algunos planos no se pudieron descargar de Flow en esta tanda. "
                "El Ensamblador NLE completará automáticamente los planos faltantes con placas tácticas 3D.\n"
            )
    else:
        print("[FASE 2] Omitida por bandera --skip-flow.\n")

    print("[FASE 3] Ejecutando Ensamblador Algorítmico NLE (Transiciones + Subtítulos Kinetic + Audio -14.8 LUFS)...")
    final_mp4 = assemble_final_video(delivery_dir)

    print("\n======================================================================")
    print(f"🎉 PRODUCCIÓN FINALIZADA CON ÉXITO: {final_mp4}")
    print("======================================================================")


if __name__ == "__main__":
    main()
