# Prompts para Google Flow

Versiones adaptadas de los prompts de vídeo existentes: misma acción, cámara, identidad y continuidad. Los TXT contienen únicamente texto para pegar. No se han probado mediante generaciones en Flow.

## Uso

1. Abre https://labs.google/fx/tools/flow y selecciona Frames to Video / Fotogramas a vídeo, con imagen inicial. Selecciona 9:16.
2. Carga únicamente la imagen inicial indicada en la tabla. Una ruta marcada pendiente todavía no está disponible en este checkout: crea o recupera esa imagen antes de generar.
3. Elige un modelo que admita imagen inicial y formato vertical. Veo 3.1 Lite/Fast permite 4, 6 u 8 segundos según la documentación consultada; comprueba las opciones y el coste en tu cuenta.
4. Copia todo el TXT del plano. Selecciona la duración de generación de la tabla; el prompt sitúa el final de la acción dentro del tiempo útil y deja el sobrante en reposo.
5. Para EP06_SH08, de 9 segundos útiles, usa un modelo con imagen inicial y 10 segundos (por ejemplo, Omni si está disponible). Si solo tienes 8 segundos, necesitarás una extensión y revisar su unión; no aceleres ni recortes la acción para fingir 9 segundos.
6. Si el modelo genera audio, siléncialo en montaje: el proyecto lleva diálogo, ambiente y foley por separado. El prompt pide ausencia de diálogo y música, pero eso no garantiza una pista muda.
7. Revisa identidad, manos, eje, luz, objetos, estado de sal y fotograma final. Recorta al tiempo útil, conserva el nombre de plano y registra qué modelo usaste. Resolución y duración se seleccionan en la interfaz; el texto no las garantiza.

## Planos e imágenes

Las rutas de imagen parten de MASTER_SERIES_PACKAGE. Estado de archivos comprobado el 2026-10-17.

| Plano / prompt | Imagen inicial | Estado | Generar | Usar en montaje |
|---|---|---|---|---|
| [EP01_SH01](EP01_SH01_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/COAT_START.png` | Disponible | 6 s | 5 s |
| [EP01_SH02](EP01_SH02_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/INES_TABLE.png` | Disponible | 6 s | 6 s |
| [EP01_SH03](EP01_SH03_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/SALT_DROP.png` | Pendiente | 6 s | 5 s |
| [EP01_SH04](EP01_SH04_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/ALBA_DOOR.png` | Disponible | 8 s | 8 s |
| [EP01_SH05](EP01_SH05_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/KEY_HAND.png` | Pendiente | 6 s | 6 s |
| [EP01_SH06](EP01_SH06_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/COAT_COLLAR.png` | Pendiente | 8 s | 7 s |
| [EP01_SH07](EP01_SH07_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/INES_TABLE.png` | Disponible | 6 s | 6 s |
| [EP01_SH08](EP01_SH08_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/COAT_START.png` | Disponible | 8 s | 8 s |
| [EP02_SH01](EP02_SH01_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/SALT_USED.png` | Pendiente | 6 s | 5 s |
| [EP02_SH02](EP02_SH02_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/INES_TABLE.png` | Disponible | 8 s | 7 s |
| [EP02_SH03](EP02_SH03_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/RECORDER.png` | Pendiente | 6 s | 5 s |
| [EP02_SH04](EP02_SH04_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/SALT_DROP.png` | Pendiente | 8 s | 8 s |
| [EP02_SH05](EP02_SH05_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/ALBA_DOOR.png` | Disponible | 6 s | 6 s |
| [EP02_SH06](EP02_SH06_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/RECORDER.png` | Pendiente | 8 s | 7 s |
| [EP02_SH07](EP02_SH07_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/SALT_USED.png` | Pendiente | 6 s | 6 s |
| [EP02_SH08](EP02_SH08_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/REPORT_TOP.png` | Pendiente | 8 s | 8 s |
| [EP03_SH01](EP03_SH01_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/KEY_TABLE.png` | Pendiente | 6 s | 5 s |
| [EP03_SH02](EP03_SH02_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/ALBA_DOOR.png` | Disponible | 8 s | 7 s |
| [EP03_SH03](EP03_SH03_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/REPORT_TOP.png` | Pendiente | 6 s | 6 s |
| [EP03_SH04](EP03_SH04_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/INES_TABLE.png` | Disponible | 8 s | 8 s |
| [EP03_SH05](EP03_SH05_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/SALT_DROP.png` | Pendiente | 6 s | 5 s |
| [EP03_SH06](EP03_SH06_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/COAT_COLLAR.png` | Pendiente | 8 s | 8 s |
| [EP03_SH07](EP03_SH07_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/ALBA_DOOR.png` | Disponible | 6 s | 6 s |
| [EP03_SH08](EP03_SH08_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/TWO_SHOT.png` | Pendiente | 8 s | 8 s |
| [EP04_SH01](EP04_SH01_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/KEY_HAND.png` | Pendiente | 6 s | 5 s |
| [EP04_SH02](EP04_SH02_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/INES_TABLE.png` | Disponible | 8 s | 8 s |
| [EP04_SH03](EP04_SH03_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/TWO_SHOT.png` | Pendiente | 8 s | 7 s |
| [EP04_SH04](EP04_SH04_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/ALBA_DOOR.png` | Disponible | 8 s | 8 s |
| [EP04_SH05](EP04_SH05_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/INES_TABLE.png` | Disponible | 6 s | 5 s |
| [EP04_SH06](EP04_SH06_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/COAT_COLLAR.png` | Pendiente | 8 s | 8 s |
| [EP04_SH07](EP04_SH07_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/ALBA_DOOR.png` | Disponible | 6 s | 6 s |
| [EP04_SH08](EP04_SH08_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/REPORT_FULL.png` | Pendiente | 8 s | 8 s |
| [EP05_SH01](EP05_SH01_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/REPORT_FULL.png` | Pendiente | 6 s | 5 s |
| [EP05_SH02](EP05_SH02_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/ALBA_DOOR.png` | Disponible | 8 s | 7 s |
| [EP05_SH03](EP05_SH03_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/PHONE.png` | Pendiente | 6 s | 6 s |
| [EP05_SH04](EP05_SH04_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/INES_TABLE.png` | Disponible | 8 s | 8 s |
| [EP05_SH05](EP05_SH05_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/SALT_DROP.png` | Pendiente | 6 s | 5 s |
| [EP05_SH06](EP05_SH06_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/COAT_COLLAR.png` | Pendiente | 8 s | 8 s |
| [EP05_SH07](EP05_SH07_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/RECORDER.png` | Pendiente | 6 s | 6 s |
| [EP05_SH08](EP05_SH08_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/SALT_USED.png` | Pendiente | 8 s | 8 s |
| [EP06_SH01](EP06_SH01_GOOGLE_FLOW.txt) | `reference_frames/EP05_SH07_LASTFRAME.png` | Pendiente | 8 s | 8 s |
| [EP06_SH02](EP06_SH02_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/COAT_END.png` | Pendiente | 8 s | 7 s |
| [EP06_SH03](EP06_SH03_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/PHONE.png` | Pendiente | 6 s | 6 s |
| [EP06_SH04](EP06_SH04_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/ALBA_DOOR.png` | Disponible | 8 s | 7 s |
| [EP06_SH05](EP06_SH05_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/PHONE.png` | Pendiente | 6 s | 5 s |
| [EP06_SH06](EP06_SH06_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/KEY_TABLE.png` | Pendiente | 8 s | 7 s |
| [EP06_SH07](EP06_SH07_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/INES_TABLE.png` | Disponible | 6 s | 6 s |
| [EP06_SH08](EP06_SH08_GOOGLE_FLOW.txt) | `SHOT_REFERENCES/COAT_END.png` | Pendiente | 10 s | 9 s |

## Documentación oficial

Funciones y modelos (consultado el 2026-10-17): https://support.google.com/flow/answer/16352836?hl=en
Créditos y duraciones: https://support.google.com/flow/answer/16526234?hl=es
Las funciones disponibles y los costes pueden cambiar. Verifica el selector antes de generar.
