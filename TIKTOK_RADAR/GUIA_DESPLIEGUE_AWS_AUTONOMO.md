# TikTok Radar · Guía de Despliegue 100% Autónomo en AWS

Cómo poner a funcionar TikTok Radar en tu servidor AWS para que **genere vídeos de forma independiente sin depender de este chat ni de tu computadora**.

---

## 1. Clonar el Repositorio en tu Servidor AWS

1. Conéctate a tu servidor AWS por SSH:
   ```bash
   ssh -i "tu-llave.pem" ubuntu@IP_DE_AWS
   ```
2. Clona este repositorio:
   ```bash
   git clone https://github.com/60456206-dev/PRUEBA-CLI.git
   cd PRUEBA-CLI
   ```
   *(Si el repositorio es privado, introduce tu usuario de GitHub y como contraseña tu **Personal Access Token (PAT)** de GitHub, o agrega una clave SSH Deploy Key).*

---

## 2. Instalar el Entorno con 1 Solo Comando

Dentro de la carpeta del proyecto en tu servidor, ejecuta nuestro script de instalación:
```bash
bash TIKTOK_RADAR/tools/instalar_servidor_aws.sh
```
Este script instala automáticamente:
* Python 3, pip, Edge-TTS, Playwright y FFmpeg.
* Google Chrome Oficial (estable).
* Escritorio ligero XFCE y xRDP para que puedas iniciar sesión visualmente.
* El lanzador de Chrome con el puerto de depuración `9222` activado.

---

## 3. Inicio de Sesión Único en Google Flow

1. En tu computadora personal, abre la terminal y haz el túnel seguro:
   ```bash
   ssh -i "tu-llave.pem" -L 3389:localhost:3389 ubuntu@IP_DE_AWS
   ```
2. Abre tu aplicación de **Escritorio Remoto (RDP)** en tu PC y conéctate a:
   ```text
   localhost:3389
   ```
3. En el escritorio de Ubuntu, abre la terminal y ejecuta:
   ```bash
   ~/iniciar_flow_chrome.sh
   ```
4. Se abrirá Google Chrome en la página de Google Flow. Inicia sesión con tu cuenta de Google **una sola vez**. Cierra el escritorio remoto. La sesión quedará guardada en el disco de AWS para siempre.

---

## 4. Cómo Automatizarlo sin Abrir Este Chat

Para que el servidor trabaje solo en segundo plano, tienes dos opciones:

### Opción A: Programación Diaria por Cron (Recomendada)
Para que el servidor genere automáticamente el noticiero todos los días (por ejemplo, a las 8:00 AM y a las 6:00 PM):
1. En la terminal de AWS ejecuta:
   ```bash
   crontab -e
   ```
2. Agrega esta línea al final del archivo:
   ```bash
   0 8,18 * * * /usr/bin/python3 /home/ubuntu/PRUEBA-CLI/TIKTOK_RADAR/tools/pipeline_autonomo.py >> /home/ubuntu/tiktok_radar.log 2>&1
   ```
3. ¡Listo! El servidor se despertará a esas horas, buscará la mejor noticia en Xataka/BBC, generará el audio de 62 segundos y los prompts sin que tú toques nada.

### Opción B: Ejecución Manual Rápida desde tu Celular o SSH
Cuando quieras un vídeo en cualquier momento sin entrar a este chat:
```bash
python3 /home/ubuntu/PRUEBA-CLI/TIKTOK_RADAR/tools/pipeline_autonomo.py
```
El vídeo y los prompts quedarán inmediatamente en `TIKTOK_RADAR/entregas/`.
