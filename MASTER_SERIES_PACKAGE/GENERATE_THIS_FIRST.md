# Generar la temporada, paso a paso

Primera prueba: EP01_SH01. Este checklist cubre los 48 planos. Primero leer START_HERE.md y FREE_VIDEO_TOOLS_CURRENT.md. Todos los archivos TXT de prompts contienen solo instrucciones pegables; ajustes y referencias están en tarjetas separadas. No subir hojas de contacto ni confundir referencia con fotograma inicial.

## EP01_SH01 · El abrigo · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/COAT_START.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP01_SH01_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Empty collar visible, coat still. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP01_SH01_V1.mp4`. Si cumple, copiar a `shots/EP01_SH01_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP01_SH01_FINAL.mp4 reference_frames/EP01_SH01_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP01/GENERATION_CARDS/EP01_SH01.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP01_SH02**.

## EP01_SH02 · El abrigo · 6 s útiles
1. Abrir Hailuo oficial y seleccionar Image-to-Video, modelo **MiniMax-Hailuo-2.3**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/INES_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/HAILUO/EP01_SH02_HAILUO.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Eyes fixed left; shoulders settle. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP01_SH02_V1.mp4`. Si cumple, copiar a `shots/EP01_SH02_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP01_SH02_FINAL.mp4 reference_frames/EP01_SH02_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Kling VIDEO 3.0**, tarjeta `EPISODES/EP01/GENERATION_CARDS/EP01_SH02.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP01_SH03**.

## EP01_SH03 · El abrigo · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/SALT_DROP.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP01_SH03_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: One wet patch; remaining salt intact. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP01_SH03_V1.mp4`. Si cumple, copiar a `shots/EP01_SH03_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP01_SH03_FINAL.mp4 reference_frames/EP01_SH03_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP01/GENERATION_CARDS/EP01_SH03.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP01_SH04**.

## EP01_SH04 · El abrigo · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/ALBA_DOOR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP01_SH04_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Chin lowered, eyes fixed right. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP01_SH04_V1.mp4`. Si cumple, copiar a `shots/EP01_SH04_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP01_SH04_FINAL.mp4 reference_frames/EP01_SH04_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP01/GENERATION_CARDS/EP01_SH04.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP01_SH05**.

## EP01_SH05 · El abrigo · 6 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/KEY_HAND.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/KEY_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP01_SH05_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Key hidden inside closed hand. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP01_SH05_V1.mp4`. Si cumple, copiar a `shots/EP01_SH05_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP01_SH05_FINAL.mp4 reference_frames/EP01_SH05_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP01/GENERATION_CARDS/EP01_SH05.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP01_SH06**.

## EP01_SH06 · El abrigo · 7 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **7 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/COAT_COLLAR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP01_SH06_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Hollow collar unchanged; no body appears. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP01_SH06_V1.mp4`. Si cumple, copiar a `shots/EP01_SH06_FINAL.mp4`; no borrar V1. Recortar a **7 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP01_SH06_FINAL.mp4 reference_frames/EP01_SH06_LASTFRAME.png --at 6.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP01/GENERATION_CARDS/EP01_SH06.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP01_SH07**.

## EP01_SH07 · El abrigo · 6 s útiles
1. Abrir Hailuo oficial y seleccionar Image-to-Video, modelo **MiniMax-Hailuo-2.3**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/INES_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/HAILUO/EP01_SH07_HAILUO.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Recognition without a smile. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP01_SH07_V1.mp4`. Si cumple, copiar a `shots/EP01_SH07_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP01_SH07_FINAL.mp4 reference_frames/EP01_SH07_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Kling VIDEO 3.0**, tarjeta `EPISODES/EP01/GENERATION_CARDS/EP01_SH07.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP01_SH08**.

## EP01_SH08 · El abrigo · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/COAT_START.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP01_SH08_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Coat at rest, no second breath. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP01_SH08_V1.mp4`. Si cumple, copiar a `shots/EP01_SH08_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP01_SH08_FINAL.mp4 reference_frames/EP01_SH08_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP01/GENERATION_CARDS/EP01_SH08.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP02_SH01**.

## EP02_SH01 · Una sola vez · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/SALT_USED.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP02_SH01_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Wet patch remains silent. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP02_SH01_V1.mp4`. Si cumple, copiar a `shots/EP02_SH01_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP02_SH01_FINAL.mp4 reference_frames/EP02_SH01_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP02/GENERATION_CARDS/EP02_SH01.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP02_SH02**.

## EP02_SH02 · Una sola vez · 7 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **7 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/INES_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP02_SH02_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Eyes lowered toward recorder. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP02_SH02_V1.mp4`. Si cumple, copiar a `shots/EP02_SH02_FINAL.mp4`; no borrar V1. Recortar a **7 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP02_SH02_FINAL.mp4 reference_frames/EP02_SH02_LASTFRAME.png --at 6.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP02/GENERATION_CARDS/EP02_SH02.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP02_SH03**.

## EP02_SH03 · Una sola vez · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/RECORDER.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/RECORDER_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP02_SH03_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Recorder running; red status light. Identidad/ropa/eje/luz; estado de sal S1; ningún miembro extra; movimiento único.
7. Guardar `shots/EP02_SH03_V1.mp4`. Si cumple, copiar a `shots/EP02_SH03_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP02_SH03_FINAL.mp4 reference_frames/EP02_SH03_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP02/GENERATION_CARDS/EP02_SH03.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP02_SH04**.

## EP02_SH04 · Una sola vez · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/SALT_DROP.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP02_SH04_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Two adjacent wet zones with dry salt beyond. Identidad/ropa/eje/luz; estado de sal S2; ningún miembro extra; movimiento único.
7. Guardar `shots/EP02_SH04_V1.mp4`. Si cumple, copiar a `shots/EP02_SH04_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP02_SH04_FINAL.mp4 reference_frames/EP02_SH04_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP02/GENERATION_CARDS/EP02_SH04.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP02_SH05**.

## EP02_SH05 · Una sola vez · 6 s útiles
1. Abrir Hailuo oficial y seleccionar Image-to-Video, modelo **MiniMax-Hailuo-2.3**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/ALBA_DOOR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/HAILUO/EP02_SH05_HAILUO.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Jaw tense, gaze right. Identidad/ropa/eje/luz; estado de sal S2; ningún miembro extra; movimiento único.
7. Guardar `shots/EP02_SH05_V1.mp4`. Si cumple, copiar a `shots/EP02_SH05_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP02_SH05_FINAL.mp4 reference_frames/EP02_SH05_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Kling VIDEO 3.0**, tarjeta `EPISODES/EP02/GENERATION_CARDS/EP02_SH05.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP02_SH06**.

## EP02_SH06 · Una sola vez · 7 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **7 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/RECORDER.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/RECORDER_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP02_SH06_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Playback status green. Identidad/ropa/eje/luz; estado de sal S2; ningún miembro extra; movimiento único.
7. Guardar `shots/EP02_SH06_V1.mp4`. Si cumple, copiar a `shots/EP02_SH06_FINAL.mp4`; no borrar V1. Recortar a **7 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP02_SH06_FINAL.mp4 reference_frames/EP02_SH06_LASTFRAME.png --at 6.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP02/GENERATION_CARDS/EP02_SH06.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP02_SH07**.

## EP02_SH07 · Una sola vez · 6 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/SALT_USED.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP02_SH07_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Dry salt in focus, used patch soft. Identidad/ropa/eje/luz; estado de sal S2; ningún miembro extra; movimiento único.
7. Guardar `shots/EP02_SH07_V1.mp4`. Si cumple, copiar a `shots/EP02_SH07_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP02_SH07_FINAL.mp4 reference_frames/EP02_SH07_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP02/GENERATION_CARDS/EP02_SH07.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP02_SH08**.

## EP02_SH08 · Una sola vez · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/REPORT_TOP.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/REPORT_MASTER.svg`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP02_SH08_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Report flat, upper section fully visible. Identidad/ropa/eje/luz; estado de sal S2; ningún miembro extra; movimiento único.
7. Guardar `shots/EP02_SH08_V1.mp4`. Si cumple, copiar a `shots/EP02_SH08_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP02_SH08_FINAL.mp4 reference_frames/EP02_SH08_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP02/GENERATION_CARDS/EP02_SH08.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP03_SH01**.

## EP03_SH01 · La llave · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/KEY_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/KEY_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP03_SH01_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Key teeth sharp. Identidad/ropa/eje/luz; estado de sal S2; ningún miembro extra; movimiento único.
7. Guardar `shots/EP03_SH01_V1.mp4`. Si cumple, copiar a `shots/EP03_SH01_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP03_SH01_FINAL.mp4 reference_frames/EP03_SH01_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP03/GENERATION_CARDS/EP03_SH01.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP03_SH02**.

## EP03_SH02 · La llave · 7 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **7 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/ALBA_DOOR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP03_SH02_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: She still occupies the doorway. Identidad/ropa/eje/luz; estado de sal S2; ningún miembro extra; movimiento único.
7. Guardar `shots/EP03_SH02_V1.mp4`. Si cumple, copiar a `shots/EP03_SH02_FINAL.mp4`; no borrar V1. Recortar a **7 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP03_SH02_FINAL.mp4 reference_frames/EP03_SH02_LASTFRAME.png --at 6.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP03/GENERATION_CARDS/EP03_SH02.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP03_SH03**.

## EP03_SH03 · La llave · 6 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/REPORT_TOP.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/REPORT_MASTER.svg`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP03_SH03_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Responsibility row centered; signatures not shown. Identidad/ropa/eje/luz; estado de sal S2; ningún miembro extra; movimiento único.
7. Guardar `shots/EP03_SH03_V1.mp4`. Si cumple, copiar a `shots/EP03_SH03_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP03_SH03_FINAL.mp4 reference_frames/EP03_SH03_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP03/GENERATION_CARDS/EP03_SH03.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP03_SH04**.

## EP03_SH04 · La llave · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/INES_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP03_SH04_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Eyes left, throat settled. Identidad/ropa/eje/luz; estado de sal S2; ningún miembro extra; movimiento único.
7. Guardar `shots/EP03_SH04_V1.mp4`. Si cumple, copiar a `shots/EP03_SH04_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP03_SH04_FINAL.mp4 reference_frames/EP03_SH04_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP03/GENERATION_CARDS/EP03_SH04.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP03_SH05**.

## EP03_SH05 · La llave · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/SALT_DROP.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP03_SH05_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Third wet zone, remaining central strip white. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP03_SH05_V1.mp4`. Si cumple, copiar a `shots/EP03_SH05_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP03_SH05_FINAL.mp4 reference_frames/EP03_SH05_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP03/GENERATION_CARDS/EP03_SH05.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP03_SH06**.

## EP03_SH06 · La llave · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/COAT_COLLAR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP03_SH06_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Lapel still, collar empty. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP03_SH06_V1.mp4`. Si cumple, copiar a `shots/EP03_SH06_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP03_SH06_FINAL.mp4 reference_frames/EP03_SH06_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP03/GENERATION_CARDS/EP03_SH06.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP03_SH07**.

## EP03_SH07 · La llave · 6 s útiles
1. Abrir Hailuo oficial y seleccionar Image-to-Video, modelo **MiniMax-Hailuo-2.3**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/ALBA_DOOR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/HAILUO/EP03_SH07_HAILUO.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Eyes open, gaze lowered. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP03_SH07_V1.mp4`. Si cumple, copiar a `shots/EP03_SH07_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP03_SH07_FINAL.mp4 reference_frames/EP03_SH07_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Kling VIDEO 3.0**, tarjeta `EPISODES/EP03/GENERATION_CARDS/EP03_SH07.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP03_SH08**.

## EP03_SH08 · La llave · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/TWO_SHOT.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`, `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP03_SH08_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Coat separates both women; door behind Alba. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP03_SH08_V1.mp4`. Si cumple, copiar a `shots/EP03_SH08_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP03_SH08_FINAL.mp4 reference_frames/EP03_SH08_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP03/GENERATION_CARDS/EP03_SH08.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP04_SH01**.

## EP04_SH01 · La otra hija · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/KEY_HAND.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/KEY_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP04_SH01_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Palm open; key visible. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP04_SH01_V1.mp4`. Si cumple, copiar a `shots/EP04_SH01_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP04_SH01_FINAL.mp4 reference_frames/EP04_SH01_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP04/GENERATION_CARDS/EP04_SH01.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP04_SH02**.

## EP04_SH02 · La otra hija · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/INES_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP04_SH02_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Eyes fixed left. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP04_SH02_V1.mp4`. Si cumple, copiar a `shots/EP04_SH02_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP04_SH02_FINAL.mp4 reference_frames/EP04_SH02_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP04/GENERATION_CARDS/EP04_SH02.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP04_SH03**.

## EP04_SH03 · La otra hija · 7 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **7 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/TWO_SHOT.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`, `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP04_SH03_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Alba touches door; Ines distant. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP04_SH03_V1.mp4`. Si cumple, copiar a `shots/EP04_SH03_FINAL.mp4`; no borrar V1. Recortar a **7 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP04_SH03_FINAL.mp4 reference_frames/EP04_SH03_LASTFRAME.png --at 6.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP04/GENERATION_CARDS/EP04_SH03.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP04_SH04**.

## EP04_SH04 · La otra hija · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/ALBA_DOOR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP04_SH04_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Chin slightly down, eyes wet but controlled. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP04_SH04_V1.mp4`. Si cumple, copiar a `shots/EP04_SH04_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP04_SH04_FINAL.mp4 reference_frames/EP04_SH04_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP04/GENERATION_CARDS/EP04_SH04.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP04_SH05**.

## EP04_SH05 · La otra hija · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/INES_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP04_SH05_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Gaze sustained. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP04_SH05_V1.mp4`. Si cumple, copiar a `shots/EP04_SH05_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP04_SH05_FINAL.mp4 reference_frames/EP04_SH05_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP04/GENERATION_CARDS/EP04_SH05.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP04_SH06**.

## EP04_SH06 · La otra hija · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/COAT_COLLAR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP04_SH06_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Empty collar unchanged. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP04_SH06_V1.mp4`. Si cumple, copiar a `shots/EP04_SH06_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP04_SH06_FINAL.mp4 reference_frames/EP04_SH06_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP04/GENERATION_CARDS/EP04_SH06.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP04_SH07**.

## EP04_SH07 · La otra hija · 6 s útiles
1. Abrir Hailuo oficial y seleccionar Image-to-Video, modelo **MiniMax-Hailuo-2.3**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/ALBA_DOOR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/HAILUO/EP04_SH07_HAILUO.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Gaze downward. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP04_SH07_V1.mp4`. Si cumple, copiar a `shots/EP04_SH07_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP04_SH07_FINAL.mp4 reference_frames/EP04_SH07_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Kling VIDEO 3.0**, tarjeta `EPISODES/EP04/GENERATION_CARDS/EP04_SH07.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP04_SH08**.

## EP04_SH08 · La otra hija · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/REPORT_FULL.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/REPORT_MASTER.svg`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP04_SH08_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Whole page visible. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP04_SH08_V1.mp4`. Si cumple, copiar a `shots/EP04_SH08_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP04_SH08_FINAL.mp4 reference_frames/EP04_SH08_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP04/GENERATION_CARDS/EP04_SH08.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP05_SH01**.

## EP05_SH01 · Mi firma · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/REPORT_FULL.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/REPORT_MASTER.svg`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP05_SH01_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Signature unobstructed. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP05_SH01_V1.mp4`. Si cumple, copiar a `shots/EP05_SH01_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP05_SH01_FINAL.mp4 reference_frames/EP05_SH01_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP05/GENERATION_CARDS/EP05_SH01.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP05_SH02**.

## EP05_SH02 · Mi firma · 7 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **7 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/ALBA_DOOR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP05_SH02_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Shoulders lowered. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP05_SH02_V1.mp4`. Si cumple, copiar a `shots/EP05_SH02_FINAL.mp4`; no borrar V1. Recortar a **7 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP05_SH02_FINAL.mp4 reference_frames/EP05_SH02_LASTFRAME.png --at 6.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP05/GENERATION_CARDS/EP05_SH02.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP05_SH03**.

## EP05_SH03 · Mi firma · 6 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/PHONE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/PHONE_SCREEN.svg`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP05_SH03_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Phone remains fixed. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP05_SH03_V1.mp4`. Si cumple, copiar a `shots/EP05_SH03_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP05_SH03_FINAL.mp4 reference_frames/EP05_SH03_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP05/GENERATION_CARDS/EP05_SH03.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP05_SH04**.

## EP05_SH04 · Mi firma · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/INES_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP05_SH04_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Gaze meets coat height. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP05_SH04_V1.mp4`. Si cumple, copiar a `shots/EP05_SH04_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP05_SH04_FINAL.mp4 reference_frames/EP05_SH04_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP05/GENERATION_CARDS/EP05_SH04.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP05_SH05**.

## EP05_SH05 · Mi firma · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/SALT_DROP.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP05_SH05_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Last salt strip beginning to dissolve. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP05_SH05_V1.mp4`. Si cumple, copiar a `shots/EP05_SH05_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP05_SH05_FINAL.mp4 reference_frames/EP05_SH05_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP05/GENERATION_CARDS/EP05_SH05.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP05_SH06**.

## EP05_SH06 · Mi firma · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/COAT_COLLAR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP05_SH06_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Collar motionless after pulse. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP05_SH06_V1.mp4`. Si cumple, copiar a `shots/EP05_SH06_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP05_SH06_FINAL.mp4 reference_frames/EP05_SH06_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP05/GENERATION_CARDS/EP05_SH06.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP05_SH07**.

## EP05_SH07 · Mi firma · 6 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/RECORDER.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/RECORDER_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP05_SH07_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Recording continues. Identidad/ropa/eje/luz; estado de sal S3; ningún miembro extra; movimiento único.
7. Guardar `shots/EP05_SH07_V1.mp4`. Si cumple, copiar a `shots/EP05_SH07_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP05_SH07_FINAL.mp4 reference_frames/EP05_SH07_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP05/GENERATION_CARDS/EP05_SH07.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP05_SH08**.

## EP05_SH08 · Mi firma · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/SALT_USED.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP05_SH08_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: No white crystals in this patch; wet wool still. Identidad/ropa/eje/luz; estado de sal S4; ningún miembro extra; movimiento único.
7. Guardar `shots/EP05_SH08_V1.mp4`. Si cumple, copiar a `shots/EP05_SH08_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP05_SH08_FINAL.mp4 reference_frames/EP05_SH08_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP05/GENERATION_CARDS/EP05_SH08.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP06_SH01**.

## EP06_SH01 · Los siete · 8 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **8 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `reference_frames/EP05_SH07_LASTFRAME.png`. Este archivo se obtiene del plano anterior indicado; no existe hasta aprobar ese vídeo. Si hay discontinuidad, usar SHOT_REFERENCES/RECORDER.png.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/RECORDER_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP06_SH01_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Recording light remains red. Identidad/ropa/eje/luz; estado de sal S4; ningún miembro extra; movimiento único.
7. Guardar `shots/EP06_SH01_V1.mp4`. Si cumple, copiar a `shots/EP06_SH01_FINAL.mp4`; no borrar V1. Recortar a **8 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP06_SH01_FINAL.mp4 reference_frames/EP06_SH01_LASTFRAME.png --at 7.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP06/GENERATION_CARDS/EP06_SH01.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP06_SH02**.

## EP06_SH02 · Los siete · 7 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **7 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/COAT_END.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP06_SH02_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Coat still and silent. Identidad/ropa/eje/luz; estado de sal S4; ningún miembro extra; movimiento único.
7. Guardar `shots/EP06_SH02_V1.mp4`. Si cumple, copiar a `shots/EP06_SH02_FINAL.mp4`; no borrar V1. Recortar a **7 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP06_SH02_FINAL.mp4 reference_frames/EP06_SH02_LASTFRAME.png --at 6.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP06/GENERATION_CARDS/EP06_SH02.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP06_SH03**.

## EP06_SH03 · Los siete · 6 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/PHONE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/PHONE_SCREEN.svg`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP06_SH03_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Screen unobstructed. Identidad/ropa/eje/luz; estado de sal S4; ningún miembro extra; movimiento único.
7. Guardar `shots/EP06_SH03_V1.mp4`. Si cumple, copiar a `shots/EP06_SH03_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP06_SH03_FINAL.mp4 reference_frames/EP06_SH03_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP06/GENERATION_CARDS/EP06_SH03.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP06_SH04**.

## EP06_SH04 · Los siete · 7 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **7 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/ALBA_DOOR.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/ALBA_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP06_SH04_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Door center clear; Alba beside it. Identidad/ropa/eje/luz; estado de sal S4; ningún miembro extra; movimiento único.
7. Guardar `shots/EP06_SH04_V1.mp4`. Si cumple, copiar a `shots/EP06_SH04_FINAL.mp4`; no borrar V1. Recortar a **7 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP06_SH04_FINAL.mp4 reference_frames/EP06_SH04_LASTFRAME.png --at 6.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP06/GENERATION_CARDS/EP06_SH04.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP06_SH05**.

## EP06_SH05 · Los siete · 5 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **5 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/PHONE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/PHONE_SCREEN.svg`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP06_SH05_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Screen steady for sent confirmation overlay. Identidad/ropa/eje/luz; estado de sal S4; ningún miembro extra; movimiento único.
7. Guardar `shots/EP06_SH05_V1.mp4`. Si cumple, copiar a `shots/EP06_SH05_FINAL.mp4`; no borrar V1. Recortar a **5 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP06_SH05_FINAL.mp4 reference_frames/EP06_SH05_LASTFRAME.png --at 4.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP06/GENERATION_CARDS/EP06_SH05.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP06_SH06**.

## EP06_SH06 · Los siete · 7 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **7 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/KEY_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/KEY_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP06_SH06_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Key alone on document. Identidad/ropa/eje/luz; estado de sal S4; ningún miembro extra; movimiento único.
7. Guardar `shots/EP06_SH06_V1.mp4`. Si cumple, copiar a `shots/EP06_SH06_FINAL.mp4`; no borrar V1. Recortar a **7 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP06_SH06_FINAL.mp4 reference_frames/EP06_SH06_LASTFRAME.png --at 6.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **MiniMax-Hailuo-2.3**, tarjeta `EPISODES/EP06/GENERATION_CARDS/EP06_SH06.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP06_SH07**.

## EP06_SH07 · Los siete · 6 s útiles
1. Abrir Hailuo oficial y seleccionar Image-to-Video, modelo **MiniMax-Hailuo-2.3**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **6 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/INES_TABLE.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: `CHARACTERS/INES_MASTER.png`. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `ninguno`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/HAILUO/EP06_SH07_HAILUO.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Steady eyes, no smile. Identidad/ropa/eje/luz; estado de sal S4; ningún miembro extra; movimiento único.
7. Guardar `shots/EP06_SH07_V1.mp4`. Si cumple, copiar a `shots/EP06_SH07_FINAL.mp4`; no borrar V1. Recortar a **6 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP06_SH07_FINAL.mp4 reference_frames/EP06_SH07_LASTFRAME.png --at 5.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Kling VIDEO 3.0**, tarjeta `EPISODES/EP06/GENERATION_CARDS/EP06_SH07.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **EP06_SH08**.

## EP06_SH08 · Los siete · 9 s útiles
1. Abrir Kling oficial y seleccionar Image-to-Video, modelo **Kling VIDEO 3.0**. Si falta acceso, usar respaldo de la tarjeta; no comprar automáticamente.
2. 9:16. Duración **9 s**. Resolución objetivo 1080 vertical; preview 720-class si es la disponible. Single-shot; audio desactivado.
3. Cargar como **primer fotograma**: `SHOT_REFERENCES/COAT_END.png`. El archivo ya pertenece al paquete.
4. Referencia de identidad opcional en Elements de Kling: ninguna. Entorno para comparar: `LOCATIONS/ARCHIVE_MASTER.png`. Prop: `PROPS/COAT_MASTER.png`. En I2V de una sola imagen cargar SOLO el primer fotograma, que ya contiene la composición.
5. Copiar TODO `VIDEO_PROMPTS/KLING/EP06_SH08_KLING.txt`. No copiar esta tarjeta al campo de prompt.
6. Generate. Verificar: Seven empty garments, room quiet. Identidad/ropa/eje/luz; estado de sal S4; ningún miembro extra; movimiento único.
7. Guardar `shots/EP06_SH08_V1.mp4`. Si cumple, copiar a `shots/EP06_SH08_FINAL.mp4`; no borrar V1. Recortar a **9 s** en la línea de tiempo.
8. Extraer último frame limpio con `python3 TOOLS/extract_last_frame.py shots/EP06_SH08_FINAL.mp4 reference_frames/EP06_SH08_LASTFRAME.png --at 8.958333`. Si último frame deforme, rechazar o elegir un punto anterior y actualizar continuidad.
9. Respaldo: **Wan2.2 TI2V-5B**, tarjeta `EPISODES/EP06/GENERATION_CARDS/EP06_SH08.md`; prompts alternativos ya escritos. Máximo de intentos según GENERATION_BUDGET.md.
10. NEXT: **montar EP06 y comprobar temporada completa**.
