# Dónde nos quedamos

Actualizado: 2026-10-17.

- Proyecto: `MASTER_SERIES_PACKAGE`. Estamos generando vídeos desde imágenes para el episodio 1: 8 planos, 51 segundos previstos. La temporada tiene 48 planos.
- Usuario: está en Perú, es estudiante y no tiene GPU dedicada. Prefiere opciones gratuitas desde el navegador. Hemos investigado PixVerse, Hailuo, Google Flow y demos de Wan; verificar ofertas vigentes antes de prometer créditos.
- Plano 1 elegido por el usuario: `shots/EP01_SH01_PIXVERSE_SIN_MARCA_PREVIEW.mp4`. Estaba borrado localmente, pero se recuperó de Git. No sustituirlo por la antigua reconstrucción `EP01_SH01_FINAL.mp4`.
- La limpieza anterior se limitó a `shots`. Después se añadieron los vídeos del plano 2. No interpretar aquella limpieza como permiso permanente para borrar nuevos archivos.
- Plano 2: imagen `SHOT_REFERENCES/INES_TABLE.png`. El original de Hailuo con marca de agua fue eliminado por petición explícita del usuario; solo se conserva la copia limpia del plano 2.
- Copia limpia creada: `shots/EP01_SH02_HAILUO_SIN_MARCA_PREVIEW.mp4`. Marca inferior eliminada mediante recorte a 720×1280 (9:16), El original se eliminó después por petición del usuario. Tiene 124 fotogramas a 24 fps: unos 5,17 segundos. Se conservó el audio original; el montaje prevé sonido por separado.
- Revisión visual del plano 2: Inés baja la mirada y luego mira a la izquierda con labios cerrados, acorde con el prompt. El acercamiento es más fuerte de lo pedido y faltan 0,83 segundos para los 6 previstos. Es una preview; todavía no se ha decidido cómo resolver estas diferencias ni aceptado como definitivo.
- Añadidos 48 prompts en `VIDEO_PROMPTS/GOOGLE_FLOW`, con README, enlaces en las tarjetas individuales y recopilaciones por episodio, y acceso desde `GENERATE_THIS_FIRST.md`. Enlaces/duraciones revisados; no probados generando en Flow. La guía indica imágenes pendientes de crear o recuperar.
- Para el plano 2 están `VIDEO_PROMPTS/HAILUO/EP01_SH02_HAILUO.txt`, `VIDEO_PROMPTS/PIXVERSE/EP01_SH02_PIXVERSE.txt` y `VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH02_GOOGLE_FLOW.txt`.
- Pendiente: resolver/aceptar el plano 2 y seguir con los planos 3–8. El usuario pidió dejar los nombres finales y ajustes de referencias del montaje para cuando estén todos los planos. No renombrar automáticamente los elegidos a `_FINAL`.
- Antes de concluir que un vídeo no existe, comprobar disco, `git status` e historial: el archivo SIN_MARCA del plano 1 sí estaba en Git aunque faltara en disco.

Este archivo conserva el contexto dentro del repositorio; no supone memoria automática fuera de él. Leerlo al retomar y actualizarlo con nuevos acuerdos.
