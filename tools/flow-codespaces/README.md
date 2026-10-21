# Flow dentro de Codespaces

Escritorio remoto real con Chromium, TigerVNC y noVNC. No hace falta descargar ni extraer el ZIP del lanzador local. El usuario introduce las credenciales en la página oficial de Google dentro del escritorio. El asistente puede operar el mismo escritorio mediante DISPLAY=:42 y xdotool después del inicio de sesión; la automatización de Flow aún no está validada.

## Arranque

Las dependencias ya están instaladas en el Codespace actual. Tras una reconstrucción:

```bash
bash tools/flow-codespaces/instalar.sh
```

Iniciar:

```bash
python3 tools/flow-codespaces/escritorio.py iniciar
```

En PUERTOS, reenviar **6080**, con visibilidad **Private/Privado**. Abrir la URL que imprime el comando. noVNC pide una clave del escritorio, visible solo ejecutando en la terminal:

```bash
cat ~/.local/share/master-series-flow-codespaces/clave.txt
```

No es la contraseña de Google. Dentro del escritorio, pulsar Create with Google Flow e iniciar sesión en Google. No es necesario iniciar sesión en Chromium ni activar su sincronización. Si Google o el centro educativo rechaza el acceso, no eludirlo: comunicar el mensaje sin compartir contraseñas/códigos. No se ha comprobado la compatibilidad del acceso institucional.

## Estado y cierre

```bash
python3 tools/flow-codespaces/escritorio.py estado
python3 tools/flow-codespaces/escritorio.py detener
```

Al parar Codespaces se detienen los procesos; volver a iniciar al reanudar. La sesión se conserva en un perfil separado en `~/.local/share/master-series-flow-codespaces/browser`, fuera del repositorio. Los logs, Xauthority y clave también están fuera del repositorio con permisos restringidos. No compartir esa carpeta.

VNC escucha solo en loopback 5942 y requiere contraseña; noVNC solo en loopback 6080, publicado mediante el túnel autenticado de GitHub. No se abre un puerto de depuración de Chromium. No reenviar 5942 ni convertir 6080 en público.

Limitación comprobada del contenedor: Chromium falla al crear namespaces para su sandbox. Por eso este lanzador usa `--no-sandbox`; el navegador no tiene su aislamiento interno habitual. Perfil dedicado únicamente a este trabajo, dentro del Codespace. No interpretar la contraseña del escritorio como sustituto del sandbox.

## Alcance autorizado

Solo EP01_SH03, una generación antes de revisar, tolerar errores menores si comunica la acción, detenerse ante límites y no comprar créditos. No se ha generado vídeo ni probado login. El agente debe esperar a que el usuario termine el acceso antes de inspeccionar/interactuar con la cuenta. No registrar credenciales, cookies ni códigos; no tomar capturas durante la introducción de credenciales.

Referencia oficial: [puertos de Codespaces](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace), [noVNC](https://novnc.com/noVNC/).
