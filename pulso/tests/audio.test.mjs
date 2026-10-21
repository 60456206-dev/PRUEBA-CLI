import test from 'node:test';
import assert from 'node:assert/strict';
import { analyzeAudio, buildChart, createDemo } from '../dist/audio.js';

function buffer(duration, sampleRate = 22050, numberOfChannels = 1) {
  const length = Math.ceil(duration * sampleRate);
  const channels = Array.from({ length: numberOfChannels }, () => new Float32Array(length));
  return { length, sampleRate, numberOfChannels, duration: length / sampleRate, getChannelData: (index) => channels[index] };
}

function pulseTrain(bpm = 120, duration = 16) {
  const audio = buffer(duration);
  const samples = audio.getChannelData(0);
  for (let time = 0.5; time < duration - 0.2; time += 60 / bpm) {
    const from = Math.round(time * audio.sampleRate);
    for (let index = 0; index < audio.sampleRate * 0.13; index += 1) {
      const t = index / audio.sampleRate;
      samples[from + index] += Math.sin(2 * Math.PI * 90 * t) * Math.exp(-t * 35) * Math.min(1, t * 1500);
    }
  }
  return audio;
}

test('silence has no fabricated BPM, onsets, or chart', async () => {
  const result = await analyzeAudio(buffer(5));
  assert.equal(result.bpm, null);
  assert.equal(result.confidence, 0);
  assert.deepEqual(result.peaks, []);
  assert.ok(result.waveform.every((sample) => sample === 0));
  assert.deepEqual(buildChart(result, 'hard', 5), []);
});

test('known 120 BPM pulses produce accurate measured onsets and tempo', async () => {
  const progress = [];
  const result = await analyzeAudio(pulseTrain(), (value) => progress.push(value));
  assert.ok(Math.abs(result.bpm - 120) <= 1, `Estimated ${result.bpm} BPM`);
  assert.ok(result.confidence > 0.7);
  assert.ok(result.peaks.length >= 29 && result.peaks.length <= 33, `Found ${result.peaks.length} onsets`);
  for (const peak of result.peaks) {
    const closestPulse = Math.round((peak.time - 0.5) / 0.5) * 0.5 + 0.5;
    assert.ok(Math.abs(peak.time - closestPulse) < 0.035, `Offset at ${peak.time}`);
  }
  assert.equal(result.waveform.length, 192);
  assert.equal(progress[0], 0);
  assert.equal(progress.at(-1), 1);
  assert.ok(progress.every((value, index) => index === 0 || value >= progress[index - 1]));
});

test('changing rhythms are retained instead of snapped to a BPM grid', async () => {
  const audio = buffer(8);
  const positions = [0.6, 1.71, 2.03, 2.84, 3.25, 4.42, 5.1, 5.91, 6.24, 7.12];
  for (const position of positions) {
    const start = Math.round(position * audio.sampleRate);
    for (let index = 0; index < 1800; index += 1) {
      const t = index / audio.sampleRate;
      audio.getChannelData(0)[start + index] = Math.sin(t * 2 * Math.PI * 120) * Math.exp(-t * 45);
    }
  }
  const result = await analyzeAudio(audio);
  for (const position of positions) assert.ok(result.peaks.some((peak) => Math.abs(peak.time - position) < 0.035), `Missing ${position}`);
  const chart = buildChart(result, 'hard', audio.duration);
  assert.ok(chart.every((note) => result.peaks.some((peak) => peak.time === note.time)));
});

test('chart difficulties preserve spacing, boundaries, determinism, and valid lanes', () => {
  const analysis = { peaks: Array.from({ length: 200 }, (_, i) => ({ time: i * 0.1, strength: 0.4 + (i % 5) * 0.15 })) };
  const charts = ['easy', 'normal', 'hard'].map((difficulty) => buildChart(analysis, difficulty, 20));
  assert.ok(charts[0].length < charts[1].length);
  assert.ok(charts[1].length < charts[2].length);
  for (const [difficultyIndex, chart] of charts.entries()) {
    const spacing = [0.37, 0.225, 0.15][difficultyIndex];
    assert.ok(chart.length > 0);
    for (let index = 0; index < chart.length; index += 1) {
      assert.ok(chart[index].time >= 1.5 && chart[index].time < 19.6);
      assert.ok(Number.isInteger(chart[index].lane) && chart[index].lane >= 0 && chart[index].lane <= 3);
      if (index) assert.ok(chart[index].time - chart[index - 1].time >= spacing - 1e-6);
    }
  }
  assert.deepEqual(buildChart(analysis, 'normal', 20), charts[1]);
});

test('opposite-phase stereo still yields audible onsets', async () => {
  const mono = pulseTrain(120, 6);
  const stereo = buffer(6, mono.sampleRate, 2);
  stereo.getChannelData(0).set(mono.getChannelData(0));
  stereo.getChannelData(1).set(mono.getChannelData(0).map((sample) => -sample));
  const result = await analyzeAudio(stereo);
  assert.ok(result.peaks.length >= 10);
  assert.ok(Math.abs(result.bpm - 120) <= 1);
});

test('demo is playable stereo PCM, bounded, and detects a chart', async () => {
  const context = {
    sampleRate: 16000,
    createBuffer: (channels, length, sampleRate) => buffer(length / sampleRate, sampleRate, channels),
  };
  const demo = await createDemo(context);
  assert.ok(demo.duration >= 48 && demo.duration <= 65);
  assert.equal(demo.numberOfChannels, 2);
  let maximum = 0;
  for (const sample of demo.getChannelData(0)) {
    assert.ok(Number.isFinite(sample));
    maximum = Math.max(maximum, Math.abs(sample));
  }
  assert.ok(maximum > 0.5 && maximum < 1);
  const result = await analyzeAudio(demo);
  assert.ok(Math.abs(result.bpm - 128) <= 3, `Estimated ${result.bpm} BPM`);
  const easy = buildChart(result, 'easy', demo.duration);
  const normal = buildChart(result, 'normal', demo.duration);
  const hard = buildChart(result, 'hard', demo.duration);
  assert.ok(easy.length >= 70, `Easy: ${easy.length}`);
  assert.ok(hard.length > easy.length, `Easy ${easy.length}; hard ${hard.length}`);
  assert.ok(normal.length >= easy.length);
});
