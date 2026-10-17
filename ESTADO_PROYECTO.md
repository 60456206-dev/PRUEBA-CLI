# Dónde nos quedamos

Actualizado: 2026-10-17.

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
