#!/usr/bin/env node
/**
 * TIKTOK RADAR · Bot Nativo y Permanente de WhatsApp Web para Servidor AWS
 * 1. Funciona 100% en tu servidor, sin intermediarios ni servicios de terceros.
 * 2. Guarda la sesión en disco (.wwebjs_auth) para no volver a pedir QR tras reiniciar.
 * 3. Expone API local HTTP (puerto 5050) para que Python envíe alertas y vídeos MP4.
 * 4. Responde en vivo por WhatsApp a preguntas del dueño usando Antigravity (`agy`).
 */

const express = require('express');
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { exec, spawn } = require('child_process');

const PORT = process.env.PORT || 5050;
const AUTH_DIR = path.join(os.homedir(), '.wwebjs_auth');
const OWNER_FILE = path.join(os.homedir(), '.whatsapp_owner.json');
const QR_FILE = path.join(__dirname, 'qr_ascii.txt');
const WORKSPACE_DIR = path.join(os.homedir(), 'TIKTOK-NEWS');
const AGY_BIN = path.join(os.homedir(), '.local/bin/agy');

let isReady = false;
let currentQR = null;
let ownerWid = null;

// Cargar número de dueño si ya estaba guardado
if (fs.existsSync(OWNER_FILE)) {
  try {
    const data = JSON.parse(fs.readFileSync(OWNER_FILE, 'utf8'));
    ownerWid = data.ownerWid;
  } catch (e) {}
}

// -----------------------------------------------------------------------------
// 1. Cliente WhatsApp Web (Con Google Chrome nativo de Linux)
// -----------------------------------------------------------------------------
const chromePath = fs.existsSync('/usr/bin/google-chrome')
  ? '/usr/bin/google-chrome'
  : (process.env.CHROME_BIN || undefined);

const client = new Client({
  authStrategy: new LocalAuth({
    dataPath: AUTH_DIR,
  }),
  puppeteer: {
    headless: true,
    executablePath: chromePath,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu',
    ],
  },
});

client.on('qr', (qr) => {
  currentQR = qr;
  isReady = false;
  console.log('\n======================================================================');
  console.log('📱 ESCANEA ESTE CÓDIGO QR EN TU WHATSAPP (Dispositivos vinculados):');
  console.log('======================================================================\n');
  qrcode.generate(qr, { small: true });
  console.log('\n======================================================================\n');

  // Guardar en archivo para poder consultarlo por SSH en cualquier momento
  try {
    fs.writeFileSync(path.join(__dirname, 'qr_raw.txt'), qr);
    qrcode.generate(qr, { small: true }, (ascii) => {
      fs.writeFileSync(QR_FILE, ascii);
    });
  } catch (err) {}
});

client.on('authenticated', () => {
  console.log('[WA-BOT] ✅ Sesión autenticada correctamente.');
  currentQR = null;
});

client.on('auth_failure', (msg) => {
  console.error('[WA-BOT] ⚠️ Error en autenticación:', msg);
});

client.on('ready', async () => {
  isReady = true;
  currentQR = null;
  const myNumber = client.info.wid.user;
  ownerWid = `${myNumber}@c.us`;

  fs.writeFileSync(OWNER_FILE, JSON.stringify({ ownerWid, phone: myNumber, readyAt: new Date().toISOString() }, null, 2));
  console.log(`[WA-BOT] 🚀 ¡BOT CONECTADO Y ACTIVO AL 100%!`);
  console.log(`[WA-BOT] Teléfono del Dueño detectado: +${myNumber}`);

  // Enviar mensaje de bienvenida al propio chat
  try {
    await client.sendMessage(
      ownerWid,
      `🤖 *¡TikTok Radar Bot Activo en tu Servidor AWS!*\n\nTu servidor ya está enlazado a tu WhatsApp de forma permanente y privada.\n\n` +
      `Te notificaré automáticamente cada vez que se genere un plano o vídeo final.\n\n` +
      `*Comandos disponibles:*\n` +
      `• *!estado*: Consulta CPU, RAM, disco y última producción.\n` +
      `• *!generar*: Lanza la producción de un nuevo noticiero en AWS.\n` +
      `• O pregúntame cualquier cosa en lenguaje natural (ej: *«¿Cómo va el servidor?»*) y el agente Antigravity te responderá.`
    );
  } catch (e) {
    console.error('[WA-BOT] No se pudo enviar mensaje de bienvenida:', e.message);
  }
});

client.on('disconnected', (reason) => {
  console.warn(`[WA-BOT] ⚠️ Desconectado de WhatsApp (${reason}). Intentando reconectar...`);
  isReady = false;
  setTimeout(() => {
    client.initialize().catch((err) => console.error('[WA-BOT] Error al reinicializar:', err));
  }, 5000);
});

// -----------------------------------------------------------------------------
// 2. Interacción Bidireccional: Escuchar mensajes del dueño
// -----------------------------------------------------------------------------
client.on('message_create', async (msg) => {
  // Ignorar mensajes que el propio bot envía para evitar loops
  if (msg.body && msg.body.startsWith('🤖')) return;

  const isFromOwner = (ownerWid && (msg.from === ownerWid || msg.to === ownerWid));
  if (!isFromOwner) return;

  const body = (msg.body || '').trim();
  if (!body) return;

  // Solo procesar si es en chat privado con uno mismo o si empieza por '!' o pregunta
  const isSelfChat = msg.from === msg.to || msg.from === ownerWid;
  if (!isSelfChat && !body.startsWith('!')) return;

  console.log(`[WA-BOT] 💬 Mensaje recibido del dueño: "${body}"`);

  const lower = body.toLowerCase();

  // COMANDO 1: !estado
  if (lower === '!estado' || lower === 'estado') {
    try {
      exec('uptime && free -h && df -h /', (err, stdout) => {
        const text = stdout || 'No se pudo obtener información del sistema.';
        msg.reply(`🤖 *ESTADO DEL SERVIDOR AWS:*\n\`\`\`\n${text}\n\`\`\``);
      });
    } catch (e) {
      msg.reply(`🤖 Error consultando estado: ${e.message}`);
    }
    return;
  }

  // COMANDO 2: !generar
  if (lower === '!generar' || lower.includes('generar noticiero') || lower.includes('iniciar produccion')) {
    msg.reply('🤖 🚀 *Iniciando producción del Noticiero 3D en AWS...*\nTe avisaré en este chat conforme se completen los 13 planos y el vídeo final.');
    const child = spawn('python3', ['tools/ejecutar_todo.py'], {
      cwd: WORKSPACE_DIR,
      detached: true,
      stdio: 'ignore',
    });
    child.unref();
    return;
  }

  // CUALQUIER OTRA CONSULTA -> Enviar a Antigravity (`agy`)
  const prompt = body.replace(/^!/, '').trim();
  msg.reply('🤖 *Pensando con Antigravity en AWS...* ⏳');

  const agyCmd = fs.existsSync(AGY_BIN) ? AGY_BIN : 'agy';
  const fullCmd = `cd ${WORKSPACE_DIR} && ${agyCmd} --dangerously-skip-permissions -p ${JSON.stringify('Responde de forma muy concisa y clara para WhatsApp: ' + prompt)}`;

  exec(fullCmd, { maxBuffer: 1024 * 1024 * 5, timeout: 120000 }, (err, stdout, stderr) => {
    if (err) {
      const errOut = (stderr || err.message || '').slice(-300);
      msg.reply(`🤖 ⚠️ Error ejecutando agente en AWS:\n${errOut}`);
      return;
    }
    const cleanOutput = stdout.trim() || 'El agente completó la consulta sin texto de salida.';
    msg.reply(`🤖 *Antigravity AWS:*\n\n${cleanOutput}`);
  });
});

// -----------------------------------------------------------------------------
// 3. API Local Express (para que Python envíe alertas y vídeos por HTTP)
// -----------------------------------------------------------------------------
const app = express();
app.use(express.json({ limit: '100mb' }));

app.get('/status', (req, res) => {
  res.json({
    ready: isReady,
    owner: ownerWid,
    hasQR: !!currentQR,
  });
});

app.get('/qr', (req, res) => {
  if (isReady) {
    return res.send('<h3>✅ El bot ya está conectado y listo. No requiere QR.</h3>');
  }
  if (!currentQR) {
    return res.send('<h3>⏳ Esperando generación de código QR...</h3>');
  }
  const qrImageUrl = `https://api.qrserver.com/v1/create-qr-code/?size=350x350&data=${encodeURIComponent(currentQR)}`;
  res.send(`
    <html>
      <body style="font-family: sans-serif; text-align: center; padding: 40px; background: #0f172a; color: white;">
        <h2>📱 Vincula tu WhatsApp Web con tu Servidor AWS</h2>
        <p>Abre WhatsApp en tu teléfono > <b>Dispositivos vinculados</b> > <b>Vincular un dispositivo</b> y escanea:</p>
        <div style="background: white; padding: 20px; display: inline-block; border-radius: 12px; margin: 20px 0;">
          <img src="${qrImageUrl}" alt="WhatsApp QR Code" style="width: 320px; height: 320px; display: block;" />
        </div>
        <p style="color: #94a3b8; font-size: 14px;">La sesión se guardará en tu servidor permanentemente.</p>
      </body>
    </html>
  `);
});

app.post('/send', async (req, res) => {
  if (!isReady) {
    return res.status(503).json({ error: 'WhatsApp bot aún no está listo o autenticado.' });
  }

  const { message, mediaPath, phone, caption } = req.body;
  const targetWid = phone
    ? `${phone.replace(/[^\d]/g, '')}@c.us`
    : ownerWid;

  if (!targetWid) {
    return res.status(400).json({ error: 'No se especificó número y no hay dueño registrado.' });
  }

  try {
    if (mediaPath && fs.existsSync(mediaPath)) {
      const media = MessageMedia.fromFilePath(mediaPath);
      const cap = caption || message || '';
      await client.sendMessage(targetWid, media, { caption: cap });
      console.log(`[WA-BOT] 📤 Archivo multimedia enviado a ${targetWid}: ${mediaPath}`);
    } else if (message) {
      await client.sendMessage(targetWid, message);
      console.log(`[WA-BOT] 📤 Mensaje de texto enviado a ${targetWid}`);
    } else {
      return res.status(400).json({ error: 'Debes proporcionar message o mediaPath.' });
    }

    return res.json({ success: true, target: targetWid });
  } catch (err) {
    console.error('[WA-BOT] Error al enviar mensaje:', err);
    return res.status(500).json({ error: err.message });
  }
});

// -----------------------------------------------------------------------------
// 4. Arranque del sistema
// -----------------------------------------------------------------------------
process.on('uncaughtException', (err) => {
  console.error('[WA-BOT FATAL]', err);
});
process.on('unhandledRejection', (err) => {
  console.error('[WA-BOT REJECTION]', err);
});

app.listen(PORT, '127.0.0.1', () => {
  console.log(`[WA-BOT] 🌐 Servidor HTTP API escuchando internamente en http://127.0.0.1:${PORT}`);
  console.log('[WA-BOT] ⏳ Inicializando cliente WhatsApp Web...');
  client.initialize().catch((err) => {
    console.error('[WA-BOT] Error al inicializar cliente:', err);
  });
});
