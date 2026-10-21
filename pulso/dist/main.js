import { analyzeAudio, createDemo, buildChart } from './audio.js';

const $ = (id) => document.getElementById(id);
const canvas = $('game-canvas');
const paint = canvas.getContext('2d');
const laneButtons = [...document.querySelectorAll('.lane-key')];
const difficultyButtons = [...document.querySelectorAll('[data-difficulty]')];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const laneColors = ['#d4ff48', '#b9e73b', '#73e4cf', '#ada2ff'];
const keyLanes = { KeyD: 0, KeyF: 1, KeyJ: 2, KeyK: 3 };
const hints = { easy: 'Menos notas. Más espacio para encontrar tu ritmo.', normal: 'Sigue el ritmo. Entra en la zona.', hard: 'Más golpes, más energía. Mantén la racha.' };
const names = { easy: 'SUAVE', normal: 'NORMAL', hard: 'INTENSO' };
const state = {
  phase: 'idle', difficulty: 'normal', buffer: null, analysis: null, title: '', isDemo: false,
  notes: [], source: null, ctx: null, gain: null, analyser: null, frequencies: null,
  startedAt: 0, position: 0, session: 0, intent: 0, busy: false, score: 0, combo: 0, maxCombo: 0,
  perfect: 0, good: 0, missed: 0, judged: 0, offset: 0, laneFlash: [0, 0, 0, 0],
  particles: [], feedbackUntil: 0, lastUi: 0, width: 0, height: 0, record: 0,
};
let toastTimer;
let previousFocus;
let demoBuffer;
const timeText = (seconds) => `${Math.floor(Math.max(0, seconds) / 60)}:${String(Math.floor(Math.max(0, seconds) % 60)).padStart(2, '0')}`;
const readStorage = (key, fallback) => { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } };
const writeStorage = (key, value) => { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* Playing works without storage. */ } };

function toast(message) {
  clearTimeout(toastTimer);
  $('toast').textContent = message;
  $('toast').hidden = false;
  toastTimer = setTimeout(() => { $('toast').hidden = true; }, 4500);
}

async function audioContext() {
  if (!state.ctx) {
    const Context = window.AudioContext || window.webkitAudioContext;
    if (!Context) throw new Error('Este navegador no admite Web Audio. Prueba con un navegador actualizado.');
    state.ctx = new Context({ latencyHint: 'interactive' });
    state.gain = state.ctx.createGain();
    state.analyser = state.ctx.createAnalyser();
    state.analyser.fftSize = 256;
    state.analyser.smoothingTimeConstant = 0.75;
    state.frequencies = new Uint8Array(state.analyser.frequencyBinCount);
    state.gain.gain.value = Number($('volume').value) / 100;
    state.gain.connect(state.analyser);
    state.analyser.connect(state.ctx.destination);
    state.ctx.addEventListener('statechange', () => {
      if ((state.ctx.state === 'suspended' || state.ctx.state === 'interrupted') && state.phase === 'playing') pause();
    });
  }
  if (state.ctx.state !== 'running') await state.ctx.resume();
  return state.ctx;
}

function stopSource() {
  state.session++;
  if (state.source) {
    state.source.onended = null;
    try { state.source.stop(); } catch { /* Already ended. */ }
    state.source.disconnect();
    state.source = null;
  }
}

function currentTime() {
  return state.phase === 'playing' ? state.ctx.currentTime - state.startedAt : state.position;
}

function setPhase(phase) {
  state.phase = phase;
  const active = phase === 'playing' || phase === 'paused';
  $('game-state').textContent = { idle: 'LISTO PARA EL RITMO', loading: 'BUSCANDO EL BEAT', ready: 'PISTA PREPARADA', playing: 'EN LA ZONA', paused: 'TOMA UN RESPIRO', finished: 'SESIÓN COMPLETADA' }[phase];
  $('arena').classList.toggle('is-playing', phase === 'playing');
  $('pause-button').disabled = !active;
  $('pause-button').textContent = phase === 'paused' ? '▶' : 'Ⅱ';
  $('pause-button').setAttribute('aria-label', phase === 'paused' ? 'Continuar partida' : 'Pausar partida');
  $('restart-button').disabled = !state.buffer || state.busy;
  difficultyButtons.forEach((button) => { button.disabled = active || state.busy; });
  $('offset').disabled = phase === 'playing' || state.busy;
  $('start-button').disabled = state.busy || phase === 'playing';
  $('browse-button').disabled = state.busy;
  $('audio-file').disabled = state.busy;
  $('demo-button').disabled = state.busy;
  $('overlay-play').disabled = state.busy;
  $('start-button').innerHTML = phase === 'loading' ? 'Analizando el ritmo…' : phase === 'paused' ? '<span aria-hidden="true">▶</span> Continuar sesión <kbd>ENTER</kbd>' : '<span aria-hidden="true">▶</span> Empezar sesión <kbd>ENTER</kbd>';
  $('arena-overlay').hidden = phase === 'playing';
  $('countdown').hidden = true;
  const heading = $('arena-overlay').querySelector('h2');
  const description = $('arena-overlay').querySelector('p');
  const overlayButton = $('overlay-play');
  if (phase === 'paused') {
    heading.textContent = 'Vuelve a tu flow.';
    description.textContent = 'Tu canción te espera justo donde la dejaste.';
    overlayButton.innerHTML = '<span aria-hidden="true">▶</span> Continuar';
  } else if (phase === 'ready' || phase === 'finished') {
    heading.textContent = phase === 'finished' ? '¿Una ronda más?' : 'Dale al play.';
    description.textContent = `${state.notes.length} notas. Cuatro carriles. Tu momento.`;
    overlayButton.innerHTML = '<span aria-hidden="true">▶</span> Empezar sesión';
  } else if (phase === 'loading') {
    heading.textContent = 'Buscando tu beat…';
    description.textContent = 'Estamos escuchando los golpes de tu canción.';
    overlayButton.textContent = 'Preparando la pista…';
  } else {
    heading.textContent = 'Siente el beat.';
    description.innerHTML = 'Carga tu canción o entra en calor<br>con nuestra sesión de prueba.';
    overlayButton.innerHTML = '<span aria-hidden="true">▶</span> Probar una sesión';
  }
}

function refreshChart() {
  if (!state.analysis || !state.buffer) return;
  state.notes = buildChart(state.analysis, state.difficulty, state.buffer.duration).map((note) => ({ ...note, hit: false, missed: false }));
  $('selected-meta').textContent = `${state.isDemo ? 'DEMO · ' : ''}${timeText(state.buffer.duration)} · ${state.notes.length} notas`;
  $('bpm-badge').textContent = state.analysis.bpm ? `≈ ${Math.round(state.analysis.bpm)} BPM` : 'RITMO LIBRE';
}

function readDuration(file) {
  return new Promise((resolve) => {
    const media = document.createElement('audio');
    const url = URL.createObjectURL(file);
    let settled = false;
    const finish = (duration) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      media.onloadedmetadata = media.onerror = null;
      media.removeAttribute('src');
      media.load();
      URL.revokeObjectURL(url);
      resolve(duration);
    };
    const timeout = setTimeout(() => finish(null), 4000);
    media.preload = 'metadata';
    media.onloadedmetadata = () => finish(Number.isFinite(media.duration) ? media.duration : null);
    media.onerror = () => finish(null);
    media.src = url;
  });
}

async function loadTrack(file = null, preserveIntent = false) {
  if (state.busy) return false;
  if (file && file.size > 100 * 1024 * 1024) {
    toast('Elige un archivo de hasta 100 MB.');
    return false;
  }
  if (!preserveIntent) state.intent++;
  stopSource();
  state.position = 0;
  state.busy = true;
  setPhase('loading');
  $('audio-status').textContent = file ? `Abriendo ${file.name}…` : 'Preparando Neon Afterhours…';
  $('audio-status').classList.remove('is-error');
  try {
    const ctx = await audioContext();
    let buffer;
    if (file) {
      const duration = await readDuration(file);
      if (duration !== null && duration < 4) throw new Error('Elige una canción de al menos 4 segundos.');
      if (duration !== null && duration > 12 * 60) throw new Error('Elige una canción de hasta 12 minutos.');
      const bytes = await file.arrayBuffer();
      try { buffer = await ctx.decodeAudioData(bytes); }
      catch { throw new Error('No se pudo abrir este audio. Prueba con un MP3 o WAV válido.'); }
    } else {
      if (!demoBuffer) demoBuffer = await createDemo(ctx);
      buffer = demoBuffer;
    }
    if (buffer.duration < 4) throw new Error('Elige una canción de al menos 4 segundos.');
    if (buffer.duration > 12 * 60) throw new Error('Elige una canción de hasta 12 minutos.');
    const analysis = await analyzeAudio(buffer, (progress) => {
      $('audio-status').textContent = `Detectando golpes y energía… ${Math.round(progress * 100)}%`;
    });
    if (analysis.peaks.length < 3) throw new Error('No detectamos suficientes golpes. Prueba una canción con percusión más marcada.');
    const notes = buildChart(analysis, state.difficulty, buffer.duration);
    if (notes.length < 2) throw new Error('El audio tiene muy pocos golpes para jugar. Prueba otra canción.');
    state.buffer = buffer;
    state.analysis = analysis;
    state.isDemo = !file;
    state.title = file ? file.name.replace(/\.[^.]+$/, '') : 'Neon Afterhours';
    $('arena-title').textContent = state.title;
    $('selected-title').textContent = state.title;
    $('selected-title').title = state.title;
    $('demo-button').title = file ? 'Volver a la pista de prueba Neon Afterhours' : 'Cargar pista de prueba Neon Afterhours';
    $('demo-button').setAttribute('aria-label', $('demo-button').title);
    $('demo-button').textContent = file ? '↺' : '↗';
    $('playing-title').textContent = state.title;
    $('audio-status').textContent = `${file ? 'Archivo local' : 'Pista de prueba'} listo. Tu próxima partida te espera.`;
    refreshChart();
    resetScore();
    return true;
  } catch (error) {
    $('audio-status').textContent = `${error.message || 'No pudimos cargar esta canción.'}${state.buffer ? ' La pista anterior sigue disponible.' : ''}`;
    $('audio-status').classList.add('is-error');
    toast(error.message || 'No pudimos cargar esta canción.');
    return false;
  } finally {
    state.busy = false;
    setPhase(state.buffer ? 'ready' : 'idle');
    updateHud();
  }
}

function resetScore() {
  state.score = state.combo = state.maxCombo = state.perfect = state.good = state.missed = state.judged = 0;
  state.particles = [];
  $('judgement').textContent = '';
  $('combo-pop').textContent = '';
  updateHud();
}

function scheduleSource(position, delay) {
  stopSource();
  const session = state.session;
  const source = state.ctx.createBufferSource();
  source.buffer = state.buffer;
  source.connect(state.gain);
  state.startedAt = state.ctx.currentTime + delay - position;
  state.position = position;
  source.onended = () => {
    if (session === state.session && state.phase === 'playing') finish();
  };
  source.start(state.ctx.currentTime + delay, position);
  state.source = source;
  setPhase('playing');
}

async function start() {
  if (state.busy || state.phase === 'playing') return;
  if (state.phase === 'paused') { await resume(); return; }
  closeModal('results-modal');
  const intent = ++state.intent;
  try {
    await audioContext();
    if (!canPlay(intent)) return;
    if (!state.buffer && !(await loadTrack(null, true))) return;
    if (!canPlay(intent)) return;
    refreshChart();
    resetScore();
    state.offset = Number($('offset').value) / 1000;
    scheduleSource(0, 2.5);
    if (matchMedia('(max-width: 720px)').matches) document.querySelector('.play-panel').scrollIntoView({ behavior: reducedMotion ? 'instant' : 'smooth', block: 'start' });
  } catch (error) { toast(error.message || 'No se pudo iniciar el audio.'); }
}

function pause() {
  state.intent++;
  if (state.phase !== 'playing') return;
  state.position = Math.max(0, currentTime());
  stopSource();
  setPhase('paused');
}

async function resume() {
  if (state.phase !== 'paused') return;
  const intent = ++state.intent;
  try {
    await audioContext();
    if (!canPlay(intent) || state.phase !== 'paused') return;
    state.offset = Number($('offset').value) / 1000;
    scheduleSource(state.position, 0.08);
    if (matchMedia('(max-width: 720px)').matches) document.querySelector('.play-panel').scrollIntoView({ behavior: reducedMotion ? 'instant' : 'smooth', block: 'start' });
  } catch (error) { toast(error.message || 'No se pudo continuar el audio.'); }
}

function canPlay(intent) {
  return state.intent === intent && !state.busy && !document.hidden && !document.querySelector('.modal-backdrop:not([hidden])');
}

function accuracy() { return state.judged ? Math.round((state.perfect + state.good * 0.65) / state.judged * 100) : 0; }

function updateHud() {
  $('score').textContent = String(state.score).padStart(6, '0');
  $('combo').innerHTML = `${state.combo}<span>×</span>`;
  $('accuracy').innerHTML = `${state.judged ? accuracy() : '—'}<span>%</span>`;
  const position = Math.max(0, currentTime());
  const duration = state.buffer?.duration || 0;
  $('track-time').textContent = `${timeText(position)} / ${timeText(duration)}`;
  const progress = duration ? Math.min(100, position / duration * 100) : 0;
  $('progress-fill').style.width = `${progress}%`;
  document.querySelector('.progress-track').setAttribute('aria-valuenow', String(Math.round(progress)));
}

function feedback(text, color) {
  $('judgement').textContent = text;
  $('judgement').style.color = color;
  $('judgement').style.opacity = '1';
  state.feedbackUntil = performance.now() + 600;
  $('combo-pop').textContent = state.combo >= 5 ? `${state.combo} COMBO` : '';
}

function hitLane(lane) {
  state.laneFlash[lane] = performance.now() + 140;
  if (state.phase !== 'playing' || currentTime() < 0) return;
  const time = currentTime();
  let closest = null;
  let distance = 0.136;
  for (const note of state.notes) {
    if (note.hit || note.missed) continue;
    if (note.time + state.offset > time + 0.135) break;
    const delta = Math.abs(note.time + state.offset - time);
    if (note.lane === lane && delta < distance) { closest = note; distance = delta; }
  }
  if (!closest) {
    // An empty key press breaks the combo so mashing every lane cannot farm a perfect run.
    state.combo = 0;
    state.score = Math.max(0, state.score - 25);
    feedback('A DESTIEMPO', '#a0a699');
    return;
  }
  closest.hit = true;
  state.combo++;
  state.maxCombo = Math.max(state.maxCombo, state.combo);
  state.judged++;
  const perfect = distance <= 0.065;
  if (perfect) state.perfect++; else state.good++;
  state.score += (perfect ? 100 : 65) * Math.min(4, 1 + Math.floor((state.combo - 1) / 10));
  feedback(perfect ? 'PERFECTO' : 'BIEN', perfect ? '#d4ff48' : '#73e4cf');
  if (!reducedMotion) {
    const { center, hitY, bottomWidth } = geometry();
    const x = center - bottomWidth / 2 + (lane + 0.5) * bottomWidth / 4;
    for (let i = 0; i < 10; i++) state.particles.push({ x, y: hitY, vx: (Math.random() - 0.5) * 5, vy: -Math.random() * 5 - 1, life: 1, color: laneColors[lane] });
  }
}

function finish() {
  if (state.phase !== 'playing') return;
  state.position = state.buffer.duration;
  stopSource();
  for (const note of state.notes) { if (!note.hit && !note.missed) { note.missed = true; state.missed++; state.judged++; } }
  setPhase('finished');
  updateHud();
  const key = `pulso:record:${state.title}:${state.buffer.length}:${state.difficulty}`;
  const best = Math.max(Number(readStorage(key, 0)) || 0, state.score);
  writeStorage(key, best);
  const precision = accuracy();
  $('result-rank').textContent = precision >= 95 ? 'S' : precision >= 80 ? 'A' : precision >= 65 ? 'B' : precision >= 45 ? 'C' : 'D';
  $('results-title').textContent = precision >= 80 ? 'Estás en la zona.' : precision >= 45 ? 'Ese es tu ritmo.' : 'Cada beat es un comienzo.';
  $('result-track').textContent = `${state.title} · ${names[state.difficulty]}`;
  $('result-score').textContent = state.score.toLocaleString('es');
  $('result-accuracy').textContent = `${precision}%`;
  $('result-combo').textContent = `${state.maxCombo}×`;
  $('result-best').textContent = best.toLocaleString('es');
  $('result-breakdown').textContent = `${state.perfect} perfectas · ${state.good} buenas · ${state.missed} perdidas`;
  openModal('results-modal');
}

function openModal(id) {
  state.intent++;
  if (state.phase === 'playing') pause();
  previousFocus = document.activeElement;
  $(id).hidden = false;
  document.body.classList.add('modal-open');
  $(id).querySelector('button').focus();
}
function closeModal(id) {
  if ($(id).hidden) return;
  $(id).hidden = true;
  document.body.classList.remove('modal-open');
  previousFocus?.focus();
}

function resize() {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(devicePixelRatio || 1, 2);
  canvas.width = Math.round(rect.width * dpr);
  canvas.height = Math.round(rect.height * dpr);
  state.width = rect.width;
  state.height = rect.height;
  paint.setTransform(dpr, 0, 0, dpr, 0, 0);
}
new ResizeObserver(resize).observe(canvas);

function geometry() {
  return { center: state.width / 2, topWidth: state.width * 0.39, bottomWidth: state.width * 0.82, topY: 8, hitY: state.height - 81 };
}
function laneX(boundary, progress) {
  const { center, topWidth, bottomWidth } = geometry();
  const width = topWidth + (bottomWidth - topWidth) * progress;
  return center - width / 2 + boundary * width / 4;
}

function drawNote(lane, progress, strength, alpha = 1) {
  if (progress < 0 || progress > 1.12) return;
  const { topY, hitY } = geometry();
  const y = topY + progress * (hitY - topY);
  const x = laneX(lane, progress) + 10;
  const width = laneX(lane + 1, progress) - x - 10;
  const height = 5 + progress * 9;
  paint.globalAlpha = alpha;
  const tail = paint.createLinearGradient(0, y - 35, 0, y);
  tail.addColorStop(0, `${laneColors[lane]}00`);
  tail.addColorStop(1, `${laneColors[lane]}25`);
  paint.fillStyle = tail;
  paint.fillRect(x, y - 35, width, 35);
  paint.shadowColor = laneColors[lane];
  paint.shadowBlur = reducedMotion ? 0 : 10 + strength * 7;
  paint.fillStyle = laneColors[lane];
  paint.beginPath();
  paint.roundRect(x, y - height / 2, width, height, 2);
  paint.fill();
  paint.shadowBlur = 0;
  paint.fillStyle = '#ffffff80';
  paint.fillRect(x + 3, y - height / 2 + 1, width - 6, 2);
  paint.globalAlpha = 1;
}

function draw(timestamp) {
  requestAnimationFrame(draw);
  if (document.hidden) return;
  const { width: w, height: h } = state;
  if (!w || !h) return;
  paint.clearRect(0, 0, w, h);
  const { center, topWidth, bottomWidth, topY, hitY } = geometry();
  const playing = state.phase === 'playing';
  const time = currentTime();
  let energy = 0;
  if (state.analyser && playing && time >= 0) {
    state.analyser.getByteFrequencyData(state.frequencies);
    for (let i = 0; i < 12; i++) energy += state.frequencies[i] / (255 * 12);
  }
  const glow = paint.createRadialGradient(center, hitY, 0, center, hitY, w * 0.6);
  glow.addColorStop(0, `rgba(150,190,45,${0.045 + (reducedMotion ? 0 : energy * 0.075)})`);
  glow.addColorStop(1, 'rgba(15,18,15,0)');
  paint.fillStyle = glow;
  paint.fillRect(0, 0, w, h);

  // A four-lane highway with a shared audio clock for animation and judgement.
  for (let lane = 0; lane < 4; lane++) {
    paint.beginPath();
    paint.moveTo(laneX(lane, 0), topY);
    paint.lineTo(laneX(lane + 1, 0), topY);
    paint.lineTo(laneX(lane + 1, 1.18), h);
    paint.lineTo(laneX(lane, 1.18), h);
    paint.closePath();
    const flash = Math.max(0, (state.laneFlash[lane] - timestamp) / 140);
    const fill = paint.createLinearGradient(0, 0, 0, h);
    fill.addColorStop(0, '#161b1400');
    fill.addColorStop(1, flash ? `${laneColors[lane]}30` : lane % 2 ? '#ffffff04' : '#ffffff08');
    paint.fillStyle = fill;
    paint.fill();
    laneButtons[lane].classList.toggle('is-pressed', flash > 0);
  }
  paint.lineWidth = 1;
  for (let boundary = 0; boundary < 5; boundary++) {
    paint.strokeStyle = boundary === 0 || boundary === 4 ? '#8a9a5e35' : '#ffffff0e';
    paint.beginPath(); paint.moveTo(laneX(boundary, 0), topY); paint.lineTo(laneX(boundary, 1.18), h); paint.stroke();
  }
  const scroll = reducedMotion ? 0 : ((playing ? time * 0.42 : timestamp / 9000) % 1 + 1) % 1;
  for (let i = 0; i < 9; i++) {
    const progress = ((i / 9 + scroll / 9) % 1) ** 1.45;
    const y = topY + progress * (hitY - topY);
    paint.strokeStyle = '#ffffff08';
    paint.beginPath(); paint.moveTo(laneX(0, progress), y); paint.lineTo(laneX(4, progress), y); paint.stroke();
  }

  // Small side meters respond to the live audio analyser.
  for (let i = 0; i < 24; i++) {
    const value = playing && time >= 0 ? (state.frequencies?.[i * 2] || 0) / 255 : 0.12 + Math.sin(i * 0.9) ** 2 * 0.2;
    const barHeight = 2 + value * 27;
    paint.fillStyle = `rgba(180,210,120,${0.12 + value * 0.2})`;
    const x = 18 + i * 3.5;
    paint.fillRect(x, hitY - barHeight - 14, 2, barHeight);
    paint.fillRect(w - x - 2, hitY - barHeight - 14, 2, barHeight);
  }
  if (state.analysis?.waveform) {
    paint.fillStyle = '#d4ff481a';
    state.analysis.waveform.forEach((value, i) => {
      const x = i / state.analysis.waveform.length * w;
      paint.fillRect(x, h - value * 17, Math.max(1, w / state.analysis.waveform.length - 1), value * 17);
    });
  }
  if (playing || state.phase === 'paused') {
    const approach = { easy: 2.7, normal: 2.3, hard: 1.85 }[state.difficulty];
    for (const note of state.notes) {
      if (note.hit || note.missed) continue;
      const until = note.time + state.offset - time;
      if (until > approach) break;
      if (playing && until < -0.135) {
        note.missed = true; state.missed++; state.judged++; state.combo = 0;
        feedback('SE ESCAPÓ', '#f59b81');
        continue;
      }
      drawNote(note.lane, 1 - until / approach, note.strength);
    }
  } else {
    const idleNotes = [[0, 0.23], [2, 0.43], [1, 0.72], [3, 0.9], [0, 0.99]];
    idleNotes.forEach(([lane, progress]) => drawNote(lane, progress, 0.4, 0.33));
  }
  const lineGlow = paint.createLinearGradient(center - bottomWidth / 2, 0, center + bottomWidth / 2, 0);
  lineGlow.addColorStop(0, '#d4ff4800'); lineGlow.addColorStop(0.1, '#d4ff48bb'); lineGlow.addColorStop(0.9, '#d4ff48bb'); lineGlow.addColorStop(1, '#d4ff4800');
  paint.strokeStyle = lineGlow; paint.lineWidth = 2;
  paint.beginPath(); paint.moveTo(center - bottomWidth / 2 - 14, hitY); paint.lineTo(center + bottomWidth / 2 + 14, hitY); paint.stroke();
  for (let lane = 0; lane < 4; lane++) {
    const x = laneX(lane, 1) + 9;
    paint.strokeStyle = `${laneColors[lane]}66`;
    paint.lineWidth = 1;
    paint.strokeRect(x, hitY - 5, bottomWidth / 4 - 18, 10);
  }
  state.particles = state.particles.filter((particle) => particle.life > 0);
  for (const particle of state.particles) {
    particle.x += particle.vx; particle.y += particle.vy; particle.vy += 0.1; particle.life -= 0.035;
    paint.globalAlpha = Math.max(0, particle.life); paint.fillStyle = particle.color; paint.fillRect(particle.x, particle.y, 3, 3);
  }
  paint.globalAlpha = 1;
  if (timestamp > state.feedbackUntil) { $('judgement').style.opacity = '0'; $('combo-pop').textContent = ''; }
  if (playing) {
    $('countdown').hidden = time >= 0;
    if (time < 0) $('countdown').textContent = String(Math.ceil(-time));
  }
  if (timestamp - state.lastUi > 80) { updateHud(); state.lastUi = timestamp; }
}

$('browse-button').addEventListener('click', () => $('audio-file').click());
$('audio-file').addEventListener('change', (event) => { const file = event.target.files[0]; if (file) loadTrack(file); event.target.value = ''; });
$('demo-button').addEventListener('click', () => loadTrack());
$('overlay-play').addEventListener('click', start);
$('start-button').addEventListener('click', start);
$('pause-button').addEventListener('click', () => state.phase === 'paused' ? resume() : pause());
$('restart-button').addEventListener('click', () => { if (state.busy) return; state.intent++; stopSource(); state.position = 0; setPhase('ready'); start(); });
$('replay-button').addEventListener('click', () => { closeModal('results-modal'); start(); });
$('help-button').addEventListener('click', () => openModal('help-modal'));
document.querySelectorAll('[data-close]').forEach((button) => button.addEventListener('click', () => closeModal(button.dataset.close)));
document.querySelectorAll('.modal-backdrop').forEach((modal) => modal.addEventListener('click', (event) => { if (event.target === modal) closeModal(modal.id); }));
difficultyButtons.forEach((button) => button.addEventListener('click', () => {
  if (state.busy || ['playing', 'paused'].includes(state.phase)) return;
  state.difficulty = button.dataset.difficulty;
  difficultyButtons.forEach((item) => { item.classList.toggle('active', item === button); item.setAttribute('aria-pressed', String(item === button)); });
  $('mode-badge').textContent = names[state.difficulty];
  $('difficulty-hint').textContent = hints[state.difficulty];
  refreshChart();
  if (state.buffer) setPhase('ready');
}));

const volume = Math.min(100, Math.max(0, Number(readStorage('pulso:volume', 70)) || 0));
const offset = Math.min(250, Math.max(-250, Number(readStorage('pulso:offset', 0)) || 0));
$('volume').value = String(volume); $('volume-value').textContent = `${volume}%`;
$('offset').value = String(offset); $('offset-value').textContent = `${offset > 0 ? '+' : ''}${offset} ms`;
$('volume').addEventListener('input', () => {
  const value = Number($('volume').value);
  $('volume-value').textContent = `${value}%`;
  if (state.gain) state.gain.gain.setTargetAtTime(value / 100, state.ctx.currentTime, 0.02);
  writeStorage('pulso:volume', value);
});
$('offset').addEventListener('input', () => {
  const value = Number($('offset').value);
  $('offset-value').textContent = `${value > 0 ? '+' : ''}${value} ms`;
  writeStorage('pulso:offset', value);
});
for (const type of ['dragenter', 'dragover']) $('dropzone').addEventListener(type, (event) => { event.preventDefault(); if (!state.busy) $('dropzone').classList.add('drag-over'); });
for (const type of ['dragleave', 'drop']) $('dropzone').addEventListener(type, (event) => { event.preventDefault(); $('dropzone').classList.remove('drag-over'); });
$('dropzone').addEventListener('drop', (event) => { const file = event.dataTransfer.files[0]; if (file && !state.busy) loadTrack(file); });
window.addEventListener('dragover', (event) => event.preventDefault());
window.addEventListener('drop', (event) => event.preventDefault());
laneButtons.forEach((button, lane) => {
  button.addEventListener('pointerdown', (event) => { event.preventDefault(); hitLane(lane); });
  button.addEventListener('click', (event) => { if (event.detail === 0) hitLane(lane); });
});
window.addEventListener('keydown', (event) => {
  const modal = document.querySelector('.modal-backdrop:not([hidden])');
  if (modal) {
    if (event.code === 'Escape') closeModal(modal.id);
    if (event.code === 'Tab') {
      const focusable = [...modal.querySelectorAll('button:not([disabled]), [href], input')];
      const first = focusable[0], last = focusable.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
    return;
  }
  if (event.repeat || event.ctrlKey || event.metaKey || event.altKey || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
  if (Object.hasOwn(keyLanes, event.code)) { event.preventDefault(); hitLane(keyLanes[event.code]); }
  if (event.code === 'Space' && ['playing', 'paused'].includes(state.phase)) { event.preventDefault(); state.phase === 'playing' ? pause() : resume(); }
  if (event.code === 'Enter' && event.target.tagName !== 'BUTTON' && event.target.tagName !== 'A') { event.preventDefault(); start(); }
});
document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
window.addEventListener('blur', pause);
setPhase('idle');
resize();
requestAnimationFrame(draw);
