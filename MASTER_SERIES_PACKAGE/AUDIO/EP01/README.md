# Audio EP01

Material generado, pendiente de escucha y aceptación del usuario. No oficializado.

- `TAKES/`: originales Gemini 3.8 Flash TTS; Gacrux (Alba), Kore (Inés), Vindemiatrix (Mara). Máximo dos solicitudes por línea. L05 requirió segunda solicitud por límite por minuto, sin audio producido en la primera.
- `EDITADOS/`: WAV mono PCM 16 bits, 48 kHz, silencios exteriores reducidos, margen conservado y fundidos de 5 ms. Ajuste de tempo máximo 10 % cuando la ventana lo requiere, sin cambiar tono. Originales conservados.
- `STEMS/`: DIALOGUE, ROOM, FOLEY y SFX, todos de 51 s. Ambiente, tela y gota sintetizados localmente, sin muestras externas. No se añadió música: se prioriza el silencio y la inteligibilidad.
- `EP01_MEZCLA_PREVIA.wav`: mezcla conforme a la timeline original, no al arranque en frío propuesto. Los extras X01/X02 se entregan separados para decidir ese montaje.
- `generacion.json`: solicitudes y resultados; `revision_tecnica.json`: duración, pico, saturación y ajuste temporal.

La revisión es técnica, no una aprobación de actuación ni una garantía de transcripción exacta. La revisión automática con modelo de escucha devolvió error HTTP y no estuvo disponible. Escuchar las voces, particularmente la edad de Alba, la respiración de Mara y la continuidad de timbre antes de aceptar. Los efectos son aproximaciones sintéticas, no foley grabado en el escenario.

Reproducibilidad: `python3 generar_voces.py` usa GEMINI_API_KEY del entorno y omite líneas ya generadas. No reintenta automáticamente errores; nunca más de dos solicitudes por línea. `python3 preparar_mezcla.py` requiere numpy y ffmpeg. No ejecutar generación para revisar archivos existentes.

Implementación TTS basada en https://ai.google.dev/gemini-api/docs/generate-content/speech-generation .
