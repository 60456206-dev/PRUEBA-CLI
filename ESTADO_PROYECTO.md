# Dónde nos quedamos

Actualizado: 2026-10-24.

## Juego PULSO (trabajo anterior)

- Compartir PULSO: el 21/10 el usuario pidió hacerlo público; Sites confirmó acceso `public` (revisión 2). Enlace para compartir: https://pulso-local-rhythm.marco36gonzales.chatgpt.site
- Generado `PULSO-para-compartir.zip` con `dist/`, README y package.json para compartir el juego descargable.
- Nuevo pedido: juego que permite cargar música local y sincroniza las notas con su ritmo. Implementado en `pulso/`, sin dependencias de ejecución; inicio local: `cd pulso && npm start` (Python 3, puerto 4173).
- Generado: interfaz en español, cuatro carriles D/F/J/K y táctiles, detector de ataques reales, BPM estimado, tres dificultades, demo original, pausa/reinicio, calibración ±250 ms, resultados y récords locales. El audio se procesa en el navegador y no se sube.
- Revisado: 6 pruebas automáticas de audio y sintaxis correctas; QA en Chromium con carga WAV, errores de audio, silencio, pausa/reanudación, resultados y móvil. Prueba con reloj real: 24/24 perfectas, 100% y 4200 puntos incluyendo pausa. Capturas de escritorio/móvil revisadas; sin desbordamiento a 320/390/1440 px. Corregido inicio pendiente al abrir ayuda y scroll al juego en móvil.
- Publicado privado mediante Sites: https://pulso-local-rhythm.marco36gonzales.chatgpt.site . Identidad persistida en `pulso/.openai/hosting.json`; fuente publicada `d6e15d294dbc601ab39b864f081ceaa2f3ab6846`. El código editable se conserva en el repositorio; Git de publicación se preparó por separado en `/tmp/pulso-site-source-z9iaycl2` para no modificar el Git principal.
- Pendiente: prueba y aceptación del usuario con su propia música. El mapa depende de los ataques detectados y funciona mejor con percusión clara; no se ha prometido transcripción musical exacta.

## Contexto audiovisual anterior

- Proyecto: `MASTER_SERIES_PACKAGE`. Estamos generando vídeos desde imágenes para el episodio 1: 8 planos, 51 segundos previstos. La temporada tiene 48 planos.
- Usuario: está en Perú, es estudiante y no tiene GPU dedicada. Prefiere opciones gratuitas desde el navegador. Hemos investigado PixVerse, Hailuo, Google Flow y demos de Wan; verificar ofertas vigentes antes de prometer créditos.
- Plano 1 elegido por el usuario: `shots/EP01_SH01_PIXVERSE_SIN_MARCA_PREVIEW.mp4`. Estaba borrado localmente, pero se recuperó de Git. No sustituirlo por la antigua reconstrucción `EP01_SH01_FINAL.mp4`.
- La limpieza anterior se limitó a `shots`. Después se añadieron los vídeos del plano 2. No interpretar aquella limpieza como permiso permanente para borrar nuevos archivos.
- Plano 2 confirmado como definitivo por el usuario: `shots/EP01_SH02_FLOW_SIN_MARCA_6S.mp4`, recortado del tramo 0–6 s de Flow/Gemini. Verificado: 720×1280, 24 fps, 144 fotogramas y 6 s; decodificación completa sin errores. No se observó marca visible en las muestras revisadas. Conserva audio, no evaluado.
- Por petición explícita se eliminaron la copia limpia de Hailuo y el original de Flow de 10 s tras verificar el recorte. Imagen inicial: `SHOT_REFERENCES/INES_TABLE.png`.
- Limitación conocida del plano 2: abre la boca aproximadamente entre 4 y 4,75 s. El usuario eligió conservar esta versión después de ser informado; el recorte no corrige ese gesto.
- Añadidos 48 prompts en `VIDEO_PROMPTS/GOOGLE_FLOW`, con README, enlaces en las tarjetas individuales y recopilaciones por episodio, y acceso desde `GENERATE_THIS_FIRST.md`. Enlaces/duraciones revisados; no probados generando en Flow. La guía indica imágenes pendientes de crear o recuperar.
- Para el plano 2 están `VIDEO_PROMPTS/HAILUO/EP01_SH02_HAILUO.txt`, `VIDEO_PROMPTS/PIXVERSE/EP01_SH02_PIXVERSE.txt` y `VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH02_GOOGLE_FLOW.txt`.
- Pendiente: seguir con los planos 3–8; planos 1 y 2 elegidos por el usuario. El usuario pidió dejar los nombres finales y ajustes de referencias del montaje para cuando estén todos los planos. No renombrar automáticamente los elegidos a `_FINAL`.
- Antes de concluir que un vídeo no existe, comprobar disco, `git status` e historial: el archivo SIN_MARCA del plano 1 sí estaba en Git aunque faltara en disco.

Este archivo conserva el contexto dentro del repositorio; no supone memoria automática fuera de él. Leerlo al retomar y actualizarlo con nuevos acuerdos.


- Plano activo: EP01_SH03. Prompt de Flow disponible en `VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH03_GOOGLE_FLOW.txt`. Imagen inicial `SHOT_REFERENCES/SALT_DROP.png` creada con image_gen usando COAT_START.png y ARCHIVE_MASTER.png como referencias. Revisada visualmente: macro del borde óxido, sal, zona húmeda S1 y una gota todavía adherida a la pipeta. Imagen propuesta para usar; vídeo del plano 3 aún pendiente. Prompt de imagen guardado en SHOT_REFERENCES/SALT_DROP_GENERATION.md. Generar 6 s y usar 5 s en montaje.

## Trabajo activo retomado: MASTER SERIES · EP01_SH03 · Google Flow

- 2026-10-21: el usuario informa que obtiene sal sin la acción esperada. Revisados guion, tarjeta, prompt e imagen; no visto el vídeo fallido.
- Modificado solo el prompt Flow de EP01_SH03: desprendimiento → contacto → disolución localizada → reposo; cámara fija y foco estable. Notas en VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH03_NOTAS.md. Demás prompts intactos.
- Imagen existente revisada y conservada: gota y pipeta legibles, humedad dominante. Sin nueva generación. Se mantiene pipeta del material activo aunque el guion antiguo menciona pincel.
- Pendiente: prueba en Flow y revisión del vídeo; prompt propuesto, no aceptado ni validado mediante generación.

- Acuerdo posterior: usuario autoriza probar automatización de navegador con su Google AI Plus institucional, empezando solo por EP01_SH03: una generación y revisión antes de otra, aceptar imperfecciones menores si comunica la acción, parar ante límites y no comprar créditos. El usuario debe iniciar sesión directamente en Google.
- Conexión pendiente: en esta sesión no hay herramienta de navegador compartido/control de escritorio disponible ni DISPLAY configurado. No se ha abierto un formulario, iniciado sesión ni conectado la cuenta. Un enlace abierto en el navegador personal no comparte esa sesión con el agente.

- Usuario usa Linux. Preparado tools/flow-local/iniciar.sh y paquete FLOW-LINUX-INICIO.zip: abre navegador local Chrome/Chromium con perfil fuera del repo y ayuda con imagen/prompt EP01_SH03. No pide credenciales, no expone depuración ni conecta al agente remoto. Generación y descarga siguen manuales; automatización remota pendiente.
- Verificado: sintaxis Bash/Python, preparación de archivos y ZIP. No probado login institucional ni navegador gráfico (entorno sin escritorio).

## Escritorio remoto en Codespaces · 2026-10-21

- Preparado y arrancado `tools/flow-codespaces/escritorio.py`: Chromium + TigerVNC + noVNC, DISPLAY=:42. Navegador situado en formulario oficial accounts.google.com para Flow; revisado visualmente antes de introducir datos. Usuario aún no autenticado.
- Acceso: https://effective-space-bassoon-6vg6rvr59xv6crgg5-6080.app.github.dev/vnc.html?autoconnect=1&resize=scale . Puerto 6080: respuesta externa sin autenticar redirige a login GitHub. Mantener privado. VNC 5942 solo loopback con contraseña (comprobado que no ofrece acceso anónimo).
- Clave del escritorio: usuario la consulta con `cat ~/.local/share/master-series-flow-codespaces/clave.txt`. Perfil, clave, logs y Xauthority fuera del repo, directorio 0700. No hay puerto CDP. Agente puede usar xdotool/Xlib con DISPLAY=:42 y XAUTHORITY=~/.local/share/master-series-flow-codespaces/Xauthority.
- Limitación real: namespaces del sandbox de Chromium fallan en este contenedor; se usa --no-sandbox y se informó al usuario. No se eluden restricciones de Google/institución.
- Verificados arranque, HTTP 200 noVNC, autenticación VNC, loopback, redirección GitHub, formulario Google y sintaxis. Scripts instalar/iniciar/estado/detener documentados. El ZIP local anterior no era solución para Codespaces; este escritorio lo sustituye para el acceso.
- Pendiente: usuario inicia sesión y avisa; no inspeccionar ni capturar mientras introduce credenciales. Luego probar una generación EP01_SH03 y revisar según tolerancia acordada. Todavía no validada automatización de Flow ni gastadas generaciones.

- Comprobación tras aviso «ya entré»: se logró activar la pestaña de Flow mediante clic remoto y ver el proyecto `df0139d1-e7fe-4650-8b3c-99aa3a94162b`, interfaz en español e insignia PLUS. Control de ratón confirmado; identidad del correo y saldo no comprobados. No se generó vídeo.
- Durante la prueba hubo cambios simultáneos de pestaña y apareció otro formulario Google vacío. Se detuvo la interacción para no interferir con el usuario. No dar por verificada escritura en Flow ni automatización completa. Antes de continuar, dejar el navegador libre en Flow; no capturar durante entrada de credenciales.

## Revisión del plano 3 · 2026-10-22

- Generado por el usuario: `MASTER_SERIES_PACKAGE/shots/Water_droplet_wetting_salt-cover…_20261022131844.mp4` (720×1280, 24 fps, unos 10 s, con audio).
- Revisado visualmente mediante muestras de todo el clip cada 0,25 s y comparación con SALT_DROP.png. Mantiene composición, lana óxido, luz y cámara estable. El agua entra en contacto con la sal, pero se estira y escurre en varias formas/gotas durante los primeros ~4 s; la disolución y el aumento de humedad no quedan claramente legibles. Después domina el reposo.
- Valoración: utilizable con concesiones para comunicar agua sobre sal; no cumple plenamente la acción acordada de una sola gota absorbida con disolución localizada visible. Recomendación: conservar como candidato, no marcar definitivo. Un recorte a 5 s mejora duración, no corrige el comportamiento del agua. Audio no evaluado.
- Pendiente: decisión del usuario sobre aceptar esta imperfección o generar otra versión. No se han recortado, renombrado ni sustituido vídeos.

- 2026-10-22: ajustado el prompt de EP01_SH03 a petición del usuario: una gota compacta con separación completa, punta vacía, absorción inmediata y cambio localizado de pocos granos. Eliminadas elongación explícita y escala de moneda. Notas actualizadas. Nueva redacción propuesta, aún no generada ni validada; clip previo conservado como candidato.

## Plano 3 aceptado y cerrado · 2026-10-22

- Usuario informa que las nuevas pruebas no mejoraron el resultado y elige conservar el shot existente; autoriza renombrar y recortar.
- Generado: `MASTER_SERIES_PACKAGE/shots/EP01_SH03_FLOW_5S.mp4`, tramo 0–5 s del clip elegido. Original conservado y renombrado a `EP01_SH03_FLOW_ORIGINAL_10S.mp4`.
- Revisado: 5 s exactos, 720×1280, 24 fps, 120 fotogramas; decodificación completa sin errores y muestras visuales cada 0,5 s. Mantiene composición y continuidad; persisten el agua estirada/escurrida y la disolución poco legible ya conocidas. Audio conservado, no evaluado.
- Aceptado: versión existente por decisión del usuario, con esas concesiones; nombres `_FINAL` aplazados hasta completar los planos.
- Siguiente plano activo: EP01_SH04 (8 s), referencia prevista `SHOT_REFERENCES/ALBA_DOOR.png` y prompt `VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH04_GOOGLE_FLOW.txt`. Pendiente preparar/revisar sus materiales antes de generar.

## Retomar generación directa en Flow · 2026-10-23

- Usuario pide continuar con el agente operando Flow; siguiente plano EP01_SH04, una generación y revisión antes de otra, sin comprar créditos.
- Revisados prompt y ALBA_DOOR.png: referencia compatible con mirada a derecha, boca cerrada y manos fuera de cuadro. No se generaron imágenes ni vídeos nuevos.
- Escritorio reactivado y control local comprobado. Flow redirige al inicio de sesión oficial de Google; pendiente que el usuario acceda de nuevo y avise antes de continuar. No inspeccionar ni capturar durante credenciales.
- A petición del usuario, borradas las cookies de google.com y sus subdominios (incluido Flow) del navegador compartido; verificado que quedan 0 en ese ámbito. Pendiente nuevo inicio de sesión del usuario.
- Usuario indica que el acceso por escritorio compartido no funciona y pide otra vía. No insistir en noVNC. Búsqueda de plugins sin integración específica de Google Flow. Alternativa por concretar: navegador en su equipo Linux y automatización local; el lanzador local existente no conecta por sí solo con este agente. Pendiente comprobar si el usuario puede abrir Flow directamente en su navegador habitual.
- Usuario confirma que puede entrar a Flow y abrir sus proyectos desde su navegador habitual. El acceso local funciona según su reporte; aún no hay conexión entre ese navegador y el agente. Pendiente identificar navegador para preparar una vía de automatización compatible. El lanzador existente crea otro perfil y no reutiliza la sesión habitual; no presentarlo como conexión resuelta.

## Conexión Firefox local · 2026-10-23

- Usuario confirma Firefox con Flow accesible y GitHub CLI (`gh`) instalado en su computadora Linux.
- Generados `tools/flow-firefox/` y `FLOW-FIREFOX-LOCAL.zip`: extensión temporal para una pestaña Flow + túnel privado SSH de GitHub. No abre otro perfil ni transfiere cookies; clave fuera del repo, sin claves en el ZIP. No requiere puertos públicos.
- Revisados: sintaxis Python/JS/Bash, ZIP y 7 pruebas de autenticación, origen, ausencia de órdenes al conectar, entrega única y caducidad. Puente arrancado en 127.0.0.1:8765; estado desconectado, 0 órdenes. No probado Firefox real ni túnel desde el equipo del usuario.
- Pendiente: usuario descarga/extrae ZIP, ejecuta conectar-linux.sh en su terminal local, carga extension/manifest.json temporalmente, introduce la clave del puente y conecta desde su proyecto Flow. Después verificar lectura/captura, carga PNG y texto antes de generar EP01_SH04. Una generación y revisión antes de otra, sin comprar créditos.

## Limpieza del plano 3 · 2026-10-24

- Por petición del usuario, eliminado `MASTER_SERIES_PACKAGE/shots/EP01_SH03_FLOW_ORIGINAL_10S.mp4` (sin recortar). Se conserva `EP01_SH03_FLOW_5S.mp4`, versión recortada, revisada y aceptada. Plano activo: EP01_SH04.

## Ajuste del prompt del plano 4 · 2026-10-24

- Usuario reporta bloqueo de políticas en Flow. Simplificado `VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH04_GOOGLE_FLOW.txt`: mujer adulta en puerta, mirada a derecha, leve descenso de barbilla, labios cerrados y cámara fija durante 8 s. Eliminadas instrucciones ajenas a la toma (sal S1, gravedad) y redundancias. Referencia conservada.
- Revisado el texto; pendiente prueba en Flow. Causa del bloqueo desconocida; no se garantiza que la reformulación lo resuelva. Sin nueva generación.

## Nuevo proyecto: TikTok Radar · 2026-10-24

- Usuario pide proyecto separado para una idea de vídeo por día, investigada al escribir «mano, ¿qué vídeo creamos hoy?», con título, imágenes, prompts de vídeo y audio.
- Creado `TIKTOK_RADAR/README.md`: flujo de investigación con fuentes y hora, selección de un tema, guion, storyboard, generación/revisión de imágenes y aprendizaje con métricas reales. Documento revisado; sin primera entrega ni automatización en segundo plano.
- Propuestos, aún no aceptados: español latinoamericano y foco Perú. Duración actual de trabajo: 20–30 s, objetivo 25 s, por prioridad del usuario de vídeos cortos y producción rápida. Pendiente nicho/audiencia. MASTER SERIES conserva EP01_SH04 pendiente de prueba del prompt reformulado.

- Ajustado `TIKTOK_RADAR/README.md`: producción ágil con 3–4 escenas, hasta 4 imágenes base y 1–2 planos generados en vídeo cuando aporten valor; estructura de 25 s y narración orientativa de 45–60 palabras. Texto revisado; sin vídeo generado ni tiempo de producción validado.

## Revisión de EP01_SH04 · 2026-10-24

- Recibido `MASTER_SERIES_PACKAGE/shots/Woman_lowers_chin_in_doorway_20261024010019.mp4`: 8 s, 720×1280, 24 fps, con pista de audio. Decodificación completa sin errores.
- Revisado visualmente con muestras generales cada 0,5 s y rostro cada 0,25 s, comparado con ALBA_DOOR.png. Conserva apariencia, ropa, puerta, luz y encuadre; mirada a derecha, labios cerrados y manos fuera de cuadro. Ligero descenso de barbilla acompañado de giro hacia derecha; aparece leve sonrisa al principio y luego mantiene la pose. Sin deformaciones evidentes en las muestras. Audio no escuchado.
- Valoración: utilizable, recomendado conservar con esas pequeñas variaciones respecto al prompt. Pendiente aceptación del usuario; no renombrado, recortado ni marcado definitivo. Este plano sigue siendo de MASTER SERIES (8 s), independiente de las duraciones de TikTok Radar.

## Plano 4 definitivo · 2026-10-24

- Usuario acepta EP01_SH04 como definitivo y autoriza recorte solo si hace falta. Renombrado a `MASTER_SERIES_PACKAGE/shots/EP01_SH04_FLOW_8S.mp4`; sufijo `_FINAL` sigue aplazado según acuerdo previo.
- No necesita recorte: 8 s exactos, 720×1280, 24 fps y 192 fotogramas. Integridad verificada por SHA-256 antes/después del renombrado; contenido y audio intactos. Revisión visual anterior aceptada con leve giro/sonrisa; audio aún no evaluado.
- Siguiente plano activo: EP01_SH05, 6 s, referencia prevista `SHOT_REFERENCES/KEY_HAND.png` y prompt `VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH05_GOOGLE_FLOW.txt`. Pendiente revisión/preparación de materiales.

## Comprobación de materiales EP01_SH05 · 2026-10-24

- Prompt Flow existente: `VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH05_GOOGLE_FLOW.txt`; acción de 6 s: Alba cierra la mano sobre una llave de hierro negro.
- No listo para generar: falta la imagen inicial `SHOT_REFERENCES/KEY_HAND.png`. Comprobados archivos del repositorio, estado de Git, archivos versionados e historial de todas las referencias para KEY_HAND; no encontrada ni recuperable en ese historial consultado.
- Pendiente crear y revisar la imagen con continuidad de Alba y diseño de llave; revisar referencias disponibles antes de generar. Prompt aún contiene instrucciones de sal ajenas a la toma y pide cinco dedos distintos durante el cierre: conviene simplificarlo para permitir oclusión natural. No se generaron imágenes ni se modificó el prompt en esta comprobación.

## Imagen inicial EP01_SH05 preparada · 2026-10-24

- Generada con image_gen y guardada `MASTER_SERIES_PACKAGE/SHOT_REFERENCES/KEY_HAND.png`, 941×1672, vertical. Referencias: ALBA_DOOR, ALBA_MASTER y ARCHIVE_MASTER. Prompt y revisión en `SHOT_REFERENCES/KEY_HAND_GENERATION.md`.
- Revisada visualmente: una mano abierta, cinco dedos legibles, una llave negra apoyada en palma, tamaño compatible con ocultarla al cerrar; cárdigan hueso, vestido topo y puerta verde coherentes. Diferencia menor: muñeca entra desde arriba-izquierda en lugar de abajo; no impide la acción. KEY_MASTER no encontrado; diseño de llave propuesto, no cotejado con master previo.
- Simplificado prompt Flow de EP01_SH05 para esta imagen: cierre natural con oclusión de dedos y llave, reposo hasta 6 s; retiradas referencias a sal y conteo visible de dedos durante cierre. Materiales preparados para prueba; imagen revisada, aún no aceptada expresamente por usuario y vídeo pendiente.

## Comprobación de EP01_SH06 · 2026-10-24

- Usuario consulta preparación del plano 6. Prompt Flow y tarjeta existentes: primer plano del cuello hueco del abrigo óxido; un pequeño pliegue tiembla y se asienta, acercamiento leve. Generar 8 s y usar 7 s.
- No listo: falta `SHOT_REFERENCES/COAT_COLLAR.png`. Comprobados archivos, estado de Git, índice e historial de todas las referencias para ese nombre; no encontrada. Disponible `COAT_START.png` como referencia para preparar la imagen y mantener continuidad. No se generó imagen ni se cambió el prompt.
- Pendiente crear/revisar imagen inicial del plano 6. La consulta no implica aceptación del vídeo del plano 5, que sigue pendiente.

## Imagen inicial EP01_SH06 generada · 2026-10-24

- Generada con image_gen y guardada `MASTER_SERIES_PACKAGE/SHOT_REFERENCES/COAT_COLLAR.png` (941×1672), usando COAT_START.png como referencia. Prompt y revisión en `SHOT_REFERENCES/COAT_COLLAR_GENERATION.md`.
- Revisada visualmente: cuello abierto sin cuerpo, forro y percha visibles, lana óxido, luz lateral izquierda y puerta verde coherentes; bajo con sal fuera de campo. Diferencias: etiqueta interior sin texto legible, ojal y costuras más definidos, percha reinterpretada con mayor grosor. Utilizable como propuesta; no réplica exacta del master.
- Materiales del plano 6 disponibles para prueba en Flow: generar 8 s y usar 7 s. Prompt de vídeo existente conservado. Imagen generada/revisada, aceptación del usuario y validación en vídeo pendientes; plano 5 no marcado aceptado.

## Revisión del vídeo EP01_SH05 · 2026-10-24

- Recibido `MASTER_SERIES_PACKAGE/shots/Woman_closing_hand_over_key_20261024012556.mp4`: 8 s, 720×1280, 24 fps, 192 fotogramas, pista de audio presente. Decodificación completa sin errores; audio no escuchado.
- Revisadas muestras de todo el clip cada 0,25 s y detalles ampliados cada 0,5 s, comparadas con KEY_HAND.png. Se ve la llave inicial y el cierre progresivo; el aro todavía asoma aproximadamente entre 2,5 y 3 s, después queda oculto. Hacia 5 s la mano mantiene la pose. Vestuario, puerta y luz compatibles.
- Diferencia: el pulgar queda más lateral que sobre los dedos; cierre menos firme que el prompt. Valoración: acción principal legible y versión utilizable, recomendación conservar y usar 0–6 s. Recorte y aceptación del usuario pendientes; archivo original intacto, no renombrado ni marcado definitivo.

## Plano 5 elegido y recortado · 2026-10-24

- Usuario autoriza recortar la versión revisada. Generado `MASTER_SERIES_PACKAGE/shots/EP01_SH05_FLOW_6S.mp4`, tramo 0–6 s; versión elegida para montaje. Original de 8 s conservado con su nombre, sin autorización de borrado.
- Verificados 6 s exactos, 720×1280, 24 fps, 144 fotogramas y decodificación completa sin errores. Revisadas muestras del recorte cada 0,5 s: conserva cierre y reposo final; persiste pulgar lateral ya informado. Audio conservado, no escuchado.
- Confirmado en disco: `SHOT_REFERENCES/COAT_COLLAR.png` ya generada y revisada para EP01_SH06. Siguiente plano activo: EP01_SH06, materiales disponibles, vídeo pendiente. No hace falta volver a generar la imagen.
