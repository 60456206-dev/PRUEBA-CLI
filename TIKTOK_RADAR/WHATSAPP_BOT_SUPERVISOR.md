# GUÍA DEL BOT DE WHATSAPP PROPIO Y MONITOREO EN AWS (`TIKTOK-NEWS`)

Esta guía explica cómo activar tu **Bot Propio de WhatsApp Web** en tu servidor AWS para:
1. **Recibir alertas y vídeos directamente en tu WhatsApp** cada vez que termine un plano (`SH01`..`SH13`) o cuando el vídeo final (`NOTICIERO_FINAL_62S.mp4`) esté listo.
2. **Hablar directamente con Antigravity (`agy`) desde tu WhatsApp**: le preguntas cómo va el servidor o le pides generar el noticiero del día y el agente ejecuta las tareas y te responde en vivo.
3. **Cero intermediarios ni caídas**: corre 100% en tu servidor AWS, con persistencia 24/7 en systemd y reconexión automática.

---

## 1. Instalación y Vinculación en 1 Solo Paso (Bot Propio Nativo)

En tu servidor AWS (`~/TIKTOK-NEWS`), solo ejecuta:

```bash
cd ~/TIKTOK-NEWS
git pull origin main
bash whatsapp_bot/instalar_y_arrancar.sh
```

El script:
- Instala Node.js 20 LTS automáticamente si no lo tienes.
- Instala las dependencias (`whatsapp-web.js`, `express`).
- Configura el servicio permanente `tiktok-whatsapp-bot` en systemd.

### Vincular tu WhatsApp (Solo se hace una vez):
Ejecuta en tu terminal:
```bash
bash ~/TIKTOK-NEWS/whatsapp_bot/ver_qr.sh
```
Aparecerá el código QR en la consola. Abre WhatsApp en tu celular > **Dispositivos vinculados** > **Vincular un dispositivo** y escanea el QR.

¡Y listo! La sesión queda guardada permanentemente en el servidor (`~/.wwebjs_auth`). No volverá a pedirte QR aunque reinicies el servidor.

---

## 2. Cómo Usar el Bot desde tu WhatsApp

Una vez vinculado, el bot te enviará un mensaje automático a tu chat personal:
> 🤖 *¡TikTok Radar Bot Activo en tu Servidor AWS!*

A partir de ahí, puedes escribirle comandos o preguntas:
* `!estado`: Te devuelve el uptime, uso de RAM, CPU y disco de AWS.
* `!generar`: Lanza la producción completa del Noticiero 3D en AWS (`tools/ejecutar_todo.py`).
* Cualquier pregunta en lenguaje natural (ej: *«¿Qué noticias se escanearon hoy?»* o *«¿Cuánto pesa el último vídeo?»*): El bot ejecuta a **Antigravity (`agy --dangerously-skip-permissions`)** en AWS y te responde al WhatsApp con su respuesta.

---

## 3. Fallback Tradicional (CallMeBot / Twilio)

Si en algún momento el bot local estuviera apagado, [`tools/whatsapp_monitor.py`](tools/whatsapp_monitor.py) cuenta con fallback automático hacia `~/.whatsapp_config.json` (CallMeBot o Twilio).


El script [`tools/whatsapp_monitor.py`](tools/whatsapp_monitor.py) tiene dos modos:

### Modo A: Monitor Silencioso de Progreso (Recomendado)
Supervisa `produccion_radar.log` y la carpeta `shots/`. Cada vez que Google Flow termina de descargar y verificar un plano, te manda un mensaje como este:
> 🎬 **Plano SH03 Listo**  
> Descargado y verificado en Flow (8.2 MB)  
> Avance: 3/13 planos.

Y cuando FFmpeg termina el montaje final:
> 🎉 **¡NOTICIERO FINAL 62S TERMINADO!**  
> 📁 Carpeta: `2026-11-03_AUTONOMO`  
> 📦 Tamaño: 28.4 MB  
> 🚀 Listo para publicar en TikTok (>60s).

Para arrancarlo en segundo plano en el servidor:
```bash
cd ~/TIKTOK-NEWS
nohup python3 tools/whatsapp_monitor.py > ~/whatsapp_monitor.log 2>&1 &
```

---

### Modo B: Bot Interactivo Bidireccional con Antigravity (`agy`)

Si ejecutas el monitor con la bandera `--server`:
```bash
cd ~/TIKTOK-NEWS
nohup python3 tools/whatsapp_monitor.py --server --port 5055 > ~/whatsapp_monitor.log 2>&1 &
```

1. Levanta un servidor Webhook local en el puerto `5055`.
2. Cuando le envías un mensaje desde WhatsApp (por ejemplo: *«¿Qué plano se está generando ahora mismo?»*), el script ejecuta internamente en el servidor:
   ```bash
   agy --dangerously-skip-permissions -p "Eres el supervisor en AWS... Responde conciso para WhatsApp: <tu pregunta>"
   ```
3. `agy` lee el log, examina la carpeta de entregas y te devuelve la respuesta directamente a tu chat de WhatsApp.

---

## 4. Comandos de Control en el Servidor AWS

| Acción | Comando en el Servidor |
| :--- | :--- |
| **Ver log del monitor en vivo** | `tail -f ~/whatsapp_monitor.log` |
| **Detener el monitor de WhatsApp** | `pkill -f whatsapp_monitor.py` |
| **Comprobar si está corriendo** | `ps aux \| grep whatsapp_monitor.py` |
