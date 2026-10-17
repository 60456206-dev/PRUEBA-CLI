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
