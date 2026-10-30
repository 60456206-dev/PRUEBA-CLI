# Dónde nos quedamos

Actualizado: 2026-10-30.

## Planificación musical activa · EP03 · 2026-10-30

- Usuario pide continuar EP03 y confirma que los prompts sean solo para música. Preparados `AUDIO/EP03/README.md` y `MUSICA_FONDO/{README.md,CUES_EP03.md,PROMPTS_EP03.md}`, enlazados desde diseño sonoro y plan de edición. Base: 53 s/24 fps; M01 16,5–25,5 s; M02 opcional 41–44,5 s. Gota, testimonio de Mara y confrontación final sin música.
- Documentación preparada y enlaces revisados; no se generaron audios ni se modificaron vídeos. Pendiente producir/revisar música y confirmar ventanas contra voces/montaje. EP01 y EP02 conservan sus briefs.

## Planificación musical · EP02 · 2026-10-30

- Usuario pide continuar con EP02 tras la carpeta musical de EP01. Preparados `AUDIO/EP02/README.md` y `MUSICA_FONDO/{README.md,CUES_EP02.md,PROMPTS_EP02.md}`, con enlaces en diseño sonoro y plan de edición. Base: 52 s, 24 fps; M01 9,5–16,5 s; M02 opcional 42,25–43,5 s. Sin música durante voz de Mara, compuerta, replay y lectura final.
- Documentación preparada y enlaces revisados; ningún audio generado ni vídeo modificado. Pendiente concretar en montaje sonoro la repetición de golpes/arrastre: la frase del replay tiene ventana 32–37 s, los efectos repetidos no tienen ventana independiente fijada. Usar mismas fuentes y toma de voz, no nuevas interpretaciones. EP01 conserva V2 y su brief sin cambios.

## Montaje y audio EP01 · en curso · 2026-10-29

- 2026-10-30: usuario pide carpeta y prompts profesionales de música de fondo, solo EP01. Creada `AUDIO/EP01/MUSICA_FONDO/` con README (dirección y entrega), `CUES_EP01.md` y `PROMPTS_EP01.md`, sobre V2 de 35,25 s. M01 12,5–21,5 s; M02 opcional 31–32,5 s; música fuera 0,5 s antes de Mara/nombre. Documentación preparada y enlaces revisados; no hay música generada, revisada ni aceptada. README de audio, diseño sonoro y plan de edición enlazan la funcionalidad para la próxima mezcla. No se modificó el render.

- 2026-10-30: usuario autoriza aplicar ajustes sin crear material adicional. Generado `FINAL/EP01_AJUSTADO_V2.mp4`: 35,25 s/846 frames/1080×1920/24 fps, audio AAC y subtítulos quemados; SRT separado. Siete frases conservadas, X01 al inicio, pausas reducidas, efectos remapeados y voces equilibradas, contraste suave. Mezcla/stems nuevos en `AUDIO/EP01/AJUSTE_V2/`; script `tools/ajustar_ep01.py`, plan activo actualizado. Revisado visualmente a 2 fps y decodificación completa correcta; audio final -15,9 LUFS, pico -2,3 dBFS. Informe `FINAL/EP01_AJUSTADO_V2_REVISION.md`. Recomendación: conservar V2 para escucha final; pendiente aceptación y revisión perceptiva (API agotó espera), no oficializado. Originales conservados.

- 2026-10-30: revisión detallada imagen/audio EP01 en `FINAL/EP01_REVISION_AUDIO_IMAGEN.md`. Picture lock sigue SIN audio; generado `FINAL/EP01_REVISION_AUDIO_V1.mp4` (misma imagen + mezcla previa, 51 s), para revisión, no aceptado. Revisadas 51 muestras generales y 24 de gota; las 7 frases caben. Pendientes: escucha de actuación/efectos, incorporar respiración X01, ajustar foley, niveles (-23,4 LUFS, rango 13,2 LU), pausas (11,19 s sin diálogo antes de Mara), subtítulos y montaje final. Recomendación: ajustar materiales existentes, no regenerar. No se modificó el montaje original.

- 2026-10-30: usuario autoriza todos los audios EP01, máximo dos intentos por audio y push. Generados en `MASTER_SERIES_PACKAGE/AUDIO/EP01/`: 7 líneas + 2 extras TTS, originales y editados; 4 stems (DIALOGUE/ROOM/FOLEY/SFX) y mezcla previa de 51 s. Ambiente/tela/gota sintetizados localmente; sin música. 23 WAV decodificados, sin saturación en tomas; todas las líneas editadas caben en sus ventanas (L02 tempo +4,43 %). L05 usa T2 tras HTTP 429 por minuto en T1; resto T1. Revisión técnica completada, actuación/transcripción y aceptación pendientes de escucha: revisión automática de audio no disponible (HTTP error). No oficializados. Extras separados, mezcla conserva timeline original. Registro y scripts incluidos; no regenerar líneas existentes automáticamente.

- 2026-10-30: conexión API Gemini comprobada: `GEMINI_API_KEY` disponible y consulta autenticada `GET /v1beta/models` devuelve HTTP 200 (50 modelos, incluidos modelos TTS). Clave no expuesta. Esto verifica autenticación y listado; generación de audio y cuota aún sin probar.

- Generado `MASTER_SERIES_PACKAGE/FINAL/EP01_PICTURE_LOCK.mp4` con `tools/render_ep01_picture_lock.sh`, según `EP01_EDIT_PLAN.md`: 1080×1920, 24 fps, 51,000 s, 1224 frames, sin audio, cortes secos. Decodificación correcta; revisados los primeros y últimos frames de cada plano (orden y cortes correctos). SH01 viene de 576×1024 (PixVerse) y se escaló ×1,875: queda más suave que el resto. Montaje de imagen pendiente de aceptación del usuario.
- 2026-10-30: el usuario dice que el picture lock, visto sin sonido, no se entiende y le resulta apagado y simple. Pide una estrategia para enganchar al espectador. Propuesta: empezar por las voces (TTS) y ajustar después el montaje: arranque en frío con la respiración y la voz de Mara, subtítulos quemados, cortes más cortos con punch-ins, etalonaje con más contraste y final en cliffhanger. Pendiente de que el usuario decida.
- 2026-10-30 14:52 UTC: túnel comprobado. Playwright MCP en localhost:8931 responde (initialize 200, initialized 202) y Chrome tiene abierta la pestaña Flow con el proyecto `2ae393e1-…`. Solo lectura, sin gastar créditos. No hay datos de la «máquina virtual» (en `ORACLE-MACHINE` solo está el script de creación de Oracle).
- 2026-10-30 14:57: el usuario aprueba empezar con el audio del EP01. Creado `AUDIO/EP01/EP01_GUION_VOCES_TTS.md` (7 líneas y 2 extras de Mara). Al intentar abrir AI Studio en una pestaña nueva, las llamadas a herramientas del navegador se quedaron colgadas, aunque el servidor MCP responde 200 y el túnel sigue activo. Probablemente la extensión de Chrome espera confirmación del usuario. Todavía no se ha generado ningún audio.
- 2026-10-30 15:06: el usuario aceptó él mismo las condiciones de AI Studio (cuenta huallbenit@gmail.com). Generate speech usa Gemini 3.8 Flash TTS. Voice Design y el filtro de voces en español solo funcionan con clave de pago. Hay unas 30 voces femeninas gratuitas. Elección provisional: Gacrux (madura) para Alba, Kore (firme) para Inés y Vindemiatrix o Tavi para Mara. La prueba en el navegador quedó en pausa sin generar nada; la pestaña de Flow se sustituyó por AI Studio. Propuesto al usuario: crear una clave gratuita y guardarla como secreto del Codespace `GEMINI_API_KEY` (sin facturación y sin pegarla en el chat) para generar con un script. Pendiente de que lo haga.
- El audio nativo de los clips de Flow es casi silencio (≈ −55 dB de media): no sirve como base.
- Propuesta de audio, pendiente de decisión del usuario: las voces (Alba, Inés, Mara) con TTS de Gemini en Google AI Studio, ya que Flow solo genera audio pegado al vídeo; room tone, foley y SFX sintetizados localmente o desde fuentes CC0; música mínima o ninguna. Stems: DIALOGUE/ROOM/FOLEY/SFX/MUSIC según `AUDIO_TIMELINE.md`.

## Punto de retoma vigente · EP04 completado (8/8 oficiales)

- 2026-10-29 23:25 UTC: usuario confirma que no hay correcciones obligatorias y pide oficializar todo. Episodios 1–4 completos: 32/48 planos.
- Los 8 `shots/EP04_SHxx_FINAL.mp4` existen, todos 720×1280, 24 fps, sin audio y con decodificación completa verificada. SH01, SH06 y SH08 se oficializaron antes desde `V1`.
- Oficializados hoy desde `V2` (V1/V2 locales eliminados tras verificar; las fuentes siguen en el proyecto Flow `6bb12840-…`):
  - `SH02` 8 s/192 frames: cumple.
  - `SH03` 0–7 s/168 frames. Concesión: Alba levanta el brazo alto hacia la izquierda (~1–3,5 s) en vez de tocar el marco y lo baja; Inés queda quieta.
  - `SH04` 8 s/192 frames: la fuente de 190 frames se rellenó con 2 frames clonados del final. Labios cerrados. Concesión: acercamiento/deriva lateral fuerte; el fondo pasa de la puerta a una pared con aplique.
  - `SH05` 0–5 s/120 frames: cumple.
  - `SH07` 0–6 s/144 frames. Concesión: la mirada vuelve a subir desde ~5,25 s.
- Tarjetas actualizadas. `EP04_EDIT_PLAN.md` ya apuntaba a los `_FINAL` con las duraciones correctas.
- Siguiente: EP05_SH01 (preparar/revisar referencias y prompts) o montaje/audio de EP01–EP04, según decida el usuario.


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

## Preparación de EP01_SH07 · 2026-10-24

- Usuario pide continuar con plano 7 y generar imagen solo si falta. `SHOT_REFERENCES/INES_TABLE.png` existe y fue revisada visualmente: mirada izquierda, labios cerrados, camisa pizarra, fondo cal y luz coherentes. Se reutiliza la referencia del plano 2 según tarjeta; no se generó otra imagen.
- Diferencia documentada: imagen de encuadre medio, más abierto que el close-up mencionado en el prompt previo. Ajustado solo prompt Flow de EP01_SH07 para conservar encuadre real, cámara fija y gesto mínimo de reconocimiento sin sonrisa; retiradas instrucciones de sal ajenas al plano. Duración objetivo 6 s; si la herramienta entrega 8 s, revisar y recortar después.
- Materiales revisados y disponibles para prueba; vídeo del plano 7 pendiente. Aceptación/revisión del vídeo del plano 6 sigue pendiente; avanzar preparación no lo marca definitivo.

- 2026-10-24: por petición explícita del usuario, eliminado el original de 8 s del plano 5 (`shots/Woman_closing_hand_over_key_20261024012556.mp4`). Conservado `shots/EP01_SH05_FLOW_6S.mp4`, recorte elegido y revisado; duración de 6 s comprobada antes de borrar.

## Sincronización Git y revisión EP01_SH06 · 2026-10-24

- Resuelta divergencia local/remota mediante merge sin conflictos y push normal (`07af865`), sin force push. El commit remoto incorporaba el vídeo del plano 6 que aún no estaba en disco.
- Revisado `shots/Hollow_coat_collar_trembles_20261024014807.mp4`: 8 s, 720×1280, 24 fps, 192 fotogramas; decodificación completa correcta. Muestras visuales de todo el clip cada 0,5 s comparadas con referencia ya revisada. Audio presente, no escuchado.
- Mantiene abrigo vacío, paleta y escenario. Diferencia relevante: entre ~0,5–2,5 s se levantan y doblan ampliamente cuello y solapas, en vez de temblar un pequeño pliegue. Después se asienta con acercamiento progresivo. No cumple plenamente el movimiento sutil acordado; no marcar definitivo. Recortar a 7 s no elimina esa diferencia. Pendiente decisión del usuario entre aceptar movimiento más marcado o nueva generación; original intacto.

## Reformulación EP01_SH06 · 2026-10-24

- A petición del usuario, actualizado prompt Flow y añadidas `VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH06_NOTAS.md`: cámara fija, reposo 0–1 s, temblor mínimo de un pliegue bajo solapa izquierda de imagen entre 1–3 s y reposo hasta 8 s. Cuello, bordes de solapas y percha inmóviles. Conservada COAT_COLLAR.png.
- Nueva propuesta revisada en texto, pendiente prueba en Flow y revisión visual. Usar 7 s en montaje si el resultado cumple; vídeo previo intacto.

## Comprobación EP01_SH08 · 2026-10-24

- Imagen `SHOT_REFERENCES/COAT_START.png` y prompt Flow existentes; duración prevista 8 s. Imagen revisada: abrigo vacío, tres botones, escenario/luz coherentes.
- No listo del todo por continuidad: la tarjeta reutiliza el master con sal inicial, mientras el plano 8 exige S1 (zona inferior izquierda humedecida/disuelta tras plano 3). Esa zona no está claramente representada en COAT_START. Pendiente preparar variante específica del plano 8 que conserve master y refleje el cambio localizado; no sobrescribir COAT_START.
- Prompt también combina inmovilidad inicial con balanceo residual; conviene precisar un movimiento mínimo que se extingue y reposo, sin otra respiración. Solo comprobación: sin nueva generación ni modificaciones de prompt. Planos 6 y 7 aún pendientes de validación de vídeo.

## Variante EP01_SH08 preparada · 2026-10-24

- Generada con image_gen `SHOT_REFERENCES/COAT_REST_S1.png` (941×1672) a partir de COAT_START (edición) y SALT_DROP (material húmedo). Original intacto. Prompt y revisión en `SHOT_REFERENCES/COAT_REST_S1_GENERATION.md`.
- Revisada visualmente: zona oscura localizada en bajo izquierdo, menos sal, abrigo vacío y tres botones, escenario y luz compatibles. Hay variaciones menores de textura y distribución de sal también fuera de la zona editada; no idéntica píxel a píxel. Valorada utilizable; aceptación del usuario pendiente.
- Tarjeta e instrucciones de imagen EP01_SH08 enlazadas a nueva variante. Prompt Flow ajustado: movimiento residual mínimo 0–2 s, reposo 2–8 s, cámara fija, sin nueva respiración ni cambios de humedad/sal. Materiales preparados para prueba; vídeo pendiente, sin validación temporal.

## Segunda revisión EP01_SH06 · 2026-10-24

- Revisado nuevo `shots/Empty_wool_coat_hanging_still_20261024092342.mp4`: 8 s, 720×1280, 24 fps, 192 fotogramas; decodificación completa sin errores. Muestras generales cada 0,25 s y detalle de solapa/pliegue cada 0,5 s, comparadas con COAT_COLLAR.png. Audio presente, no escuchado.
- Mejora respecto al anterior: abrigo vacío, luz/color/escenario coherentes y sin levantamiento amplio de cuello/solapas. Persisten pequeñas variaciones de forma/posición de solapas y paño a lo largo de la toma; no se distingue claramente un único temblor localizado entre 1–3 s seguido de reposo desde 3 s.
- Valoración: mejor candidato visual, utilizable con concesión como plano de atmósfera; no validado como cumplimiento completo de la acción narrativa. Recortar a 7 s no hace más legible ese gesto. Pendiente aceptación del usuario; originales intactos, sin recorte ni renombrado. Revisión activa de plano 6; materiales de planos 7 y 8 siguen preparados.

## Plano 6 elegido y recortado · 2026-10-24

- Usuario acepta el nuevo candidato con las diferencias informadas y autoriza recorte y limpieza de vídeos sobrantes del plano 6. Generado `shots/EP01_SH06_FLOW_7S.mp4`, tramo 0–7 s, elegido para montaje.
- Verificados 7 s exactos, 720×1280, 24 fps, 168 fotogramas y decodificación completa sin errores; muestras visuales cada 0,5 s revisadas. Conserva continuidad y las pequeñas variaciones del paño ya informadas; el gesto localizado sigue poco legible. Audio conservado, no escuchado.
- Eliminados tras verificar el recorte los originales `Empty_wool_coat_hanging_still_20261024092342.mp4` y `Hollow_coat_collar_trembles_20261024014807.mp4`, por autorización del usuario. Referencias, prompts y otros planos conservados.
- Siguiente plano activo: EP01_SH07. Confirmado que reutiliza `SHOT_REFERENCES/INES_TABLE.png` del plano 2; vídeo pendiente.

## Revisión EP01_SH07 · 2026-10-24

- Recibido `shots/Woman_showing_recognition_in_video_20261024093349.mp4`. Vídeo: 720×1280, 24 fps, 144 fotogramas (6 s); contenedor 6,016 s con audio. Decodificación completa sin errores; audio no escuchado.
- Revisadas muestras generales cada 0,25 s y rostro ampliado cada 0,5 s, comparadas con INES_TABLE.png. Conserva apariencia, camisa, luz y escenario; labios cerrados, sin deformaciones evidentes en muestras. Expresión cambia de forma contenida y se mantiene al final.
- Diferencias: hacia 3–4 s aparece una leve sonrisa y la mirada/cabeza se orientan algo más al frente. El prompt pedía seriedad sin sonrisa y sin giro. Valoración: utilizable con esas concesiones, recomendado conservar según tolerancia previa, pero no cumplimiento literal; matiz más cálido que el reconocimiento serio previsto.
- Pendiente aceptación del usuario. No necesita recorte narrativo (ya tiene 6 s de vídeo); original intacto, sin renombrado ni borrado. Plano 7 sigue activo.

## Preparación confirmada EP01_SH08 · 2026-10-24

- Tras el «okey» del usuario a la recomendación del plano 7, se continúa con EP01_SH08; vídeo del 7 conservado con su nombre, sin limpieza adicional solicitada.
- Comprobados en disco tarjeta, prompt Flow y COAT_REST_S1.png; imagen revisada de nuevo: abrigo vacío, tres botones y zona oscura en bajo izquierdo, coherentes con el cierre previsto. Se mantienen las variaciones menores de textura/sal documentadas.
- Plano 8 listo para generar 8 s en Flow: movimiento residual mínimo 0–2 s, reposo 2–8 s, cámara fija y humedad/sal constantes. Vídeo aún pendiente de generación y revisión.

## Plano 7 renombrado y revisión EP01_SH08 · 2026-10-24

- Plano 7 elegido tras conformidad del usuario: renombrado a `shots/EP01_SH07_FLOW_6S.mp4`; SHA-256 idéntico antes/después. Sin recorte ni recodificación; conserva vídeo de 6 s y audio original (contenedor 6,016 s), con leve sonrisa/giro ya informados.
- Revisado `shots/Hanging_wool_coat_still_fabric_20261024094402.mp4`: 8 s exactos, 720×1280, 24 fps, 192 fotogramas, decodificación completa sin errores. Muestras generales cada 0,25 s y bajo ampliado cada 0,5 s, comparadas con COAT_REST_S1.png. Audio presente, no escuchado.
- Conserva abrigo vacío, tres botones, escenario/luz y zona oscura en bajo izquierdo con sal alrededor. No se observa una nueva inflación/respiración en las muestras. Movimiento inicial visible de paño y mangas, más amplio que el mínimo pedido; después se reduce, aunque persisten leves variaciones y no hay inmovilidad absoluta desde 2 s.
- Valoración: utilizable como cierre con esa concesión; recomendado conservar, sin afirmar cumplimiento literal del reposo. No requiere recorte (8 s previstos). Aceptación del usuario pendiente; original del plano 8 intacto, sin renombrar ni borrar. Plano activo: EP01_SH08.

## Plano 8 oficial y siguiente plano · 2026-10-24

- Usuario acepta explícitamente plano 8 como oficial con diferencias informadas. Renombrado a `shots/EP01_SH08_FLOW_8S.mp4`, sin recorte ni recodificación; SHA-256 idéntico antes/después. Los ocho planos del episodio 1 tienen versión elegida; montaje/audio final todavía pendientes.
- Consulta sobre «plano 09»: la numeración reinicia por episodio; el siguiente (noveno global) es EP02_SH01, 5 s de montaje, generar 6 s en Flow. Acción prevista: gota sobre zona de lana ya húmeda, sin aparición de sal ni inflación.
- Tarjeta y prompt Flow existen. Falta `SHOT_REFERENCES/SALT_USED.png`: comprobados archivos, Git e historial de todas las referencias para ese nombre, sin resultados. No listo para generar; pendiente preparar/revisar esa imagen y comprobar prompt con ella. No se generó imagen en esta consulta. Siguiente plano propuesto: EP02_SH01.

## Imagen EP02_SH01 preparada · 2026-10-24

- Generada con image_gen integrado `SHOT_REFERENCES/SALT_USED.png` (941×1672), editando SALT_DROP con COAT_REST_S1 como referencia de continuidad. Originales intactos; prompt completo y revisión en SALT_USED_GENERATION.md.
- Revisada visualmente: macro del mismo borde óxido, luz y fondo coherentes, pipeta/gota única dirigida a centro húmedo sin sal; cristales laterales conservados con pequeñas variaciones de distribución y textura. Imagen utilizable como propuesta, no idéntica a la referencia; aceptación del usuario pendiente.
- Precisado prompt Flow EP02_SH01 para una gota desprendida y absorbida en zona usada, punta vacía, sal lateral constante y reposo final sin inflación. Materiales preparados para generar 6 s y usar 5 s; vídeo y validación temporal pendientes. Plano activo EP02_SH01.

## Revisión EP02_SH01 · 2026-10-24

- Revisado `shots/Water_drop_landing_on_wool_20261024100233.mp4`: 720×1280, 24 fps, 144 fotogramas (6 s de vídeo; contenedor 6,016 s), audio presente no escuchado. Decodificación completa sin errores. Muestras generales y detalle de pipeta/paño cada 0,25 s comparados con SALT_USED.png.
- Conserva encuadre, lana óxido, luz, zona húmeda y sal lateral reconocible; sin inflación ni respuesta del abrigo. Primera gota se desprende hacia 1,5–1,75 s, queda como volumen brillante sobre la tela y escurre hacia el bajo aproximadamente entre 2–4 s. Hacia 3,5 s se aprecia otra gota desde la punta. Final más quieto desde ~4,25 s.
- Valoración: utilizable con concesiones para narrar que vuelve a mojar la zona y no ocurre respuesta; no cumple una sola gota absorbida localmente sin escurrimiento. Recomendado conservar según tolerancia previa, explicando diferencias. Tramo 0–5 s mantiene acción y breve reposo, pero no corrige agua ni segunda gota.
- Pendiente elección del usuario; sin recortar, renombrar ni eliminar. Plano activo EP02_SH01.

## EP02_SH01 elegido y EP02_SH02 preparado · 2026-10-24

- Usuario acepta conservar EP02_SH01 y autoriza ajuste: generado `shots/EP02_SH01_FLOW_5S.mp4`, tramo 0–5 s. Verificados 5 s exactos, 720×1280, 24 fps, 120 fotogramas y decodificación completa sin errores. Muestras cada 0,5 s revisadas; conserva escurrimiento y segunda gota ya aceptados. Audio conservado, no escuchado. Original de 6 s conservado; no se solicitó borrarlo.
- Plano activo EP02_SH02. INES_TABLE.png existente y revisada visualmente: rostro, camisa, luz, mirada inicial izquierda y labios cerrados adecuados. Se reutiliza según tarjeta; no hace falta generar otra imagen.
- Ajustado solo prompt Flow para conservar encuadre real, esperar 0–2 s, bajar solo mirada 2–5 s y mantenerla 5–8 s, sin sonrisa ni giro. Grabadora/mesa fuera de campo; eliminadas instrucciones de sal ajenas al plano y encuadre que podía provocar recomposición.
- Materiales listos para prueba: generar 8 s y usar 7 s tras revisión. Prompt revisado en texto; vídeo pendiente de generar/validar.

## Limpieza EP02_SH01 y revisión EP02_SH02 · 2026-10-24

- Por petición explícita, eliminado `shots/Water_drop_landing_on_wool_20261024100233.mp4` tras comprobar duración de 5 s y decodificación completa del elegido `EP02_SH01_FLOW_5S.mp4`. Recorte conservado.
- Revisado `shots/Woman_lowering_gaze_in_video_20261024101744.mp4`: 8 s, 720×1280, 24 fps, 192 fotogramas; decodificación completa sin errores. Muestras generales cada 0,25 s y rostro cada 0,5 s, comparadas con INES_TABLE.png revisada. Audio presente, no escuchado.
- Acción legible: parte mirando izquierda, baja la mirada aproximadamente entre 1,5–4 s y la mantiene hasta el final. Expresión seria, labios cerrados; apariencia, ropa, fondo y luz coherentes, sin deformaciones evidentes en las muestras.
- Diferencia: acompaña el gesto con leve descenso y giro de cabeza hacia el frente; el prompt pedía mover solo ojos. Empieza algo antes de los 2 s previstos. Valoración: utilizable y recomendado conservar con esas concesiones; primeros 7 s contienen acción y reposo suficiente.
- Pendiente aceptación y recorte del plano 2; vídeo intacto, sin renombrar ni eliminar. Plano activo EP02_SH02.

## EP02_SH02 elegido y comprobación EP02_SH03 · 2026-10-24

- Usuario acepta plano 2 y autoriza recorte y borrado del original. Generado `shots/EP02_SH02_FLOW_7S.mp4` (0–7 s), elegido para montaje. Verificados 7 s exactos, 720×1280, 24 fps, 168 fotogramas, decodificación completa y muestras visuales cada 0,5 s. Conserva mirada baja y reposo, con leve movimiento de cabeza ya aceptado; audio conservado, no escuchado.
- Eliminado `shots/Woman_lowering_gaze_in_video_20261024101744.mp4` después de verificar el recorte.
- Siguiente plano EP02_SH03: tarjeta y prompt Flow existentes; acción de dedo que pulsa una vez grabación y sale, grabadora fija con indicador rojo final. Generar 6 s para usar 5 s.
- No listo: faltan `SHOT_REFERENCES/RECORDER.png` y `PROPS/RECORDER_MASTER.png`, sin resultados en archivos ni historial Git consultado para RECORDER. Pendiente definir imagen de grabadora coherente con archivo/luz, generar y revisar; después ajustar prompt a imagen concreta. No se generó imagen en esta comprobación.

## Imagen EP02_SH03 preparada y envío Git · 2026-10-24

- Generada con image_gen y guardada `SHOT_REFERENCES/RECORDER.png` (941×1672); referencias ARCHIVE_MASTER e INES_MASTER. Dos resultados revisados visualmente: corregido objeto negro adicional al fondo. Prompt/revisión en RECORDER_GENERATION.md.
- Final propuesto: grabadora negra única, botón rojo y LED separado apagado, índice suspendido antes de pulsar, puño pizarra, mesa de madera. Diferencias: nuevo diseño de controles (sin master independiente), lámpara al fondo izquierdo por nuevo ángulo y luz cálida más acusada. Utilizable con esas diferencias; aceptación y vídeo pendientes.
- Prompt Flow EP02_SH03 adaptado al botón/LED visibles: pulsación 0–2 s, retirada hasta 3 s, reposo hasta 6 s; usar 5 s en montaje. Materiales listos para prueba. Futuros planos de grabadora sin mano requieren variante/fotograma revisado.
- Usuario autoriza commit y push de trabajo actual, incluidos recorte elegido EP02_SH02 y borrados autorizados de originales EP02_SH01/02. Sincronización remota se comprobará tras el envío.

## Revisión EP02_SH03 · 2026-10-24

- Revisado `shots/Finger_pressing_recorder_button_20261024103351.mp4`: 720×1280, 24 fps, 144 fotogramas (6 s de vídeo; contenedor 6,016 s), audio presente no escuchado. Decodificación completa sin errores. Muestras generales y detalle botón/LED cada 0,25 s comparados con RECORDER.png ya revisada.
- Acción legible: dedo contacta botón hacia 0,5–0,75 s, mantiene pulsación, LED separado se enciende rojo hacia 1,5 s; mano se retira aproximadamente 2,25–3 s. Después grabadora sola con LED rojo estable y pantalla oscura. Sin segunda pulsación ni deformaciones evidentes en las muestras; materiales, vestuario y luz compatibles.
- Valoración: cumple la acción principal, recomendado conservar. Pulsación algo sostenida y pequeñas variaciones de encuadre/textura sin impedir lectura. Usar primeros 5 s conserva acción y unos 2 s de reposo. Pendiente aceptación/recorte; original intacto, sin renombrar ni borrar. Plano activo EP02_SH03.

## EP02_SH03 oficial y comprobación EP02_SH04 · 2026-10-24

- Usuario acepta EP02_SH03 como oficial y autoriza recorte/borrado. Generado `shots/EP02_SH03_FLOW_5S.mp4` (0–5 s). Verificados 5 s exactos, 720×1280, 24 fps, 120 fotogramas, decodificación completa sin errores y muestras visuales cada 0,5 s. Conserva pulsación, retirada y LED rojo final; audio conservado, no escuchado.
- Eliminado original `shots/Finger_pressing_recorder_button_20261024103351.mp4` tras verificación. Versión oficial sin sufijo FINAL, según convención vigente.
- Siguiente plano EP02_SH04: tarjeta, prompt Flow y SALT_DROP.png existentes. Imagen revisada de nuevo: pipeta con gota adherida sobre sal intacta contigua a zona húmeda, lana óxido/luz/encuadre compatibles. Se reutiliza según tarjeta; no hace falta nueva imagen. Distribución de cristales no idéntica a SALT_USED, variación ya conocida de las referencias.
- Materiales disponibles para prueba de 8 s: gota sobre sal intacta, disolución localizada y segunda zona húmeda junto a la anterior. Falta generar y revisar vídeo, especialmente gota única y disolución legible; prompt existente no modificado en esta comprobación.

## Revisión EP02_SH04 · 2026-10-24

- Revisado `shots/Drop_dissolving_into_wool_salt_20261024104932.mp4`: 8 s, 720×1280, 24 fps, 192 fotogramas, decodificación completa sin errores. Muestras generales y detalle pipeta/sal cada 0,25 s comparados con SALT_DROP.png. Audio presente, no escuchado.
- Conserva macro, lana óxido, iluminación y zona húmeda anterior. Agua toca la zona salada, pero hay descargas repetidas (aprox. 1,25, 2 y 3,5 s), volúmenes brillantes/abultados sobre la tela y escurrimiento hasta ~6 s. Después queda más quieto.
- Hay cambios locales de brillo y textura, pero la reducción de sal y una segunda zona húmeda diferenciada no resultan claramente legibles. Valoración: candidato utilizable con concesiones como agua sobre sal, no validado para demostrar consumo de una nueva zona, que es la función de este plano. Recomendable nueva prueba si esa regla debe entenderse visualmente; recorte no corrige la acción y ya tiene los 8 s previstos.
- Pendiente decisión del usuario; archivo intacto, sin renombrar, recortar ni borrar. Plano activo EP02_SH04. Cambios previamente staged respetados.

## Reformulación EP02_SH04 · 2026-10-24

- Por petición del usuario, actualizado prompt Flow: una gota 1–2 s; disolución localizada visible 2–5 s mediante reducción/transparencia/desaparición de cristales y exposición de lana oscura; reposo 5–8 s. Punta vacía, sin escurrimiento ni agua abultada, sal circundante y humedad anterior constantes. Cámara/foco fijos.
- Conservada SALT_DROP.png como inicio y vídeo anterior como candidato. Notas en VIDEO_PROMPTS/GOOGLE_FLOW/EP02_SH04_NOTAS.md. Texto revisado; nueva prueba y revisión de vídeo pendientes, no se ha generado otra versión.

## Segunda revisión EP02_SH04 · 2026-10-24

- Revisado nuevo `shots/Water_droplet_dissolving_salt_cr…_20261024111339.mp4`: 8 s, 720×1280, 24 fps, 192 fotogramas; decodificación completa sin errores. Muestras generales y detalle cada 0,25 s, cotejados con SALT_DROP y revisión anterior. Audio presente, no escuchado.
- Conserva composición, material y luz. Se aprecia algo más de lana oscura expuesta en la parte inferior de la zona tratada, pero la sal directamente bajo la punta permanece mayormente blanca; disolución localizada todavía poco clara. Repite gotas, con agua abultada/escurrida entre ~1–4 s y otra descarga hacia ~6,75 s, rompiendo reposo final.
- Valoración: mejora parcial del cambio de superficie, no cumplimiento del objetivo de una sola gota y disolución legible. Utilizable solo con concesiones como agua sobre sal; no recomendado marcar oficial para demostrar consumo de una nueva zona. Un recorte antes de la última gota no corrige el resto y acorta los 8 s previstos. Ambos candidatos conservados, sin modificaciones. Pendiente decisión del usuario.

## Corrección: dos referencias solo para EP02_SH04 · 2026-10-24

- Usuario aclara que las dos imágenes son únicamente para EP02_SH04, que está dando problemas, no para EP02_SH05. La atribución anterior fue un malentendido; plano 5 sin cambios.
- Plano activo EP02_SH04. Propuesta: inicio SALT_DROP.png y final derivado con disolución localizada legible, lana húmeda expuesta, misma composición, humedad anterior y sal circundante conservadas.
- Pendiente preparar/revisar ambas imágenes e incorporar sus funciones al prompt según modo de entrada disponible. No se generaron imágenes ni se modificó el prompt. Ambos vídeos candidatos conservados, sin aceptación oficial.

## EP02_SH04 · pareja de referencias preparada · 2026-10-24

- Usuario autoriza preparar imágenes y prompt. Inicio: SALT_DROP.png reutilizada intacta. Final generado mediante image_gen integrado: SHOT_REFERENCES/EP02_SH04_END_S2.png; prompt completo y revisión en EP02_SH04_END_S2_GENERATION.md.
- Revisado visualmente: punta vacía, reducción clara del grupo blanco bajo la punta y lana oscura expuesta junto a humedad previa; conserva encuadre, luz y depósitos exteriores. Variaciones menores en fibras, cristales y contorno de punta; las zonas húmedas contiguas se unen visualmente. Propuesta utilizable, todavía no aceptada por usuario.
- Prompt Flow actualizado para roles inicio/final, una gota 1–2 s, disolución 2–5 s y reposo 5–8 s. Tarjeta y notas enlazan la pareja. Falta comprobar modo con campos inicial/final en interfaz actual, generar vídeo y revisar continuidad temporal. No se ha generado en Flow ni modificado los dos candidatos anteriores. Plano activo EP02_SH04; EP02_SH05 intacto.

## Revisión EP02_SH04 con pareja de referencias · 2026-10-25

- Revisado nuevo `shots/Water_droplet_dissolving_salt_cr…_20261024191634.mp4`, identificado como la prueba más reciente tras preparar inicio/final. Comparado visualmente con SALT_DROP.png y EP02_SH04_END_S2.png: muestras cada 0,25 s y detalle inicial cada 0,125 s. 8 s, 720×1280, 24 fps, 192 fotogramas; decodificación completa sin errores. Audio no escuchado.
- Mejora clara: el grupo blanco bajo la pipeta disminuye hasta dejar lana oscura expuesta hacia 5 s; final estable y compatible con referencia S2, con encuadre/luz/material conservados. Ahora se comunica consumo de sal en la nueva zona.
- Concesiones: dos descargas visibles aproximadamente a 1,1 y 2 s; agua temporalmente abultada/brillante sobre sal antes de absorberse. No cumple literalmente gota única ni absorción inmediata, pero se recomienda conservar como candidato utilizable por cumplir el cambio de superficie principal.
- Pendiente aceptación del usuario; no marcado oficial, recortado, renombrado ni borrado. Plano activo EP02_SH04.

## EP02_SH04 oficial · 2026-10-25

- Usuario acepta como oficial `shots/Water_droplet_dissolving_salt_cr…_20261024191634.mp4` (8 s), ya generado y revisado visualmente. Aceptadas las dos descargas y el agua temporalmente abultada; la reducción de sal y el final estable cumplen la acción principal.
- Elección registrada para montaje. Archivo conservado con su nombre y duración actuales; candidatos anteriores conservados. EP02_SH04 cerrado; siguiente plano pendiente: EP02_SH05.

## Comprobación EP02_SH05 · 2026-10-25

- Plano activo EP02_SH05. Tarjeta, imagen ALBA_DOOR.png y prompt Flow existentes: Alba oye algo fuera de campo y tensa la mandíbula una vez, boca cerrada, mirada derecha y cámara fija; generar/usar 6 s.
- Imagen existente revisada visualmente: boca cerrada, mirada derecha, puerta oscura y vestuario visibles. Encuadre más abierto (hasta cintura) que el primer plano descrito en tarjeta/prompt; conviene preservar la composición de la referencia. Materiales disponibles para prueba; no generado ni aceptado vídeo de este plano en los archivos consultados (sin historial bajo EP02_SH05).

## Comprobación EP02_SH06 · 2026-10-25

- Consulta activa: EP02_SH06; EP02_SH05 sigue pendiente de vídeo/revisión. Prompt Flow existente: grabadora inmóvil, LED de rojo a verde una vez; generar 8 s y usar 7 s.
- No listo para generar con la referencia actual: RECORDER.png revisada visualmente muestra mano antes de pulsar y LED apagado, mientras este plano necesita grabadora sola con LED inicialmente rojo. Pendiente preparar/revisar inicio coherente; opción: fotograma final del EP02_SH03 oficial. No se ha extraído ni generado imagen ni cambiado el prompt. Sin vídeo EP02_SH06 localizado en shots ni historial por ese nombre.

## Imagen EP02_SH06 preparada · 2026-10-25

- Preparada SHOT_REFERENCES/EP02_SH06_START_RED.png: extracción del último fotograma (4,958333 s) del EP02_SH03 oficial, 720×1280, sin IA ni retoque. Revisada visualmente: grabadora sola, LED rojo encendido, botón rojo separado y pantalla oscura; continuidad directa de mesa/luz/objetos del vídeo aceptado. Conserva su detalle 720p y pequeñas variaciones respecto a RECORDER.png.
- Tarjeta y prompt Flow actualizados para esta imagen y cambio exclusivo del LED a verde, sin manos. Generar 8 s, usar 7 s. Procedencia/revisión en EP02_SH06_START_RED_GENERATION.md.
- Plano activo EP02_SH06: imagen revisada lista para prueba; aceptación y vídeo pendientes. EP02_SH05 sigue pendiente de vídeo/revisión.

## EP02_SH05 y separación de TikTok Radar · 2026-10-26

- Usuario confirma que la reformulación es para EP02_SH05 (plano 05 del episodio 2). Prompt Flow simplificado conservando escucha fuera de campo, mandíbula tensa una vez, boca cerrada, mirada derecha y cámara fija; eliminadas sal/lente y contradicción de encuadre. Texto revisado, prueba en Flow y vídeo pendientes; causa del bloqueo desconocida. Notas en EP02_SH05_NOTAS.md. Plano activo EP02_SH05; EP02_SH04 sigue oficial.
- TikTok Radar: independencia total, prohibido reutilizar material de MASTER SERIES. Estilo animado, interpretado como microseries de frutas, nada realista; prompts para Flow e iniciativa en selección de ideas. README actualizado. Solicitud actual solo idea/prompts, sin generar imágenes o vídeos.
- Propuesta guardada en TIKTOK_RADAR/entregas/2026-10-26/IDEA_Y_PROMPTS_FLOW.md: «El plátano que se compró una cáscara nueva», ficción original de 25 s con cuatro planos, guion y prompts Flow. Texto revisado; sin activos generados, prueba ni aceptación.

## Corrección del usuario sobre TikTok Radar · 2026-10-26

- Solo tomar el estilo de animación de las series citadas, no temática de frutas ni frutinovelas. Cada idea debe surgir de investigación profunda de contenido viral actual en TikTok y otras redes al momento de la solicitud, con fuentes y señales verificables; no ficción aleatoria. Mantener independencia total de MASTER SERIES y prompts para Flow.
- README corregido; propuesta del plátano marcada descartada, conservada solo como registro. No hay todavía investigación de tendencias ni propuesta válida que la sustituya. Esta aclaración no genera nuevos activos. EP02_SH05 conserva prompt reformulado, pendiente prueba en Flow.

## TikTok Radar · primera propuesta investigada · 2026-10-26 UTC / 25 Perú

- Investigación pública de tendencias realizada; comparados Ghost Photoshoot, entrada lenta Pray For Me, What iPad y transición de ventilador. Elegido «Tu disfraz de Halloween ya está en tu cama», explicación animada del regreso estacional de las fotos de fantasmas, no ficción aleatoria. Fuentes y límites en TIKTOK_RADAR/entregas/2026-10-25_01/INVESTIGACION.md.
- Evidencia principalmente secundaria de octubre; TikTok bloqueó vídeos y Creative Center no expuso ranking, Instagram limitó acceso. No verificada viralidad actual en Perú ni crecimiento en últimas 48 h; ventana ampliada a octubre. Propuesta editorial con limitaciones explícitas, revalidar si se retrasa más allá de Halloween.
- Guion de 25 s, cuatro escenas, dirección animada original, voz y cuatro prompts Flow (dos principales y dos opcionales) en PROPUESTA.md y PROMPTS_FLOW/. Textos revisados; sin imágenes, voz o vídeos generados ni aceptación. MASTER SERIES intacto. Propuesta del plátano sigue descartada.

## Oficialización corregida · 2026-10-26

- EP02_SH04: `shots/EP02_SH04_FINAL.mp4`, versión elegida 20261024191634. 8 s exactos, 720×1280, 24 fps, 192 frames. Decodificación completa y muestras visuales correctas; no necesita recorte. Renombrado sin recodificar, hash idéntico 7354e06e06829771a5118fecfeda7d959995e89cdf066105485c53f49da8c560. Audio conservado, no escuchado. Concesiones aceptadas intactas.
- Eliminados sus dos descartes 20261024104932 y 20261024111339; tarjeta actualizada.
- Regla permanente en AGENTS.md: Cuando el usuario diga «oficializar», «es oficial» o «me quedo con esa versión», preparar el vídeo elegido: comprobar identidad, ajustar a duración de montaje si corresponde, verificar duración/decodificación y continuidad, renombrar `EPxx_SHxx_FINAL.mp4`, actualizar tarjeta y estado y eliminar vídeos descartados del mismo plano tras verificar el oficial. No borrar otros planos ni referencias. Sustituye el acuerdo anterior de aplazar nombres finales.
- TikTok Radar: referencias Ghost Photoshoot solicitadas, en generación. Sin vídeo nuevo.

## Referencias TikTok Radar listas · 2026-10-26

- Generadas con image_gen y revisadas individualmente: `TIKTOK_RADAR/entregas/2026-10-25_01/REFERENCIAS/01_CAMA.png`, `02_PERSONAJE.png`, `04_LAVANDERIA.png` (941×1672). Prompts exactos y revisión en esa carpeta. Plano 03 usará fotograma del futuro clip 02.
- Paleta/diseño coherentes; lavandería añade decoración, materiales más detallados/brillantes que mate estricto y leves variaciones de gafas/pliegues. Propuestas listas para prueba, no aceptadas todavía. Sin material de MASTER SERIES.
- No hay herramienta directa de generación de vídeo disponible en esta sesión; no generado vídeo ni voz. Flow pendiente.

## Revisión EP02_SH05 · 2026-10-26

- Revisado `shots/Woman_reacting_to_sound_20261025222022.mp4` frente a ALBA_DOOR.png y prompt Flow: muestras generales cada 0,5 s y rostro cada 0,25 s. Vídeo 720×1280, 24 fps, 144 fotogramas (6 s de imagen; contenedor 6,016 s), decodificación completa sin errores. Audio presente, no escuchado.
- Conserva personaje, vestuario, puerta, luz, encuadre y mirada a derecha; cámara estable. Se aprecia reacción de atención/sorpresa con leve giro de cabeza y cambio de cejas.
- Diferencia principal: abre los labios hacia 1,5 s y los mantiene separados durante buena parte del resto. No se distingue claramente el único apretón de mandíbula con boca cerrada pedido. Utilizable con concesión como reacción a un sonido, no cumplimiento literal de la actuación. Recortar no soluciona la acción conservando los 6 s.
- Recomendación: candidato válido si se acepta sorpresa en vez de tensión contenida; nueva prueba si boca cerrada/mandíbula son imprescindibles. Pendiente elección del usuario; sin renombrar, recortar ni eliminar. EP02_SH06 sigue con imagen y prompt listos, vídeo pendiente.

- Acuerdo 2026-10-26: cada evaluación de vídeo debe cerrar con una recomendación concreta y justificada, con una opción preferida. Guardado en AGENTS.md; no equivale a aceptación del usuario.

## EP02_SH05 oficial · 2026-10-26

- Usuario acepta la versión revisada, incluida boca entreabierta y reacción de sorpresa. Preparado `shots/EP02_SH05_FINAL.mp4`: 6 s exactos, 720×1280, 24 fps, 144 fotogramas. Vídeo copiado sin recodificación; hash del flujo de vídeo idéntico al original revisado. Audio ajustado de 6,016 a 6 s y recodificado AAC, no escuchado. Decodificación completa correcta.
- Eliminado el duplicado original `Woman_reacting_to_sound_20261025222022.mp4` después de verificar. No hay otros candidatos de este plano en shots. Tarjeta actualizada; EP02_SH05 cerrado.
- Siguiente plano activo: EP02_SH06, imagen y prompt preparados; generación y revisión de vídeo pendientes.

## Comprobación EP02_SH07 · 2026-10-26

- Consulta activa EP02_SH07: tarjeta y prompt Flow existen, generar/usar 6 s; cambio de foco desde lana húmeda a sal seca contigua, sin nueva gota ni movimiento de objetos.
- SALT_USED.png revisada frente al final de EP02_SH04_FINAL.mp4: la referencia antigua muestra gota adherida y distinta distribución de sal/humedad. No lista para continuidad estricta del estado S2 aceptado.
- Recomendación: preparar inicio desde último fotograma del plano 04 oficial (punta vacía, sal consumida conservada) y precisar en prompt que solo cambia foco, pipeta inmóvil y sin gotas. Fotograma temporal inspeccionado, no incorporado al proyecto ni modificado prompt. Preparación pendiente; EP02_SH06 sigue pendiente de vídeo.

## Revisión candidato EP02_SH06 y preparación EP02_SH07 · 2026-10-26

- Vídeo nuevo identificado como `shots/Woman_reacting_to_sound_20261025225448.mp4`, aportado para plano 06: 720×1280, 24 fps, 144 frames (6 s de imagen, contenedor 6,016 s), decodificación completa correcta. Revisado visualmente cada 0,5 s; audio no escuchado.
- No cumple EP02_SH06: empieza en grabadora con indicador rojizo, cámara se desplaza hacia una mujer y pierde grabadora; no se observa transición verificable del LED a verde ni final de reproducción. Dura 6 s frente a 7 s de montaje previstos. Recomendación: regenerar usando EP02_SH06_START_RED.png y prompt específico del 06, comprobar no usar el prompt de reacción del 05. No se conoce configuración usada en Flow. Archivo conservado, sin oficializar.
- EP02_SH07: creada `SHOT_REFERENCES/EP02_SH07_START_S2.png` desde último fotograma del 04 oficial, sin IA/retoque; revisada visualmente, continuidad exacta del estado consumido, punta vacía. Tarjeta, shotlist y prompt Flow actualizados. Solo cambio de foco, sin gotas ni movimiento de objetos; generar/usar 6 s. Referencia lista para prueba, vídeo pendiente. SALT_USED.png intacta para otros planos.

## Retirada de vídeo equivocado · 2026-10-26

- Usuario confirma que el vídeo enviado era equivocado y solicita eliminarlo: retirado `shots/Woman_reacting_to_sound_20261025225448.mp4`. Su revisión no permite concluir que el prompt del plano 06 falló; no correspondía al vídeo que se quería revisar. EP02_SH06 sigue pendiente del vídeo correcto.
- Prompt simplificado del 06 propuesto en conversación, aún no aplicado al archivo. Referencia y prompt del 07 preparados; referencia del plano 01 conservada en shotlist.

## Revisión vídeo correcto EP02_SH06 · 2026-10-26

- Revisado `shots/Recorder_LED_changes_to_green_20261025230346.mp4` frente a EP02_SH06_START_RED.png y prompt: muestras generales cada 0,5 s y detalle grabadora cada 0,25 s durante todo el clip. 8 s exactos, 720×1280, 24 fps, 192 fotogramas; decodificación completa correcta. Audio presente, no escuchado.
- Cumple acción visual: pequeño LED rojo cambia a verde alrededor de 3,5 s y permanece verde hasta final; botón grande sigue rojo y pantalla oscura. Grabadora/cámara estables, sin manos ni personas; conserva mesa, encuadre y luz de referencia. Sin diferencias relevantes observadas en las muestras.
- Recomendación: conservar y oficializar usando tramo 0–7 s para montaje, sin nueva generación. Pendiente aceptación del usuario; archivo intacto, no renombrado ni recortado. EP02_SH07 continúa listo para prueba con referencia S2.

## EP02_SH06 oficial y comprobación EP02_SH08 · 2026-10-26

- Usuario acepta plano 06. Preparado `shots/EP02_SH06_FINAL.mp4`, tramo 0–7 s, H.264/AAC: 7 s exactos, 720×1280, 24 fps, 168 frames. Decodificación completa y muestras visuales correctas; mantiene cambio LED rojo a verde y reposo final. Audio conservado, no escuchado. Original de 8 s eliminado tras verificar; tarjeta actualizada.
- Consulta activa EP02_SH08: prompt Flow y tarjeta existentes, generar/usar 8 s. Informe quieto sobre mesa, cámara cenital fija y sombra leve. Guion requiere que el informe establezca evacuación completa a las 18:00.
- No listo para generar: REPORT_TOP.png y PROPS/REPORT_MASTER.svg referenciados no localizados en disco ni historial Git consultado (búsqueda global de REPORT/informe). Falta preparar y revisar referencia del informe con dato horario legible; el prompt actual no especifica ese texto. Sin vídeo EP02_SH08 en shots. EP02_SH07 sigue pendiente de vídeo.

## Revisión EP02_SH07 y referencia EP02_SH08 · 2026-10-26

- Revisado `shots/Shifting_focus_from_wool_patch_20261025230845.mp4`: 720×1280, 24 fps, 144 frames (6 s de imagen, contenedor 6,016 s), decodificación completa correcta. Muestras generales y detalle cada 0,5 s comparadas con EP02_SH07_START_S2.png. Audio presente, no escuchado.
- El foco cambia, pero alrededor de 2,5–3 s aparece una superficie de madera con sal adicional bajo la tela y cambia encuadre/relación espacial. Enfoca esa sal nueva en vez de conservar exclusivamente los cristales sobre la lana. No cumple cámara/objetos inmóviles ni continuidad. Recomendación: repetir, explicitando que el foco termina en la sal existente adherida a la misma lana, sin mesa ni cristales nuevos. Archivo intacto; no aceptado ni oficializado.
- EP02_SH08: generada `SHOT_REFERENCES/REPORT_TOP.png` con image_gen integrada, referencia de madera/luz EP02_SH06_START_RED.png. Revisada: hoja cenital plana, texto exacto y legible «INFORME DE EVACUACIÓN», «Evacuación completa: 18:00», «No quedaba nadie en el edificio.». Madera compatible en estilo, veta distinta del plano de grabadora; papel envejecido con pliegues leves. Imagen propuesta lista para prueba, no aceptada todavía.
- Prompt Flow del 08 actualizado para preservar texto/geometría durante 8 s y mover solo sombra inferior. Tarjeta corregida para no depender del SVG inexistente. Prompt de imagen/procedencia/revisión en REPORT_TOP_GENERATION.md. Vídeo del 08 pendiente; si Flow deforma texto, usar imagen fija en montaje.

## Reformulación EP02_SH07 · 2026-10-26

- A petición del usuario, prompt Flow actualizado: foco hacia cristales existentes sobre la misma lana, debajo/derecha de zona húmeda; eliminado «lower foreground». Inicio 0–1 s, foco óptico leve 1–4 s, reposo 4–6 s. Fondo/encuadre/escala intactos, sin mesa nueva, sal añadida, caída de tela ni gotas.
- Tarjeta y notas actualizadas; EP02_SH07_START_S2.png conservada. Texto revisado, prueba pendiente. Vídeo anterior intacto, no oficial.

## Segunda revisión EP02_SH07 · 2026-10-26

- Revisado `shots/Shifting_focus_on_salt_crystals_20261025231908.mp4`: 720×1280, 24 fps, 144 fotogramas (6 s de imagen, contenedor 6,016 s); decodificación completa correcta. Muestras generales cada 0,5 s y detalle cada 0,25 s frente a EP02_SH07_START_S2.png. Audio presente, no escuchado.
- Ya no aparece la mesa con sal del intento anterior, pero introduce nuevas descargas de agua aproximadamente a 1, 2 y 3 s, un grupo blanco prominente que no estaba en el inicio y retirada de pipeta hacia 4–4,5 s. El cambio de foco no queda claramente legible como única acción. Rompe continuidad de superficie y pipeta inmóviles.
- Recomendación: no oficializar esta versión. Preparar el plano de 6 s desde la referencia fija con cambio de enfoque controlado en edición para conservar el estado S2, en lugar de otra generación libre. Propuesta pendiente de autorización; no se ha creado montaje. Ambos candidatos conservados intactos.

## EP02_SH07 oficial mediante edición · 2026-10-26

- Usuario autoriza solución desde imagen fija y la elige como final. Creado `shots/EP02_SH07_FINAL.mp4` desde EP02_SH07_START_S2.png: 6 s exactos, 720×1280, 24 fps, 144 frames, sin audio para montaje.
- Cambio de enfoque simulado: referencia intacta 0–1 s; desenfoque localizado suave de zona consumida 1–4 s, sal seca adyacente conserva detalle; reposo 4–6 s. No es cambio óptico real ni reparación del movimiento de Flow; escena reconstruida desde referencia. Pipeta vacía, sal, encuadre y fondo permanecen inmóviles.
- Revisados contacto cada segundo y detalle inicio/final, decodificación completa sin errores. Efecto sutil, más visible en detalle. Script reproducible tools/render_ep02_sh07.py. Tarjeta/notas actualizadas.
- Eliminados tras verificar los dos descartes 20261025230845 y 20261025231908. EP02_SH07 cerrado; siguiente plano EP02_SH08 con REPORT_TOP.png y prompt listos, vídeo pendiente.

## EP02_SH08 · más dinamismo · 2026-10-26

- Usuario informa resultado demasiado estático y pide modificar prompt. Flow actualizado: acercamiento cenital suave de ~10 % hacia «Evacuación completa: 18:00», frenado y reposo 7–8 s; título/línea completos y nítidos. Solo cámara se mueve, papel/texto/luz constantes. Sustituye cámara fija para Flow; referencia conservada.
- Tarjeta y notas actualizadas. Texto revisado; nueva generación y revisión pendientes. No se evaluó un vídeo nuevo en esta petición.

## Revisión candidato EP02_SH08 · 2026-10-26

- Revisado `shots/Camera_zooms_in_on_report_20261025234500.mp4`: 8 s exactos, 720×1280, 24 fps, 192 fotogramas; decodificación completa correcta. Contacto cada 0,5 s y lectura ampliada cotejada con REPORT_TOP.png y prompt. Audio presente, no escuchado.
- El acercamiento hace el plano más dinámico y el dato «Evacuación completa: 18:00» se mantiene legible durante buena parte del clip. Sin embargo, el zoom es mucho más fuerte que el 10 % pedido: hacia el final recorta el título y deja la línea/documento demasiado pegados o cortados por los bordes. El contenido no muestra letras reescritas, pero se pierde el contexto de informe completo en el cierre.
- Recomendación: no oficializar este candidato todavía; recortar el acercamiento a un máximo aproximado del 10 % en edición desde REPORT_TOP.png, manteniendo visibles encabezado y hora. No hace falta otra generación libre. Archivo intacto, pendiente elección del usuario.

## Retoma y verificación EP02_SH08 · 2026-10-26

- Encontrados vídeo `shots/EP02_SH08_FINAL.mp4` y script `tools/render_ep02_sh08.py` ya registrados en aa69921, sin revisión registrada en el resumen.
- Revisado: 8 s exactos, 720×1280, 24 fps, 192 frames, sin audio; decodificación completa correcta. Muestras cada segundo frente a REPORT_TOP.png: zoom controlado del 10 %, título y hora completos y estables, reposo final. Bordes laterales del papel cerca del encuadre al final; texto con margen. Movimiento desde imagen fija, sin sombra animada.
- Recomendación: conservar y oficializar esta edición. Pese al nombre FINAL existente, aceptación explícita pendiente según contexto disponible. Candidato Flow conservado. Plano activo EP02_SH08.

## EP02_SH08 oficial y siguiente plano · 2026-10-26

- Usuario oficializa la edición revisada `shots/EP02_SH08_FINAL.mp4`: 8 s exactos, 720×1280, 24 fps, 192 frames, sin audio. Verificación técnica y visual completada al retomar; título/hora conservados con acercamiento del 10 %. Tarjeta actualizada y descarte Flow 20261025234500 eliminado.
- Plano activo: EP03_SH01, llave negra sobre dibujo de compuerta; montaje 5 s (Flow generar 6 s). Guion, tarjeta y prompt leídos. KEY_TABLE.png y KEY_MASTER.png no localizados en disco ni historial consultado; existe KEY_HAND.png para continuidad. Pendiente preparar y revisar imagen inicial antes de generar vídeo.


## TikTok Radar · cambio de estilo · 2026-10-26

- Usuario pide mantener animación con mayor realismo y detalle, aplicado a las shot references. Sustituye el acuerdo anterior «nunca realista»: dirección actual 3D cinematográfica semirrealista, materiales/texturas/luz creíbles y diseño animado.
- Generadas con image_gen y revisadas individualmente 01_CAMA_V2.png, 02_PERSONAJE_V2.png y 04_LAVANDERIA_V2.png en TIKTOK_RADAR/entregas/2026-10-25_01/REFERENCIAS/. Originales conservados. Más tejido, costuras y reflejos; pliegues varían y lavandería tiene sombras de ventana más fuertes que estudio. Propuestas, no aceptadas aún; vídeo sin probar.
- Actualizados README, dirección de propuesta y cuatro prompts Flow. Prompts exactos y revisión V2 guardados. MASTER SERIES sin cambios; su plano pendiente sigue EP03_SH01.

## Animación SVG · trabajo activo · 2026-10-26

- Usuario pide intro basada en `ANIMACIONES_SVG/Sin título.png`, más saturación, negro puro y vapor conservado; aclara que el movimiento de engranajes es esencial.
- Generados `ENGRANAJES_INTRO_V1.svg`, `VISTA_PREVIA.html`, generador y README en esa carpeta. SVG híbrido con PNG integrado, saturación 1,38, vapor animado y giro opuesto oscilante ±1,4°/±1,9° en 12 s; no rotación completa ni vectorización pura. Referencia intacta.
- Revisado visualmente en Chromium en extremos del movimiento: composición/texturas conservadas, ligera suavidad/duplicación de bordes por recortes superpuestos. Propuesta V1, pendiente de aceptación y ajustes; no integrada en app. Proyectos audiovisuales anteriores sin cambios.

## Animación SVG · cámara y móvil · 2026-10-26

- Usuario pide cámara con aceleración/desaceleración y formato móvil. Generada ENGRANAJES_INTRO_V2.svg, autónoma, 1080×1920 (9:16); V1 y referencia conservadas. Vista previa y generador apuntan a V2.
- Cámara: acercamiento 4 % y desplazamiento leve hacia arriba, regreso en bucle de 12 s; curva suave de aceleración/frenado en ambos trayectos. Conserva giro, vapor y saturación. Movimiento reducido desactiva cámara.
- Revisado XML y capturas Chromium a 390×693 en inicio y máximo acercamiento: ruedas completas, más aire negro vertical. Persiste suavidad/duplicación periférica propia de los recortes de V1. No probado en dispositivo físico. V2 propuesta, aceptación pendiente.

- Ajuste SVG V2 posterior: usuario pide más velocidad en engranajes. Ciclo de giro reducido de 12 a 4 s (3× velocidad), misma amplitud y suavizado; cámara/vapor intactos. SVG regenerado, duraciones comprobadas y captura Chromium a 2 s revisada: ruedas completas, persiste ligera duplicación de bordes. Propuesta actualizada, pendiente aceptación.

- Ajuste para ventana de atención de 2 s: V2 ahora recorre 18°/24° en esos 2 s (amplitud ±9°/±12°, ciclo 4 s), entrada de 0,25 s desde 65 % de opacidad. Retirada copia fija debajo de ruedas; fallback estático conservado para movimiento reducido. XML y capturas Chromium inicio/2 s revisados: giro mucho mayor, ruedas completas; huecos oscuros visibles entre algunos dientes por recortes de la imagen, sin reconstrucción 3D. Propuesta pendiente de aceptación.

## Animación SVG · V3 frontal · 2026-10-26

- Usuario pide aceleración constante, vista frontal y humo moviéndose con los engranajes. Creada V3 vectorial con generador crear_svg_frontal.py; vista previa apunta a V3. V1/V2 y PNG conservados.
- Giro opuesto con aceleración constante por ciclo de 4 s, recorrido 90°/112,5° a 2 s; velocidad se reinicia cada ciclo. Estelas giran con ruedas, además de desplazarse y variar opacidad. Cámara suave y 9:16 conservados.
- Revisados XML y capturas Chromium 0/2 s a tamaño móvil: ruedas completas y frontales. Cambio relevante: diseño vectorial gráfico, pierde acabado fotográfico y volumen cristalino original; vapor estilizado. Propuesta, pendiente aceptación, sin push en este turno.

## Retorno a SVG V2 · misma imagen · 2026-10-26

- Usuario rechaza V3 y elige explícitamente el aspecto de V2. Objetivo activo: acelerar esos mismos engranajes sobre la misma imagen, sin rediseño frontal. Vista previa restaurada a V2; V3 conservada pero no activa.
- Giro V2 reducido de 4 a 1,6 s (2,5× más rápido), mismos ±9°/±12°. Cámara, vapor, PNG, colores y 9:16 intactos. Continúa oscilación, no giro 3D continuo.
- XML/duraciones verificados y extremo a 0,8 s revisado en Chromium móvil: ruedas completas, persisten huecos oscuros de recorte. Apariencia V2 elegida; nuevo ritmo pendiente de aceptación.

## SVG V2 · giro continuo rápido · 2026-10-26

- Usuario pide giro continuo acelerando/desacelerando y movimiento rápido claramente perceptible. Sustituida oscilación por vueltas completas opuestas de 2 s, curva (.4,.12,.6,.88), sin parada ni inversión; velocidad continua al repetir. Misma imagen, cámara, vapor y 9:16.
- Generador y V2 actualizados. Revisados XML y seis capturas Chromium móvil, incluyendo 1,999/2,001 s: cierre sin salto visible. Persisten huecos negros y solapes; al rotar recortes planos también rota la perspectiva de sus ejes, sin reconstrucción mecánica 3D.
- Propuesta generada y revisada; pendiente aceptación del usuario. Vista previa sigue en V2; V1/V3 y referencia conservadas.

## SVG V2 · efecto de giro sin fin · 2026-10-26

- Usuario aclara que no quiere percibir un ciclo de 2 s, sino giro continuo mediante un efecto. Sustituido frenado por vuelta por giro base constante de 300°/s y modulación independiente ±55°/3,7 s; aceleración/desaceleración sin parada ni inversión. Mantiene imagen y resto de V2.
- Generados SVG y generador actualizados; XML verificado. Revisión visual en Chromium móvil registrada tras capturas. Persisten limitaciones de recortes 2D (huecos, solapes y perspectiva rotatoria). Propuesta pendiente de aceptación.

## EP03 · evaluación de automatización · 2026-10-28

- Usuario retoma MASTER SERIES tras EP02 y delega operación de generación y push; pide primero evaluar alternativas a Flow/Firefox local conservando el flujo de producción en Flow. Plano siguiente EP03_SH01; preparación de referencia sigue pendiente según último estado.
- Revisados puente Firefox, manifiesto y operaciones: lectura/clic/texto/carga/captura; no implementa recepción del MP4 en el repositorio. Sigue sin prueba integral en equipo del usuario.
- Recomendación propuesta: Flow en Chrome local + Playwright (extensión para sesión abierta) y conexión privada con este entorno; validar carga, generación única, descarga y transferencia antes de automatizar EP03. Chrome DevTools MCP es alternativa; Firefox propio queda como respaldo. Veo API es otra vía técnica, con facturación propia y sin equivalencia con trabajar en el proyecto Flow.
- Fuentes oficiales revisadas: support.google.com/flow/answer/16353333, playwright.dev/mcp/configuration/browser-extension, github.com/ChromeDevTools/chrome-devtools-mcp, ai.google.dev/gemini-api/docs/veo y /pricing. Búsqueda de plugins no devolvió integración directa pertinente (catálogo no exhaustivo).
- No instalado/conectado navegador ni generados vídeos en esta evaluación. Arquitectura propuesta, no validada ni elegida por el usuario. Se conserva revisión visual por intento y no comprar créditos. Oficialización/borrado siguen sujetos al acuerdo de aceptación vigente; delegación operativa y push no se interpretan como aceptación automática de candidatos.

- Usuario elige avanzar con conexión Chrome/Playwright y pide pasos para delegar control. Procedimiento: extensión oficial, servidor local Playwright MCP 0.0.83 en loopback:8931 y túnel SSH inverso hacia el Codespace actual. Comandos CLI comprobados en este entorno; conexión del usuario, carga/descarga y generación todavía pendientes. Usar URL http://localhost:8931/mcp por validación Host del servidor. No hace falta transmitir contraseñas ni token de extensión por chat.

- Conexión 2026-10-28: usuario informa ambas terminales abiertas. Verificados HTTP 200, inicialización MCP y listado de herramientas a través de localhost:8931; túnel operativo. Solicitada primera lectura browser_snapshot; pendiente respuesta/conexión de extensión con pestaña Flow. No se ha generado ni gastado créditos. Cliente temporal en /tmp/flow-mcp/client.py, sesión fuera del repositorio.

- Conexión Chrome confirmada: browser_snapshot devuelve proyecto Flow af9c3819-f006-4572-85b5-0aaf9636308a, título «oct 27 - 20:13», interfaz española e insignia PLUS. Campo de petición vacío y generación deshabilitada. Lectura de pestaña verificada; carga/descarga, escritura y generación aún sin probar. No se gastaron créditos.

## EP03 · producción autónoma autorizada · 2026-10-28

- Usuario autoriza completar los ocho planos: preparar/revisar imagen, generar en Flow, descargar y evaluar; máximo dos generaciones de vídeo por plano (segunda con prompt corregido solo si falla primera); después ajustar duración, renombrar FINAL, actualizar documentación y hacer push. Esta delegación sustituye la aceptación individual pendiente para EP03. Sin tercera generación; documentar concesiones. Parar y avisar si faltan créditos para que usuario cambie cuenta; no comprar.
- Plano activo EP03_SH01. KEY_TABLE/KEY_MASTER ausentes en disco e historial; image_gen en curso con KEY_HAND y ARCHIVE_MASTER como referencias. Interfaz Flow leída/capturada: 9:16, una salida y confirmación previa; modelo mostrado Omni 1.1 Flash. Intento de seleccionar Veo 3.1 Fast agotó tiempo; cambio NO confirmado.

- KEY_TABLE.png generada/revisada/seleccionada; prompt Flow SH01 ajustado y tarjeta actualizada. Concesiones visuales y prompt de imagen en KEY_TABLE_GENERATION.md. Ninguna generación de vídeo enviada (0/2). Conexión dejó de responder incluso a initialize MCP (8 s sin bytes), tras acceso inicial correcto; pendiente diagnóstico de terminales locales del usuario. Descarga MP4 aún no validada.
- Precisión del acuerdo EP03: si primera versión falla, una segunda con prompt ajustado y conservar esa segunda sin generar una tercera; ajustar duración y documentar limitaciones, sin afirmar que cumple si no cumple.

- Pausa solicitada por el usuario: esperar a que su internet sea estable. Materiales de EP03_SH01 guardados y publicados en commit 4d1c362; 0/2 intentos de vídeo enviados. Al retomar, usuario reinicia Playwright local y túnel SSH; comprobar nueva sesión MCP y pestaña Flow antes de cargar referencia/generar. No repetir KEY_TABLE.png.

- Retoma autorizada 2026-10-28: usuario reitera una sola corrección/regeneración si falla el primer vídeo (máximo 2 por plano), formato 9:16 y comienzo inmediato. KEY_TABLE revisada nuevamente, conservada. Servidor MCP responde initialize HTTP 200 y initialized 202, pero browser_snapshot y tools/list agotan espera sin respuesta; pestaña y ajustes actuales no verificables. 0/2 vídeos enviados. Pendiente conexión efectiva de extensión/diagnóstico local; no confundir servidor accesible con control de Chrome.
- Reintento posterior exitoso: control de Chrome confirmado en proyecto 3bf0acb8-9167-4f46-a14a-7310fb2a7dd4 («oct 28 - 07:38»). 9:16 y x1 comprobados; Veo 3.1 Fast seleccionado y guardado. KEY_TABLE.png subida y adjunta al chat. Enviado prompt EP03_SH01 al agente Flow; estado «Pensando», pendiente confirmación/generación. No reenviar sin comprobar estado para evitar duplicados. Cliente temporal /tmp/flow-mcp-call.py y sesión /tmp/flow-session.json.
- EP03_SH01: Flow informa Veo Fast imagen-a-vídeo de 8 s en este plan. Confirmado generar 8 s para recortar a 5 s; un único vídeo, 9:16. Pulsado «Aprobar» en solicitud explícita de 1 vídeo por 20 puntos a las 12:55 UTC; contar como primer intento enviado (1/2) hasta conocer resultado. No duplicar orden. Pendiente resultado, descarga y revisión.
- V1 descargada a shots/EP03_SH01_V1.mp4: 8 s, 720×1280, 24 fps. Revisadas 16 muestras: llave/dibujo conservados, pero zoom progresivo incumple cámara fija. Recomendada y enviada única corrección (2/2), aprobada por 20 puntos; prompt guardado en VIDEO_PROMPTS/GOOGLE_FLOW/EP03_SH01_CORRECCION.txt. No generar una tercera. Pendiente resultado y oficialización de V2 según delegación.

- EP03_SH01 cerrado bajo delegación: FINAL proviene de V2, 5 s/720×1280/24 fps/120 frames/sin audio, decodificación correcta. V2 añade segunda llave y mano: incumplimiento visual explícito; conservada por mandato de conservar segunda, sin tercera. Descartes locales del mismo plano eliminados tras verificar FINAL; resultados fuente siguen en Flow. Plano activo EP03_SH02, ALBA_DOOR existente revisada, compatible; carga en curso.
- EP03_SH02 V1 descargada/revisada: persona extra cruza detrás de Alba al comienzo. Enviada única corrección para Alba sola y puerta cerrada, aprobada 20 puntos; 2/2 intentos, pendiente resultado. REPORT_RESPONSABLE.png generada/revisada para SH03, texto «Responsable: Alba Vidal» correcto; tarjeta y prompt actualizados, original conservado.

- Reconexión comprobada 2026-10-28: túnel y Playwright operativos (initialize 200, initialized 202, browser_snapshot 200). Chrome muestra Flow, proyecto 5de132dd-1fd3-4fc6-bc17-448187668ac3 («oct 28 - 14:37»), biblioteca vacía e insignia PLUS. Proyecto diferente al de la generación pendiente de SH02; no confundirlos ni reenviar generación. Esta comprobación solo leyó la pestaña, sin generar ni consumir créditos.

- Retoma solicitada: recuperar resultado pendiente SH02 y continuar EP03 con guardado en repositorio. V1 de SH02 y FINAL SH01 ya versionados en commit 816a0f5. Navegación al proyecto anterior y lectura posterior agotan 55 s; solicitud de reconectar extensión enviada al usuario. Ninguna nueva generación de vídeo enviada.
- Generada/revisada/seleccionada TWO_SHOT.png para EP03_SH08 mediante image_gen; prompt y concesiones en TWO_SHOT_GENERATION.md. Dos mujeres y abrigo vacío coherentes, pero puerta desplazada y profundidad reducida respecto al master; hem fuera de campo evita contradicción de sal S3. Vídeo pendiente.

- Reintento de conexión exitoso: leído proyecto anterior 3bf0acb8-9167-4f46-a14a-7310fb2a7dd4. La corrección SH02 muestra Error explícito, sin vídeo recuperable. Por petición nueva de regenerar el pendiente, reenviada esa corrección (reintento técnico del segundo resultado, no nueva variante creativa), solicitud de 20 puntos; aprobación enviada. Verificar resultado antes de cualquier reenvío.

- PAUSA solicitada por usuario («luego lo continuamos»). Reintento técnico SH02 aprobado por 20 puntos y observado al 99 %, todavía sin MP4 descargable al último control. Resultado en https://flow.google.com/project/3bf0acb8-9167-4f46-a14a-7310fb2a7dd4/edit/1b19b60b-1cab-4dde-93e7-fce7bbf78591 («Alba standing before closed door»). Al retomar, comprobar este resultado y descargar/revisar antes de reenviar nada; no duplicar. V1 local conservada; SH03–SH08 sin vídeos generados. Prompt de corrección guardado en EP03_SH02_CORRECCION.txt. No se enviarán más órdenes durante la pausa; la generación ya aceptada puede terminar en Flow.

- Retoma 2026-10-29 autorizada: Chrome/Flow operativo. El reintento pendiente SH02 terminó en Error (verificado en chat; descarga deshabilitada). Reenviada la misma corrección como reintento técnico del segundo resultado, aprobada una salida Veo 3.1 Fast/8 s/9:16 por 20 puntos a las 00:42 UTC; en cola, no duplicar. REPORT_RESPONSABLE.png revisada otra vez y carga iniciada para preparar SH03. V1 SH02 permanece conservada; ninguna nueva versión oficial todavía.
- SH02 reintento técnico completado: vista previa 8 s disponible en edit/7d990ec6-a53b-4cb5-8bc1-ea28e6a703f2; descarga original 720p solicitada, revisión pendiente. SH03: REPORT_RESPONSABLE.png cargada/adjunta y primera generación aprobada por 20 puntos a las 00:44 UTC (1/2), 8 s para recortar a 6 s; en cola. No reenviar ninguno.
- SH02 oficializado bajo delegación: FINAL de V2, 7 s/720×1280/24 fps/168 fotogramas/sin audio, decodificación correcta. Revisión de 16 muestras: Alba sola, puerta cerrada y encuadre estable; descartes locales del mismo plano eliminados tras verificar. SH03 V1 descargada/revisada: añade manos y levanta papel; enviada única corrección (2/2), aprobada 00:46 UTC, priorizando papel/texto estáticos sobre movimiento de cámara. SH04 referencia INES_TABLE revisada, carga en curso.

- SH03 oficializado desde V2: 6 s/720×1280/24 fps/144 frames/sin audio, verificado. Texto estable y sin manos; concesión cámara fija. Descartes locales eliminados tras verificación. SH04 primera generación aprobada 00:48 UTC (1/2); SH05 referencia S2 revisada y carga en preparación.
- SH04 V1 descargada/revisada: abre la boca entre aproximadamente 1–4 s. Corrección preparada para labios siempre cerrados (segunda y última variante). SH05 primera generación aprobada 00:49 UTC (1/2), 8 s para montaje de 5 s, pendiente resultado.
- SH04 corrección aprobada 00:51 UTC (2/2); pendiente descarga/revisión, no tercera. SH05 V1 sigue pendiente. COAT_COLLAR revisada para SH06: cuello hueco y abrigo vacío, referencia subida en preparación, aún 0/2 vídeos.

- SH04 oficial desde V2 (8 s/192 frames/sin audio, verificado), con concesiones explícitas: labios entreabiertos al inicio, acercamiento excesivo y mirada final derecha; conservado por mandato segunda sin tercera. SH05 V1 revisada: chorro, gotas repetidas y pipeta móvil; corrección única aprobada 00:53 UTC (2/2). SH06 V1 aprobada 00:52 UTC (1/2), pendiente revisión.

- Cierre 2026-10-29 00:54 UTC: SH05 corrección también rechazada por cuota diaria (Error explícito, sin cobro según Flow). SH06 sin vídeo producido por el mismo límite. No hay trabajos pendientes en cola. Detenidas nuevas órdenes; continuar cuando usuario cambie cuenta o vuelva la cuota. SH05 V1 conservada; corrección pendiente como segundo resultado, SH06 sin primera versión efectiva.

- Usuario pide terminar ajustes: generado/revisado SH05_V1_AJUSTADO_5S como provisional; original conservado. Chrome sigue en la misma cuenta con rechazo por cuota; consultado cambio de cuenta o espera. No se han reenviado generaciones.
- Retoma 2026-10-29 20:50–21:00 UTC: reconectado MCP en `localhost:8931` y abierto proyecto `6bb12840-f2cd-45a4-9055-bea65d46b4f3`.
  - `EP03_SH06`: descargada y revisada V1 (`edit/fae4b44a-4b41-4f30-92a9-a0c97cc5f8cf`, 16 muestras); descartada por mano con objeto peludo entre 1,0–4,2 s. Creado `EP03_SH06_CORRECCION.txt`, enviada y aprobada única corrección (2/2, 20 puntos). Descargada y revisada V2 (`edit/9232e433-81db-4772-b31b-0d47d17b0f35`, 16 muestras): presenta breve intrusión de dos manos tocando las solapas en ~0,3–1,4 s y abrigo vacío e inmóvil de 1,5 a 8,0 s. Oficializado `shots/EP03_SH06_FINAL.mp4` (8 s, 720×1280, 24 fps, 192 frames, sin audio) por mandato de conservar segunda versión sin tercera, documentando esa limitación; eliminados descartes locales tras verificar.
  - `EP03_SH07`: descargada y revisada V1 (`edit/3f248ada-ad7e-4651-b743-4d643fd894a4`, 16 muestras): cierra los ojos suavemente (~0,5–1,0 s), los mantiene cerrados (~1,0–2,5 s) y los abre (~3,0 s) sosteniendo mirada baja hasta 6 s, boca cerrada y cámara fija, con leve giro frontal de cabeza como concesión menor. Oficializado `shots/EP03_SH07_FINAL.mp4` (tramo 0–6 s, 6 s exactos, 720×1280, 24 fps, 144 frames, sin audio); eliminado descarte local tras verificar.
  - `EP03_SH08`: adjuntada `TWO_SHOT.png` y aprobada V1 (1/2, 20 puntos). Descargada y revisada V1 (`edit/ff03bd4e-90ca-4b31-8bc5-7220f09172f9`, 16 muestras): Alba e Inés a ambos lados del abrigo vacío con puerta cerrada detrás, Inés eleva sutilmente la barbilla (~0,5–2,5 s) con labios cerrados y ambas mantienen la posición hasta 8 s; concesión menor de leve reencuadre suave en 0–1,5 s. Oficializado `shots/EP03_SH08_FINAL.mp4` (8 s, 720×1280, 24 fps, 192 frames, sin audio); eliminado descarte local tras verificar. Episodio 3 completado (8/8 planos).
