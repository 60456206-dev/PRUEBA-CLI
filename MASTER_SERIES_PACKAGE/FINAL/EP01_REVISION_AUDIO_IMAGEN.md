# Revisión EP01 · 2026-10-30

Dictamen: AJUSTAR montaje y mezcla antes de oficializar. Conservar los planos existentes; no hace falta regenerar vídeos para resolver los principales problemas. Ningún plano ni audio ha sido oficializado por esta revisión.

## Alcance y evidencia

Revisado EP01_PICTURE_LOCK.mp4, guion, plan de edición, diseño sonoro, script de mezcla y WAV editados. Inspección visual de 51 muestras (1 por segundo) y 24 muestras adicionales de SH03 (8 por segundo entre 11–14 s). Esto permite evaluar composición y acción general, no garantiza ausencia de artefactos entre muestras. No se realizó escucha humana/perceptiva: actuación, pronunciación, timbre y naturalidad de efectos siguen pendientes. No confundir medidas técnicas con aprobación artística.

Vídeo original: H.264, 1080×1920, 24 fps, 1224 frames, 51 s, BT.709, SIN pista de audio. Decodificación completa correcta; detectores no señalaron tramos negros de ≥0,04 s ni congelaciones ≥1 s con los umbrales utilizados. No garantiza ausencia de microartefactos. SH01 procede de una fuente de menor resolución y queda más suave. No hay subtítulos visibles en las muestras.

Generado EP01_REVISION_AUDIO_V1.mp4: copia de la imagen sin recodificación, mezcla previa AAC 192 kb/s, imagen y audio de 51 s. Es una copia de revisión del estado actual, no una versión corregida ni final.

## Revisión plano por plano

| Plano / tiempo | Observación | Ajuste recomendado |
|---|---|---|
| SH01 / 0–5 | Abrigo vacío y oscilación visibles; la respiración del pecho es menos inequívoca que la intención del guion. La mezcla tiene roce sintético, pero X01 no se usa. | Sincronizar X01 con la expansión visible y ajustar el roce. Evitar aumentar demasiado el recorte por la menor definición de la fuente. |
| SH02 / 5–11 | Inés escucha la voz OFF de Alba, correspondencia correcta. Boca entreabierta alrededor de 9 s sin frase de Inés; limitación ya aceptada. | Acortar la cola de reacción o cubrir el gesto si parece que intenta hablar; no exigir sincronía labial de Alba, que está fuera de campo. |
| SH03 / 11–16 | La pipeta sustituye al pincel del guion antiguo. Se ve agua cayendo y goteando, no una sola absorción limpia. Primer desprendimiento/contacto aproximadamente 12,0–12,25 s; gotas adicionales cerca de 13–14 s. | SFX actual empieza en 12,0 s: está cerca del evento, pero requiere ajuste al fotograma y escucha. Preferir contacto húmedo discreto; evitar un único “plop” que sugiera una sola gota si se conserva todo el goteo. |
| SH04 / 16–24 | Alba escucha a Inés: cobertura OFF correcta. Expresión se suaviza hacia 18–19 s, menos alarmada de lo que sugiere la situación. Frase termina a 19,814 s. | Recortar parte de los ~4,19 s restantes tras la frase; no intentar solucionar la expresión solo aumentando contraste. |
| SH05 / 24–30 | Llave legible al inicio, mano se cierra hacia 25–26 s y sostiene el gesto. Roce actual comienza en 26 s. | Adelantar roce hacia el cierre y reducir reposo final. Este plano contribuye a la pausa larga antes de Mara. |
| SH06 / 30–37 | Cuello vacío con voz de Mara: asociación visual correcta. Frase 31–33,900 s; quedan ~3,10 s de plano después. | Dar a Mara una perspectiva muy cercana con tratamiento sutil de espacio/tela; conservar inteligibilidad. Recortar parte de la espera final. El script actual solo modifica nivel, no crea ese espacio acústico. |
| SH07 / 37–43 | Inés reacciona mientras Alba habla OFF: encaja. Orden termina a 39,063 s, quedan ~3,94 s de reacción. | Acortar después de establecer reconocimiento; conservar el gesto importante. |
| SH08 / 43–51 | Plano general del abrigo, no detalle de manga descrito en guion antiguo. Ambas frases de Inés funcionan OFF. “Es Mara” termina a 48,138 s; quedan ~2,86 s. | Conservar identificación y terminar tras una pausa más breve (propuesta 0,8–1,2 s). El encuadre actual es válido como cierre, aunque no cumple literalmente la cobertura de manga. |

## Correspondencia de voces

| Línea | Personaje | Inicio–fin del WAV editado en mezcla |
|---|---|---|
| L01 | Alba | 6,000–6,909 |
| L02 | Inés | 11,500–13,999 |
| L03 | Inés | 16,500–19,814 |
| L04 | Mara | 31,000–33,900 |
| L05 | Alba | 38,000–39,063 |
| L06 | Inés | 43,500–44,882 |
| L07 | Inés | 47,000–48,138 |

Todas caben en sus ventanas sin invadir el plano siguiente. L02 tiene ajuste de tempo +4,43 %. La pausa sin diálogo más larga entre frases es 19,814–31,000: 11,186 s, con ambiente/foley, no silencio digital. Puede servir al suspense, pero para el objetivo expresado de más ritmo conviene acortarla.

## Mezcla y pendientes concretos

- Mezcla PCM medida: -23,4 LUFS integrados, rango 13,2 LU y pico verdadero -6,5 dBFS. No está saturada; hay margen, pero el nivel y la dinámica requieren ajuste para una escucha móvil cómoda. Propuesta creativa inicial: acercarse a -16 LUFS y techo de -1 dBTP, verificando el resultado con escucha; no es una obligación de plataforma.
- RMS de clips editados: L01 -28,8; L02 -22,0; L03 -23,9; L04 -28,7; L05 -23,2; L06 -28,6; L07 -28,9 dBFS. Diferencia de ~6,9 dB: normalizar por pico no igualó la intensidad media. RMS no equivale a sonoridad percibida. Ajustar ganancia por frase y compresión suave preservando intención; no subir todo de forma ciega.
- ROOM/FOLEY/SFX son síntesis aproximada: no se validó que suenen a sala, lana y agua de forma convincente. Revisarlos con auriculares y altavoz móvil, cambiarlos o bajar nivel si llaman la atención por artificialidad.
- X01/X02 existen pero no forman parte de la mezcla. Incorporar X01 para la respiración del inicio. Recomiendo mantener por ahora la primera frase de Mara en SH06: adelantar X02 cambiaría la revelación y requiere una decisión de montaje.
- Añadir subtítulos sincronizados después de fijar duraciones; diseñarlos sin tapar llave, gota o rostros. Son una mejora de comprensión, no un fallo de codificación.
- Ajuste leve de contraste/localización de atención por plano, preservando detalle del abrigo oscuro y continuidad. No aplicar un aumento global intenso: la imagen ya es legible, el problema principal es ritmo y contexto sonoro.
- Al acortar planos, reconstruir tiempos de TODOS los stems/subtítulos. No pegar el WAV actual de 51 s a un montaje más corto.
- EP01_EDIT_PLAN.md apunta a nombres _FINAL que no son los archivos usados. El script de render sí usa las versiones existentes elegidas. Actualizar esa documentación cuando se cierre el montaje para evitar futuras exportaciones con rutas erróneas.

## Orden propuesto

1. Escuchar y aceptar/corregir voces existentes dentro del límite de intentos; no regenerar automáticamente.
2. Editar pausas de SH04–SH08 y cola de SH02, conservando acciones y revelaciones.
3. Reubicar diálogos y foley; integrar respiración X01; ajustar sonoridad y perspectiva de Mara.
4. Subtítulos, igualación de imagen, exportación de revisión con audio y control final.

Recomendación preferida: AJUSTAR con los materiales actuales. La continuidad básica y las voces OFF funcionan; faltan escucha, mezcla final y un ritmo más intencional. No recomendar oficializar todavía ni regenerar todos los planos.
