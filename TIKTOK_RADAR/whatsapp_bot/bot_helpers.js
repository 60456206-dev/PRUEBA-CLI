const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * Conjunto acotado FIFO para evitar fugas de memoria al deduplicar IDs de mensajes.
 */
class BoundedIdSet {
  constructor(maxSize = 500) {
    this.maxSize = maxSize;
    this._set = new Set();
  }

  add(id) {
    if (!id) return;
    if (this._set.has(id)) {
      this._set.delete(id);
    }
    this._set.add(id);
    while (this._set.size > this.maxSize) {
      const oldest = this._set.values().next().value;
      this._set.delete(oldest);
    }
  }

  has(id) {
    return Boolean(id && this._set.has(id));
  }

  get size() {
    return this._set.size;
  }
}

/**
 * Resuelve la raíz del proyecto TIKTOK_RADAR (soporta ejecución en repo o ~/TIKTOK-NEWS).
 */
function resolveWorkspaceDir(botDir, env = process.env, homeDir = os.homedir(), existsSync = fs.existsSync) {
  if (env.TIKTOK_WORKSPACE_DIR && existsSync(env.TIKTOK_WORKSPACE_DIR)) {
    return env.TIKTOK_WORKSPACE_DIR;
  }

  const parentDir = path.resolve(botDir, '..');
  if (existsSync(path.join(parentDir, 'tools', 'ejecutar_todo.py'))) {
    return parentDir;
  }

  const awsDefault = path.join(homeDir, 'TIKTOK-NEWS');
  if (existsSync(path.join(awsDefault, 'tools', 'ejecutar_todo.py')) || existsSync(awsDefault)) {
    return awsDefault;
  }

  return parentDir;
}

/**
 * Detecta el ejecutable de Chrome/Chromium disponible en Linux.
 */
function resolveChromePath(env = process.env, existsSync = fs.existsSync) {
  const candidates = [
    env.CHROME_BIN,
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/snap/bin/chromium',
  ].filter(Boolean);

  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      return candidate;
    }
  }
  return undefined;
}

function normalizePhone(widOrPhone) {
  if (!widOrPhone) return '';
  const local = String(widOrPhone).split('@')[0];
  return local.replace(/[^\d]/g, '');
}

function isDirectUserChat(wid) {
  if (!wid || typeof wid !== 'string') return false;
  if (
    wid === 'status@broadcast' ||
    wid.endsWith('@g.us') ||
    wid.endsWith('@broadcast') ||
    wid.endsWith('@newsletter')
  ) {
    return false;
  }
  return wid.endsWith('@c.us') || wid.endsWith('@lid');
}

function isSelfChatMessage(msg, botWid, botLid = null) {
  if (!msg || !msg.fromMe || !botWid || !msg.to) return false;
  return (
    msg.to === botWid ||
    msg.to === msg.from ||
    (Boolean(botLid) && msg.to === botLid)
  );
}

/**
 * Evalúa autorización estricta de mensajes entrantes y self-chat.
 */
function authorizeMessage({ msg, senderWid, ownerWid, botWid, botLid = null, body = '', env = process.env }) {
  if (!msg || msg.isStatus || !isDirectUserChat(senderWid)) {
    return { allowed: false, isSelfChat: false, bindOwner: false, reason: 'non_direct_chat' };
  }

  const isIncoming = !msg.fromMe;
  const isSelfChat = isSelfChatMessage(msg, botWid, botLid);

  if (!isIncoming && !isSelfChat) {
    return { allowed: false, isSelfChat: false, bindOwner: false, reason: 'outbound_to_other' };
  }

  if (isSelfChat) {
    return { allowed: true, isSelfChat: true, bindOwner: false, reason: 'self_chat' };
  }

  const trimmed = String(body || '').trim();
  const pinMatch = /^!(vincular|admin)(?:\s+(\S+))?/i.exec(trimmed);
  const configuredPin = (env.WA_ADMIN_PIN || '').trim();
  const configuredOwnerPhone = normalizePhone(env.WHATSAPP_OWNER_PHONE || '');
  const senderPhone = normalizePhone(senderWid);

  if (pinMatch) {
    const providedPin = (pinMatch[2] || '').trim();
    if (configuredPin) {
      if (providedPin && providedPin === configuredPin) {
        return { allowed: true, isSelfChat: false, bindOwner: true, reason: 'pin_bind' };
      }
      return { allowed: false, isSelfChat: false, bindOwner: false, reason: 'invalid_pin' };
    }
    // Sin WA_ADMIN_PIN configurado: solo permitir si aún no hay dueño válido o si ya es el dueño
    const ownerIsSelfBot = Boolean(ownerWid && botWid && normalizePhone(ownerWid) === normalizePhone(botWid));
    if (!ownerWid || ownerIsSelfBot) {
      if (configuredOwnerPhone && senderPhone !== configuredOwnerPhone) {
        return { allowed: false, isSelfChat: false, bindOwner: false, reason: 'owner_phone_mismatch' };
      }
      return { allowed: true, isSelfChat: false, bindOwner: true, reason: 'initial_bind' };
    }
    const alreadyOwner =
      senderWid === ownerWid ||
      (Boolean(normalizePhone(ownerWid)) && senderPhone === normalizePhone(ownerWid));
    return alreadyOwner
      ? { allowed: true, isSelfChat: false, bindOwner: false, reason: 'owner_match' }
      : { allowed: false, isSelfChat: false, bindOwner: false, reason: 'owner_already_bound' };
  }

  if (configuredOwnerPhone) {
    const matchesConfigured = Boolean(senderPhone && senderPhone === configuredOwnerPhone);
    if (!matchesConfigured && senderWid !== ownerWid) {
      return { allowed: false, isSelfChat: false, bindOwner: false, reason: 'unauthorized_sender' };
    }
    if (matchesConfigured && (!ownerWid || ownerWid !== senderWid)) {
      return { allowed: true, isSelfChat: false, bindOwner: true, reason: 'configured_owner_bind' };
    }
    return { allowed: true, isSelfChat: false, bindOwner: false, reason: 'configured_owner_match' };
  }

  const ownerIsSelfBot = Boolean(ownerWid && botWid && normalizePhone(ownerWid) === normalizePhone(botWid));
  if (!ownerWid || ownerIsSelfBot) {
    return { allowed: true, isSelfChat: false, bindOwner: true, reason: 'first_owner_bind' };
  }

  const ownerPhone = normalizePhone(ownerWid);
  const matchesOwner = senderWid === ownerWid || (Boolean(ownerPhone) && senderPhone === ownerPhone);
  if (!matchesOwner) {
    return { allowed: false, isSelfChat: false, bindOwner: false, reason: 'unauthorized_sender' };
  }

  return { allowed: true, isSelfChat: false, bindOwner: false, reason: 'owner_match' };
}

/**
 * Parsea !generar y frases equivalentes a argumentos seguros para tools/ejecutar_todo.py.
 */
function parseGenerateCommand(lowerText) {
  const lower = String(lowerText || '').toLowerCase();
  const args = ['tools/ejecutar_todo.py'];
  let modeText = 'todos los géneros diarios (Aviación, Ciberataques, IA, Espacio)';

  const countMatch = lower.match(/(\d+)\s*(?:videos?|noticias?)/) || lower.match(/!generar\s+(\d+)/);
  let count = 1;
  if (countMatch) {
    const parsed = parseInt(countMatch[1], 10);
    if (parsed >= 1 && parsed <= 10) count = parsed;
  }

  if (/\b(todos|all)\b/.test(lower)) {
    args.push('--all');
  } else if (/\bslot[\s_-]*1\b/.test(lower)) {
    args.push('--genre', 'SLOT_1');
    modeText = 'Slot 1 (✈️ Aviación Internacional & Catástrofes)';
  } else if (/\bslot[\s_-]*2\b/.test(lower)) {
    args.push('--genre', 'SLOT_2');
    modeText = 'Slot 2 (💻 IA, Chips, Tech & Ciencia Extrema)';
  } else if (/\b(g1|aviacion|aviación|vuelo|mayday|aereo|aéreo|catastrofe|catástrofe)\b/.test(lower)) {
    args.push('--genre', 'G1');
    modeText = 'Género 1 (✈️ Aviación Internacional & Seguridad Aérea)';
  } else if (/\b(g2|ciber|ciberataque|hacker)\b/.test(lower)) {
    args.push('--genre', 'G2');
    modeText = 'Género 2 (💻 Ciberataques & Amenazas)';
  } else if (/\b(g3|ia|ai|tech|robot|chip|chips|hardware)\b/.test(lower)) {
    args.push('--genre', 'G3');
    modeText = "Género 3 (🤖 IA, Chips & Hardware)";
  } else if (/\b(g4|espacio|nasa|ciencia)\b/.test(lower)) {
    args.push('--genre', 'G4');
    modeText = 'Género 4 (🚀 Espacio & Ciencia Extrema)';
  } else {
    args.push('--all');
  }

  if (count > 1 && args.includes('--genre')) {
    args.push('--count', count.toString());
    modeText += ` [Lote de ${count} vídeos ordenados por cronología e impacto]`;
  }

  return { args, modeText, count };
}

module.exports = {
  BoundedIdSet,
  resolveWorkspaceDir,
  resolveChromePath,
  normalizePhone,
  isDirectUserChat,
  isSelfChatMessage,
  authorizeMessage,
  parseGenerateCommand,
};
