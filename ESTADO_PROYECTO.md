# Dónde nos quedamos

Actualizado: 2026-10-21.

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
