#!/usr/bin/env python3
"""
Montaje y Postproducción Profesional V3.2 (EP01 a EP06 + 3 Capítulos Dobles Fusionados) con Epidemic Sound API:
- Rebalanceo acústico integral de los 5 stems (DIALOGUE, ROOM, FOLEY, SFX, MUSIC):
  * ROOM_BASEMENT ecualizado (calidez en 180 Hz y aire de bóveda en 850 Hz) y subido a -31.0 dBFS RMS (+15 dB respecto a V3 inicial) con ducking suave (-3.0 dB).
  * Normalización individual de cada activo de FOLEY y SFX (gotas de agua, roce de lana gruesa, llaves de hierro, hojas de informe, clics de grabadora, compuerta metálica, risers y booms subgraves) para presencia cinematográfica real en celulares, laptops y audífonos.
  * Banda sonora continua (98%+ del metraje) combinando cama grave de tensión + capas melódicas/texturales de Epidemic Sound (-25.5 dBFS RMS activo) con ducking suave (-4.8 dB) bajo diálogos.
- Renderizado de los 6 episodios individuales (EP01 a EP06) y de los 3 Capítulos Dobles Fusionados (Opción 2):
  * PARTE_01_EP01_EP02 (65.25 s / 1 min 05 s)
  * PARTE_02_EP03_EP04 (69.75 s / 1 min 10 s)
  * PARTE_03_EP05_EP06 (75.50 s / 1 min 15 s)
- Masterización EBU R128 en dos pasadas a -14.5 LUFS / -1.0 dBTP y sincronización automática en /workspaces/PRUEBA-CLI/LISTOS/.
"""
import json
import shutil
import subprocess
import wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
AUDIO_DIR = ROOT / "AUDIO"
ES_MUSIC = AUDIO_DIR / "EPIDEMIC_SOUND" / "MUSIC"
ES_SFX = AUDIO_DIR / "EPIDEMIC_SOUND" / "SFX"
FINAL_DIR = ROOT / "FINAL"
LISTOS_DIR = REPO_ROOT / "LISTOS"
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


def slice_wav(x: np.ndarray, start_s: float, end_s: float, fade_in: float = 0.03, fade_out: float = 0.05) -> np.ndarray:
    i0 = max(0, round(start_s * SR))
    i1 = min(len(x), round(end_s * SR))
    if i1 <= i0:
        return np.zeros(1, dtype="<f4")
    seg = x[i0:i1].copy()
    fi = min(len(seg) // 2, round(fade_in * SR))
    fo = min(len(seg) // 2, round(fade_out * SR))
    if fi > 1:
        seg[:fi] *= np.linspace(0.0, 1.0, fi, dtype="<f4")
    if fo > 1:
        seg[-fo:] *= np.linspace(1.0, 0.0, fo, dtype="<f4")
    return seg


def norm_clip(
    x: np.ndarray,
    target_rms_db: float = -22.0,
    max_peak_db: float = -4.5,
    fade_in: float = 0.02,
    fade_out: float = 0.04,
) -> np.ndarray:
    """Normaliza un fragmento de audio por RMS activo y protege su pico máximo con limitación suave."""
    if len(x) == 0:
        return x
    y = x.copy()
    active = y[np.abs(y) > 1e-4]
    rms = float(np.sqrt(np.mean(active * active))) if len(active) > 16 else float(np.sqrt(np.mean(y * y)))
    rms = max(rms, 1e-7)
    target_rms = float(10 ** (target_rms_db / 20.0))
    y = y * (target_rms / rms)

    max_peak = float(10 ** (max_peak_db / 20.0))
    peak = float(np.max(np.abs(y)))
    if peak > max_peak:
        # Compresión suave de transientes para mantener cuerpo sin saturar
        y = max_peak * np.tanh(y / max_peak)

    fi = min(len(y) // 2, round(fade_in * SR))
    fo = min(len(y) // 2, round(fade_out * SR))
    if fi > 1:
        y[:fi] *= np.linspace(0.0, 1.0, fi, dtype="<f4")
    if fo > 1:
        y[-fo:] *= np.linspace(1.0, 0.0, fo, dtype="<f4")
    return y.astype("<f4")


def add_at(dst: np.ndarray, src: np.ndarray, t_sec: float, gain: float = 1.0) -> None:
    i = max(0, round(t_sec * SR))
    if i >= len(dst):
        return
    n = min(len(src), len(dst) - i)
    dst[i : i + n] += src[:n] * gain


def load_es_library() -> dict[str, np.ndarray]:
    lib = {}
    for p in ES_SFX.glob("*.wav"):
        lib[p.stem] = read_wav(p)
    for p in ES_MUSIC.glob("*.wav"):
        lib[p.stem] = read_wav(p)
    return lib


def build_water_drop(lib: dict[str, np.ndarray], dull: bool = False) -> np.ndarray:
    """Construye una gota de agua cristalina y táctil con impacto + absorción sobre lana."""
    d1 = norm_clip(slice_wav(lib["SFX_WATER_DROP_SINGLE"], 0.0, 0.65, 0.004, 0.12), target_rms_db=-19.0, max_peak_db=-3.5)
    d2 = norm_clip(slice_wav(lib["SFX_WATER_DROP_CLOTH"], 1.82, 2.55, 0.008, 0.15), target_rms_db=-22.0, max_peak_db=-6.0)
    n = max(len(d1), len(d2))
    out = np.zeros(n, dtype="<f4")
    out[: len(d1)] += d1 * (0.75 if dull else 1.0)
    out[: len(d2)] += d2 * (0.95 if dull else 0.75)
    flt = "highpass=f=90,lowpass=f=2800" if dull else "highpass=f=110,lowpass=f=7500,equalizer=f=1400:t=q:w=1.2:g=3.0"
    out = af_process(out, flt)
    return norm_clip(out, target_rms_db=-20.5 if dull else -18.5, max_peak_db=-4.5 if dull else -3.2)


def build_floodgate_motif(lib: dict[str, np.ndarray]) -> np.ndarray:
    """Dos golpes metálicos profundos (0.0s y 0.80s) + arrastre de compuerta (1.40s-2.65s) con presencia potente."""
    total = round(2.85 * SR)
    out = np.zeros(total, dtype="<f4")
    hit1 = norm_clip(slice_wav(lib["SFX_FLOODGATE_HIT"], 0.0, 0.85, 0.004, 0.20), target_rms_db=-19.0, max_peak_db=-3.5)
    boom1 = norm_clip(slice_wav(lib["SFX_FLOODGATE_BOOM"], 0.42, 1.25, 0.005, 0.30), target_rms_db=-20.5, max_peak_db=-4.5)
    hit2 = norm_clip(slice_wav(lib["SFX_FLOODGATE_HIT"], 3.72, 4.65, 0.004, 0.22), target_rms_db=-18.5, max_peak_db=-3.2)
    boom2 = norm_clip(slice_wav(lib["SFX_FLOODGATE_BOOM"], 0.42, 1.30, 0.005, 0.35), target_rms_db=-20.0, max_peak_db=-4.2)
    scrape = norm_clip(slice_wav(lib["SFX_FLOODGATE_SCRAPE"], 0.18, 1.55, 0.04, 0.25), target_rms_db=-19.5, max_peak_db=-4.5)
    add_at(out, hit1, 0.0, 0.90)
    add_at(out, boom1, 0.0, 0.70)
    add_at(out, hit2, 0.80, 0.95)
    add_at(out, boom2, 0.80, 0.75)
    add_at(out, scrape, 1.40, 0.85)
    return norm_clip(out, target_rms_db=-18.5, max_peak_db=-3.2)


def apply_dialogue_ducking(
    track: np.ndarray,
    dialogue_events: list[dict],
    duck_db: float = -4.8,
    mara_extra_db: float = -2.2,
) -> np.ndarray:
    """Atenúa suavemente la música o el ambiente cuando hay voz hablada sin desaparecer del fondo."""
    n = len(track)
    env = np.ones(n, dtype="<f4")
    duck_lin = float(10 ** (duck_db / 20.0))
    mara_lin = float(10 ** ((duck_db + mara_extra_db) / 20.0))
    pad_pre = round(0.15 * SR)
    pad_post = round(0.24 * SR)
    ramp = round(0.22 * SR)
    for ev in dialogue_events:
        i0 = max(0, round(ev["start"] * SR) - pad_pre)
        i1 = min(n, round(ev["end"] * SR) + pad_post)
        target = mara_lin if ev.get("style") == "Mara" else duck_lin
        env[i0:i1] = np.minimum(env[i0:i1], target)
    if ramp > 1:
        kernel = np.ones(ramp, dtype="<f4") / ramp
        env = np.convolve(env, kernel, mode="same")
    return (track * env).astype("<f4")


def build_music_bed_layer(
    src: np.ndarray,
    start_offset: float,
    duration: float,
    target_rms_db: float,
    eq_filter: str | None = None,
) -> np.ndarray:
    """Extrae una capa musical continua de duración exacta con ecualización y RMS controlado."""
    total_samples = round(duration * SR)
    i0 = round(start_offset * SR) % max(1, len(src) - SR)
    reps = (total_samples // max(1, len(src) - i0)) + 2
    ext = np.tile(src[i0:], reps)[:total_samples].copy()
    if eq_filter:
        ext = af_process(ext, eq_filter)
    return norm_clip(ext, target_rms_db=target_rms_db, max_peak_db=-5.0, fade_in=0.25, fade_out=0.35)


def format_srt_ts(t: float) -> str:
    ms = max(0, round(t * 1000))
    return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d},{ms % 1000:03d}"


def format_ass_ts(t: float) -> str:
    cs = max(0, round(t * 100))
    return f"{cs // 360000:01d}:{(cs // 6000) % 60:02d}:{(cs // 100) % 60:02d}.{cs % 100:02d}"


def write_subtitles(
    srt_path: Path,
    ass_path: Path,
    ep_label: str,
    hook_sub: str,
    events: list[dict],
    extra_banners: list[tuple[float, float, str, str]] | None = None,
) -> None:
    srt_blocks = []
    for idx, ev in enumerate(events, 1):
        srt_blocks.append(f"{idx}\n{format_srt_ts(ev['start'])} --> {format_srt_ts(ev['end'] + 0.12)}\n{ev['text']}")
    srt_path.write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8")

    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,50,&H00FFFFFF,&H000000FF,&H00121212,&H88000000,-1,0,0,0,100,100,0.5,0,1,3.8,2.2,2,64,64,225,1
Style: Mara,DejaVu Sans,50,&H00E6F2FF,&H000000FF,&H00101820,&H99000000,-1,-1,0,0,100,100,0.8,0,1,4.0,2.5,2,64,64,225,1
Style: DocSafe,DejaVu Sans,44,&H00FFFFFF,&H000000FF,&H000E0E0E,&HAA000000,-1,0,0,0,100,100,0.4,0,1,3.5,2.0,2,60,60,48,1
Style: HookTag,DejaVu Sans,28,&H00D8E2EC,&H000000FF,&H00101010,&H80000000,-1,0,0,0,100,100,3.5,0,1,2.2,1.2,8,60,60,115,1
Style: HookSub,DejaVu Sans,34,&H0098B8D8,&H000000FF,&H00101010,&H80000000,0,-1,0,0,100,100,1.2,0,1,2.4,1.4,8,60,60,160,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [
        f"Dialogue: 2,0:00:00.08,0:00:02.55,HookTag,,0,0,0,,{{\\fad(150,350)}}{ep_label}",
        f"Dialogue: 2,0:00:00.18,0:00:02.55,HookSub,,0,0,0,,{{\\fad(200,350)}}{hook_sub}",
    ]
    if extra_banners:
        for b_start, b_end, b_tag, b_sub in extra_banners:
            st_b = format_ass_ts(b_start)
            en_b = format_ass_ts(b_end)
            lines.append(f"Dialogue: 2,{st_b},{en_b},HookTag,,0,0,0,,{{\\fad(180,320)}}{b_tag}")
            if b_sub:
                lines.append(f"Dialogue: 2,{st_b},{en_b},HookSub,,0,0,0,,{{\\fad(220,320)}}{b_sub}")

    for ev in events:
        st = format_ass_ts(ev["start"])
        en = format_ass_ts(ev["end"] + 0.12)
        style = ev.get("style", "Default")
        txt = ev["text"].replace("\n", "\\N")
        lines.append(f"Dialogue: 1,{st},{en},{style},,0,0,0,,{{\\fad(70,60)}}{txt}")

    ass_path.write_text(ass_header + "\n".join(lines) + "\n", encoding="utf-8")


EPISODE_CONFIGS = {
    "EP01": {
        "ep_label": "ARCHIVO NORTE · EPISODIO 1",
        "hook_sub": "Doce años después de la inundación",
        "segments": [
            (1.25, 4.00, "push_in_fast", 0.90),  # SH01: 2.75s [0.00 - 2.75]
            (5.00, 7.50, "push_in", 0.65),       # SH02: 2.50s [2.75 - 5.25]
            (11.00, 14.75, "macro_in", 0.75),    # SH03: 3.75s [5.25 - 9.00]
            (16.00, 20.25, "push_in", 0.65),     # SH04: 4.25s [9.00 - 13.25]
            (24.25, 27.25, "macro_in", 0.70),    # SH05: 3.00s [13.25 - 16.25]
            (30.00, 34.25, "push_in_fast", 0.75),# SH06: 4.25s [16.25 - 20.50]
            (37.00, 39.75, "push_in", 0.65),     # SH07: 2.75s [20.50 - 23.25]
            (43.00, 48.50, "pull_back", 0.70),   # SH08: 5.50s [23.25 - 28.75]
        ],
        "dialogue": [
            ("L01", "EDITADOS/EP01_ALBA_L01_EDIT.wav", 3.00, "¿Qué has hecho?", "Default", False, False),
            ("L02", "EDITADOS/EP01_INES_L02_EDIT.wav", 6.00, "Solo agua.\\NPara quitar la sal.", "Default", False, False),
            ("L03", "EDITADOS/EP01_INES_L03_EDIT.wav", 9.35, "Lleva doce años\\Nen una bolsa.", "Default", False, False),
            ("L04", "EDITADOS/EP01_MARA_L04_EDIT.wav", 16.65, "Inés. Quédate\\Ndonde estás.", "Mara", True, False),
            ("L05", "EDITADOS/EP01_ALBA_L05_EDIT.wav", 20.85, "No la escuches.", "Default", False, False),
            ("L06", "EDITADOS/EP01_INES_L06_EDIT.wav", 23.60, "Es mi hermana.", "Default", False, False),
            ("L07", "EDITADOS/EP01_INES_L07_EDIT.wav", 26.60, "Es Mara.", "Default", False, False),
        ],
    },
    "EP02": {
        "ep_label": "ARCHIVO NORTE · EPISODIO 2",
        "hook_sub": "El duplicado en la grabadora",
        "segments": [
            (0.00, 3.75, "macro_in", 0.75),      # SH01: 3.75s [0.00 - 3.75]
            (5.00, 8.75, "push_in", 0.65),       # SH02: 3.75s [3.75 - 7.50]
            (12.00, 15.25, "macro_in", 0.70),    # SH03: 3.25s [7.50 - 10.75]
            (17.00, 23.00, "push_in_fast", 0.75),# SH04: 6.00s [10.75 - 16.75]
            (25.00, 29.00, "push_in", 0.65),     # SH05: 4.00s [16.75 - 20.75]
            (31.00, 37.00, "macro_in", 0.70),    # SH06: 6.00s [20.75 - 26.75]
            (38.00, 42.25, "push_in", 0.70),     # SH07: 4.25s [26.75 - 31.00]
            (44.00, 49.50, "doc_frame", 0.75),   # SH08: 5.50s [31.00 - 36.50]
        ],
        "dialogue": [
            ("L01", "EDITADOS/EP02_INES_L01_EDIT.wav", 0.40, "Mara. ¿Me oyes?", "Default", False, False),
            ("L02", "EDITADOS/EP02_ALBA_L02_EDIT.wav", 4.10, "No vuelve. Ya no está.", "Default", False, False),
            ("L03", "EDITADOS/EP02_MARA_L03_EDIT.wav", 11.35, "Son las seis y diez.\\NHan cerrado. Seguimos aquí.", "Mara", True, False),
            ("L04", "EDITADOS/EP02_MARA_L04_EDIT.wav", 21.40, "Son las seis y diez.\\NHan cerrado. Seguimos aquí.", "Mara", False, True),
            ("L05", "EDITADOS/EP02_INES_L05_EDIT.wav", 27.15, "La tela se calla.\\NLa grabación no.", "Default", False, False),
            ("L06", "EDITADOS/EP02_INES_L06_EDIT.wav", 31.50, "Aquí pone que a las seis\\Nya no quedaba nadie.", "DocSafe", False, False),
        ],
    },
    "EP03": {
        "ep_label": "ARCHIVO NORTE · EPISODIO 3",
        "hook_sub": "La llave de la compuerta norte",
        "segments": [
            (0.50, 3.00, "macro_in", 0.75),      # SH01: 2.50s [0.00 - 2.50]
            (5.00, 9.50, "push_in", 0.65),       # SH02: 4.50s [2.50 - 7.00]
            (12.00, 16.50, "doc_frame", 0.75),   # SH03: 4.50s [7.00 - 11.50]
            (19.50, 23.75, "push_in", 0.65),     # SH04: 4.25s [11.50 - 15.75]
            (26.00, 29.25, "macro_in", 0.75),    # SH05: 3.25s [15.75 - 19.00]
            (32.50, 38.00, "push_in_fast", 0.75),# SH06: 5.50s [19.00 - 24.50]
            (39.00, 42.50, "push_in", 0.65),     # SH07: 3.50s [24.50 - 28.00]
            (45.00, 50.75, "pull_back", 0.70),   # SH08: 5.75s [28.00 - 33.75]
        ],
        "dialogue": [
            ("L01", "EDITADOS/EP03_INES_L01_EDIT.wav", 2.85, "¿Por qué guardabas la llave\\Nde la compuerta?", "Default", False, False),
            ("L02", "EDITADOS/EP03_ALBA_L02_EDIT.wav", 7.45, "Yo llevaba las llaves.\\NEso ya lo sabes.", "DocSafe", False, False),
            ("L03", "EDITADOS/EP03_ALBA_L03_EDIT.wav", 12.00, "No busques solo mi nombre.", "Default", False, False),
            ("L04", "EDITADOS/EP03_MARA_L04_EDIT.wav", 19.50, "Mamá. Te oigo al otro lado.\\NAbre.", "Mara", True, False),
            ("L05", "EDITADOS/EP03_INES_L05_EDIT.wav", 28.50, "La oíste.", "Default", False, False),
            ("L06", "EDITADOS/EP03_INES_L06_EDIT.wav", 31.05, "Y no abriste.", "Default", False, False),
        ],
    },
    "EP04": {
        "ep_label": "ARCHIVO NORTE · EPISODIO 4",
        "hook_sub": "La firma al pie del acta",
        "segments": [
            (1.50, 4.00, "macro_in", 0.75),      # SH01: 2.50s [0.00 - 2.50]
            (5.00, 10.50, "push_in", 0.65),      # SH02: 5.50s [2.50 - 8.00]
            (13.00, 17.25, "push_in", 0.65),     # SH03: 4.25s [8.00 - 12.25]
            (20.00, 24.50, "push_in", 0.65),     # SH04: 4.50s [12.25 - 16.75]
            (28.00, 31.00, "push_in_fast", 0.70),# SH05: 3.00s [16.75 - 19.75]
            (33.00, 39.75, "push_in", 0.70),     # SH06: 6.75s [19.75 - 26.50]
            (41.00, 44.50, "push_in", 0.65),     # SH07: 3.50s [26.50 - 30.00]
            (47.00, 53.00, "doc_frame", 0.75),   # SH08: 6.00s [30.00 - 36.00]
        ],
        "dialogue": [
            ("L01", "EDITADOS/EP04_ALBA_L01_EDIT.wav", 2.80, "El agua iba hacia la sala norte.\\NTú estabas allí.", "Default", False, False),
            ("L02", "EDITADOS/EP04_ALBA_L02_EDIT.wav", 8.45, "Cerré para que\\Nno te alcanzara.", "Default", False, False),
            ("L03", "EDITADOS/EP04_INES_L03_EDIT.wav", 12.75, "¿Sabías que Mara\\Nseguía dentro?", "Default", False, False),
            ("L04", "EDITADOS/EP04_ALBA_L04_EDIT.wav", 17.30, "Sí.", "Default", False, False),
            ("L05", "EDITADOS/EP04_ALBA_L05_EDIT.wav", 20.15, "No podía perderos\\Na las dos.", "Default", False, False),
            ("L06", "EDITADOS/EP04_INES_L06_EDIT.wav", 23.25, "La perdiste tú.\\NA mí me mentiste.", "Default", False, False),
            ("L07", "EDITADOS/EP04_ALBA_L07_EDIT.wav", 30.55, "Yo cerré la puerta. Tú firmaste\\Nque no quedaba nadie.", "DocSafe", False, False),
        ],
    },
    "EP05": {
        "ep_label": "ARCHIVO NORTE · EPISODIO 5",
        "hook_sub": "La última línea de sal",
        "segments": [
            (0.00, 3.25, "doc_frame", 0.75),     # SH01: 3.25s [0.00 - 3.25]
            (5.00, 10.25, "push_in", 0.65),      # SH02: 5.25s [3.25 - 8.50]
            (12.00, 15.75, "doc_frame", 0.75),   # SH03: 3.75s [8.50 - 12.25]
            (18.00, 21.25, "push_in", 0.65),     # SH04: 3.25s [12.25 - 15.50]
            (26.00, 29.25, "macro_in", 0.75),    # SH05: 3.25s [15.50 - 18.75]
            (31.00, 37.25, "push_in_fast", 0.75),# SH06: 6.25s [18.75 - 25.00]
            (39.00, 43.00, "macro_in", 0.70),    # SH07: 4.00s [25.00 - 29.00]
            (45.00, 49.75, "macro_in", 0.75),    # SH08: 4.75s [29.00 - 33.75]
        ],
        "dialogue": [
            ("L01", "EDITADOS/EP05_INES_L01_EDIT.wav", 0.35, "Me dijiste que\\Nhabías comprobado.", "DocSafe", False, False),
            ("L02", "EDITADOS/EP05_INES_L02_EDIT.wav", 3.65, "Y yo firmé. Sin mirar.\\NMe acuerdo.", "Default", False, False),
            ("L03", "EDITADOS/EP05_ALBA_L03_EDIT.wav", 8.95, "Puedes mandar\\Nsolo la grabación.", "DocSafe", False, False),
            ("L04", "EDITADOS/EP05_MARA_L04_EDIT.wav", 19.20, "Somos siete. Si alguien oye esto,\\Nque no quite a ninguno.", "Mara", True, False),
            ("L05", "EDITADOS/EP05_INES_L05_EDIT.wav", 25.45, "La página entera.\\NY mi nombre.", "Default", False, False),
            ("L06", "EDITADOS/EP05_MARA_L06_EDIT.wav", 29.55, "Voy a decir los nombres.", "Mara", True, False),
        ],
    },
    "EP06": {
        "ep_label": "ARCHIVO NORTE · FINAL DE TEMPORADA",
        "hook_sub": "Los siete nombres del archivo",
        "segments": [
            (0.00, 6.50, "macro_in", 0.70),      # SH01: 6.50s [0.00 - 6.50]
            (8.00, 14.00, "push_in", 0.70),      # SH02: 6.00s [6.50 - 12.50]
            (15.00, 19.75, "doc_frame", 0.75),   # SH03: 4.75s [12.50 - 17.25]
            (21.00, 25.25, "push_in", 0.65),     # SH04: 4.25s [17.25 - 21.50]
            (28.75, 32.75, "doc_frame", 0.75),   # SH05: 4.00s [21.50 - 25.50]
            (33.00, 39.00, "macro_in", 0.70),    # SH06: 6.00s [25.50 - 31.50]
            (40.00, 44.25, "push_in_fast", 0.70),# SH07: 4.25s [31.50 - 35.75]
            (46.00, 52.00, "pull_back", 0.75),   # SH08: 6.00s [35.75 - 41.75]
        ],
        "dialogue": [
            ("L01", "EDITADOS/EP06_MARA_L01_EDIT.wav", 0.35, "Elena Ríos. Tomás Vera.\\NLuz Arce. Bruno Sol.", "Mara", True, False),
            ("L02", "EDITADOS/EP06_MARA_L02_EDIT.wav", 6.85, "Celia Paz. Samuel Costa.\\NY yo, Mara Vidal.", "Mara", True, False),
            ("L03", "EDITADOS/EP06_INES_L03_EDIT.wav", 12.90, "Firmé sin comprobar.\\NAdjuntaré mi declaración.", "DocSafe", False, False),
            ("L04", "EDITADOS/EP06_INES_L04_EDIT.wav", 17.75, "No voy a quitar\\Ntu nombre.", "Default", False, False),
            ("L05", "EDITADOS/EP06_ALBA_L05_EDIT.wav", 26.10, "Deja el mío también.\\N¿Puedo quedarme?", "Default", False, False),
            ("L06", "EDITADOS/EP06_MARA_L06_EDIT.wav", 32.05, "Y yo, Mara Vidal.", "Mara", False, True),
            ("L07", "EDITADOS/EP06_INES_L07_EDIT.wav", 36.35, "Si no apagas eso.", "Default", False, False),
        ],
    },
}

DOUBLE_CHAPTERS = [
    {
        "id": "PARTE_01_EP01_EP02",
        "ep_a": "EP01",
        "ep_b": "EP02",
        "top_label": "ARCHIVO NORTE · PARTE 1 (EP. 1 Y 2)",
        "top_sub": "Doce años después de la inundación · El duplicado",
        "mid_label": "ARCHIVO NORTE · EPISODIO 2",
        "mid_sub": "El duplicado en la grabadora",
    },
    {
        "id": "PARTE_02_EP03_EP04",
        "ep_a": "EP03",
        "ep_b": "EP04",
        "top_label": "ARCHIVO NORTE · PARTE 2 (EP. 3 Y 4)",
        "top_sub": "La llave de la compuerta · La firma al pie del acta",
        "mid_label": "ARCHIVO NORTE · EPISODIO 4",
        "mid_sub": "La firma al pie del acta",
    },
    {
        "id": "PARTE_03_EP05_EP06",
        "ep_a": "EP05",
        "ep_b": "EP06",
        "top_label": "ARCHIVO NORTE · PARTE 3 · FINAL (EP. 5 Y 6)",
        "top_sub": "La última línea de sal · Los siete nombres",
        "mid_label": "ARCHIVO NORTE · FINAL DE TEMPORADA",
        "mid_sub": "Los siete nombres del archivo",
    },
]


def loudnorm_two_pass(premaster: np.ndarray, out_wav: Path, duration: float) -> dict:
    premaster_path = out_wav.parent / f"_TMP_{out_wav.name}"
    save_wav(premaster_path, premaster)
    p_meas = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(premaster_path),
            "-af",
            "loudnorm=I=-14.5:TP=-1.0:LRA=7.5:print_format=json",
            "-f",
            "null",
            "-",
        ]
    )
    log = p_meas.stderr.decode()
    meas = json.JSONDecoder().raw_decode(log[log.rfind("{") :])[0]
    ln_filter = (
        "loudnorm=I=-14.5:TP=-1.0:LRA=7.5:linear=true:"
        f"measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
        f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:"
        f"offset={meas['target_offset']},atrim=duration={duration}"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(premaster_path),
            "-af",
            ln_filter,
            "-ar",
            str(SR),
            "-c:a",
            "pcm_s24le",
            str(out_wav),
        ]
    )
    premaster_path.unlink(missing_ok=True)
    return meas


def build_episode_audio_and_subs(ep: str, cfg: dict, lib: dict[str, np.ndarray]) -> dict:
    ep_dir = AUDIO_DIR / ep
    out_dir = ep_dir / "AJUSTE_V3"
    out_dir.mkdir(parents=True, exist_ok=True)

    segments = cfg["segments"]
    starts = np.cumsum([0.0] + [b - a for a, b, _, _ in segments]).tolist()
    duration = float(starts[-1])
    total_samples = round(duration * SR)

    foley = np.zeros(total_samples, dtype="<f4")
    sfx = np.zeros(total_samples, dtype="<f4")
    music = np.zeros(total_samples, dtype="<f4")
    dialogue = np.zeros(total_samples, dtype="<f4")

    # 1. DIALOGUE STEM (con picos controlados a -4.5 dBFS para dejar headroom rico a ambiente, foley y música)
    dialogue_events = []
    for lid, rel_wav, t_start, txt, style, is_mara_cloth, is_recorder_playback in cfg["dialogue"]:
        x = read_wav(ep_dir / rel_wav)
        if is_recorder_playback:
            x = af_process(
                x,
                "highpass=f=320,lowpass=f=3400,acompressor=threshold=0.07:ratio=3.2:attack=4:release=75:makeup=1.25",
            )
            x = norm_clip(x, target_rms_db=-22.2, max_peak_db=-5.2, fade_in=0.015, fade_out=0.03)
        elif is_mara_cloth:
            x = af_process(
                x,
                "highpass=f=100,lowpass=f=6400,acompressor=threshold=0.08:ratio=2.6:attack=6:release=90:makeup=1.15",
            )
            x = norm_clip(x, target_rms_db=-21.5, max_peak_db=-4.8, fade_in=0.015, fade_out=0.03)
            x = af_process(x, "aecho=0.96:0.88:27|53:0.06|0.035")
        else:
            x = af_process(
                x,
                "highpass=f=85,lowpass=f=10500,acompressor=threshold=0.08:ratio=2.6:attack=6:release=90:makeup=1.15",
            )
            x = norm_clip(x, target_rms_db=-20.8, max_peak_db=-4.5, fade_in=0.015, fade_out=0.03)

        save_wav(out_dir / f"{lid}.wav", x)
        add_at(dialogue, x, t_start, 1.0)
        dialogue_events.append(
            {
                "id": lid,
                "start": round(t_start, 3),
                "end": round(t_start + len(x) / SR, 3),
                "text": txt,
                "style": style,
            }
        )

    # 2. ROOM STEM (ROOM_BASEMENT ecualizado para que resuene en celulares/laptops y normalizado a -30.5 dBFS antes de ducking)
    room_offset = (int(ep[-1]) - 1) * 32.0
    room_eq = "highpass=f=55,lowpass=f=5200,equalizer=f=175:t=q:w=1.1:g=4.0,equalizer=f=780:t=q:w=1.0:g=3.0"
    room = build_music_bed_layer(lib["ROOM_BASEMENT"], room_offset, duration, target_rms_db=-30.5, eq_filter=room_eq)
    room = apply_dialogue_ducking(room, dialogue_events, duck_db=-2.8, mara_extra_db=-0.5)

    # 3. ACTIVOS DE ESTUDIO FOLEY Y SFX NORMALIZADOS
    coat_eq = "highpass=f=110,lowpass=f=8500,equalizer=f=950:t=q:w=1.2:g=2.5"
    coat_mov1 = norm_clip(af_process(slice_wav(lib["FOLEY_COAT_THICK"], 0.55, 2.35, 0.06, 0.14), coat_eq), target_rms_db=-22.5, max_peak_db=-5.5)
    coat_mov2 = norm_clip(af_process(slice_wav(lib["FOLEY_COAT_THICK"], 3.40, 5.10, 0.06, 0.14), coat_eq), target_rms_db=-22.5, max_peak_db=-5.5)
    coat_flap = norm_clip(af_process(slice_wav(lib["FOLEY_COAT_FLAP"], 2.00, 2.85, 0.04, 0.10), coat_eq), target_rms_db=-22.8, max_peak_db=-5.8)

    key_eq = "highpass=f=220,lowpass=f=11500,equalizer=f=3200:t=q:w=1.2:g=3.0"
    key_hand = norm_clip(af_process(slice_wav(lib["FOLEY_KEYS_HAND"], 1.30, 2.50, 0.03, 0.10), key_eq), target_rms_db=-21.0, max_peak_db=-4.8)
    key_clink = norm_clip(af_process(slice_wav(lib["FOLEY_KEYS_HAND"], 11.50, 12.45, 0.02, 0.10), key_eq), target_rms_db=-20.8, max_peak_db=-4.5)

    paper_eq = "highpass=f=160,lowpass=f=9500,equalizer=f=2200:t=q:w=1.2:g=2.5"
    paper_turn = norm_clip(af_process(slice_wav(lib["FOLEY_PAPER_TURN"], 0.02, 1.25, 0.03, 0.12), paper_eq), target_rms_db=-22.0, max_peak_db=-5.2)

    rec_click = norm_clip(slice_wav(lib["SFX_RECORDER_BUTTONS"], 11.76, 12.32, 0.008, 0.04), target_rms_db=-20.5, max_peak_db=-4.2)
    ui_confirm = norm_clip(slice_wav(lib["SFX_UI_CONFIRM"], 0.0, 0.65, 0.01, 0.08), target_rms_db=-20.5, max_peak_db=-4.5)

    sub_eq = "highpass=f=45,lowpass=f=1800,equalizer=f=115:t=q:w=1.1:g=3.5"
    riser_hook = norm_clip(af_process(slice_wav(lib["SFX_RISER_LOW"], 1.80, 4.40, 0.10, 0.25), sub_eq), target_rms_db=-22.0, max_peak_db=-5.0)
    dark_boom = norm_clip(af_process(slice_wav(lib["SFX_DARK_BOOM"], 0.0, 3.20, 0.02, 0.40), sub_eq), target_rms_db=-21.5, max_peak_db=-4.8)
    rumble_rise = norm_clip(af_process(slice_wav(lib["SFX_RUMBLE_RISING"], 5.80, 9.80, 0.25, 0.35), sub_eq), target_rms_db=-22.5, max_peak_db=-5.2)

    bass_eq = "highpass=f=50,lowpass=f=2400,equalizer=f=130:t=q:w=1.1:g=3.0"
    inst_eq = "highpass=f=95,lowpass=f=9000,equalizer=f=420:t=q:w=1.1:g=2.0"

    if ep == "EP01":
        # FOLEY & SFX
        add_at(sfx, riser_hook, 0.0, 0.85)
        add_at(sfx, dark_boom, 0.0, 0.78)
        breath = read_wav(AUDIO_DIR / "EP01" / "EDITADOS" / "EP01_MARA_X01_EDIT.wav")
        breath = norm_clip(af_process(breath, "highpass=f=110,lowpass=f=6000"), target_rms_db=-21.5, max_peak_db=-5.0)
        add_at(foley, breath, 0.35, 0.95)
        add_at(foley, coat_mov1, 0.25, 0.92)
        add_at(foley, coat_flap, 2.75, 0.72)  # Movimiento al corte SH02
        # SH03 (5.25s): Gota de agua en sal
        add_at(sfx, build_water_drop(lib, dull=False), starts[2] + 0.55, 1.0)
        add_at(sfx, build_water_drop(lib, dull=True), starts[2] + 1.45, 0.65)
        add_at(foley, coat_mov2, starts[3] + 0.20, 0.70)
        # SH05 (13.25s): Llave en palma de Alba
        add_at(foley, key_hand, starts[4] + 0.45, 1.0)
        add_at(foley, key_clink, starts[4] + 1.15, 0.80)
        add_at(foley, coat_flap, starts[4] + 0.65, 0.75)
        # SH06 (16.25s): Temblor del cuello del abrigo + voz de Mara
        add_at(foley, coat_mov2, starts[5] + 0.15, 0.95)
        add_at(sfx, riser_hook, 13.40, 0.72)
        # SH08 (23.25s): Retroceso final
        add_at(foley, coat_mov1, starts[7] + 0.30, 0.78)
        add_at(sfx, rumble_rise, 22.80, 0.80)
        add_at(sfx, dark_boom, 26.90, 0.88)

        # MÚSICA CONTINUA (100% del episodio): Cama grave ORO_BASS + capas melódicas de thriller
        bed_bass = build_music_bed_layer(lib["ORO_BASS"], 0.0, duration, target_rms_db=-26.5, eq_filter=bass_eq)
        bed_inst1 = norm_clip(af_process(slice_wav(lib["ORO_INSTRUMENTS"], 0.0, 16.5, 0.35, 0.75), inst_eq), target_rms_db=-24.5, max_peak_db=-5.5)
        bed_inst2 = norm_clip(af_process(slice_wav(lib["CREEPING_ANXIETY_INSTRUMENTS"], 2.0, 16.5, 0.50, 0.75), inst_eq), target_rms_db=-25.5, max_peak_db=-5.5)
        bed_inst3 = norm_clip(af_process(slice_wav(lib["DONT_TURN_AROUND_INSTRUMENTS"], 12.0, 26.0, 0.55, 0.45), inst_eq), target_rms_db=-24.0, max_peak_db=-5.2)
        add_at(music, bed_bass, 0.0, 1.0)
        add_at(music, bed_inst1, 0.0, 0.90)
        add_at(music, bed_inst2, 6.0, 0.85)
        add_at(music, bed_inst3, 15.5, 0.95)

    elif ep == "EP02":
        # FOLEY & SFX
        add_at(sfx, dark_boom, 0.0, 0.82)
        add_at(sfx, build_water_drop(lib, dull=False), 1.85, 0.98)
        add_at(foley, coat_mov1, 0.30, 0.82)
        add_at(foley, coat_flap, starts[1] + 0.25, 0.75)
        # SH03 (7.50s): Grabadora
        add_at(foley, coat_flap, starts[2] + 0.25, 0.80)
        add_at(sfx, rec_click, starts[2] + 1.35, 1.0)
        # SH04 (10.75s): Gota activa voz de Mara
        add_at(sfx, build_water_drop(lib, dull=False), starts[3] + 0.42, 0.98)
        add_at(foley, coat_mov2, starts[3] + 0.55, 0.88)
        # SH05 (16.75s): Motivo de compuerta real (dos golpes + arrastre)
        motif = build_floodgate_motif(lib)
        add_at(sfx, motif, starts[4] + 0.45, 1.0)
        # SH06 (20.75s): Replay en grabadora
        add_at(sfx, rec_click, starts[5] + 0.20, 0.92)
        motif_speaker = af_process(motif, "highpass=f=350,lowpass=f=3200,acompressor=threshold=0.07:ratio=3.2")
        motif_speaker = norm_clip(motif_speaker, target_rms_db=-21.0, max_peak_db=-4.8)
        add_at(sfx, motif_speaker, starts[5] + 2.95, 0.90)
        # SH07 (26.75s): Gota sorda sobre lana saturada
        add_at(sfx, build_water_drop(lib, dull=True), starts[6] + 0.35, 0.95)
        add_at(foley, coat_mov1, starts[6] + 0.60, 0.78)
        # SH08 (31.00s): Papel del informe sobre mesa
        add_at(foley, paper_turn, starts[7] + 0.25, 1.0)
        add_at(sfx, rumble_rise, 28.00, 0.78)
        add_at(sfx, dark_boom, 34.00, 0.88)

        # MÚSICA CONTINUA
        bed_bass = build_music_bed_layer(lib["CREEPING_ANXIETY_BASS"], 2.0, duration, target_rms_db=-26.5, eq_filter=bass_eq)
        bed_inst1 = norm_clip(af_process(slice_wav(lib["ORO_INSTRUMENTS"], 8.0, 26.5, 0.40, 0.65), inst_eq), target_rms_db=-24.5, max_peak_db=-5.5)
        bed_inst2 = norm_clip(af_process(slice_wav(lib["DARK_PUZZLE_INSTRUMENTS"], 0.0, 22.0, 0.50, 0.45), inst_eq), target_rms_db=-24.2, max_peak_db=-5.2)
        add_at(music, bed_bass, 0.0, 1.0)
        add_at(music, bed_inst1, 0.0, 0.90)
        add_at(music, bed_inst2, 16.0, 0.92)

    elif ep == "EP03":
        # FOLEY & SFX
        add_at(sfx, dark_boom, 0.0, 0.82)
        add_at(foley, key_clink, 0.40, 1.0)
        add_at(foley, paper_turn, 0.25, 0.88)
        add_at(foley, coat_flap, starts[1] + 0.30, 0.75)
        # SH03 (7.00s): Informe
        add_at(foley, paper_turn, starts[2] + 0.25, 0.95)
        add_at(foley, key_hand, starts[3] + 0.35, 0.75)
        # SH05 (15.75s): Gota sobre sal
        add_at(sfx, build_water_drop(lib, dull=False), starts[4] + 0.75, 1.0)
        # SH06 (19.00s): Súplica de Mara desde el abrigo
        add_at(foley, coat_mov1, starts[5] + 0.25, 0.92)
        add_at(sfx, riser_hook, 16.80, 0.75)
        # SH08 (28.00s): Confrontación final
        add_at(foley, coat_flap, starts[7] + 0.35, 0.82)
        add_at(sfx, rumble_rise, 25.00, 0.80)
        add_at(sfx, dark_boom, 31.20, 0.88)

        # MÚSICA CONTINUA
        bed_bass = build_music_bed_layer(lib["SHIFTING_GROUND_BASS"], 0.0, duration, target_rms_db=-26.5, eq_filter=bass_eq)
        bed_inst1 = norm_clip(af_process(slice_wav(lib["DARK_PUZZLE_INSTRUMENTS"], 2.0, 21.0, 0.35, 0.65), inst_eq), target_rms_db=-24.5, max_peak_db=-5.5)
        bed_inst2 = norm_clip(af_process(slice_wav(lib["CREEPING_ANXIETY_INSTRUMENTS"], 6.0, 24.5, 0.55, 0.45), inst_eq), target_rms_db=-24.0, max_peak_db=-5.2)
        add_at(music, bed_bass, 0.0, 1.0)
        add_at(music, bed_inst1, 0.0, 0.90)
        add_at(music, bed_inst2, 16.5, 0.94)

    elif ep == "EP04":
        # FOLEY & SFX
        add_at(sfx, riser_hook, 0.0, 0.85)
        add_at(foley, key_hand, 0.30, 1.0)
        add_at(foley, key_clink, 0.95, 0.85)
        add_at(foley, coat_flap, starts[1] + 0.30, 0.75)
        add_at(foley, coat_mov1, starts[2] + 0.35, 0.82)
        # SH05 (16.75s): "Sí."
        add_at(sfx, dark_boom, starts[4] + 0.15, 0.78)
        add_at(foley, coat_mov2, starts[5] + 0.30, 0.80)
        # SH08 (30.00s): Firma manuscrita Inés Vidal
        add_at(foley, paper_turn, starts[7] + 0.25, 1.0)
        add_at(sfx, riser_hook, 27.20, 0.80)
        add_at(sfx, dark_boom, 33.40, 0.88)

        # MÚSICA CONTINUA
        bed_bass = build_music_bed_layer(lib["ORO_BASS"], 4.0, duration, target_rms_db=-26.5, eq_filter=bass_eq)
        bed_inst1 = norm_clip(af_process(slice_wav(lib["DONT_TURN_AROUND_INSTRUMENTS"], 0.0, 20.0, 0.35, 0.65), inst_eq), target_rms_db=-24.5, max_peak_db=-5.5)
        bed_inst2 = norm_clip(af_process(slice_wav(lib["DISTURBING_EVIDENCE_INSTRUMENTS"], 2.0, 22.0, 0.55, 0.45), inst_eq), target_rms_db=-24.0, max_peak_db=-5.2)
        add_at(music, bed_bass, 0.0, 1.0)
        add_at(music, bed_inst1, 0.0, 0.90)
        add_at(music, bed_inst2, 17.5, 0.95)

    elif ep == "EP05":
        # FOLEY & SFX
        add_at(sfx, dark_boom, 0.0, 0.82)
        add_at(foley, paper_turn, 0.20, 1.0)
        add_at(foley, coat_flap, starts[1] + 0.30, 0.78)
        # SH03 (8.50s): Móvil sobre mesa
        add_at(foley, key_clink, starts[2] + 0.30, 0.72)
        # SH05 (15.50s): Última gota sobre línea de sal S3
        add_at(sfx, build_water_drop(lib, dull=False), starts[4] + 0.70, 1.0)
        # SH06 (18.75s): "Somos siete..."
        add_at(foley, coat_mov1, starts[5] + 0.25, 0.92)
        add_at(sfx, rec_click, starts[6] + 0.30, 0.85)
        # SH08 (29.00s): Gota sorda final hacia S4
        add_at(sfx, build_water_drop(lib, dull=True), starts[7] + 0.45, 0.95)
        add_at(sfx, rumble_rise, 25.80, 0.82)
        add_at(sfx, dark_boom, 31.20, 0.88)

        # MÚSICA CONTINUA
        bed_bass = build_music_bed_layer(lib["SHIFTING_GROUND_BASS"], 2.0, duration, target_rms_db=-26.5, eq_filter=bass_eq)
        bed_inst1 = norm_clip(af_process(slice_wav(lib["DISTURBING_EVIDENCE_INSTRUMENTS"], 4.0, 22.5, 0.35, 0.65), inst_eq), target_rms_db=-24.5, max_peak_db=-5.5)
        bed_inst2 = norm_clip(af_process(slice_wav(lib["SHIFTING_GROUND_INSTRUMENTS"], 2.0, 20.5, 0.55, 0.45), inst_eq), target_rms_db=-24.2, max_peak_db=-5.2)
        add_at(music, bed_bass, 0.0, 1.0)
        add_at(music, bed_inst1, 0.0, 0.90)
        add_at(music, bed_inst2, 16.5, 0.94)

    elif ep == "EP06":
        # FOLEY & SFX
        add_at(sfx, rec_click, 0.08, 1.0)
        add_at(sfx, dark_boom, 0.0, 0.78)
        # SH02 (6.50s): Abrigo en S4
        add_at(foley, coat_mov2, starts[1] + 0.30, 0.88)
        add_at(foley, paper_turn, starts[2] + 0.30, 0.82)
        add_at(foley, coat_flap, starts[3] + 0.30, 0.78)
        # SH05 (21.50s): Confirmación "Informe enviado"
        add_at(sfx, ui_confirm, starts[4] + 1.55, 1.0)
        # SH06 (25.50s): Mano anciana suelta llave sobre plano
        add_at(foley, key_clink, starts[5] + 0.70, 1.0)
        add_at(foley, coat_flap, starts[5] + 1.80, 0.82)
        # SH07 (31.50s): Playback de Mara en grabadora
        add_at(sfx, rec_click, starts[6] + 0.18, 0.90)
        # SH08 (35.75s): Los siete abrigos
        add_at(foley, coat_mov1, starts[7] + 0.35, 0.85)
        add_at(sfx, rumble_rise, 35.80, 0.85)
        add_at(sfx, dark_boom, 38.60, 0.92)

        # MÚSICA CONTINUA
        bed_bass = build_music_bed_layer(lib["ORO_BASS"], 6.0, duration, target_rms_db=-26.2, eq_filter=bass_eq)
        bed_inst1 = norm_clip(af_process(slice_wav(lib["ORO_INSTRUMENTS"], 2.0, 26.0, 0.35, 0.65), inst_eq), target_rms_db=-24.2, max_peak_db=-5.2)
        bed_inst2 = norm_clip(af_process(slice_wav(lib["CREEPING_ANXIETY_INSTRUMENTS"], 0.0, 22.0, 0.55, 0.50), inst_eq), target_rms_db=-24.0, max_peak_db=-5.0)
        add_at(music, bed_bass, 0.0, 1.0)
        add_at(music, bed_inst1, 0.0, 0.92)
        add_at(music, bed_inst2, 20.5, 0.95)

    # Normalizar el stem de música antes de aplicar ducking para garantizar presencia uniforme en todos los capítulos
    music = norm_clip(music, target_rms_db=-23.8, max_peak_db=-4.8, fade_in=0.15, fade_out=0.25)
    music = apply_dialogue_ducking(music, dialogue_events, duck_db=-4.8, mara_extra_db=-2.0)

    # Fundido de salida limpio en los últimos 0.20s de todos los stems ambientales
    fade_n = round(0.20 * SR)
    fade_curve = np.linspace(1.0, 0.0, fade_n, dtype="<f4")
    for stem_arr in (room, foley, sfx, music):
        stem_arr[-fade_n:] *= fade_curve

    for name, arr in [
        ("DIALOGUE", dialogue),
        ("ROOM", room),
        ("FOLEY", foley),
        ("SFX", sfx),
        ("MUSIC", music),
    ]:
        save_wav(out_dir / f"{ep}_{name}_V3.wav", arr)

    premaster = dialogue + room + foley + sfx + music
    mix_path = out_dir / f"{ep}_MEZCLA_V3.wav"
    meas = loudnorm_two_pass(premaster, mix_path, duration)

    # Subtítulos SRT + ASS
    srt_path = FINAL_DIR / f"{ep}_AJUSTADO_V3.srt"
    ass_path = FINAL_DIR / f"{ep}_AJUSTADO_V3.ass"
    write_subtitles(srt_path, ass_path, cfg["ep_label"], cfg["hook_sub"], dialogue_events)

    manifest = {
        "episode": ep,
        "version": "V3.2_EPIDEMIC_SOUND_REBALANCED",
        "duration": duration,
        "segments": [
            {
                "shot": i + 1,
                "source_in": a,
                "source_out": b,
                "zoom_mode": zm,
                "start": round(starts[i], 3),
                "end": round(starts[i + 1], 3),
            }
            for i, (a, b, zm, _) in enumerate(segments)
        ],
        "dialogue": dialogue_events,
        "loudnorm_first_pass": meas,
    }
    (out_dir / "montaje_v3.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "duration": duration,
        "dialogue_events": dialogue_events,
        "stems": {
            "DIALOGUE": dialogue,
            "ROOM": room,
            "FOLEY": foley,
            "SFX": sfx,
            "MUSIC": music,
        },
    }


def build_shot_video_filter(stream_in: str, stream_out: str, src_in: float, src_out: float, zoom_mode: str, sharp: float) -> str:
    """Construye filtro de encuadre dinámico a 24 fps, nitidez y color grading de thriller para cada plano."""
    dur = src_out - src_in
    n_frames = max(1, round(dur * 24.0))
    if zoom_mode == "push_in_fast":
        z_expr = f"1.0+0.065*(on/{n_frames:.1f})"
        y_bias = 0.42
    elif zoom_mode == "push_in":
        z_expr = f"1.0+0.042*(on/{n_frames:.1f})"
        y_bias = 0.40
    elif zoom_mode == "macro_in":
        z_expr = f"1.02+0.048*(on/{n_frames:.1f})"
        y_bias = 0.48
    elif zoom_mode == "pull_back":
        z_expr = f"1.06-0.055*(on/{n_frames:.1f})"
        y_bias = 0.45
    else:  # doc_frame
        z_expr = f"1.015+0.015*(on/{n_frames:.1f})"
        y_bias = 0.72

    framing = (
        f"scale=1620:2880:flags=bilinear,"
        f"zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*{y_bias:.2f}':d=1:s=1080x1920:fps=24"
    )
    grade = (
        f"eq=contrast=1.045:brightness=-0.008:saturation=1.04,"
        f"unsharp=5:5:{sharp:.2f}:3:3:0.0,"
        f"vignette=PI/6"
    )
    return f"[{stream_in}]trim=start={src_in}:end={src_out},setpts=PTS-STARTPTS,{framing},{grade}[{stream_out}]"


def render_episode_v3(ep: str, cfg: dict, duration: float) -> Path:
    segments = cfg["segments"]
    n_seg = len(segments)
    filters = [f"[0:v]split={n_seg}" + "".join(f"[s{i}]" for i in range(n_seg))]
    for i, (src_in, src_out, zm, sharp) in enumerate(segments):
        filters.append(build_shot_video_filter(f"s{i}", f"v{i}", src_in, src_out, zm, sharp))

    ass_path = FINAL_DIR / f"{ep}_AJUSTADO_V3.ass"
    concat_in = "".join(f"[v{i}]" for i in range(n_seg))
    filters.append(f"{concat_in}concat=n={n_seg}:v=1:a=0,ass={ass_path}[out]")

    pic_lock = FINAL_DIR / f"{ep}_PICTURE_LOCK.mp4"
    mix_wav = AUDIO_DIR / ep / "AJUSTE_V3" / f"{ep}_MEZCLA_V3.wav"
    out_mp4 = FINAL_DIR / f"{ep}_AJUSTADO_V3.mp4"

    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-filter_complex_threads",
            "2",
            "-i",
            str(pic_lock),
            "-i",
            str(mix_wav),
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

    starts = np.cumsum([0.0] + [b - a for a, b, _, _ in segments]).tolist()
    mids = [(starts[i] + starts[i + 1]) / 2.0 for i in range(n_seg)]
    select_expr = "+".join(f"eq(n\\,{round(m * 24)})" for m in mids)
    contact_png = FINAL_DIR / f"{ep}_AJUSTADO_V3_CONTACT.png"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(out_mp4),
            "-vf",
            f"select='{select_expr}',scale=360:640,tile=4x2",
            "-frames:v",
            "1",
            str(contact_png),
        ]
    )

    # Sincronizar copia en LISTOS/EPxx/EPxx_FINAL.mp4
    ep_listo_dir = LISTOS_DIR / ep
    ep_listo_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_mp4, ep_listo_dir / f"{ep}_FINAL.mp4")
    return out_mp4


def render_double_chapter(
    dcfg: dict,
    ep_data: dict[str, dict],
    lib: dict[str, np.ndarray],
) -> Path:
    """Construye y renderiza un Capítulo Doble fusionado (16 planos, ~65–75 s) con puente sonoro continuo y subtítulos unificados."""
    part_id = dcfg["id"]
    ep_a = dcfg["ep_a"]
    ep_b = dcfg["ep_b"]
    data_a = ep_data[ep_a]
    data_b = ep_data[ep_b]
    dur_a = float(data_a["duration"])
    dur_b = float(data_b["duration"])
    total_dur = dur_a + dur_b
    total_samples = round(total_dur * SR)

    out_audio_dir = AUDIO_DIR / "DOBLES_V3"
    out_audio_dir.mkdir(parents=True, exist_ok=True)

    # Unir stems de A y B + añadir puente sonoro cinematográfico en la unión (t = dur_a)
    combined_stems = {}
    for sname in ("DIALOGUE", "ROOM", "FOLEY", "SFX", "MUSIC"):
        arr_a = data_a["stems"][sname].copy()
        arr_b = data_b["stems"][sname].copy()
        # En ROOM y MUSIC, suavizar la unión entre el final de A y el inicio de B para que no haya bache
        if sname in ("ROOM", "MUSIC"):
            fade_len = min(round(0.22 * SR), len(arr_a) // 4, len(arr_b) // 4)
            if fade_len > 1:
                # Restaurar nivel en la cola de A donde había fade-out individual
                arr_a[-fade_len:] = arr_a[-2 * fade_len : -fade_len]
        combined_stems[sname] = np.concatenate([arr_a, arr_b])[:total_samples]

    # Añadir puente subgrave/riser suave justo en la transición entre ep_a y ep_b (dur_a - 1.1s a dur_a + 1.5s)
    sub_eq = "highpass=f=45,lowpass=f=1800,equalizer=f=115:t=q:w=1.1:g=3.5"
    bridge_riser = norm_clip(
        af_process(slice_wav(lib["SFX_RISER_LOW"], 2.20, 4.40, 0.25, 0.35), sub_eq),
        target_rms_db=-23.5,
        max_peak_db=-5.5,
    )
    add_at(combined_stems["SFX"], bridge_riser, max(0.0, dur_a - 1.15), 0.70)

    premaster = (
        combined_stems["DIALOGUE"]
        + combined_stems["ROOM"]
        + combined_stems["FOLEY"]
        + combined_stems["SFX"]
        + combined_stems["MUSIC"]
    )
    mix_wav = out_audio_dir / f"{part_id}_MEZCLA_V3.wav"
    loudnorm_two_pass(premaster, mix_wav, total_dur)

    # Eventos de diálogo unificados (desplazando ep_b en +dur_a)
    merged_events = [dict(ev) for ev in data_a["dialogue_events"]]
    for ev in data_b["dialogue_events"]:
        ev_copy = dict(ev)
        ev_copy["id"] = f"{ep_b}_{ev['id']}"
        ev_copy["start"] = round(ev["start"] + dur_a, 3)
        ev_copy["end"] = round(ev["end"] + dur_a, 3)
        merged_events.append(ev_copy)

    srt_path = FINAL_DIR / f"{part_id}_FINAL.srt"
    ass_path = FINAL_DIR / f"{part_id}_FINAL.ass"
    extra_banners = [(dur_a + 0.08, dur_a + 2.45, dcfg["mid_label"], dcfg["mid_sub"])]
    write_subtitles(srt_path, ass_path, dcfg["top_label"], dcfg["top_sub"], merged_events, extra_banners=extra_banners)

    # Renderizar vídeo uniendo los 8 planos de ep_a + los 8 planos de ep_b (16 planos en total) con subtítulos ASS nativos
    segs_a = EPISODE_CONFIGS[ep_a]["segments"]
    segs_b = EPISODE_CONFIGS[ep_b]["segments"]
    n_a = len(segs_a)
    n_b = len(segs_b)

    filters = [
        f"[0:v]split={n_a}" + "".join(f"[sa{i}]" for i in range(n_a)),
        f"[1:v]split={n_b}" + "".join(f"[sb{i}]" for i in range(n_b)),
    ]
    for i, (src_in, src_out, zm, sharp) in enumerate(segs_a):
        filters.append(build_shot_video_filter(f"sa{i}", f"va{i}", src_in, src_out, zm, sharp))
    for i, (src_in, src_out, zm, sharp) in enumerate(segs_b):
        filters.append(build_shot_video_filter(f"sb{i}", f"vb{i}", src_in, src_out, zm, sharp))

    concat_in = "".join(f"[va{i}]" for i in range(n_a)) + "".join(f"[vb{i}]" for i in range(n_b))
    filters.append(f"{concat_in}concat=n={n_a + n_b}:v=1:a=0,ass={ass_path}[out]")

    pic_a = FINAL_DIR / f"{ep_a}_PICTURE_LOCK.mp4"
    pic_b = FINAL_DIR / f"{ep_b}_PICTURE_LOCK.mp4"
    out_mp4 = FINAL_DIR / f"{part_id}_FINAL.mp4"

    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-filter_complex_threads",
            "2",
            "-i",
            str(pic_a),
            "-i",
            str(pic_b),
            "-i",
            str(mix_wav),
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-map",
            "2:a:0",
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
            str(total_dur),
            "-movflags",
            "+faststart",
            str(out_mp4),
        ]
    )

    # Hoja de contacto 4x4 (16 planos) para el capítulo doble
    all_Lens = [b - a for a, b, _, _ in segs_a] + [b - a for a, b, _, _ in segs_b]
    starts = np.cumsum([0.0] + all_Lens).tolist()
    mids = [(starts[i] + starts[i + 1]) / 2.0 for i in range(len(all_Lens))]
    select_expr = "+".join(f"eq(n\\,{round(m * 24)})" for m in mids)
    contact_png = FINAL_DIR / f"{part_id}_FINAL_CONTACT.png"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(out_mp4),
            "-vf",
            f"select='{select_expr}',scale=270:480,tile=4x4",
            "-frames:v",
            "1",
            str(contact_png),
        ]
    )

    # Copiar a LISTOS/PARTE_0X_EP0X_EP0Y/
    part_listo_dir = LISTOS_DIR / part_id
    part_listo_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_mp4, part_listo_dir / f"{part_id}_FINAL.mp4")
    return out_mp4


def verify_mp4(mp4_path: Path) -> dict:
    run(["ffmpeg", "-v", "error", "-i", str(mp4_path), "-f", "null", "-"])
    p_ln = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(mp4_path),
            "-af",
            "loudnorm=print_format=json",
            "-f",
            "null",
            "-",
        ]
    )
    log = p_ln.stderr.decode()
    meas = json.JSONDecoder().raw_decode(log[log.rfind("{") :])[0]
    p_probe = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,nb_frames,duration",
            "-of",
            "json",
            str(mp4_path),
        ]
    )
    vinfo = json.loads(p_probe.stdout.decode())["streams"][0]
    return {
        "decode": "DECODE_OK",
        "width": vinfo["width"],
        "height": vinfo["height"],
        "frames": int(vinfo["nb_frames"]),
        "duration": float(vinfo["duration"]),
        "lufs": float(meas["input_i"]),
        "tp": float(meas["input_tp"]),
    }


def main() -> None:
    print("Cargando biblioteca WAV de Epidemic Sound...", flush=True)
    lib = load_es_library()
    summary = {"individuales": {}, "dobles": {}}
    ep_data = {}

    for ep, cfg in EPISODE_CONFIGS.items():
        print(f"[{ep}] Construyendo stems rebalanceados (ROOM/FOLEY/SFX/MUSIC presentes) + mezcla -14.5 LUFS...", flush=True)
        ep_data[ep] = build_episode_audio_and_subs(ep, cfg, lib)
        dur = ep_data[ep]["duration"]
        print(f"[{ep}] Renderizando vídeo {dur:.2f}s y actualizando LISTOS/{ep}/...", flush=True)
        out_mp4 = render_episode_v3(ep, cfg, dur)
        info = verify_mp4(out_mp4)
        summary["individuales"][ep] = info
        print(
            f"[{ep}] LISTO -> {info['duration']:.2f}s ({info['frames']}f) | {info['lufs']:.1f} LUFS | {info['tp']:.2f} dBTP | {info['decode']}",
            flush=True,
        )

    for dcfg in DOUBLE_CHAPTERS:
        pid = dcfg["id"]
        print(f"[{pid}] Fusionando {dcfg['ep_a']} + {dcfg['ep_b']} con puente sonoro y subtítulos continuos...", flush=True)
        out_mp4 = render_double_chapter(dcfg, ep_data, lib)
        info = verify_mp4(out_mp4)
        summary["dobles"][pid] = info
        print(
            f"[{pid}] LISTO -> {info['duration']:.2f}s ({info['frames']}f) | {info['lufs']:.1f} LUFS | {info['tp']:.2f} dBTP | {info['decode']}",
            flush=True,
        )

    (FINAL_DIR / "RESUMEN_V3_EPIDEMIC.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Temporada completa (6 episodios individuales + 3 capítulos dobles) renderizada y verificada.", flush=True)


if __name__ == "__main__":
    main()
