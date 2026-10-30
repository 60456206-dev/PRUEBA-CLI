# Montaje activo · EP01 V2 · 35,25 s

Ajustes autorizados 2026-10-30. Generado, pendiente de aceptación. 1080×1920, 24 fps, cortes secos, audio y subtítulos incorporados. Exportación: `FINAL/EP01_AJUSTADO_V2.mp4`. Reproducible con `python3 tools/ajustar_ep01.py` desde MASTER_SERIES_PACKAGE (numpy y ffmpeg). El script reutiliza el picture lock de 51 s como fuente de imagen; correspondencia con originales abajo.

|Plano|Entrada–salida montaje (s)|Archivo fuente elegido|Tramo local (s)|
|---|---|---|---|
|SH01|0.00–5.00|shots/EP01_SH01_PIXVERSE_SIN_MARCA_PREVIEW.mp4|0–5.00|
|SH02|5.00–8.50|shots/EP01_SH02_FLOW_SIN_MARCA_6S.mp4|0–3.50|
|SH03|8.50–12.50|shots/EP01_SH03_FLOW_5S.mp4|0–4.00|
|SH04|12.50–17.50|shots/EP01_SH04_FLOW_8S.mp4|0–5.00|
|SH05|17.50–21.00|shots/EP01_SH05_FLOW_6S.mp4|0–3.50|
|SH06|21.00–25.75|shots/EP01_SH06_FLOW_7S.mp4|0–4.75|
|SH07|25.75–29.00|shots/EP01_SH07_FLOW_6S.mp4|0–3.25|
|SH08|29.00–35.25|shots/EP01_SH08_FLOW_8S.mp4|0–6.25|

Audio, tiempos de frases y tramos del picture lock: `AUDIO/EP01/AJUSTE_V2/montaje.json`. Subtítulos: `FINAL/EP01_AJUSTADO_V2.srt`. El guion y AUDIO_TIMELINE originales conservan los tiempos de 51 s como preproducción; usar este plan y manifiesto para V2. No se adelantó la frase de Mara al inicio, solo su respiración X01.

## Capa musical prevista

Antes de la próxima mezcla, consultar [MUSICA_FONDO](../../AUDIO/EP01/MUSICA_FONDO/README.md): cue principal 12,500–21,500 s y recurso opcional 31,000–32,500 s, ambos con salidas completas antes del diálogo revelador. Solo documentación preparada; V2 permanece sin música. No cambiar duración ni voces para acomodar una composición.

## Archivo histórico: montaje de 51 s

Las rutas `_FINAL` de la tabla histórica eran nombres previstos; los archivos elegidos reales son los de la tabla activa anterior. El script antiguo contiene esas rutas reales.

# Montaje

Proyecto 1080×1920, 24fps. Sin speed ramp. Audio separado. Cortes al cambio de información; ninguna transición añade duración. Las marcas L CUT significan cola de ambiente, no repetición de diálogo.

|Entrada|Salida|Archivo|Selección fuente|Corte entrada|Motivo|
|---|---|---|---|---|---|
|00:00.000|00:05.000|shots/EP01_SH01_FINAL.mp4|0–5 s|CUT|Hacer visible la anomalía antes del diálogo.|
|00:05.000|00:11.000|shots/EP01_SH02_FINAL.mp4|0–6 s|CUT|Anclar fenómeno a una persona.|
|00:11.000|00:16.000|shots/EP01_SH03_FINAL.mp4|0–5 s|CUT|Explicar causa física mínima.|
|00:16.000|00:24.000|shots/EP01_SH04_FINAL.mp4|0–8 s|CUT|Mostrar reconocimiento anterior al de Inés.|
|00:24.000|00:30.000|shots/EP01_SH05_FINAL.mp4|0–6 s|CUT|Sembrar llave mediante ironía dramática.|
|00:30.000|00:37.000|shots/EP01_SH06_FINAL.mp4|0–7 s|CUT|Entregar prueba acústica.|
|00:37.000|00:43.000|shots/EP01_SH07_FINAL.mp4|0–6 s|CUT|Reconocimiento sin diálogo explicativo.|
|00:43.000|00:51.000|shots/EP01_SH08_FINAL.mp4|0–8 s|CUT|Identificar relación y abrir esperanza peligrosa.|