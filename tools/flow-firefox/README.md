# Flow desde Firefox de tu computadora

Prueba de conexión para el plano EP01_SH04. Usa tu Firefox ya autenticado; no abre otro perfil ni mueve cookies. **Preparado, todavía no validado en el Firefox del usuario.**

## Pasos en tu computadora Linux

1. Descarga `FLOW-FIREFOX-LOCAL.zip` desde el explorador de archivos de Codespaces (clic derecho → Descargar) y extráelo.
2. Abre una terminal **local**, entra en la carpeta extraída y ejecuta `bash conectar-linux.sh`. Si `gh` pide iniciar sesión, ejecuta `gh auth login` y vuelve a intentarlo. Mantén abierta la terminal. Este túnel depende de tu acceso GitHub al Codespace.
3. En Firefox abre `about:debugging#/runtime/this-firefox`, pulsa **Cargar complemento temporal** y elige `extension/manifest.json` de la carpeta extraída.
4. En la terminal de **Codespaces**, consulta tu clave con `cat ~/.local/share/master-series-flow-firefox/clave.txt`. No la envíes por el chat: pégala en el campo de la extensión.
5. Vuelve a la pestaña con tu proyecto Flow ya abierto. En el menú de extensiones de Firefox, abre **Flow · conexión local**, pega la clave y pulsa **Conectar**. Espera unos segundos y abre otra vez el panel para comprobar que dice **Conectado a Flow**. Avísale al asistente y deja esa pestaña visible.

Solo controla la pestaña elegida de `flow.google.com` o `labs.google/fx/`. Puede leer la interfaz, pulsar controles, introducir el prompt, cargar la referencia PNG y tomar capturas de la pestaña activa. No solicita acceso a cookies ni a cuentas.google.com; no incluye código para leer contraseñas. No se envían órdenes de generación automáticamente al conectar.

**Detener** corta la recepción de órdenes nuevas; una acción ya iniciada puede terminar. Cerrar Firefox elimina la instalación temporal. Para quitar también el túnel, pulsa Ctrl+C en la terminal local. No publiques el puerto 8765 ni compartas la clave. La extensión conserva la clave solo en memoria hasta desconectar/cerrar.

## En Codespaces (asistente)

Iniciar `python3 tools/flow-firefox/bridge.py`; escucha solo en loopback. El túnel SSH reenvía el puerto a loopback del equipo del usuario. La conexión HTTP exige una clave privada; no publica CORS para webs.

Estado: `python3 tools/flow-firefox/control.py --estado`.
Orden por stdin: `{"op":"snapshot"}`. Usar los identificadores de esa instantánea para `click`, `fill` o `upload`; volver a inspeccionar después de cambios de interfaz. Captura: `{"op":"screenshot"}` con `control.py --imagen /tmp/flow.png`.

Una generación de EP01_SH04 y revisión antes de otra. No comprar créditos ni reintentar clics de generación sin comprobar el resultado. No interactuar durante login. La compatibilidad de carga PNG, edición y captura requiere una prueba en Firefox real antes de generar.

Fuentes: [instalación temporal de Mozilla](https://extensionworkshop.com/documentation/develop/temporary-installation-in-firefox/), [túnel mediante GitHub CLI](https://cli.github.com/manual/gh_codespace_ssh).
