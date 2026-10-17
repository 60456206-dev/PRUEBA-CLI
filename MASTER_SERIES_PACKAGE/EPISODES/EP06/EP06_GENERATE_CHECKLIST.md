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
