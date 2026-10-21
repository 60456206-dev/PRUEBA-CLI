// All decoding, analysis and synthesis stay in this browser.
const yieldToBrowser = () => new Promise((resolve) => setTimeout(resolve, 0));
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

function percentile(values, fraction) {
  if (!values.length) return 0;
  const ordered = Array.from(values).sort((a, b) => a - b);
  return ordered[Math.floor((ordered.length - 1) * fraction)];
}

function estimateTempo(novelty, stepSeconds) {
  // Autocorrelation uses the actual changing onset envelope; tempo is descriptive
  // only. The chart below always uses individual measured transients.
  const firstLag = Math.ceil(60 / 200 / stepSeconds);
  const lastLag = Math.min(Math.floor(60 / 60 / stepSeconds), novelty.length - 2);
  const correlations = new Float64Array(lastLag + 2);
  let bestLag = 0;
  let bestScore = 0;
  for (let lag = firstLag; lag <= lastLag; lag += 1) {
    let cross = 0;
    let left = 0;
    let right = 0;
    for (let i = lag; i < novelty.length; i += 1) {
      cross += novelty[i] * novelty[i - lag];
      left += novelty[i] * novelty[i];
      right += novelty[i - lag] * novelty[i - lag];
    }
    const correlation = cross / Math.sqrt(left * right || 1);
    correlations[lag] = correlation;
    const bpm = 60 / (lag * stepSeconds);
    const preference = 0.93 + 0.07 * Math.exp(-Math.pow(Math.log(bpm / 120), 2) / 0.25);
    if (correlation * preference > bestScore) {
      bestScore = correlation * preference;
      bestLag = lag;
    }
  }
  if (!bestLag || bestScore < 0.12) return { bpm: null, confidence: 0 };
  const before = correlations[bestLag - 1] || 0;
  const center = correlations[bestLag];
  const after = correlations[bestLag + 1] || 0;
  const denominator = before - 2 * center + after;
  const offset = denominator ? clamp(0.5 * (before - after) / denominator, -0.5, 0.5) : 0;
  return {
    bpm: Math.round(60 / ((bestLag + offset) * stepSeconds)),
    confidence: clamp(center, 0, 1),
  };
}

/** Analyze AudioBuffer-shaped PCM without network requests or runtime dependencies. */
export async function analyzeAudio(buffer, onProgress = () => {}) {
  if (!buffer || !Number.isFinite(buffer.sampleRate) || buffer.sampleRate <= 0 || !buffer.length || !buffer.numberOfChannels) {
    throw new Error('No se pudo leer el audio de este archivo.');
  }
  onProgress(0);
  const sampleRate = buffer.sampleRate;
  const hop = Math.max(1, Math.round(sampleRate * 0.01));
  const stepSeconds = hop / sampleRate;
  const frameCount = Math.ceil(buffer.length / hop);
  const channels = Array.from({ length: Math.min(buffer.numberOfChannels, 2) }, (_, index) => buffer.getChannelData(index));
  // The detector needs band energy, not high-fidelity resampling. A bounded rate
  // keeps 96/192 kHz uploads affordable while retaining useful attacks.
  const stride = Math.max(1, Math.floor(sampleRate / 16000));
  const lowCoefficient = 1 - Math.exp(-2 * Math.PI * 180 * stride / sampleRate);
  const midCoefficient = 1 - Math.exp(-2 * Math.PI * 1800 * stride / sampleRate);
  const lowFilter = channels.map(() => 0);
  const midFilter = channels.map(() => 0);
  const energy = new Float32Array(frameCount);
  const lowEnergy = new Float32Array(frameCount);
  const highEnergy = new Float32Array(frameCount);
  const rawEnergy = new Float32Array(frameCount);
  let previousTotal = 0;
  let previousLow = 0;
  let previousHigh = 0;
  let previousSamples = 0;
  let maximumEnergy = 0;

  for (let frame = 0; frame < frameCount; frame += 1) {
    const end = Math.min(buffer.length, (frame + 1) * hop);
    let total = 0;
    let low = 0;
    let high = 0;
    let samples = 0;
    for (let index = frame * hop; index < end; index += stride) {
      for (let channel = 0; channel < channels.length; channel += 1) {
        const sample = channels[channel][index];
        lowFilter[channel] += lowCoefficient * (sample - lowFilter[channel]);
        midFilter[channel] += midCoefficient * (sample - midFilter[channel]);
        total += sample * sample;
        low += lowFilter[channel] * lowFilter[channel];
        const treble = sample - midFilter[channel];
        high += treble * treble;
        samples += 1;
      }
    }
    // Twenty-millisecond windows reduce false attacks from oscillator cycles.
    const windowSamples = Math.max(1, samples + previousSamples);
    energy[frame] = Math.sqrt((total + previousTotal) / windowSamples);
    lowEnergy[frame] = Math.sqrt((low + previousLow) / windowSamples);
    highEnergy[frame] = Math.sqrt((high + previousHigh) / windowSamples);
    rawEnergy[frame] = Math.sqrt(total / Math.max(1, samples));
    maximumEnergy = Math.max(maximumEnergy, energy[frame]);
    previousTotal = total;
    previousLow = low;
    previousHigh = high;
    previousSamples = samples;
    if (frame % 180 === 179) {
      onProgress(0.8 * frame / frameCount);
      await yieldToBrowser();
    }
  }

  const waveform = Array.from({ length: 192 }, (_, bin) => {
    const from = Math.floor(bin * frameCount / 192);
    const to = Math.max(from + 1, Math.floor((bin + 1) * frameCount / 192));
    let peak = 0;
    for (let frame = from; frame < Math.min(to, frameCount); frame += 1) peak = Math.max(peak, rawEnergy[frame]);
    return maximumEnergy > 0 ? clamp(Math.pow(peak / maximumEnergy, 0.65), 0, 1) : 0;
  });
  if (maximumEnergy < 0.00001) {
    onProgress(1);
    return { bpm: null, confidence: 0, peaks: [], waveform };
  }

  const novelty = new Float32Array(frameCount);
  const bandWeights = [0.42, 0.4, 0.18];
  const bands = [energy, lowEnergy, highEnergy];
  let maximumNovelty = 0;
  for (let frame = 1; frame < frameCount; frame += 1) {
    for (let band = 0; band < bands.length; band += 1) {
      const values = bands[band];
      const preceding = 0.6 * values[frame - 1] + 0.3 * values[Math.max(0, frame - 2)] + 0.1 * values[Math.max(0, frame - 3)];
      novelty[frame] += bandWeights[band] * Math.max(0, Math.log1p(values[frame] * 50) - Math.log1p(preceding * 50));
    }
    maximumNovelty = Math.max(maximumNovelty, novelty[frame]);
  }
  const minimumNovelty = Math.max(maximumNovelty * 0.055, percentile(novelty, 0.8) * 0.24, 0.006);
  const peaks = [];
  for (let frame = 2; frame < frameCount - 2; frame += 1) {
    const value = novelty[frame];
    if (value < minimumNovelty || energy[frame] < maximumEnergy * 0.002) continue;
    if (value < novelty[frame - 1] || value < novelty[frame - 2] || value <= novelty[frame + 1] || value <= novelty[frame + 2]) continue;
    const localMedian = percentile(novelty.subarray(Math.max(0, frame - 16), Math.min(frameCount, frame + 17)), 0.5);
    if (value < localMedian * 2.1 + minimumNovelty * 0.55) continue;
    const peak = {
      time: Math.max(0, frame * stepSeconds - 0.005),
      strength: clamp(Math.sqrt(value / maximumNovelty), 0, 1),
    };
    const previous = peaks[peaks.length - 1];
    if (previous && peak.time - previous.time < 0.09) {
      if (peak.strength > previous.strength) peaks[peaks.length - 1] = peak;
    } else {
      peaks.push(peak);
    }
    if (frame % 500 === 0) await yieldToBrowser();
  }
  onProgress(0.9);
  await yieldToBrowser();
  const tempo = peaks.length >= 4 ? estimateTempo(novelty, stepSeconds) : { bpm: null, confidence: 0 };
  onProgress(1);
  return { ...tempo, peaks, waveform };
}

/** Select measured onsets, favoring stronger attacks at lower difficulties. */
export function buildChart(analysis, difficulty = 'normal', duration = Infinity) {
  const settings = {
    easy: { spacing: 0.37, quantile: 0.46 },
    normal: { spacing: 0.225, quantile: 0.2 },
    hard: { spacing: 0.15, quantile: 0 },
  }[difficulty] || { spacing: 0.225, quantile: 0.2 };
  const candidates = (analysis?.peaks || [])
    .filter((peak) => Number.isFinite(peak.time) && peak.time >= 1.5 && peak.time < duration - 0.4 && Number.isFinite(peak.strength) && peak.strength > 0)
    .map((peak) => ({ ...peak }))
    .sort((a, b) => a.time - b.time);
  const cutoff = percentile(candidates.map((peak) => peak.strength), settings.quantile);
  const selected = [];
  for (const peak of candidates) {
    if (peak.strength < cutoff) continue;
    const previous = selected[selected.length - 1];
    // Keep the earliest qualifying attack so a crescendo cannot repeatedly
    // push the preceding note forward and erase an entire rhythmic phrase.
    if (!previous || peak.time - previous.time >= settings.spacing - 0.000001) selected.push(peak);
  }
  // A repeatable hand-friendly phrase; rhythm and strength come from the song.
  const lanePhrase = [0, 1, 3, 2, 1, 0, 2, 3, 0, 2, 1, 3, 2, 0, 3, 1];
  return selected.map((peak, index) => ({
    time: peak.time,
    lane: lanePhrase[index % lanePhrase.length],
    strength: clamp(peak.strength, 0, 1),
  }));
}

/** Original 128 BPM instrumental, synthesized locally into an AudioBuffer. */
export async function createDemo(audioContext) {
  const sampleRate = audioContext.sampleRate;
  const duration = 60.4;
  const output = audioContext.createBuffer(2, Math.ceil(duration * sampleRate), sampleRate);
  const left = output.getChannelData(0);
  const right = output.getChannelData(1);
  const beat = 60 / 128;
  let seed = 5817;
  const noise = () => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 2147483648 - 1;
  };
  const mix = (time, length, synth, pan = 0) => {
    const start = Math.floor(time * sampleRate);
    const count = Math.min(Math.ceil(length * sampleRate), left.length - start);
    const gainLeft = Math.sqrt((1 - pan) * 0.5);
    const gainRight = Math.sqrt((1 + pan) * 0.5);
    for (let index = 0; index < count; index += 1) {
      const value = synth(index / sampleRate, index);
      left[start + index] += value * gainLeft;
      right[start + index] += value * gainRight;
    }
  };
  const midi = (note) => 440 * Math.pow(2, (note - 69) / 12);
  const roots = [45, 41, 48, 43];
  const melody = [0, 7, 12, 7, 3, 10, 7, 15];

  for (let bar = 0; bar < 32; bar += 1) {
    const root = roots[Math.floor(bar / 2) % roots.length];
    const breakSection = bar >= 16 && bar < 20;
    const intro = bar < 4;
    for (let quarter = 0; quarter < 4; quarter += 1) {
      const time = (bar * 4 + quarter) * beat;
      if (!breakSection || quarter === 0) {
        mix(time, 0.32, (t) => {
          const phase = 2 * Math.PI * (46 * t + 95 * 0.024 * (1 - Math.exp(-t / 0.024)));
          return Math.sin(phase) * Math.exp(-t * 17) * 0.9 + noise() * Math.exp(-t * 270) * 0.08;
        });
      }
      if ((quarter === 1 || quarter === 3) && !intro && !breakSection) {
        let lastNoise = 0;
        mix(time, 0.19, (t) => {
          const sample = noise();
          const high = sample - lastNoise * 0.75;
          lastNoise = sample;
          return (high * 0.29 + Math.sin(2 * Math.PI * 182 * t) * 0.12) * Math.exp(-t * 25) * Math.min(1, t * 2000);
        }, 0.12);
      }
      if (!breakSection) {
        for (let eighth = 0; eighth < 2; eighth += 1) {
          mix(time + eighth * beat / 2, 0.06, (t) => noise() * Math.exp(-t * 90) * (eighth ? 0.1 : 0.065), eighth ? 0.35 : -0.3);
        }
        const bassFrequency = midi(root - 12 + (quarter === 3 ? 7 : 0));
        mix(time + beat / 2, beat * 0.45, (t) => {
          const envelope = Math.min(1, t * 140) * Math.exp(-t * 9);
          return (Math.sin(2 * Math.PI * bassFrequency * t) + 0.24 * Math.sin(4 * Math.PI * bassFrequency * t)) * envelope * 0.29;
        });
      }
      if (bar >= 4 && !breakSection) {
        for (let eighth = 0; eighth < 2; eighth += 1) {
          const note = root + 12 + melody[(quarter * 2 + eighth + (bar % 2 ? 2 : 0)) % melody.length];
          const frequency = midi(note);
          const noteTime = time + eighth * beat / 2;
          const notePan = eighth ? 0.45 : -0.45;
          const pluck = (t) => {
            const envelope = Math.min(1, t * 350) * Math.exp(-t * 15);
            return (Math.sin(2 * Math.PI * frequency * t) + 0.2 * Math.sin(4 * Math.PI * frequency * t)) * envelope * 0.125;
          };
          mix(noteTime, 0.38, pluck, notePan);
          mix(noteTime + beat * 0.75, 0.38, (t) => pluck(t) * 0.24, -notePan);
        }
      }
    }
    for (const interval of [0, 3, 7]) {
      const frequency = midi(root + 12 + interval);
      mix(bar * 4 * beat, 4 * beat + 0.15, (t) => {
        const envelope = Math.min(1, t * 4) * Math.min(1, Math.max(0, (4 * beat + 0.15 - t) * 4));
        return (Math.sin(2 * Math.PI * frequency * t) + 0.35 * Math.sin(2 * Math.PI * frequency * 1.003 * t)) * envelope * (breakSection ? 0.045 : 0.027);
      }, interval === 3 ? -0.4 : 0.3);
    }
    if (bar % 2 === 1) await yieldToBrowser();
  }
  let maximum = 0;
  for (let index = 0; index < left.length; index += 1) maximum = Math.max(maximum, Math.abs(left[index]), Math.abs(right[index]));
  const gain = maximum ? 0.91 / maximum : 1;
  for (let index = 0; index < left.length; index += 1) {
    const fade = Math.min(1, index / (sampleRate * 0.008), (left.length - index) / (sampleRate * 0.5));
    left[index] *= gain * fade;
    right[index] *= gain * fade;
  }
  return output;
}
