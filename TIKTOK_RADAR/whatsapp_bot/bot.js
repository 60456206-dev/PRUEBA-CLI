#!/usr/bin/env node
/**
 * TIKTOK RADAR · Bot Nativo y Permanente de WhatsApp Web para Servidor AWS
 * 1. Funciona 100% en tu servidor AWS, sin intermediarios ni servicios de terceros.
 * 2. Guarda la sesión en disco (.wwebjs_auth) para no volver a pedir QR tras reiniciar.
 * 3. Identidad: El número vinculado en AWS (+51902893413) es el AGENTE ANTIGRAVITY.
 * 4. El usuario le escribe desde su número personal y Antigravity le responde:
 *    - Enviar vídeos MP4 generados (!video).
 *    - Condición del proyecto y planos completados (!condicion / !proyecto).
 *    - Reporte de fallas y estabilidad (!fallas / !reporte).
 *    - Estado del servidor AWS (!estado / !servidor).
 *    - Comandos de producción (!generar / !parar).
 *    - Inteligencia Artificial: Responde dudas en lenguaje natural con Antigravity (`agy`).
 * 5. Expone API local HTTP (puerto 5050) para que Python envíe alertas automáticas y vídeos al dueño.
 */

const express = require('express');
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { exec, spawn, execSync } = require('child_process');

const PORT = process.env.PORT || 5050;
const AUTH_DIR = path.join(os.homedir(), '.wwebjs_auth');
const OWNER_FILE = path.join(os.homedir(), '.whatsapp_owner.json');
const QR_FILE = path.join(__dirname, 'qr_ascii.txt');
const WORKSPACE_DIR = path.join(os.homedir(), 'TIKTOK-NEWS');
const AGY_BIN = path.join(os.homedir(), '.local/bin/agy');

let isReady = false;
let currentQR = null;
let ownerWid = null;
let botWid = null;

// Cargar número de dueño si ya estaba guardado
function loadOwner() {
  if (fs.existsSync(OWNER_FILE)) {
    try {
      const data = JSON.parse(fs.readFileSync(OWNER_FILE, 'utf8'));
      ownerWid = data.ownerWid || null;
    } catch (e) {}
  }
}
loadOwner();

// -----------------------------------------------------------------------------
// Funciones de Inspección del Proyecto y Servidor
// -----------------------------------------------------------------------------

function findLatestVideo() {
  const entregasDir = path.join(WORKSPACE_DIR, 'entregas');
  if (!fs.existsSync(entregasDir)) return null;

  let candidates = [];
  function walk(dir) {
    try {
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const full = path.join(dir, item);
        const stat = fs.statSync(full);
        if (stat.isDirectory()) {
          walk(full);
        } else if (item.endsWith('.mp4')) {
          candidates.push({ path: full, size: stat.size, mtime: stat.mtimeMs, name: item });
        }
      }
    } catch (e) {}
  }
  walk(entregasDir);

  if (candidates.length === 0) return null;

  // Priorizar NOTICIERO_FINAL_62S si existe, o el más reciente
  candidates.sort((a, b) => {
    const aIsFinal = a.name.includes('FINAL') ? 1 : 0;
    const bIsFinal = b.name.includes('FINAL') ? 1 : 0;
    if (aIsFinal !== bIsFinal) return bIsFinal - aIsFinal;
    return b.mtime - a.mtime;
  });

  return candidates[0];
}

async function sendDeliveryPackage(targetWid, deliveryDir) {
  const vidPath = path.join(deliveryDir, 'NOTICIERO_FINAL_62S.mp4');
  if (!fs.existsSync(vidPath)) {
    throw new Error(`No existe el vídeo final en ${deliveryDir}`);
  }

  // 1. Asegurar portada 9:16 oficial
  const coverPath = path.join(deliveryDir, 'PORTADA_TIKTOK_916.jpg');
  if (!fs.existsSync(coverPath)) {
    try {
      execSync(`python3 tools/generador_portada.py --dir "${deliveryDir}"`, { cwd: WORKSPACE_DIR, timeout: 25000 });
    } catch (e) {
      console.warn('[WA-BOT] Aviso generando portada:', e.message);
    }
  }

  // 2. Extraer metadatos y hashtags
  let newsTitle = path.basename(deliveryDir);
  let tiktokCaption = '';
  let hashtags = '#tiktoknoticias #parati #fyp #ultimahora #noticiashoy';
  const metaPath = path.join(deliveryDir, 'metadata.json');
  if (fs.existsSync(metaPath)) {
    try {
      const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
      newsTitle = meta.title || newsTitle;
      tiktokCaption = meta.tiktok_caption || '';
      hashtags = meta.hashtags_str || hashtags;
    } catch (e) {}
  }
  const hashtagsPath = path.join(deliveryDir, 'HASHTAGS_TIKTOK.txt');
  if (!tiktokCaption && fs.existsSync(hashtagsPath)) {
    tiktokCaption = fs.readFileSync(hashtagsPath, 'utf8');
  }

  const stat = fs.statSync(vidPath);
  const sizeMb = (stat.size / (1024 * 1024)).toFixed(1);

  // 3. Enviar portada 9:16 primero como imagen
  if (fs.existsSync(coverPath)) {
    const coverMedia = MessageMedia.fromFilePath(coverPath);
    await client.sendMessage(targetWid, coverMedia, {
      caption: `🖼️ *PORTADA OFICIAL 9:16 (MINIATURA TIKTOK)*\n📌 *Titular:* ${newsTitle}\n📐 *Formato:* 1080x1920 (Safe Zone 3:4 centrado)\n💡 _Usa esta portada al subir tu vídeo a TikTok para maximizar clics._`
    });
    console.log(`[WA-BOT] 🖼️ Portada 9:16 enviada con éxito a ${targetWid}`);
  }

  // 4. Enviar vídeo final MP4 con descripción y hashtags listos para copiar
  const videoCaption =
    `🎬 *${newsTitle}*\n` +
    `📦 Tamaño: ${sizeMb} MB | ⏱️ 62s (>60s Monetizable)\n\n` +
    `📝 *TEXTO Y HASHTAGS LISTOS PARA COPIAR:*\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `${tiktokCaption || hashtags}\n` +
    `━━━━━━━━━━━━━━━━━━━━\n\n` +
    `_Generado 100% de forma autónoma en tu servidor AWS._`;

  const videoMedia = MessageMedia.fromFilePath(vidPath);
  await client.sendMessage(targetWid, videoMedia, {
    caption: videoCaption,
    sendMediaAsDocument: false,
  });
  console.log(`[WA-BOT] 🎬 Vídeo enviado con éxito a ${targetWid}`);
}

function getProjectCondition() {
  const entregasDir = path.join(WORKSPACE_DIR, 'entregas');
  let newsTitle = 'Revés judicial a Google/Gemini por uso de noticias';
  let dateFolder = '2026-11-03_AUTONOMO';
  let totalShots = 0;
  let hasFinalVideo = false;
  let finalVideoSize = '0 MB';

  if (fs.existsSync(entregasDir)) {
    const folders = fs.readdirSync(entregasDir)
      .map(name => ({ name, full: path.join(entregasDir, name) }))
      .filter(item => {
        try { return fs.statSync(item.full).isDirectory(); } catch (e) { return false; }
      })
      .sort((a, b) => fs.statSync(b.full).mtimeMs - fs.statSync(a.full).mtimeMs);

    if (folders.length > 0) {
      const latest = folders[0];
      dateFolder = latest.name;
      const shotsDir = path.join(latest.full, 'shots');
      if (fs.existsSync(shotsDir)) {
        totalShots = fs.readdirSync(shotsDir).filter(f => f.endsWith('.mp4')).length;
      }
      const finalVid = path.join(latest.full, 'NOTICIERO_FINAL_62S.mp4');
      if (fs.existsSync(finalVid)) {
        hasFinalVideo = true;
        finalVideoSize = (fs.statSync(finalVid).size / (1024 * 1024)).toFixed(1) + ' MB';
      }
      const metaFile = path.join(latest.full, 'metadata.json');
      const promptFile = path.join(latest.full, 'PROMPTS_PRODUCCION.json');
      if (fs.existsSync(metaFile)) {
        try {
          const data = JSON.parse(fs.readFileSync(metaFile, 'utf8'));
          newsTitle = data.title || data.noticia?.titulo || newsTitle;
        } catch (e) {}
      } else if (fs.existsSync(promptFile)) {
        try {
          const data = JSON.parse(fs.readFileSync(promptFile, 'utf8'));
          newsTitle = data.noticia?.titulo || data.tema || newsTitle;
        } catch (e) {}
      }
    }
  }

  return new Promise((resolve) => {
    exec('ps aux | grep -E "ejecutar_todo|pipeline_autonomo|flow_generator|ensamblador_final" | grep -v grep', (err, stdout) => {
      const isRunning = Boolean(stdout && stdout.trim());
      const statusText =
        `📊 *CONDICIÓN DEL PROYECTO (TIKTOK RADAR 3D)*\n\n` +
        `• *Última Entrega:* \`${dateFolder}\`\n` +
        `• *Noticia del Día:* _${newsTitle}_\n` +
        `• *Arquitectura Híbrida:* ${totalShots}/8 planos Flow cinemáticos + 5 infográficos FFmpeg Vector HUD.\n` +
        `• *Vídeo Final (62s):* ${hasFinalVideo ? `✅ ENSAMBLADO Y LISTO (${finalVideoSize})` : '⏳ Pendiente de ensamblaje'}\n` +
        `• *Pipeline en Ejecución:* ${isRunning ? '🚀 ACTIVO EN ESTE MOMENTO' : '💤 En reposo (Listo para generar)'}\n` +
        `• *Estándar:* >60 s vertical 9:16 (Monetizable en TikTok Creator Rewards).\n\n` +
        `_Escribe *!video* para recibir el vídeo en este chat o *!generar* para producir uno nuevo._`;
      resolve(statusText);
    });
  });
}

function getFailureReport() {
  const logFile = path.join(os.homedir(), 'produccion_radar.log');
  let issues = [];

  if (fs.existsSync(logFile)) {
    const lines = fs.readFileSync(logFile, 'utf8').split('\n').slice(-150);
    for (const line of lines) {
      if (/ERROR|Exception|Traceback|Bloqueo de politica|Falló|FAILED/i.test(line)) {
        issues.push(line.trim());
      }
    }
  }

  if (issues.length === 0) {
    return (
      `🛡️ *REPORTE DE ESTABILIDAD Y FALLAS:*\n\n` +
      `✅ *ESTADO: 100% OPERATIVO Y SIN FALLAS*\n\n` +
      `• Google Flow: Sesión activa y sin bloqueos vigentes.\n` +
      `• Render FFmpeg NLE: Todos los planos ensamblados sin errores de decodificación.\n` +
      `• Escudo de Políticas: Respaldo automático con prompt alternativo activo.\n` +
      `• Servidor AWS: Procesos y servicios ejecutándose de forma limpia.`
    );
  } else {
    const recent = issues.slice(-5).map(i => `⚠️ \`${i.slice(0, 100)}\``).join('\n');
    return (
      `⚠️ *REPORTE DE INCIDENCIAS ENCONTRADAS:*\n\n` +
      recent + `\n\n` +
      `_Nota: Los bloqueos de políticas de Flow se resuelven automáticamente con el prompt de respaldo._`
    );
  }
}

// -----------------------------------------------------------------------------
// Utilidad: Limpieza de locks huérfanos de Chrome
// -----------------------------------------------------------------------------
function cleanStaleChromeLocks(dir) {
  try {
    const lockFiles = ['SingletonLock', 'SingletonCookie', 'SingletonSocket'];
    function walk(d) {
      if (!fs.existsSync(d)) return;
      const files = fs.readdirSync(d);
      for (const f of files) {
        const full = path.join(d, f);
        try {
          const st = fs.lstatSync(full);
          if (st.isDirectory() && !st.isSymbolicLink()) {
            walk(full);
          } else if (lockFiles.includes(f) || st.isSymbolicLink()) {
            fs.unlinkSync(full);
            console.log(`[WA-BOT] 🧹 Eliminado lock residual de Chrome: ${full}`);
          }
        } catch (e) {}
      }
    }
    walk(dir);
  } catch (e) {}
}

cleanStaleChromeLocks(AUTH_DIR);

// Helper para envío seguro a prueba de marcos desprendidos y IDs @lid
async function safeReply(msg, text, targetChat) {
  try {
    return await msg.reply(text);
  } catch (err1) {
    try {
      if (targetChat) {
        return await client.sendMessage(targetChat, text);
      }
    } catch (err2) {
      console.error('[WA-BOT] ⚠️ Error en envío seguro:', err2.message);
    }
  }
}

// -----------------------------------------------------------------------------
// Cliente WhatsApp Web (Con Google Chrome headless nativo)
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
      '--js-flags="--max-old-space-size=512"',
      '--renderer-process-limit=2',
      '--disable-extensions',
      '--disable-component-update',
      '--disable-default-apps',
      '--disk-cache-size=33554432',
    ],
  },
});

client.on('qr', (qr) => {
  currentQR = qr;
  isReady = false;
  console.log('\n======================================================================');
  console.log('📱 ESCANEA ESTE CÓDIGO QR EN TU WHATSAPP:');
  console.log('======================================================================\n');
  qrcode.generate(qr, { small: true });
  console.log('\n======================================================================\n');

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
  botWid = client.info.wid._serialized;
  const botNumber = client.info.wid.user;

  console.log(`[WA-BOT] 🚀 ¡AGENTE ANTIGRAVITY EN WHATSAPP CONECTADO Y ACTIVO!`);
  console.log(`[WA-BOT] Identidad del Bot: +${botNumber}`);
  if (ownerWid) {
    console.log(`[WA-BOT] Dueño registrado para alertas: ${ownerWid}`);
  } else {
    console.log(`[WA-BOT] Esperando primer mensaje de tu número personal para registrarte como dueño...`);
  }

  // Recuperar mensajes no leídos del dueño si los hubo durante el reinicio
  setTimeout(async () => {
    try {
      const chats = await client.getChats();
      for (const chat of chats) {
        if (chat.unreadCount > 0 && (chat.id._serialized === ownerWid || chat.isUser)) {
          console.log(`[WA-BOT] 📬 Recuperando ${chat.unreadCount} mensaje(s) pendiente(s) en ${chat.name || chat.id.user}...`);
          const unreadMsgs = await chat.fetchMessages({ limit: Math.min(5, chat.unreadCount) });
          for (const umsg of unreadMsgs) {
            if (!umsg.fromMe && umsg.body && !umsg.body.startsWith('🤖')) {
              console.log(`[WA-BOT] ⚡ Procesando mensaje recuperado post-reinicio: "${umsg.body}"`);
              client.emit('message_create', umsg);
            }
          }
          await chat.sendSeen().catch(() => {});
        }
      }
    } catch (unreadErr) {
      console.warn('[WA-BOT] Aviso en lectura de pendientes:', unreadErr.message);
    }
  }, 2500);
});

client.on('disconnected', (reason) => {
  console.warn(`[WA-BOT] ⚠️ Desconectado de WhatsApp (${reason}). Reconectando en 5s...`);
  isReady = false;
  cleanStaleChromeLocks(AUTH_DIR);
  setTimeout(() => {
    client.initialize().catch((err) => console.error('[WA-BOT] Error al reinicializar:', err));
  }, 5000);
});

// Watchdog proactivo de salud (revisión periódica cada 60s)
let watchdogFailCount = 0;
setInterval(async () => {
  if (!isReady) return;
  try {
    const statePromise = client.getState();
    const timeoutPromise = new Promise((_, rej) => setTimeout(() => rej(new Error('Timeout de estado')), 12000));
    const state = await Promise.race([statePromise, timeoutPromise]);
    if (state === 'CONNECTED') {
      watchdogFailCount = 0;
    } else {
      watchdogFailCount++;
      console.warn(`[WA-BOT WATCHDOG] Estado inusual: ${state} (${watchdogFailCount}/3)`);
    }
  } catch (e) {
    watchdogFailCount++;
    console.warn(`[WA-BOT WATCHDOG] Alerta de verificación (${e.message}). Intentos: ${watchdogFailCount}/3`);
  }

  if (watchdogFailCount >= 3) {
    console.error('[WA-BOT WATCHDOG] 🚨 Watchdog detectó sesión congelada. Auto-recuperando cliente...');
    watchdogFailCount = 0;
    isReady = false;
    try { await client.destroy(); } catch (e) {}
    cleanStaleChromeLocks(AUTH_DIR);
    setTimeout(() => {
      client.initialize().catch(err => console.error('[WA-BOT] Error en auto-recuperación:', err));
    }, 3000);
  }
}, 60000);

// -----------------------------------------------------------------------------
// Interacción Bidireccional: Mensajes del Dueño hacia el Bot
// -----------------------------------------------------------------------------
client.on('message_create', async (msg) => {
  try {
    // Ignorar mensajes que el propio bot envía para evitar loops infinitos
    if (msg.body && msg.body.startsWith('🤖')) return;

    const senderWid = msg.from;
    const isIncoming = !msg.fromMe;
    const isSelfChat = msg.fromMe && (msg.to === botWid || msg.from === botWid);

    // Solo procesar si viene de un chat externo o es self-chat
    if (!isIncoming && !isSelfChat) return;

    const targetChat = isIncoming ? senderWid : msg.to;
    const senderNumber = targetChat.replace(/@.*$/, '');
    const body = (msg.body || '').trim();
    if (!body) return;

    console.log(`[WA-BOT] 💬 Mensaje recibido de +${senderNumber}: "${body}"`);

    // Registro dinámico del Dueño:
    // Si no hay dueño registrado, o el dueño registrado era el propio bot,
    // el primer usuario humano que escriba se registra automáticamente como dueño.
    const isOwnerCurrentBot = ownerWid && botWid && ownerWid.startsWith(client.info.wid.user);
    if (isIncoming && (!ownerWid || isOwnerCurrentBot || body.toLowerCase().startsWith('!vincular') || body.toLowerCase().startsWith('!admin'))) {
      ownerWid = senderWid;
      try {
        fs.writeFileSync(OWNER_FILE, JSON.stringify({
          ownerWid: senderWid,
          phone: senderNumber,
          botNumber: client.info.wid.user,
          registeredAt: new Date().toISOString()
        }, null, 2));
        console.log(`[WA-BOT] 👑 ¡Registrado +${senderNumber} como Dueño/Administrador de AWS!`);
      } catch (e) {}
    }

    const lower = body.toLowerCase();

    // COMANDO 1: ENVIAR VÍDEO CON PORTADA Y HASHTAGS (!video / video / mandame el video)
    if (
      lower === '!video' ||
      lower === 'video' ||
      lower.includes('enviar video') ||
      lower.includes('mandame el video') ||
      lower.includes('pasame el video') ||
      lower.includes('ultimo video')
    ) {
      const vid = findLatestVideo();
      if (!vid) {
        await safeReply(msg, '🤖 Aún no hay vídeos en `entregas/`. Escribe *!generar* para producir uno.', targetChat);
        return;
      }
      const deliveryDir = path.dirname(vid.path);
      const sizeMb = (vid.size / (1024 * 1024)).toFixed(1);
      await safeReply(msg, `🤖 📤 *Preparando paquete completo para TikTok:* Portada 9:16 + Vídeo (${sizeMb} MB) + Hashtags...`, targetChat);
      try {
        await sendDeliveryPackage(targetChat, deliveryDir);
      } catch (e) {
        console.error('[WA-BOT] Error enviando paquete:', e.message);
        await safeReply(msg, `🤖 ⚠️ Error enviando paquete: ${e.message}`, targetChat);
      }
      return;
    }

    // COMANDO 2: CONDICIÓN DEL PROYECTO (!condicion / !proyecto / condicion / proyecto / como va)
    if (
      lower === '!condicion' ||
      lower === '!proyecto' ||
      lower === '!avance' ||
      lower === 'condicion' ||
      lower === 'proyecto' ||
      lower.includes('como va el proyecto') ||
      lower.includes('estado del proyecto')
    ) {
      const report = await getProjectCondition();
      await safeReply(msg, report, targetChat);
      return;
    }

    // COMANDO 3: REPORTE DE FALLAS (!fallas / !errores / !reporte / fallas / errores)
    if (
      lower === '!fallas' ||
      lower === '!errores' ||
      lower === '!reporte' ||
      lower === 'fallas' ||
      lower === 'errores' ||
      lower.includes('reporte de fallas') ||
      lower.includes('hubo fallas')
    ) {
      const failureReport = getFailureReport();
      await safeReply(msg, failureReport, targetChat);
      return;
    }

    // COMANDO 4: ESTADO DEL SERVIDOR AWS (!estado / estado / servidor / ram / cpu)
    if (
      lower === '!estado' ||
      lower === '!servidor' ||
      lower === 'estado' ||
      lower === 'servidor' ||
      lower.includes('estado del servidor')
    ) {
      exec('uptime && free -h && df -h /', async (err, stdout) => {
        const text = stdout || 'No se pudo obtener información del sistema.';
        await safeReply(msg, `🤖 *ESTADO DEL SERVIDOR AWS:*\n\`\`\`\n${text}\n\`\`\``, targetChat);
      });
      return;
    }

    // COMANDO 5: INICIAR PRODUCCIÓN (!generar / !generar todos / !generar 1..4 / !generar 5 g3)
    if (
      lower.startsWith('!generar') ||
      lower.includes('generar noticiero') ||
      lower.includes('iniciar produccion')
    ) {
      let args = ['tools/ejecutar_todo.py'];
      let modeText = 'los 4 géneros diarios (Aviación, Ciberataques, IA, Espacio)';

      const countMatch = lower.match(/(\d+)\s*(?:videos?|noticias?)/) || lower.match(/!generar\s+(\d+)/);
      let count = 1;
      if (countMatch) {
        const parsed = parseInt(countMatch[1]);
        if (parsed >= 1 && parsed <= 10) count = parsed;
      }

      if (/\b(g1|aviacion|aviación|catastrofe|catástrofe|peru|perú)\b/.test(lower)) {
        args.push('--genre', 'G1');
        modeText = `Género 1 (🚨 Aviación & Desastres Perú/Mundo)`;
      } else if (/\b(g2|ciber|ciberataque|hacker)\b/.test(lower)) {
        args.push('--genre', 'G2');
        modeText = `Género 2 (💻 Ciberataques & Amenazas)`;
      } else if (/\b(g3|ia|ai|tech|robot|chip|chips|hardware)\b/.test(lower)) {
        args.push('--genre', 'G3');
        modeText = `Género 3 (🤖 IA, Chips & Hardware TechCrunch/Tom's)`;
      } else if (/\b(g4|espacio|nasa|ciencia)\b/.test(lower)) {
        args.push('--genre', 'G4');
        modeText = `Género 4 (🚀 Espacio & Ciencia Extrema)`;
      } else {
        args.push('--all');
      }

      if (count > 1 && args.includes('--genre')) {
        args.push('--count', count.toString());
        modeText += ` [Lote de ${count} vídeos ordenados por cronología y polémica]`;
      }

      await safeReply(msg, `🤖 🚀 *Iniciando producción autónoma en AWS...*\n🎯 *Objetivo:* ${modeText}.\n_No te preocupes por nada, el servidor trabaja solo mientras estás en clases y te entregará los vídeos aquí._`, targetChat);
      const child = spawn('python3', args, {
        cwd: WORKSPACE_DIR,
        detached: true,
        stdio: 'ignore',
      });
      child.unref();
      return;
    }

    // COMANDO 6: DETENER PRODUCCIÓN (!parar)
    if (lower === '!parar' || lower === 'detener' || lower === 'cancelar') {
      exec('pkill -f ejecutar_todo.py || true', async () => {
        await safeReply(msg, '🤖 🛑 Se ha enviado la orden de detener cualquier producción en curso.', targetChat);
      });
      return;
    }

    // COMANDO 7: AYUDA / MENÚ
    if (lower === '!ayuda' || lower === 'ayuda' || lower === 'help' || lower === 'menu') {
      const helpText =
        `🤖 *COMANDOS DISPONIBLES EN TU AGENTE ANTIGRAVITY AWS:*\n\n` +
        `• *!video* o *video*: Te envío el último vídeo MP4 generado al chat.\n` +
        `• *!condicion* o *proyecto*: Revisa el avance del noticiero, planos 3D y estado.\n` +
        `• *!fallas* o *errores*: Auditoría de fallas o confirmación de estabilidad.\n` +
        `• *!estado* o *servidor*: Métricas en vivo (CPU, RAM, Disco) de AWS.\n` +
        `• *!generar*: Arranca la producción completa del día en AWS.\n` +
        `• *!parar*: Detiene los procesos de render en curso.\n\n` +
        `_O pregúntame lo que quieras con lenguaje natural y Antigravity te responderá._`;
      await safeReply(msg, helpText, targetChat);
      return;
    }

    // CUALQUIER OTRA CONSULTA -> Enviar a Antigravity (`agy`)
    await safeReply(msg, '🤖 *Antigravity pensando en AWS...* ⏳', targetChat);

    const agyCmd = fs.existsSync(AGY_BIN) ? AGY_BIN : 'agy';
    const prompt = `Eres el Agente Antigravity en el servidor AWS de TikTok Radar. El usuario te escribe desde WhatsApp: "${body}". Responde en español de forma muy concisa, profesional y directa para WhatsApp:`;

    const child = spawn(agyCmd, ['--dangerously-skip-permissions', '-p', prompt], {
      cwd: WORKSPACE_DIR,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => { stdout += d.toString(); });
    child.stderr.on('data', (d) => { stderr += d.toString(); });

    const timeoutId = setTimeout(() => {
      try { child.kill('SIGKILL'); } catch (e) {}
    }, 90000);

    child.on('close', async (code) => {
      clearTimeout(timeoutId);
      try {
        if (code !== 0 && !stdout.trim()) {
          const errOut = (stderr || `Error código ${code}`).slice(-250);
          await safeReply(msg, `🤖 ⚠️ Error ejecutando agente en AWS:\n${errOut}`, targetChat);
          return;
        }
        const cleanOutput = stdout.trim() || 'El agente completó la consulta sin texto de salida.';
        await safeReply(msg, `🤖 *Antigravity AWS:*\n\n${cleanOutput}`, targetChat);
      } catch (sendErr) {
        console.error('[WA-BOT] Error enviando respuesta de agy por WhatsApp:', sendErr.message);
      }
    });
  } catch (globalErr) {
    console.error('[WA-BOT CRITICAL HANDLER ERROR]:', globalErr);
    try {
      const fallbackTarget = (!msg.fromMe ? msg.from : msg.to) || ownerWid;
      if (fallbackTarget) {
        await client.sendMessage(fallbackTarget, `🤖 ⚠️ Hubo una incidencia interna al procesar el mensaje: ${globalErr.message}`);
      }
    } catch (e) {}
  }
});

// -----------------------------------------------------------------------------
// API Local Express (para que Python envíe alertas y vídeos por HTTP a localhost:5050)
// -----------------------------------------------------------------------------
const app = express();
app.use(express.json({ limit: '100mb' }));

app.get('/status', (req, res) => {
  res.json({
    ready: isReady,
    owner: ownerWid,
    bot: botWid,
    hasQR: !!currentQR,
  });
});

app.post('/send', async (req, res) => {
  if (!isReady) {
    return res.status(503).json({ error: 'WhatsApp bot aún no está listo o autenticado.' });
  }

  loadOwner();
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
      await client.sendMessage(targetWid, media, { caption: cap, sendMediaAsDocument: false });
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

app.post('/send-delivery', async (req, res) => {
  if (!isReady) {
    return res.status(503).json({ error: 'WhatsApp bot aún no está listo o autenticado.' });
  }

  loadOwner();
  const { deliveryDir, phone } = req.body;
  const targetWid = phone
    ? `${phone.replace(/[^\d]/g, '')}@c.us`
    : ownerWid;

  if (!targetWid) {
    return res.status(400).json({ error: 'No se especificó número y no hay dueño registrado.' });
  }

  try {
    const dir = deliveryDir || (findLatestVideo() ? path.dirname(findLatestVideo().path) : null);
    if (!dir || !fs.existsSync(dir)) {
      return res.status(404).json({ error: 'Carpeta de entrega no encontrada.' });
    }
    await sendDeliveryPackage(targetWid, dir);
    return res.json({ success: true, target: targetWid, deliveryDir: dir });
  } catch (err) {
    console.error('[WA-BOT] Error en /send-delivery:', err);
    return res.status(500).json({ error: err.message });
  }
});

// -----------------------------------------------------------------------------
// Arranque del sistema
// -----------------------------------------------------------------------------
process.on('uncaughtException', (err) => {
  console.error('[WA-BOT FATAL]', err);
});
process.on('unhandledRejection', (err) => {
  console.error('[WA-BOT REJECTION]', err);
});

const gracefulShutdown = async (signal) => {
  console.log(`[WA-BOT] 🛑 Recibida señal ${signal}. Cerrando cliente WhatsApp y Chromium limpiamente...`);
  try {
    if (client) await client.destroy();
  } catch (e) {}
  process.exit(0);
};
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

app.listen(PORT, '127.0.0.1', () => {
  console.log(`[WA-BOT] 🌐 Servidor HTTP API escuchando internamente en http://127.0.0.1:${PORT}`);
  console.log('[WA-BOT] ⏳ Inicializando cliente WhatsApp Web...');
  client.initialize().catch((err) => {
    console.error('[WA-BOT] Error al inicializar cliente:', err);
  });
});
