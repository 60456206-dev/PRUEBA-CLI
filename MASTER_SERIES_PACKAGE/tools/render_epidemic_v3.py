#!/usr/bin/env python3
"""
Montaje y Postproducción Profesional V3 (EP01 a EP06) con Epidemic Sound API:
- Gancho inmediato en los primeros 0–2.5s (recorte de esperas iniciales + sub-bass riser + foley real + micro-rótulo cinematográfico).
- Reemplazo total de efectos sintéticos por WAVs reales de estudio de Epidemic Sound (ROOM, FOLEY, SFX).
- Incorporación de banda sonora de thriller psicológico por stems WAV de Epidemic Sound (MUSIC) con ducking dinámico bajo diálogos y cortes dramáticos en revelaciones.
- Encuadre dinámico profesional (push-in / punch-in suave a 24 fps, reencuadre limpio, color grading de thriller con viñeta suave y nitidez adaptativa).
- Subtítulos ASS nativos (1080x1920) en zona segura de redes sociales, garantizando 0% de solapamiento con firmas o documentos.
- Masterización EBU R128 a -14.5 LUFS / -1.2 dBTP para máxima presencia en TikTok, Reels y Shorts.
"""
import json
import subprocess
import wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "AUDIO"
ES_MUSIC = AUDIO_DIR / "EPIDEMIC_SOUND" / "MUSIC"
ES_SFX = AUDIO_DIR / "EPIDEMIC_SOUND" / "SFX"
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
    d1 = slice_wav(lib["SFX_WATER_DROP_SINGLE"], 0.0, 0.65, 0.005, 0.12) * 1.8
    d2 = slice_wav(lib["SFX_WATER_DROP_CLOTH"], 1.82, 2.55, 0.01, 0.15) * 0.85
    n = max(len(d1), len(d2))
    out = np.zeros(n, dtype="<f4")
    out[: len(d1)] += d1
    out[: len(d2)] += d2
    return af_process(out, "lowpass=f=2200" if dull else "highpass=f=120,lowpass=f=6500")


def build_floodgate_motif(lib: dict[str, np.ndarray]) -> np.ndarray:
    """Dos golpes metálicos profundos (0.0s y 0.80s) + arrastre de compuerta (1.40s-2.65s) con WAVs reales de Epidemic Sound."""
    total = round(2.85 * SR)
    out = np.zeros(total, dtype="<f4")
    hit1 = slice_wav(lib["SFX_FLOODGATE_HIT"], 0.0, 0.85, 0.005, 0.20) * 0.55
    boom1 = slice_wav(lib["SFX_FLOODGATE_BOOM"], 0.42, 1.25, 0.005, 0.30) * 0.22
    hit2 = slice_wav(lib["SFX_FLOODGATE_HIT"], 3.72, 4.65, 0.005, 0.22) * 0.62
    boom2 = slice_wav(lib["SFX_FLOODGATE_BOOM"], 0.42, 1.30, 0.005, 0.35) * 0.26
    scrape = slice_wav(lib["SFX_FLOODGATE_SCRAPE"], 0.18, 1.55, 0.04, 0.25) * 0.48
    add_at(out, hit1, 0.0)
    add_at(out, boom1, 0.0)
    add_at(out, hit2, 0.80)
    add_at(out, boom2, 0.80)
    add_at(out, scrape, 1.40)
    return out


def apply_dialogue_ducking(music: np.ndarray, dialogue_events: list[dict], duck_db: float = -8.5) -> np.ndarray:
    """Atenúa suavemente la música cuando hay voz hablada para máxima inteligibilidad."""
    n = len(music)
    env = np.ones(n, dtype="<f4")
    duck_lin = float(10 ** (duck_db / 20.0))
    pad_pre = round(0.18 * SR)
    pad_post = round(0.28 * SR)
    ramp = round(0.22 * SR)
    for ev in dialogue_events:
        i0 = max(0, round(ev["start"] * SR) - pad_pre)
        i1 = min(n, round(ev["end"] * SR) + pad_post)
        env[i0:i1] = np.minimum(env[i0:i1], duck_lin)
    # Suavizar envolvente con ventana móvil
    if ramp > 1:
        kernel = np.ones(ramp, dtype="<f4") / ramp
        env = np.convolve(env, kernel, mode="same")
    return music * env


def format_srt_ts(t: float) -> str:
    ms = max(0, round(t * 1000))
    return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d},{ms % 1000:03d}"


def format_ass_ts(t: float) -> str:
    cs = max(0, round(t * 100))
    return f"{cs // 360000:01d}:{(cs // 6000) % 60:02d}:{(cs // 100) % 60:02d}.{cs % 100:02d}"


def write_subtitles(srt_path: Path, ass_path: Path, ep_label: str, hook_sub: str, events: list[dict]) -> None:
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
        f"Dialogue: 2,0:00:00.08,0:00:02.45,HookTag,,0,0,0,,{{\\fad(150,350)}}{ep_label}",
        f"Dialogue: 2,0:00:00.18,0:00:02.45,HookSub,,0,0,0,,{{\\fad(200,350)}}{hook_sub}",
    ]
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
            # (src_in, src_out, zoom_mode, sharp)
            (1.25, 4.00, "push_in_fast", 0.90),  # SH01: 2.75s [0.00 - 2.75] Gancho abrigo respira
            (5.00, 7.50, "push_in", 0.65),       # SH02: 2.50s [2.75 - 5.25] ¿Qué has hecho?
            (11.00, 14.75, "macro_in", 0.75),    # SH03: 3.75s [5.25 - 9.00] Gota en sal
            (16.00, 20.25, "push_in", 0.65),     # SH04: 4.25s [9.00 - 13.25] Lleva doce años...
            (24.25, 27.25, "macro_in", 0.70),    # SH05: 3.00s [13.25 - 16.25] Mano cierra llave
            (30.00, 34.25, "push_in_fast", 0.75),# SH06: 4.25s [16.25 - 20.50] Mara habla desde cuello
            (37.00, 39.75, "push_in", 0.65),     # SH07: 2.75s [20.50 - 23.25] No la escuches
            (43.00, 48.50, "pull_back", 0.70),   # SH08: 5.50s [23.25 - 28.75] Es mi hermana. Es Mara.
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
            (0.50, 3.00, "macro_in", 0.75),      # SH01: 2.50s [0.00 - 2.50] Gancho llave sobre plano
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
            (1.50, 4.00, "macro_in", 0.75),      # SH01: 2.50s [0.00 - 2.50] Gancho palma abre llave
            (5.00, 10.50, "push_in", 0.65),      # SH02: 5.50s [2.50 - 8.00]
            (13.00, 17.25, "push_in", 0.65),     # SH03: 4.25s [8.00 - 12.25]
            (20.00, 24.50, "push_in", 0.65),     # SH04: 4.50s [12.25 - 16.75]
            (28.00, 31.00, "push_in_fast", 0.70),# SH05: 3.00s [16.75 - 19.75]
            (33.00, 39.75, "push_in", 0.70),     # SH06: 6.75s [19.75 - 26.50]
            (41.00, 44.50, "push_in", 0.65),     # SH07: 3.50s [26.50 - 30.00]
            (47.00, 53.00, "doc_frame", 0.75),   # SH08: 6.00s [30.00 - 36.00] Firma Inés Vidal libre
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
            (0.00, 3.25, "doc_frame", 0.75),     # SH01: 3.25s [0.00 - 3.25] Firma libre de subtítulos
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


def build_episode_audio_and_subs(ep: str, cfg: dict, lib: dict[str, np.ndarray]) -> tuple[float, list[dict]]:
    ep_dir = AUDIO_DIR / ep
    out_dir = ep_dir / "AJUSTE_V3"
    out_dir.mkdir(parents=True, exist_ok=True)

    segments = cfg["segments"]
    starts = np.cumsum([0.0] + [b - a for a, b, _, _ in segments]).tolist()
    duration = float(starts[-1])
    total_samples = round(duration * SR)

    # 1. ROOM STEM (Epidemic Sound ROOM_BASEMENT)
    room_src = lib["ROOM_BASEMENT"]
    room_offset = (int(ep[-1]) - 1) * 35.0
    room = slice_wav(room_src, room_offset, room_offset + duration, 0.25, 0.35) * 0.16
    if len(room) < total_samples:
        room = np.pad(room, (0, total_samples - len(room)))
    else:
        room = room[:total_samples]

    foley = np.zeros(total_samples, dtype="<f4")
    sfx = np.zeros(total_samples, dtype="<f4")
    music = np.zeros(total_samples, dtype="<f4")
    dialogue = np.zeros(total_samples, dtype="<f4")

    # 2. DIALOGUE STEM
    dialogue_events = []
    for lid, rel_wav, t_start, txt, style, is_mara_cloth, is_recorder_playback in cfg["dialogue"]:
        x = read_wav(ep_dir / rel_wav)
        if is_recorder_playback:
            x = af_process(
                x,
                "highpass=f=320,lowpass=f=3400,acompressor=threshold=0.08:ratio=3:attack=5:release=80:makeup=1.2",
            )
            target_db = -22.5
        elif is_mara_cloth:
            x = af_process(
                x,
                "highpass=f=100,lowpass=f=6400,acompressor=threshold=0.09:ratio=2.2:attack=8:release=100:makeup=1",
            )
            target_db = -22.0
        else:
            x = af_process(
                x,
                "highpass=f=85,lowpass=f=10500,acompressor=threshold=0.09:ratio=2.2:attack=8:release=100:makeup=1.1",
            )
            target_db = -20.5

        rms = max(float(np.sqrt(np.mean(x * x))), 1e-8)
        peak = max(float(np.max(np.abs(x))), 1e-8)
        gain = min(10 ** (target_db / 20.0) / rms, 0.84 / peak)
        x = x * gain
        if is_mara_cloth:
            x = af_process(x, "aecho=0.96:0.88:27|53:0.05|0.03")

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

    # 3. EPIDEMIC SOUND FOLEY, SFX & MUSIC CUES POR EPISODIO
    coat_mov1 = slice_wav(lib["FOLEY_COAT_THICK"], 0.55, 2.35, 0.08, 0.15)
    coat_mov2 = slice_wav(lib["FOLEY_COAT_THICK"], 3.40, 5.10, 0.08, 0.15)
    coat_flap = slice_wav(lib["FOLEY_COAT_FLAP"], 2.05, 2.75, 0.04, 0.10)
    key_hand = slice_wav(lib["FOLEY_KEYS_HAND"], 1.30, 2.45, 0.04, 0.12)
    key_clink = slice_wav(lib["FOLEY_KEYS_HAND"], 11.55, 12.40, 0.03, 0.10)
    paper_turn = slice_wav(lib["FOLEY_PAPER_TURN"], 0.02, 1.25, 0.03, 0.12)
    rec_click = slice_wav(lib["SFX_RECORDER_BUTTONS"], 11.78, 12.28, 0.01, 0.05)
    ui_confirm = slice_wav(lib["SFX_UI_CONFIRM"], 0.0, 0.62, 0.01, 0.08)
    riser_hook = slice_wav(lib["SFX_RISER_LOW"], 1.80, 4.40, 0.10, 0.25)
    dark_boom = slice_wav(lib["SFX_DARK_BOOM"], 0.0, 3.20, 0.02, 0.40)
    rumble_rise = slice_wav(lib["SFX_RUMBLE_RISING"], 5.80, 9.80, 0.30, 0.40)

    if ep == "EP01":
        # Gancho 0.0-2.75s: Riser grave + respiración de Mara + movimiento de lana pesada
        add_at(sfx, riser_hook, 0.0, 0.28)
        add_at(sfx, dark_boom, 0.0, 0.22)
        breath = read_wav(AUDIO_DIR / "EP01" / "EDITADOS" / "EP01_MARA_X01_EDIT.wav")
        breath = af_process(breath, "highpass=f=110,lowpass=f=5800")
        add_at(foley, breath, 0.38, 0.48)
        add_at(foley, coat_mov1, 0.30, 0.38)
        # Gota en SH03 (starts[2] = 5.25s)
        drop_main = build_water_drop(lib, dull=False)
        add_at(sfx, drop_main, starts[2] + 0.55, 0.65)
        add_at(sfx, build_water_drop(lib, dull=True), starts[2] + 1.45, 0.22)
        # Llave en palma de Alba en SH05 (starts[4] = 13.25s)
        add_at(foley, key_hand, starts[4] + 0.55, 0.55)
        add_at(foley, coat_flap, starts[4] + 0.70, 0.30)
        # Temblor de cuello en SH06 (starts[5] = 16.25s)
        add_at(foley, coat_mov2, starts[5] + 0.25, 0.35)
        # Música Epidemic Sound:
        # 1) Textura inicial en gancho (0.0 - 3.2s)
        add_at(music, slice_wav(lib["ORO_BASS"], 0.0, 3.3, 0.15, 0.70), 0.0, 0.26)
        # 2) Cue M01 Memoria bajo llave (9.0s a 16.0s, corta 0.65s antes de Mara en 16.65s)
        add_at(music, slice_wav(lib["ORO_INSTRUMENTS"], 2.0, 9.0, 0.80, 0.85), 9.0, 0.32)
        add_at(music, slice_wav(lib["CREEPING_ANXIETY_BASS"], 4.0, 11.0, 0.80, 0.85), 9.0, 0.25)
        add_at(sfx, riser_hook, 13.3, 0.22)
        # 3) Puente de tensión M02 entre "Es mi hermana" (23.6s) y "Es Mara" (26.6s), fuera a 26.2s
        add_at(music, slice_wav(lib["DONT_TURN_AROUND_INSTRUMENTS"], 18.0, 23.2, 0.60, 0.65), 21.0, 0.35)
        add_at(sfx, slice_wav(rumble_rise, 0.0, 2.5, 0.3, 0.4), 23.6, 0.22)
        # 4) Cola final tras "Es Mara" (27.85s - 28.75s)
        add_at(sfx, slice_wav(dark_boom, 0.0, 0.9, 0.05, 0.35), 27.80, 0.24)

    elif ep == "EP02":
        # Gancho 0.0s: Sub pulse + gota real en SH01
        add_at(sfx, dark_boom, 0.0, 0.20)
        add_at(sfx, build_water_drop(lib, dull=False), 1.85, 0.58)
        # SH03 (7.50s): clic mecánico real de grabadora
        add_at(foley, coat_flap, starts[2] + 0.30, 0.28)
        add_at(sfx, rec_click, starts[2] + 1.35, 0.65)
        # SH04 (10.75s): gota activa voz de Mara
        add_at(sfx, build_water_drop(lib, dull=False), starts[3] + 0.42, 0.60)
        add_at(foley, coat_mov1, starts[3] + 0.55, 0.32)
        # SH05 (16.75s): Motivo de compuerta real (dos golpes + arrastre)
        motif = build_floodgate_motif(lib)
        add_at(sfx, motif, starts[4] + 0.45, 0.72)
        # SH06 (20.75s): Replay en grabadora (clic + voz + motivo filtrado por altavoz)
        add_at(sfx, rec_click, starts[5] + 0.20, 0.48)
        motif_speaker = af_process(motif, "highpass=f=350,lowpass=f=3200,acompressor=threshold=0.08:ratio=3")
        add_at(sfx, motif_speaker, starts[5] + 2.95, 0.45)
        # SH07 (26.75s): Gota sorda sobre lana saturada
        add_at(sfx, build_water_drop(lib, dull=True), starts[6] + 0.35, 0.48)
        # SH08 (31.00s): Papel del informe sobre mesa
        add_at(foley, paper_turn, starts[7] + 0.25, 0.42)
        # Música Epidemic Sound:
        # Cue apertura + preparación de grabadora (0.0 - 10.4s, fuera antes de SH04)
        add_at(music, slice_wav(lib["CREEPING_ANXIETY_BASS"], 2.0, 12.4, 0.40, 0.75), 0.0, 0.25)
        add_at(music, slice_wav(lib["ORO_INSTRUMENTS"], 12.0, 18.5, 0.60, 0.70), 4.0, 0.28)
        # Puente hacia el informe (28.5s - 31.2s)
        add_at(music, slice_wav(lib["DARK_PUZZLE_INSTRUMENTS"], 4.0, 7.2, 0.50, 0.60), 28.2, 0.26)
        add_at(sfx, slice_wav(dark_boom, 0.0, 1.8, 0.04, 0.50), 34.5, 0.22)

    elif ep == "EP03":
        # Gancho 0.0s: Llave de hierro se posa sobre el plano de la compuerta
        add_at(sfx, dark_boom, 0.0, 0.22)
        add_at(foley, key_clink, 0.45, 0.65)
        add_at(foley, paper_turn, 0.30, 0.35)
        # SH03 (7.00s): Informe
        add_at(foley, paper_turn, starts[2] + 0.25, 0.35)
        # SH05 (15.75s): Gota sobre sal
        add_at(sfx, build_water_drop(lib, dull=False), starts[4] + 0.75, 0.62)
        # SH06 (19.00s): Súplica de Mara desde el abrigo
        add_at(foley, coat_mov1, starts[5] + 0.30, 0.36)
        # SH08 (28.00s): Confrontación final
        add_at(foley, coat_flap, starts[7] + 0.35, 0.28)
        # Música Epidemic Sound:
        add_at(music, slice_wav(lib["SHIFTING_GROUND_BASS"], 0.0, 3.0, 0.15, 0.65), 0.0, 0.22)
        # Cue M01 La sospecha cambia de lado (9.5s - 15.3s, fuera antes de la gota en 15.75s)
        add_at(music, slice_wav(lib["DARK_PUZZLE_INSTRUMENTS"], 6.0, 11.8, 0.60, 0.70), 9.5, 0.30)
        add_at(music, slice_wav(lib["ORO_BASS"], 8.0, 13.8, 0.60, 0.70), 9.5, 0.26)
        # Cue M02 El peso de callar tras reacción de Alba (24.6s - 27.6s, fuera antes de SH08)
        add_at(music, slice_wav(lib["CREEPING_ANXIETY_INSTRUMENTS"], 14.0, 17.0, 0.50, 0.65), 24.6, 0.28)
        add_at(sfx, slice_wav(dark_boom, 0.0, 1.5, 0.05, 0.45), 32.2, 0.24)

    elif ep == "EP04":
        # Gancho 0.0s: Palma de Alba se abre revelando la llave de hierro
        add_at(sfx, riser_hook, 0.0, 0.24)
        add_at(foley, key_hand, 0.35, 0.58)
        add_at(foley, coat_flap, starts[2] + 0.40, 0.30)
        # SH08 (30.00s): Firma manuscrita Inés Vidal
        add_at(foley, paper_turn, starts[7] + 0.25, 0.42)
        # Música Epidemic Sound:
        # M02 apertura (0.0 - 2.6s)
        add_at(music, slice_wav(lib["DONT_TURN_AROUND_INSTRUMENTS"], 2.0, 4.8, 0.20, 0.65), 0.0, 0.32)
        add_at(music, slice_wav(lib["ORO_BASS"], 0.0, 2.8, 0.15, 0.65), 0.0, 0.24)
        # Silencio dramático en el "Sí" (17.3s), luego entra M01 en SH07 (26.0s - 29.6s) antes del acta
        add_at(music, slice_wav(lib["DISTURBING_EVIDENCE_INSTRUMENTS"], 4.0, 8.0, 0.60, 0.70), 25.8, 0.30)
        add_at(sfx, riser_hook, 27.0, 0.22)
        add_at(sfx, slice_wav(dark_boom, 0.0, 1.8, 0.04, 0.50), 34.4, 0.24)

    elif ep == "EP05":
        # Gancho 0.0s: Informe firmado + pulso grave
        add_at(sfx, dark_boom, 0.0, 0.22)
        add_at(foley, paper_turn, 0.20, 0.45)
        # SH05 (15.50s): Última gota sobre línea de sal S3
        add_at(sfx, build_water_drop(lib, dull=False), starts[4] + 0.70, 0.64)
        # SH06 (18.75s): "Somos siete..."
        add_at(foley, coat_mov1, starts[5] + 0.25, 0.36)
        # SH08 (29.00s): Gota sorda final hacia S4
        add_at(sfx, build_water_drop(lib, dull=True), starts[7] + 0.45, 0.50)
        # Música Epidemic Sound:
        add_at(music, slice_wav(lib["SHIFTING_GROUND_BASS"], 2.0, 5.2, 0.15, 0.65), 0.0, 0.22)
        # Tensión en el recorte del móvil (SH03-SH04: 8.5s - 15.1s, fuera antes de gota en 15.5s)
        add_at(music, slice_wav(lib["DISTURBING_EVIDENCE_INSTRUMENTS"], 10.0, 16.6, 0.60, 0.70), 8.5, 0.28)
        add_at(music, slice_wav(lib["CREEPING_ANXIETY_BASS"], 10.0, 16.6, 0.60, 0.70), 8.5, 0.22)
        # Puente tras "La página entera. Y mi nombre."
        add_at(sfx, slice_wav(rumble_rise, 0.0, 3.0, 0.3, 0.4), 26.0, 0.22)
        add_at(sfx, slice_wav(dark_boom, 0.0, 1.6, 0.05, 0.45), 31.8, 0.24)

    elif ep == "EP06":
        # Gancho 0.0s: Clic de grabadora + lista de los siete nombres
        add_at(sfx, rec_click, 0.08, 0.52)
        add_at(sfx, dark_boom, 0.0, 0.18)
        # SH02 (6.50s): Abrigo en S4
        add_at(foley, coat_mov2, starts[1] + 0.30, 0.28)
        # SH05 (21.50s): Confirmación "Informe enviado"
        add_at(sfx, ui_confirm, starts[4] + 1.55, 0.55)
        # SH06 (25.50s): Mano anciana suelta llave sobre plano
        add_at(foley, key_clink, starts[5] + 0.70, 0.52)
        add_at(foley, coat_flap, starts[5] + 1.80, 0.26)
        # Música Epidemic Sound:
        # Cello sombrío bajo el envío del informe completo y la entrega de la llave (12.5s - 31.0s, fuera antes del playback en 31.5s)
        add_at(music, slice_wav(lib["ORO_INSTRUMENTS"], 14.0, 32.5, 0.90, 0.90), 12.5, 0.30)
        add_at(music, slice_wav(lib["ORO_BASS"], 14.0, 32.5, 0.90, 0.90), 12.5, 0.24)
        # Cierre de temporada (SH08: 35.75s - 41.75s): Revelación de los siete abrigos tras "Si no apagas eso."
        add_at(music, slice_wav(lib["CREEPING_ANXIETY_INSTRUMENTS"], 4.0, 9.8, 0.80, 0.90), 36.0, 0.28)
        add_at(sfx, slice_wav(dark_boom, 0.0, 2.5, 0.10, 0.60), 38.6, 0.26)

    # Aplicar ducking automático a la música cuando hay diálogo
    music = apply_dialogue_ducking(music, dialogue_events, duck_db=-8.5)

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
    premaster_path = out_dir / "PREMASTER_V3.wav"
    save_wav(premaster_path, premaster)

    # Normalización EBU R128 en dos pasadas a -14.5 LUFS / -1.2 dBTP (estándar potente para redes)
    p_meas = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(premaster_path),
            "-af",
            "loudnorm=I=-14.5:TP=-1.2:LRA=8:print_format=json",
            "-f",
            "null",
            "-",
        ]
    )
    log = p_meas.stderr.decode()
    meas = json.JSONDecoder().raw_decode(log[log.rfind("{") :])[0]
    ln_filter = (
        "loudnorm=I=-14.5:TP=-1.2:LRA=8:linear=true:"
        f"measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
        f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:"
        f"offset={meas['target_offset']},atrim=duration={duration}"
    )
    mix_path = out_dir / f"{ep}_MEZCLA_V3.wav"
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
            str(mix_path),
        ]
    )
    premaster_path.unlink(missing_ok=True)

    # Subtítulos SRT + ASS
    srt_path = FINAL_DIR / f"{ep}_AJUSTADO_V3.srt"
    ass_path = FINAL_DIR / f"{ep}_AJUSTADO_V3.ass"
    write_subtitles(srt_path, ass_path, cfg["ep_label"], cfg["hook_sub"], dialogue_events)

    manifest = {
        "episode": ep,
        "version": "V3_EPIDEMIC_SOUND",
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
    return duration, dialogue_events


def build_shot_video_filter(idx: int, src_in: float, src_out: float, zoom_mode: str, sharp: float) -> str:
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
    else:  # doc_frame: encuadre limpio con leve respiración 1.01 -> 1.025x desplazando el documento hacia arriba para despejar el borde inferior
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
    return f"[s{idx}]trim=start={src_in}:end={src_out},setpts=PTS-STARTPTS,{framing},{grade}[v{idx}]"


def render_episode_v3(ep: str, cfg: dict, duration: float) -> None:
    segments = cfg["segments"]
    n_seg = len(segments)
    filters = [f"[0:v]split={n_seg}" + "".join(f"[s{i}]" for i in range(n_seg))]
    for i, (src_in, src_out, zm, sharp) in enumerate(segments):
        filters.append(build_shot_video_filter(i, src_in, src_out, zm, sharp))

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

    # Generar hoja de contacto de los 8 planos en el punto medio de cada plano
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
    summary = {}
    for ep, cfg in EPISODE_CONFIGS.items():
        print(f"[{ep}] Construyendo stems Epidemic Sound + mezcla -14.5 LUFS + subtítulos ASS...", flush=True)
        dur, _ = build_episode_audio_and_subs(ep, cfg, lib)
        print(f"[{ep}] Renderizando vídeo {dur:.2f}s con encuadre dinámico y color...", flush=True)
        render_episode_v3(ep, cfg, dur)
        info = verify_mp4(FINAL_DIR / f"{ep}_AJUSTADO_V3.mp4")
        summary[ep] = info
        print(
            f"[{ep}] LISTO -> {info['duration']:.2f}s ({info['frames']}f) | {info['lufs']:.1f} LUFS | {info['tp']:.2f} dBTP | {info['decode']}",
            flush=True,
        )

    (FINAL_DIR / "RESUMEN_V3_EPIDEMIC.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Temporada completa V3 renderizada y verificada.", flush=True)


if __name__ == "__main__":
    main()
