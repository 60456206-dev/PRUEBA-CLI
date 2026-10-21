# Inicio local de Flow en Linux

Ejecutar en el escritorio de la computadora del usuario, con Python 3 y Chrome/Chromium instalados:

```bash
bash tools/flow-local/iniciar.sh
```

Abre Google Flow y una ayuda con la imagen y el prompt actual del plano 3. El inicio de sesión se realiza únicamente en Google, incluyendo el acceso institucional y segundo factor. Si Google o la institución impide el acceso, detenerse: este lanzador no elude restricciones.

El perfil de navegador se conserva fuera del repositorio, en `${XDG_DATA_HOME:-$HOME/.local/share}/master-series-flow/browser`. No compartir ese directorio. No se abre puerto de depuración ni se exportan cookies. Cerrar la ventana conserva la sesión como en un navegador habitual.

**Alcance:** prepara archivos y abre el navegador local; no concede control al asistente remoto, no rellena Flow ni genera/descarga automáticamente. La conexión remota y automatización siguen pendientes. El usuario genera una variante, descarga el vídeo y lo comparte para revisión. No hay reintentos automáticos ni compras.

Comprobación de archivos sin escritorio:

```bash
bash tools/flow-local/iniciar.sh --comprobar
```

No se ha probado el inicio de sesión institucional ni la interfaz de Flow desde este entorno sin escritorio. La disponibilidad de modelos, duraciones y funciones depende de la cuenta.
