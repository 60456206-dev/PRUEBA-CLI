# GUÍA DE MONITOREO Y BOT DE WHATSAPP PARA EL SERVIDOR AWS (`TIKTOK-NEWS`)

Esta guía explica cómo activar el **Bot Monitor de WhatsApp** en tu servidor AWS para que:
1. Te envíe alertas automáticas a tu WhatsApp personal cada vez que termine un plano (`SH01`..`SH13`) o cuando el vídeo final (`NOTICIERO_FINAL_62S.mp4`) esté listo.
2. Si le escribes un mensaje por WhatsApp (ej. *«¿Cómo va el render?»* o *«¿Cuánto falta?»*), el servidor invoque automáticamente a **Antigravity (`agy --dangerously-skip-permissions`)** y te responda directamente por WhatsApp con el estado del servidor.

---

## 1. Configuración Gratuita en 2 Minutos (Sin Tarjetas de Crédito)

Usamos la API gratuita de **CallMeBot para WhatsApp**, que no requiere suscripciones, ni números de empresa, ni configurar Meta Developers.

### Paso 1: Obtener tu API Key personal de WhatsApp (1 minuto)
1. En tu teléfono, agrega a tus contactos el número oficial del bot de CallMeBot:  
   👉 **`+34 644 59 87 23`** (o guarda el enlace directo: [wa.me/34644598723](https://wa.me/34644598723))
2. Envíale este mensaje exacto desde tu WhatsApp:
   ```text
   I allow callmebot to send me messages
   ```
3. En 5 segundos, el bot te responderá con tu mensaje de confirmación y tu **apikey**:
   > *«API Key Generated: 123456»*

---

## 2. Guardar tu Configuración en el Servidor AWS

Conéctate por SSH a tu servidor AWS y crea tu archivo de configuración:

```bash
cat << 'EOF' > ~/.whatsapp_config.json
{
  "provider": "callmebot",
  "phone": "+519XXXXXXXX",
  "apikey": "TU_API_KEY_AQUI"
}
EOF
```
*(Reemplaza `+519XXXXXXXX` por tu número con código de país de Perú o tu país, y `TU_API_KEY_AQUI` por la clave que te dio el bot).*

### Probar que funcione el envío
Ejecuta este comando en el servidor:
```bash
python3 ~/TIKTOK-NEWS/tools/whatsapp_monitor.py --test-msg "🚀 Probando conexión WhatsApp desde Servidor AWS TikTok Radar"
```
¡Recibirás el mensaje en tu WhatsApp al instante!

---

## 3. Cómo Funciona el Supervisor Autónomo con `agy`

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
