const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

const {
  BoundedIdSet,
  resolveWorkspaceDir,
  resolveChromePath,
  normalizePhone,
  isDirectUserChat,
  isSelfChatMessage,
  authorizeMessage,
  parseGenerateCommand,
} = require('../whatsapp_bot/bot_helpers');

test('BoundedIdSet evicts oldest IDs beyond maxSize and promotes duplicates', () => {
  const s = new BoundedIdSet(3);
  s.add('a');
  s.add('b');
  s.add('c');
  assert.equal(s.size, 3);
  s.add('a'); // refresh 'a'
  s.add('d'); // should evict 'b', keeping 'c', 'a', 'd'
  assert.equal(s.has('b'), false);
  assert.equal(s.has('a'), true);
  assert.equal(s.has('c'), true);
  assert.equal(s.has('d'), true);
});

test('normalizePhone strips WID suffixes and formatting characters', () => {
  assert.equal(normalizePhone('34612345678@c.us'), '34612345678');
  assert.equal(normalizePhone('+34 612-345-678'), '34612345678');
  assert.equal(normalizePhone('12345678901234@lid'), '12345678901234');
});

test('isDirectUserChat filters out groups, broadcasts, channels, and status', () => {
  assert.equal(isDirectUserChat('34612345678@c.us'), true);
  assert.equal(isDirectUserChat('9876543210@lid'), true);
  assert.equal(isDirectUserChat('120363000000@g.us'), false);
  assert.equal(isDirectUserChat('status@broadcast'), false);
  assert.equal(isDirectUserChat('12345@newsletter'), false);
  assert.equal(isDirectUserChat(''), false);
});

test('isSelfChatMessage only allows messages sent to own WID/LID or self', () => {
  const botWid = '34600111222@c.us';
  const botLid = '999888777@lid';
  assert.equal(isSelfChatMessage({ fromMe: true, from: botWid, to: botWid }, botWid, botLid), true);
  assert.equal(isSelfChatMessage({ fromMe: true, from: botWid, to: botLid }, botWid, botLid), true);
  assert.equal(isSelfChatMessage({ fromMe: true, from: botWid, to: '34699000111@c.us' }, botWid, botLid), false);
  assert.equal(isSelfChatMessage({ fromMe: false, from: '34699000111@c.us', to: botWid }, botWid, botLid), false);
});

test('authorizeMessage blocks groups, outbound messages, strangers, and bad PINs', () => {
  const botWid = '34600111222@c.us';
  const ownerWid = '34655444333@c.us';
  const strangerWid = '34699888777@c.us';

  // Reject group message
  assert.deepEqual(
    authorizeMessage({
      msg: { fromMe: false, isStatus: false },
      senderWid: '12036300000@g.us',
      ownerWid,
      botWid,
      body: '!estado',
    }),
    { allowed: false, isSelfChat: false, bindOwner: false, reason: 'non_direct_chat' }
  );

  // Reject outbound to stranger
  assert.deepEqual(
    authorizeMessage({
      msg: { fromMe: true, from: botWid, to: strangerWid, isStatus: false },
      senderWid: strangerWid,
      ownerWid,
      botWid,
      body: 'hola',
    }),
    { allowed: false, isSelfChat: false, bindOwner: false, reason: 'outbound_to_other' }
  );

  // Allow self-chat
  const selfRes = authorizeMessage({
    msg: { fromMe: true, from: botWid, to: botWid, isStatus: false },
    senderWid: botWid,
    ownerWid: null,
    botWid,
    body: '!estado',
  });
  assert.equal(selfRes.allowed, true);
  assert.equal(selfRes.isSelfChat, true);
  assert.equal(selfRes.reason, 'self_chat');

  // Block stranger once owner is bound
  const strangerRes = authorizeMessage({
    msg: { fromMe: false, from: strangerWid, to: botWid, isStatus: false },
    senderWid: strangerWid,
    ownerWid,
    botWid,
    body: '!estado',
    env: {},
  });
  assert.equal(strangerRes.allowed, false);
  assert.equal(strangerRes.reason, 'unauthorized_sender');

  // Reject invalid WA_ADMIN_PIN and accept matching WA_ADMIN_PIN
  const badPin = authorizeMessage({
    msg: { fromMe: false, from: strangerWid, to: botWid, isStatus: false },
    senderWid: strangerWid,
    ownerWid,
    botWid,
    body: '!vincular 0000',
    env: { WA_ADMIN_PIN: '9911' },
  });
  assert.equal(badPin.allowed, false);
  assert.equal(badPin.reason, 'invalid_pin');

  const goodPin = authorizeMessage({
    msg: { fromMe: false, from: strangerWid, to: botWid, isStatus: false },
    senderWid: strangerWid,
    ownerWid,
    botWid,
    body: '!vincular 9911',
    env: { WA_ADMIN_PIN: '9911' },
  });
  assert.equal(goodPin.allowed, true);
  assert.equal(goodPin.bindOwner, true);
  assert.equal(goodPin.reason, 'pin_bind');

  // When WHATSAPP_OWNER_PHONE is set, reject non-matching incoming callers even on first bind
  const restrictedBind = authorizeMessage({
    msg: { fromMe: false, from: strangerWid, to: botWid, isStatus: false },
    senderWid: strangerWid,
    ownerWid: null,
    botWid,
    body: '!estado',
    env: { WHATSAPP_OWNER_PHONE: '+34655444333' },
  });
  assert.equal(restrictedBind.allowed, false);

  const ownerBind = authorizeMessage({
    msg: { fromMe: false, from: ownerWid, to: botWid, isStatus: false },
    senderWid: ownerWid,
    ownerWid: null,
    botWid,
    body: '!estado',
    env: { WHATSAPP_OWNER_PHONE: '+34655444333' },
  });
  assert.equal(ownerBind.allowed, true);
  assert.equal(ownerBind.bindOwner, true);
});

test('parseGenerateCommand parses slots, genres, todos, and counts safely', () => {
  assert.deepEqual(parseGenerateCommand('!generar slot 1').args, ['tools/ejecutar_todo.py', '--genre', 'SLOT_1']);
  assert.deepEqual(parseGenerateCommand('!generar slot 2').args, ['tools/ejecutar_todo.py', '--genre', 'SLOT_2']);
  assert.deepEqual(parseGenerateCommand('!generar g3 3 videos').args, ['tools/ejecutar_todo.py', '--genre', 'G3', '--count', '3']);
  assert.deepEqual(parseGenerateCommand('!generar todos').args, ['tools/ejecutar_todo.py', '--all']);
  // Out of bounds count (>10) is ignored
  assert.deepEqual(parseGenerateCommand('!generar g1 99 videos').args, ['tools/ejecutar_todo.py', '--genre', 'G1']);
});

test('resolveWorkspaceDir and resolveChromePath pick existing paths cleanly', () => {
  const ws = resolveWorkspaceDir(
    '/repo/TIKTOK_RADAR/whatsapp_bot',
    {},
    '/home/ubuntu',
    (p) => p === path.resolve('/repo/TIKTOK_RADAR/tools/ejecutar_todo.py')
  );
  assert.equal(ws, path.resolve('/repo/TIKTOK_RADAR'));

  const awsFallback = resolveWorkspaceDir(
    '/other/whatsapp_bot',
    {},
    '/home/ubuntu',
    (p) => p === '/home/ubuntu/TIKTOK-NEWS/tools/ejecutar_todo.py'
  );
  assert.equal(awsFallback, '/home/ubuntu/TIKTOK-NEWS');

  const chrome = resolveChromePath({}, (p) => p === '/usr/bin/chromium');
  assert.equal(chrome, '/usr/bin/chromium');
});
