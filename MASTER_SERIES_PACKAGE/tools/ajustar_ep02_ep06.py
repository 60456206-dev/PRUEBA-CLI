#!/usr/bin/env python3
"""Prepara stems, mezcla EBU R128 (-16 LUFS), subtítulos y renderiza EP02 a EP06 ajustados (V2)."""
import json
import subprocess
import wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "AUDIO"
FINAL_DIR = ROOT / "FINAL"
SR = 48000


def run(cmd: list[str], input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, input=input_bytes, check=True, capture_output=True)


def read_wav(p: Path) -> np.ndarray:
    out = run(["ffmpeg", "-v", "error", "-i", str(p), "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"]).stdout
    return np.frombuffer(out, dtype="<f4").copy()


def save_wav(p: Path, x: np.ndarray) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(p), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((np.clip(x, -1.0, 1.0) * 32767).astype("<i2").tobytes())


def af_process(x: np.ndarray, af_filter: str) -> np.ndarray:
    p = run(
        ["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "pipe:0", "-af", af_filter, "-f", "f32le", "pipe:1"],
        input_bytes=x.astype("<f4").tobytes(),
    )
    return np.frombuffer(p.stdout, dtype="<f4").copy()


def add_at(dst: np.ndarray, src: np.ndarray, t_sec: float) -> None:
    i = max(0, round(t_sec * SR))
    if i >= len(dst):
        return
    n = min(len(src), len(dst) - i)
    dst[i : i + n] += src[:n]


def synth_noise(rng: np.random.Generator, n: int, width: int) -> np.ndarray:
    x = rng.normal(size=n)
    x = np.convolve(x, np.ones(width) / width, mode="same")
    return x / (np.std(x) + 1e-9)


def synth_rustle(rng: np.random.Generator, seconds: float, amp: float) -> np.ndarray:
    n = int(seconds * SR)
    t = np.arange(n) / SR
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    mod = 0.65 + 0.35 * np.sin(2 * np.pi * 6.5 * t)
    return synth_noise(rng, n, 18) * env * mod * amp


def synth_paper(rng: np.random.Generator, seconds: float, amp: float) -> np.ndarray:
    n = int(seconds * SR)
    env = np.sin(np.pi * np.arange(n) / n) ** 1.5
    raw = synth_noise(rng, n, 6) * env * amp
    return af_process(raw, "highpass=f=450,lowpass=f=6500")


def synth_drop(amp: float = 0.032, dull: bool = False) -> np.ndarray:
    t = np.arange(int(0.26 * SR)) / SR
    f0, f1 = (950, 650) if dull else (1420, 1080)
    drop = amp * np.sin(2 * np.pi * (f0 * t - f1 * t * t)) * np.exp(-t * 30)
    return af_process(drop, f"lowpass=f={1300 if dull else 1850}")


def synth_button_click() -> np.ndarray:
    t = np.arange(int(0.06 * SR)) / SR
    click1 = 0.045 * np.sin(2 * np.pi * 2100 * t) * np.exp(-t * 140)
    click2 = 0.030 * np.sin(2 * np.pi * 1400 * t) * np.exp(-t * 110)
    out = np.zeros(int(0.14 * SR), dtype="<f4")
    add_at(out, click1, 0.0)
    add_at(out, click2, 0.045)
    return out


def synth_floodgate_motif(rng: np.random.Generator) -> np.ndarray:
    """Dos golpes metálicos (0.0s y 0.8s relativos) + arrastre metálico (1.4–2.5s)."""
    total = int(2.8 * SR)
    out = np.zeros(total, dtype="<f4")
    t_hit = np.arange(int(0.45 * SR)) / SR
    for hit_t, gain in [(0.0, 0.085), (0.8, 0.095)]:
        hit = gain * (
            0.6 * np.sin(2 * np.pi * 165 * t_hit) * np.exp(-t_hit * 14)
            + 0.3 * np.sin(2 * np.pi * 312 * t_hit) * np.exp(-t_hit * 22)
            + 0.1 * np.sin(2 * np.pi * 540 * t_hit) * np.exp(-t_hit * 35)
        )
        add_at(out, hit, hit_t)
    n_drag = int(1.1 * SR)
    t_drag = np.arange(n_drag) / SR
    env = np.sin(np.pi * np.arange(n_drag) / n_drag) ** 1.3
    scrape = synth_noise(rng, n_drag, 12) * env * 0.035
    tonal = 0.025 * np.sin(2 * np.pi * (240 + 40 * np.sin(2 * np.pi * 2.5 * t_drag)) * t_drag) * env
    drag = af_process(scrape + tonal, "bandpass=f=420:w=280")
    add_at(out, drag, 1.45)
    return out


def synth_key_touch() -> np.ndarray:
    t = np.arange(int(0.18 * SR)) / SR
    clink = 0.028 * (
        0.7 * np.sin(2 * np.pi * 2850 * t) * np.exp(-t * 45)
        + 0.3 * np.sin(2 * np.pi * 4120 * t) * np.exp(-t * 65)
    )
    return af_process(clink, "highpass=f=600,lowpass=f=5500")


def synth_ui_confirm() -> np.ndarray:
    t = np.arange(int(0.22 * SR)) / SR
    tone = 0.018 * np.sin(2 * np.pi * 880 * t) * np.exp(-t * 24)
    return af_process(tone, "lowpass=f=2200")


def stamp_srt(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


EPISODE_CONFIG = {
    "EP02": {
        "full_duration": 52,
        # (shot_idx_1based, source_in, source_out, max_source_out)
        "segments": [
            (0.0, 4.0, 5.0),     # SH01 (0-5)
            (5.0, 9.25, 12.0),   # SH02 (5-12)
            (12.0, 15.5, 17.0),  # SH03 (12-17)
            (17.0, 23.5, 25.0),  # SH04 (17-25)
            (25.0, 29.5, 31.0),  # SH05 (25-31)
            (31.0, 37.5, 38.0),  # SH06 (31-38)
            (38.0, 42.75, 44.0), # SH07 (38-44)
            (44.0, 50.0, 52.0),  # SH08 (44-52)
        ],
        # (line_id, shot_idx_0based, offset_in_shot, mode, subtitle_text, full_timeline_time)
        "dialogue": [
            ("L01", 0, 0.55, "off", "Mara. ¿Me oyes?", 0.5),
            ("L02", 1, 0.55, "off", "No vuelve. Ya no está.", 6.0),
            ("L03", 3, 0.65, "mara_tela", "Son las seis y diez. Han cerrado.\nSeguimos aquí.", 18.0),
            ("L04", 5, 0.85, "mara_playback", "Son las seis y diez. Han cerrado.\nSeguimos aquí.", 32.0),
            ("L05", 6, 0.45, "off", "La tela se calla. La grabación no.", 38.5),
            ("L06", 7, 0.55, "off", "Aquí pone que a las seis\nya no quedaba nadie.", 45.0),
        ],
        "high_contrast_shots": {0, 3, 6},
    },
    "EP03": {
        "full_duration": 53,
        "segments": [
            (0.0, 3.5, 5.0),     # SH01 (0-5)
            (5.0, 10.0, 12.0),   # SH02 (5-12)
            (12.0, 16.75, 18.0), # SH03 (12-18)
            (19.5, 24.25, 26.0), # SH04 (18-26, skip first 1.5s parted lips)
            (26.0, 29.75, 31.0), # SH05 (26-31)
            (32.5, 38.5, 39.0),  # SH06 (31-39, skip first 1.5s unwanted hands!)
            (39.0, 43.0, 45.0),  # SH07 (39-45, eyes close/open 0.5-3.0s)
            (45.0, 51.5, 53.0),  # SH08 (45-53)
        ],
        "dialogue": [
            ("L01", 1, 0.55, "off", "¿Por qué guardabas la llave\nde la compuerta?", 6.0),
            ("L02", 2, 0.50, "off", "Yo llevaba las llaves.\nEso ya lo sabes.", 12.5),
            ("L03", 3, 0.55, "off", "No busques solo mi nombre.", 19.0),
            ("L04", 5, 0.55, "mara_tela", "Mamá. Te oigo al otro lado. Abre.", 32.0),
            ("L05", 7, 0.60, "off", "La oíste.", 46.0),
            ("L06", 7, 3.20, "off", "Y no abriste.", 50.0),
        ],
        "high_contrast_shots": {0, 4, 5},
    },
    "EP04": {
        "full_duration": 55,
        "segments": [
            (1.25, 5.0, 5.0),    # SH01 (0-5, start at 1.25s palm opening reveal)
            (5.0, 11.0, 13.0),   # SH02 (5-13)
            (13.0, 17.75, 20.0), # SH03 (13-20)
            (20.0, 25.0, 28.0),  # SH04 (20-28)
            (28.0, 31.25, 33.0), # SH05 (28-33)
            (33.0, 40.25, 41.0), # SH06 (33-41)
            (41.0, 45.0, 46.0),  # SH07 (41-47, stop at 45.0s before gaze lifts at 5.25s!)
            (47.0, 53.5, 55.0),  # SH08 (47-55)
        ],
        "dialogue": [
            ("L01", 1, 0.45, "off", "El agua iba hacia la sala norte.\nTú estabas allí.", 5.5),
            ("L02", 2, 0.50, "off", "Cerré para que no te alcanzara.", 13.5),
            ("L03", 3, 0.55, "off", "¿Sabías que Mara seguía dentro?", 21.0),
            ("L04", 4, 0.65, "off", "Sí.", 29.0),
            ("L05", 5, 0.50, "off", "No podía perderos a las dos.", 34.0),
            ("L06", 5, 3.80, "off", "La perdiste tú. A mí me mentiste.", 38.0),
            ("L07", 7, 0.55, "off", "Yo cerré la puerta.\nTú firmaste que no quedaba nadie.", 48.0),
        ],
        "high_contrast_shots": {0, 5, 7},
    },
    "EP05": {
        "full_duration": 53,
        "segments": [
            (0.0, 3.75, 5.0),    # SH01 (0-5)
            (5.0, 10.5, 12.0),   # SH02 (5-12)
            (12.0, 16.25, 18.0), # SH03 (12-18)
            (18.0, 22.0, 26.0),  # SH04 (18-26)
            (26.0, 29.75, 31.0), # SH05 (26-31)
            (31.0, 37.75, 39.0), # SH06 (31-39)
            (39.0, 43.25, 45.0), # SH07 (39-45)
            (45.0, 50.25, 53.0), # SH08 (45-53)
        ],
        "dialogue": [
            ("L01", 0, 0.45, "off", "Me dijiste que habías comprobado.", 0.5),
            ("L02", 1, 0.50, "off", "Y yo firmé. Sin mirar. Me acuerdo.", 5.5),
            ("L03", 2, 0.55, "off", "Puedes mandar solo la grabación.", 13.0),
            ("L04", 5, 0.50, "mara_tela", "Somos siete. Si alguien oye esto,\nque no quite a ninguno.", 31.5),
            ("L05", 6, 0.55, "off", "La página entera. Y mi nombre.", 40.0),
            ("L06", 7, 0.65, "mara_tela", "Voy a decir los nombres.", 46.0),
        ],
        "high_contrast_shots": {4, 5, 7},
    },
    "EP06": {
        "full_duration": 54,
        "segments": [
            (0.0, 6.75, 8.0),    # SH01 (0-8)
            (8.0, 14.25, 15.0),  # SH02 (8-15)
            (15.0, 20.25, 21.0), # SH03 (15-21)
            (21.0, 26.0, 28.0),  # SH04 (21-28)
            (28.75, 33.0, 33.0), # SH05 (28-33, capture spinner -> green checkmark 3.5-5.0s!)
            (33.0, 39.5, 40.0),  # SH06 (33-40, hand withdraws by ~6s)
            (40.0, 44.5, 46.0),  # SH07 (40-46)
            (46.0, 52.5, 54.0),  # SH08 (46-54)
        ],
        "dialogue": [
            ("L01", 0, 0.45, "mara_tela", "Elena Ríos. Tomás Vera.\nLuz Arce. Bruno Sol.", 0.5),
            ("L02", 1, 0.50, "mara_tela", "Celia Paz. Samuel Costa.\nY yo, Mara Vidal.", 8.5),
            ("L03", 2, 0.50, "off", "Firmé sin comprobar.\nAdjuntaré mi declaración.", 15.5),
            ("L04", 3, 0.65, "off", "No voy a quitar tu nombre.", 22.0),
            ("L05", 5, 0.65, "off", "Deja el mío también.\n¿Puedo quedarme?", 34.0),
            ("L06", 6, 0.55, "mara_playback", "Y yo, Mara Vidal.", 40.5),
            ("L07", 7, 0.65, "off", "Si no apagas eso.", 46.5),
        ],
        "high_contrast_shots": {1, 5, 7},
    },
}


def process_episode(ep: str, cfg: dict) -> None:
    print(f"=== Procesando {ep} ===", flush=True)
    ep_dir = AUDIO_DIR / ep
    ajuste_dir = ep_dir / "AJUSTE_V2"
    ajuste_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(int(ep[-2:]) * 101)

    records = json.loads((ep_dir / "generacion.json").read_text())
    latest_by_id = {}
    for r in records:
        if r.get("file") and (ep_dir / r["file"]).exists():
            latest_by_id[r["id"]] = r

    # 1. Edit & QA raw voice takes + prepare full-duration stems
    n_full = cfg["full_duration"] * SR
    room_full = synth_noise(rng, n_full, 200) * 0.0012
    room_full *= np.minimum(1.0, np.arange(n_full) / SR) * np.minimum(1.0, np.arange(n_full)[::-1] / SR)
    foley_full = np.zeros(n_full, dtype="<f4")
    sfx_full = np.zeros(n_full, dtype="<f4")
    dialog_full = np.zeros(n_full, dtype="<f4")

    qa = []
    edited_map: dict[str, Path] = {}
    edited_dur: dict[str, float] = {}

    for d_id, shot_idx, offset_in_shot, mode, sub_txt, full_t in cfg["dialogue"]:
        r = latest_by_id[d_id]
        src_p = ep_dir / r["file"]
        x = read_wav(src_p)
        peak = float(np.max(np.abs(x)))
        rms = float(np.sqrt(np.mean(x * x)))
        active = np.where(np.abs(x) > 0.003)[0]
        if len(active):
            x = x[max(0, active[0] - int(0.06 * SR)) : min(len(x), active[-1] + int(0.12 * SR))]
        ratio = (len(x) / SR) / r["target_seconds"]
        if 1.0 < ratio <= 1.15:
            x = af_process(x, f"atempo={ratio:.6f}")
        elif ratio > 1.15:
            x = af_process(x, "atempo=1.12")
        x *= min(3.0, 0.45 / max(peak, 1e-8))
        fade = min(240, len(x) // 2)
        if fade > 0:
            x[:fade] *= np.linspace(0.0, 1.0, fade)
            x[-fade:] *= np.linspace(1.0, 0.0, fade)
        edit_name = f"{ep}_{r['file'].split('/')[-1].split('_T')[0].split('_', 1)[1]}_EDIT.wav"
        edit_p = ep_dir / "EDITADOS" / edit_name
        save_wav(edit_p, x)
        edited_map[d_id] = edit_p
        edited_dur[d_id] = len(x) / SR
        qa.append(
            {
                "id": d_id,
                "source": r["file"],
                "edited": str(edit_p.relative_to(ep_dir)),
                "seconds": round(len(x) / SR, 4),
                "tempo_ratio": round(ratio, 4) if 1.0 < ratio <= 1.15 else (1.12 if ratio > 1.15 else 1.0),
                "peak_source": round(peak, 4),
                "rms_source": round(rms, 4),
                "fits_window": (len(x) / SR) <= (r["target_seconds"] + 0.5),
            }
        )
        add_at(dialog_full, x, full_t)

    (ep_dir / "revision_tecnica.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2))
    for sname, sarr in [("DIALOGUE", dialog_full), ("ROOM", room_full), ("FOLEY", foley_full), ("SFX", sfx_full)]:
        save_wav(ep_dir / "STEMS" / f"{ep}_{sname}.wav", sarr)
    save_wav(ep_dir / f"{ep}_MEZCLA_PREVIA.wav", dialog_full + room_full + foley_full + sfx_full)

    # 2. Ensure segment durations comfortably fit all dialogue lines in each shot
    segments = []
    for s_idx, (src_in, src_out, max_out) in enumerate(cfg["segments"]):
        req_len = src_out - src_in
        for d_id, d_shot, d_off, _mode, _txt, _ft in cfg["dialogue"]:
            if d_shot == s_idx:
                needed = d_off + edited_dur[d_id] + 0.35
                if needed > req_len:
                    req_len = needed
        # Round up to nearest 0.25s (6 frames at 24fps) within max_out
        req_len = np.ceil(req_len * 4.0) / 4.0
        final_out = min(max_out, src_in + req_len)
        segments.append((src_in, final_out))

    starts = np.cumsum([0.0] + [b - a for a, b in segments]).tolist()
    duration = round(starts[-1], 4)
    n_v2 = round(duration * SR)

    # 3. Build V2 Stems (ROOM, FOLEY, SFX, DIALOGUE)
    room_v2 = synth_noise(rng, n_v2, 200) * 0.0011
    room_v2 *= np.minimum(1.0, np.arange(n_v2) / SR) * np.minimum(1.0, np.arange(n_v2)[::-1] / SR)
    foley_v2 = np.zeros(n_v2, dtype="<f4")
    sfx_v2 = np.zeros(n_v2, dtype="<f4")
    dialog_v2 = np.zeros(n_v2, dtype="<f4")

    # Add subtle sleeve/cloth foley on shot transitions & actions
    for s_idx in range(8):
        t_shot = starts[s_idx]
        add_at(foley_v2, synth_rustle(rng, 0.65, 0.0032), t_shot + 0.25)

    # Episode-specific Foley & SFX
    if ep == "EP02":
        # SH01: dull drop on already-clean wool
        add_at(sfx_v2, synth_drop(0.018, dull=True), starts[0] + 0.35)
        # SH03: button press on recorder
        add_at(sfx_v2, synth_button_click(), starts[2] + 1.1)
        # SH04: water drop on fresh salt
        add_at(sfx_v2, synth_drop(0.028, dull=False), starts[3] + 0.30)
        # SH05: floodgate motif (2 strikes + metallic drag)
        motif = synth_floodgate_motif(rng)
        add_at(sfx_v2, motif, starts[4] + 0.45)
        # SH06: replayed floodgate motif (filtered through recorder speaker)
        motif_replay = af_process(motif * 0.42, "highpass=f=350,lowpass=f=3200")
        add_at(sfx_v2, motif_replay, starts[5] + 0.15)
        # SH07: subtle drop echo
        add_at(sfx_v2, synth_drop(0.014, dull=True), starts[6] + 0.20)
        # SH08: dry paper foley
        add_at(foley_v2, synth_paper(rng, 0.9, 0.0045), starts[7] + 0.25)

    elif ep == "EP03":
        # SH01: subtle key/paper touch
        add_at(foley_v2, synth_key_touch() * 0.45, starts[0] + 0.4)
        # SH03: dry paper foley
        add_at(foley_v2, synth_paper(rng, 0.85, 0.0042), starts[2] + 0.2)
        # SH05: water drop on salt
        add_at(sfx_v2, synth_drop(0.028, dull=False), starts[4] + 0.75)
        # SH06: textile breath before Mara speaks
        breath_p = AUDIO_DIR / "EP01/EDITADOS/EP01_MARA_X01_EDIT.wav"
        if breath_p.exists():
            b_wav = af_process(read_wav(breath_p), "highpass=f=120,lowpass=f=5500") * 0.30
            add_at(foley_v2, b_wav, starts[5] + 0.1)

    elif ep == "EP04":
        # SH01: palm opens on iron key
        add_at(foley_v2, synth_key_touch() * 0.55, starts[0] + 0.5)
        # SH06: wool textile presence
        add_at(foley_v2, synth_rustle(rng, 1.2, 0.0045), starts[5] + 0.15)
        # SH08: dry paper foley
        add_at(foley_v2, synth_paper(rng, 0.95, 0.0045), starts[7] + 0.2)

    elif ep == "EP05":
        # SH01: dry paper foley
        add_at(foley_v2, synth_paper(rng, 0.8, 0.0042), starts[0] + 0.15)
        # SH05: water drop on last white salt strip
        add_at(sfx_v2, synth_drop(0.028, dull=False), starts[4] + 0.85)
        # SH06: textile breath
        breath_p = AUDIO_DIR / "EP01/EDITADOS/EP01_MARA_X01_EDIT.wav"
        if breath_p.exists():
            b_wav = af_process(read_wav(breath_p), "highpass=f=120,lowpass=f=5500") * 0.28
            add_at(foley_v2, b_wav, starts[5] + 0.08)
        # SH08: final dissolution drop
        add_at(sfx_v2, synth_drop(0.020, dull=True), starts[7] + 0.30)

    elif ep == "EP06":
        # SH02: wool settling
        add_at(foley_v2, synth_rustle(rng, 1.1, 0.0040), starts[1] + 0.20)
        # SH05: subtle UI send confirmation
        add_at(sfx_v2, synth_ui_confirm(), starts[4] + 1.85)
        # SH06: key left on paper document as hand withdraws
        add_at(foley_v2, synth_key_touch() * 0.50, starts[5] + 0.35)
        add_at(foley_v2, synth_paper(rng, 0.7, 0.0038), starts[5] + 0.45)

    # Process and place V2 dialogue lines
    events = []
    for d_id, shot_idx, offset_in_shot, mode, sub_txt, _ft in cfg["dialogue"]:
        x = read_wav(edited_map[d_id])
        t_start = round(starts[shot_idx] + offset_in_shot, 3)
        if mode == "mara_tela":
            x = af_process(
                x,
                "highpass=f=85,lowpass=f=6500,acompressor=threshold=0.09:ratio=2:attack=8:release=100:makeup=1",
            )
            target_db = -24.0
            gain = min(
                10 ** (target_db / 20.0) / max(np.sqrt(np.mean(x * x)), 1e-8),
                0.78 / max(np.max(np.abs(x)), 1e-8),
            )
            x *= gain
            x = af_process(x, "aecho=0.96:1:27|53:0.045|0.025")
        elif mode == "mara_playback":
            x = af_process(
                x,
                "highpass=f=320,lowpass=f=3400,acompressor=threshold=0.08:ratio=2.8:attack=5:release=90:makeup=1.1",
            )
            target_db = -23.5
            gain = min(
                10 ** (target_db / 20.0) / max(np.sqrt(np.mean(x * x)), 1e-8),
                0.75 / max(np.max(np.abs(x)), 1e-8),
            )
            x *= gain
        else:
            x = af_process(
                x,
                "highpass=f=85,lowpass=f=10000,acompressor=threshold=0.09:ratio=2:attack=8:release=100:makeup=1",
            )
            target_db = -22.0
            gain = min(
                10 ** (target_db / 20.0) / max(np.sqrt(np.mean(x * x)), 1e-8),
                0.78 / max(np.max(np.abs(x)), 1e-8),
            )
            x *= gain

        save_wav(ajuste_dir / f"{d_id}.wav", x)
        add_at(dialog_v2, x, t_start)
        t_end = round(t_start + len(x) / SR, 3)
        events.append({"id": d_id, "shot": shot_idx + 1, "start": t_start, "end": t_end, "text": sub_txt.replace("\n", " "), "sub": sub_txt})

    # Fade out tails on room, foley, sfx
    fade_out_n = round(0.18 * SR)
    for arr in (room_v2, foley_v2, sfx_v2):
        arr[-fade_out_n:] *= np.linspace(1.0, 0.0, fade_out_n)

    for sname, sarr in [("DIALOGUE", dialog_v2), ("ROOM", room_v2), ("FOLEY", foley_v2), ("SFX", sfx_v2)]:
        save_wav(ajuste_dir / f"{ep}_{sname}_V2.wav", sarr)

    premaster = dialog_v2 + room_v2 + foley_v2 + sfx_v2
    premaster_p = ajuste_dir / "PREMASTER.wav"
    save_wav(premaster_p, premaster)

    # Two-pass EBU R128 loudness normalization (-16 LUFS, -1.5 dBTP)
    p = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(premaster_p),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json",
            "-f",
            "null",
            "-",
        ]
    )
    log = p.stderr.decode("utf-8", errors="replace")
    meas = json.JSONDecoder().raw_decode(log[log.rfind("{") :])[0]
    ln_filter = (
        "loudnorm=I=-16:TP=-1.5:LRA=9:linear=true:"
        f"measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
        f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:"
        f"offset={meas['target_offset']},volume=-0.85dB,atrim=duration={duration}"
    )
    mezcla_v2_p = ajuste_dir / f"{ep}_MEZCLA_V2.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(premaster_p),
            "-af",
            ln_filter,
            "-ar",
            str(SR),
            "-c:a",
            "pcm_s24le",
            str(mezcla_v2_p),
        ]
    )
    premaster_p.unlink(missing_ok=True)

    # Write SRT
    srt_blocks = []
    for idx, ev in enumerate(events, 1):
        # Clamp subtitle end to 0.08s before next subtitle or episode end
        sub_end = min(duration - 0.1, ev["end"] + 0.1)
        if idx < len(events):
            sub_end = min(sub_end, events[idx]["start"] - 0.06)
        srt_blocks.append(f"{idx}\n{stamp_srt(ev['start'])} --> {stamp_srt(sub_end)}\n{ev['sub']}")
    srt_path = FINAL_DIR / f"{ep}_AJUSTADO_V2.srt"
    srt_path.write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8")

    manifest = {
        "episode": ep,
        "duration": duration,
        "segments": [
            {"shot": i + 1, "source_in": a, "source_out": b, "start": round(starts[i], 3), "end": round(starts[i + 1], 3)}
            for i, (a, b) in enumerate(segments)
        ],
        "dialogue": [{k: v for k, v in e.items() if k != "sub"} for e in events],
        "first_pass_loudness": meas,
    }
    (ajuste_dir / "montaje.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

    # Render video + audio + burned-in subtitles
    plock_path = FINAL_DIR / f"{ep}_PICTURE_LOCK.mp4"
    out_mp4 = FINAL_DIR / f"{ep}_AJUSTADO_V2.mp4"
    filters = ["[0:v]split=8" + "".join(f"[s{i}]" for i in range(8))]
    for i, (a, b) in enumerate(segments):
        contrast = 1.025 if i in cfg["high_contrast_shots"] else 1.015
        filters.append(f"[s{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,eq=contrast={contrast}:saturation=1.015[v{i}]")
    sub_style = (
        "FontName=DejaVu Sans,FontSize=14,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101010,"
        "BorderStyle=1,Outline=1.3,Shadow=0.5,Alignment=2,MarginV=28,MarginL=18,MarginR=18"
    )
    filters.append(
        "".join(f"[v{i}]" for i in range(8))
        + f"concat=n=8:v=1:a=0,subtitles={srt_path}:force_style='{sub_style}'[out]"
    )
    print(f"Renderizando {out_mp4.name} ({duration:.2f} s) ...", flush=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-filter_complex_threads",
            "2",
            "-i",
            str(plock_path),
            "-i",
            str(mezcla_v2_p),
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-threads",
            "2",
            "-preset",
            "medium",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            str(duration),
            "-movflags",
            "+faststart",
            str(out_mp4),
        ]
    )
    print(f"OK {out_mp4.name}", flush=True)


def main() -> None:
    for ep, cfg in EPISODE_CONFIG.items():
        process_episode(ep, cfg)


if __name__ == "__main__":
    main()
