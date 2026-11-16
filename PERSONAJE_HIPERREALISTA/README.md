# PERSONAJE_HIPERREALISTA · Candidato C + Motor Genjutsu Live-Action

Pipeline modular para producir vídeos 9:16 hiperrealistas (`1080×1920 @ 24fps`, `H.264 High CRF 16`, `-14.0 LUFS`) del **Candidato C** con transición **Genjutsu Live-Action**, preservando micro-poros de piel y continuidad biométrica.

## Requisitos verificados
- Sistema: `ffmpeg`, `ffprobe`, fuentes `Montserrat` (`/usr/share/fonts/truetype/montserrat/`).
- Python: `Pillow`, `numpy`, `pysubs2`, `edge-tts`.
- Variables de entorno: `GEMINI_API_KEY` para locución principal (`gemini-3.8-flash-tts`, voz `Puck`); si falta o falla, cambia automáticamente a `Edge-TTS`.

## Uso rápido

1. **Comprobar entorno y archivos maestros (sin generar vídeo):**
   ```bash
   python3 PERSONAJE_HIPERREALISTA/tools/pipeline_personaje.py --preflight-only
   ```

2. **Ejecutar prueba completa en local (`local_preview`: Voz + SFX Genjutsu + Subtítulos + `I2V_PACK` + QC):**
   ```bash
   python3 PERSONAJE_HIPERREALISTA/tools/pipeline_personaje.py \
     --script "Tu gancho científico aquí. [GENJUTSU] Tu remate dentro de la ilusión."
   ```

3. **Generar solo audio limpio, mezcla `-14 LUFS` y paquete listo para Google Flow / GPU Lip-Sync (`I2V_PACK/`):**
   ```bash
   python3 PERSONAJE_HIPERREALISTA/tools/pipeline_personaje.py --export-i2v-only
   ```

4. **Restaurar poros + inyectar fractura Genjutsu + muxear audio sobre un vídeo externo de Flow (`Veo 3.1`), `Kling`, `Hallo2` o `LivePortrait`:**
   ```bash
   python3 PERSONAJE_HIPERREALISTA/tools/pipeline_personaje.py \
     --input-video /ruta/al/clip_i2v.mp4 \
     --audio-file PERSONAJE_HIPERREALISTA/04_motor_video_voz/PRUEBA_01_GENJUTSU/VOZ_LIMPIA.wav \
     --cue-sec 5.88
   ```

5. **Correr la suite de pruebas automatizadas:**
   ```bash
   python3 -m unittest discover -s PERSONAJE_HIPERREALISTA/tests -v
   ```
