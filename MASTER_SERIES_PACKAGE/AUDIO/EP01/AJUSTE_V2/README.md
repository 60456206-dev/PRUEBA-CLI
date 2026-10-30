# EP01 · mezcla y montaje V2

Montaje de 35,25 s, 846 fotogramas a 24 fps. Siete frases existentes conservadas; sin generaciones nuevas de voz o vídeo. Respiración X01 en 0,9 s; X02 no usado para mantener la revelación en SH06.

Los cuatro stems están alineados al montaje V2 y son anteriores al procesamiento del máster. Su suma no equivale al WAV masterizado porque este incluye normalización/limitación. No usar los stems antiguos de 51 s con V2. `L01.wav`–`L07.wav` son frases procesadas antes del mastering.

Procesamiento: filtro de graves, reducción de agudos, compresión suave y ajuste RMS por frase con límite de pico; Mara ~2 dB más baja y reflexiones discretas de 27/53 ms. Foley existente recolocado, gota filtrada con dos escurrimientos secundarios de menor nivel, ambiente continuo y fundido de salida de 150 ms. Música omitida.

La normalización se dirige a -16 LUFS y deja margen de pico; valores finales comprobados en el informe de FINAL. Subtítulos quemados y SRT independiente. Reproducibilidad: `tools/ajustar_ep01.py`, requiere numpy y ffmpeg con libass. Usa exclusivamente archivos locales. Manifiesto: `montaje.json`.

Revisado técnicamente y visualmente por muestras; pendiente de escucha y aceptación. El intento de análisis perceptivo por API agotó 90 s sin respuesta, no constituye validación de voces. La síntesis de efectos y los matices de actuación conservan esta limitación.
