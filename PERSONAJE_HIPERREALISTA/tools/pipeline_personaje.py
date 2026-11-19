#!/usr/bin/env python3
"""
ORQUESTADOR MAESTRO · PERSONAJE HIPERREALISTA (CANDIDATO C + GENJUTSU LIVE-ACTION)
Prepara, valida y ejecuta sin errores la generación audiovisual completa:
1. Preflight Check integral (dependencias, fuentes, ADN maestro, keyframes y espacio).
2. Locución actoral bi-fase (Acto 1 Normal -> [GENJUTSU] -> Acto 2 Eclipse) + marcas de palabra.
3. Mezcla sonora Genjutsu (riser + fractura + boom + aleteo + cama duckeada) a -14.0 LUFS.
4. Subtítulos Kinetic ASS en Safe Zone (Montserrat Black vía pysubs2).
5. Exportación automática de I2V_PACK (Google Flow Veo 3.1 FLF2V / Kling / Hallo2 / LivePortrait).
6. Renderizado de vídeo CRF 16 (modo local_preview o postprocesado --input-video con restauración de poros).
7. Auditoría QC automática (técnica + biométrica) y Contact Sheet visual.
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pysubs2
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PERSONAJE_HIPERREALISTA.tools.audio_personaje import (  # noqa: E402
    measure_audio_loudness,
    mix_genjutsu_soundscape,
    probe_audio_duration,
    resolve_sfx_assets,
    synthesize_actor_speech,
)
from PERSONAJE_HIPERREALISTA.tools.genjutsu_video_engine import (  # noqa: E402
    fit_vertical_cover,
    process_i2v_video_with_pore_restoration,
    probe_media_duration,
    render_genjutsu_master_video,
)
from PERSONAJE_HIPERREALISTA.tools.motor_personaje import (  # noqa: E402
    PROJECT_ROOT,
    VIDEO_DIR,
    load_character_config,
    measure_frame_biometrics,
    resolve_project_path,
)
from PERSONAJE_HIPERREALISTA.tools.studio_api_client import (  # noqa: E402
    FalStudioAvatarClient,
    HeyGenAvatarIVClient,
    get_studio_api_status,
)


def run_preflight_checks(
    config: Optional[Dict[str, Any]] = None,
    out_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Valida binarios, librerías, fuentes, referencias biométricas, keyframes y almacenamiento.
    Lanza RuntimeError descriptivo si falta algún requisito crítico.
    """
    cfg = config or load_character_config()
    errors: List[str] = []
    warnings: List[str] = []

    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            errors.append(f"Falta binario del sistema requerido: {binary}")

    for mod in ("PIL", "numpy", "pysubs2", "edge_tts"):
        if importlib.util.find_spec(mod) is None:
            errors.append(f"Falta módulo Python requerido: {mod}")

    pcfg = cfg["personaje"]
    required_files = {
        "semilla_oficial": resolve_project_path(pcfg["semilla_oficial"]),
        "adn_json": resolve_project_path(pcfg["adn_json"]),
        "adn_embedding": resolve_project_path(pcfg["adn_embedding"]),
        "kf1_normal": resolve_project_path(pcfg["kf1_normal"]),
        "kf2_genjutsu": resolve_project_path(pcfg["kf2_genjutsu"]),
    }
    for label, fpath in required_files.items():
        if not fpath.exists():
            errors.append(f"Falta archivo clave '{label}': {fpath}")

    if pcfg.get("kf3_plano_medio"):
        kf3_path = resolve_project_path(pcfg["kf3_plano_medio"])
        if not kf3_path.exists():
            warnings.append(f"Tercer encuadre plano medio no encontrado aún: {kf3_path}")

    font_candidates = [
        Path("/usr/share/fonts/truetype/montserrat/Montserrat-Black.ttf"),
        Path("/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf"),
    ]
    if not any(p.exists() for p in font_candidates):
        warnings.append("Fuentes Montserrat no encontradas en /usr/share/fonts/truetype/montserrat/.")

    if not os.getenv("GEMINI_API_KEY", "").strip():
        warnings.append("GEMINI_API_KEY no definida; la locución usará Edge-TTS fallback.")

    studio_apis = get_studio_api_status(cfg)
    sfx_assets = resolve_sfx_assets(cfg)
    if sfx_assets.get("genjutsu_fracture") is None:
        errors.append("No se pudo generar o localizar SFX_GENJUTSU_FRACTURE.wav")

    target_dir = out_dir or (VIDEO_DIR / "PRUEBA_01_GENJUTSU")
    target_dir.mkdir(parents=True, exist_ok=True)
    disk_free_mb = shutil.disk_usage(target_dir).free / (1024 * 1024)
    if disk_free_mb < 400:
        errors.append(f"Espacio libre insuficiente en disco: {disk_free_mb:.1f} MB (< 400 MB)")

    report = {
        "ready": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "disk_free_mb": round(disk_free_mb, 1),
        "tts_primary": "elevenlabs" if (studio_apis["elevenlabs"]["configured"] and studio_apis["elevenlabs"]["preferred_in_config"]) else ("gemini" if os.getenv("GEMINI_API_KEY", "").strip() else "edge_tts"),
        "studio_apis": studio_apis,
        "sfx_assets": {k: str(v) if v else None for k, v in sfx_assets.items()},
    }
    if errors:
        raise RuntimeError("Preflight fallido:\n- " + "\n- ".join(errors))
    return report


def generate_personaje_ass(
    word_boundaries: List[Dict[str, Any]],
    out_ass: Path,
    cue_sec: float,
    config: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Genera subtítulos vectoriales Kinetic ASS (1080x1920, Safe Zone TikTok/Reels)
    en ráfagas de 2-3 palabras cambiando acento a carmesí tras activar el Genjutsu.
    """
    cfg = config or load_character_config()
    scfg = cfg.get("subtitles", {})
    vcfg = cfg["video"]

    subs = pysubs2.SSAFile()
    subs.info["PlayResX"] = str(vcfg.get("width", 1080))
    subs.info["PlayResY"] = str(vcfg.get("height", 1920))
    subs.info["ScaledBorderAndShadow"] = "yes"

    style_normal = pysubs2.SSAStyle(
        fontname=str(scfg.get("font_name", "Montserrat Black")),
        fontsize=float(scfg.get("font_size", 66)),
        primarycolor=pysubs2.Color(255, 255, 255, 0),
        secondarycolor=pysubs2.Color(255, 220, 70, 0),
        outlinecolor=pysubs2.Color(10, 12, 16, 0),
        backcolor=pysubs2.Color(0, 0, 0, 180),
        bold=True,
        outline=float(scfg.get("outline", 6.0)),
        shadow=0.0,
        alignment=pysubs2.Alignment.BOTTOM_CENTER,
        marginl=55,
        marginr=55,
        marginv=int(scfg.get("margin_v", 340)),
    )
    subs.styles["Default"] = style_normal

    max_words = max(1, int(scfg.get("max_words_per_burst", 3)))
    clean_words = [w for w in word_boundaries if str(w.get("text", "")).strip()]

    # Agrupar ráfagas respetando cambios de acto, fin de oración y pausas > 0.28s
    bursts: List[List[Dict[str, Any]]] = []
    cur_burst: List[Dict[str, Any]] = []
    for w in clean_words:
        if cur_burst:
            prev = cur_burst[-1]
            act_changed = w.get("act") is not None and prev.get("act") is not None and w.get("act") != prev.get("act")
            crosses_cue = float(prev["start"]) < cue_sec <= float(w["start"])
            gap = float(w["start"]) - float(prev["end"])
            prev_ends_sentence = str(prev["text"]).strip().endswith((".", "?", "!"))
            if len(cur_burst) >= max_words or act_changed or crosses_cue or gap >= 0.28 or prev_ends_sentence:
                bursts.append(cur_burst)
                cur_burst = []
        cur_burst.append(w)
    if cur_burst:
        bursts.append(cur_burst)

    for chunk in bursts:
        start_s = float(chunk[0]["start"])
        end_s = max(start_s + 0.18, float(chunk[-1]["end"]))

        tokens = [re.sub(r"[^\w\sáéíóúüñÁÉÍÓÚÜÑ¿?¡!.,…-]", "", str(w["text"]).upper()).strip() for w in chunk]
        tokens = [t for t in tokens if t]
        if not tokens:
            continue

        is_genjutsu = (chunk[0].get("act") == 2) or (start_s >= cue_sec)
        # Color ASS en &HBBGGRR&: amarillo cálido antes del Genjutsu, coral-carmesí luminoso después
        accent = "&H0038EEFF" if not is_genjutsu else "&H005A5CFF"
        bounce = r"{\fscx84\fscy84\t(0,55,\fscx108\fscy108)\t(55,120,\fscx100\fscy100)}"
        if len(tokens) > 1:
            head = " ".join(tokens[:-1])
            tail = tokens[-1]
            line_txt = f"{bounce}{head} {{\\c{accent}}}{tail}{{\\c&H00FFFFFF&}}"
        else:
            line_txt = f"{bounce}{{\\c{accent}}}{tokens[0]}{{\\c&H00FFFFFF&}}"

        subs.events.append(
            pysubs2.SSAEvent(
                start=int(round(start_s * 1000)),
                end=int(round(end_s * 1000)),
                style="Default",
                text=line_txt,
            )
        )

    out_ass.parent.mkdir(parents=True, exist_ok=True)
    subs.save(str(out_ass), encoding="utf-8")
    return out_ass


def export_i2v_lipsync_pack(
    out_dir: Path,
    kf1_path: Path,
    kf2_path: Path,
    clean_voice_wav: Path,
    master_audio_wav: Path,
    script_text: str,
    cue_sec: float,
    total_duration_sec: float,
) -> Path:
    """
    Prepara un paquete listo para motores I2V / Lip-Sync externos (Google Flow Veo 3.1
    First-Last-Frame, Kling, Hallo2, LivePortrait, EchoMimicV2) y deja escrito el
    comando exacto para reinyectar el clip resultante con restauración de poros.
    """
    pack_dir = out_dir / "I2V_PACK"
    pack_dir.mkdir(parents=True, exist_ok=True)

    kf1_out = pack_dir / "01_KF1_FIRST_FRAME.jpg"
    kf2_out = pack_dir / "02_KF2_LAST_FRAME.jpg"
    fit_vertical_cover(Image.open(kf1_path).convert("RGB"), 1080, 1920).save(kf1_out, quality=96)
    fit_vertical_cover(Image.open(kf2_path).convert("RGB"), 1080, 1920).save(kf2_out, quality=96)

    voice_out = pack_dir / "03_VOZ_LIMPIA_PARA_LIPSYNC.wav"
    master_out = pack_dir / "04_AUDIO_MASTER_FINAL.wav"
    shutil.copy2(clean_voice_wav, voice_out)
    shutil.copy2(master_audio_wav, master_out)

    manifest = {
        "personaje": "Candidato C Oficial (29 años, 85mm f/1.8 RAW)",
        "duracion_objetivo_seg": round(total_duration_sec, 2),
        "genjutsu_cue_seg": round(cue_sec, 2),
        "guion": script_text,
        "archivos": {
            "first_frame": str(kf1_out),
            "last_frame": str(kf2_out),
            "clean_voice_wav": str(voice_out),
            "master_audio_wav": str(master_out),
        },
        "google_flow_veo3_first_last_frame": {
            "aspect_ratio": "9:16",
            "nota_duracion": "Veo 3.1 en Google Flow genera clips cortos (~5-8s) y NO sincroniza labios a un WAV externo; úsalo para segmentos cortos (Acto 1 o Acto 2 por separado) o usa --studio-lipsync para sincronización exacta al WAV.",
            "first_frame": str(kf1_out),
            "last_frame": str(kf2_out),
            "prompt": (
                f"Vertical 9:16 photorealistic 85mm f/1.8 live-action studio shot of the exact same 29-year-old "
                f"Latino man talking naturally to camera with subtle hand gestures and authentic blinking. "
                f"Preserve 100% of his natural human skin pores, 2-day dark stubble, and facial bone structure. "
                f"At {cue_sec:.1f}s, a subtle live-action Genjutsu lighting shift bends the studio background "
                f"from warm tungsten bokeh to deep crimson eclipse chiaroscuro as black raven feathers drift "
                f"through shallow foreground bokeh and crimson ring reflections appear in his irises. "
                f"Strictly NO anime filter on skin, NO plastic skin smoothing, 24fps cinema motion."
            ),
        },
        "studio_apis_commands": {
            "fal_omnihuman": f"python3 PERSONAJE_HIPERREALISTA/tools/pipeline_personaje.py --studio-lipsync fal_omnihuman --framing close --out-dir {out_dir}",
            "fal_kling_avatar": f"python3 PERSONAJE_HIPERREALISTA/tools/pipeline_personaje.py --studio-lipsync fal_kling_avatar --framing medium --out-dir {out_dir}",
            "heygen_avatar_iv": f"python3 PERSONAJE_HIPERREALISTA/tools/pipeline_personaje.py --studio-lipsync heygen_avatar_iv --public-audio-url https://TU_SERVIDOR/voz.wav --out-dir {out_dir}",
        },
        "gpu_lipsync_hallo2_o_liveportrait": {
            "nota": "Ejecutar en máquina con GPU NVIDIA y luego pasar el MP4 resultante a --input-video",
            "ejemplo_echomimic_o_hallo2": (
                f"python inference.py --source_image {kf1_out} --driving_audio {voice_out} --output raw_lipsync.mp4"
            ),
        },
        "postproceso_restauracion_poros_local": (
            f"python3 PERSONAJE_HIPERREALISTA/tools/pipeline_personaje.py "
            f"--input-video /ruta/a/CLIP_I2V_O_LIPSYNC.mp4 "
            f"--audio-file {voice_out} "
            f"--cue-sec {cue_sec:.2f} "
            f"--out-dir {out_dir}"
        ),
    }
    (pack_dir / "05_PROMPTS_FLOW_Y_LIPSYNC.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return pack_dir


def _extract_video_stream_info(video_path: Path) -> Dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration,size,bit_rate",
        "-of",
        "json",
        str(video_path),
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=15).decode()
    data = json.loads(out)
    streams = data.get("streams", [])
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fps_val = 0.0
    if v_stream and "/" in str(v_stream.get("r_frame_rate", "")):
        num, den = v_stream["r_frame_rate"].split("/", 1)
        fps_val = round(float(num) / max(1.0, float(den)), 3)
    fmt = data.get("format", {})
    return {
        "video": v_stream,
        "audio": a_stream,
        "fps": fps_val,
        "duration_sec": round(float(fmt.get("duration", 0.0)), 3),
        "size_mb": round(float(fmt.get("size", 0.0)) / (1024 * 1024), 2),
        "bitrate_kbps": round(float(fmt.get("bit_rate", 0.0)) / 1000.0, 1),
    }


def _detect_black_frames(video_path: Path) -> int:
    cmd = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-vf",
        "blackdetect=d=0.25:pix_th=0.10",
        "-an",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return len(re.findall(r"black_start:", proc.stderr))


def audit_personaje_video(
    video_path: Path,
    dna_npy_path: Path,
    cue_sec: float,
    out_dir: Path,
    config: Optional[Dict[str, Any]] = None,
    has_audio: bool = True,
    master_image_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Ejecuta auditoría técnica + biométrica sobre el vídeo generado y construye
    CONTACT_SHEET_PERSONAJE.jpg (6 fotogramas clave con puntuación de poros e identidad).
    """
    cfg = config or load_character_config()
    qcfg = cfg["qc"]
    errors: List[str] = []
    warnings: List[str] = []

    info = _extract_video_stream_info(video_path)
    v = info["video"] or {}
    a = info["audio"]
    dur = info["duration_sec"]

    if v.get("width") != 1080 or v.get("height") != 1920:
        errors.append(f"Resolución inválida: {v.get('width')}x{v.get('height')} (esperado 1080x1920)")
    if abs(info["fps"] - 24.0) > 0.1:
        errors.append(f"FPS inválido: {info['fps']} (esperado 24.0)")
    if has_audio and a is None:
        errors.append("El vídeo no contiene pista de audio.")

    black_events = _detect_black_frames(video_path)
    if black_events > 0:
        errors.append(f"Detectados {black_events} segmentos en negro.")

    loudness: Dict[str, float] = {}
    if has_audio and a is not None:
        loudness = measure_audio_loudness(video_path)
        lufs = loudness["input_i"]
        tp = loudness["input_tp"]
        if not (float(qcfg["lufs_min"]) <= lufs <= float(qcfg["lufs_max"])):
            warnings.append(f"Sonoridad fuera de rango objetivo: {lufs} LUFS")
        if tp > float(qcfg["max_true_peak_db"]):
            errors.append(f"True Peak excesivo: {tp} dBTP (> {qcfg['max_true_peak_db']})")

    # Muestreo biométrico de frames + Contact Sheet 3x2
    sample_count = int(qcfg.get("sample_frames", 6))
    sample_dir = out_dir / "_qc_samples"
    sample_dir.mkdir(parents=True, exist_ok=True)
    frame_metrics: List[Dict[str, Any]] = []

    times = [
        round(min(max(0.1, dur - 0.15), (dur * (i + 0.5)) / sample_count), 2)
        for i in range(sample_count)
    ]
    for i, ts in enumerate(times):
        f_jpg = sample_dir / f"sample_{i:02d}.jpg"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{ts:.2f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(f_jpg),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        bio = measure_frame_biometrics(f_jpg, dna_npy_path, master_image_path=master_image_path)
        act_label = "ACTO 2 (GENJUTSU)" if ts >= cue_sec else "ACTO 1 (NORMAL)"
        min_sim = (
            float(qcfg["min_identity_similarity_act2"])
            if ts >= cue_sec
            else float(qcfg["min_identity_similarity_act1"])
        )
        if bio["pore_texture_energy"] < float(qcfg["min_pore_energy"]):
            errors.append(f"Pérdida de poros en t={ts}s: {bio['pore_texture_energy']} < {qcfg['min_pore_energy']}")
        if bio["identity_similarity"] < min_sim:
            warnings.append(f"Similitud reducida en t={ts}s: {bio['identity_similarity']}% < {min_sim}%")
        frame_metrics.append({"t_sec": ts, "act": act_label, "image": str(f_jpg), **bio})

    # Construir CONTACT_SHEET_PERSONAJE.jpg (3 columnas x 2 filas)
    cw, ch = 360, 640
    cols, rows = 3, 2
    sheet = Image.new("RGB", (cols * cw + 80, rows * (ch + 64) + 96), (12, 14, 19))
    draw = ImageDraw.Draw(sheet)
    try:
        f_head = ImageFont.truetype("/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf", 22)
        f_meta = ImageFont.truetype("/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf", 14)
    except Exception:
        f_head = f_meta = ImageFont.load_default()

    draw.text(
        (20, 20),
        f"QC VISUAL & BIOMÉTRICO · {video_path.name} ({info['size_mb']} MB | {dur:.2f}s @ {info['fps']}fps)",
        fill=(245, 247, 250),
        font=f_head,
    )
    lufs_txt = f"Audio: {loudness.get('input_i', 'N/A')} LUFS / TP {loudness.get('input_tp', 'N/A')} dBTP" if loudness else "Sin audio"
    draw.text((20, 50), f"{lufs_txt} · Cue Genjutsu: {cue_sec:.2f}s", fill=(255, 209, 102), font=f_meta)

    for idx, fm in enumerate(frame_metrics):
        r, c = divmod(idx, cols)
        x0 = 20 + c * (cw + 20)
        y0 = 84 + r * (ch + 64)
        tile = Image.open(fm["image"]).convert("RGB").resize((cw, ch), Image.Resampling.LANCZOS)
        sheet.paste(tile, (x0, y0))
        border = (230, 57, 70) if "ACTO 2" in fm["act"] else (70, 85, 110)
        draw.rectangle([x0 - 1, y0 - 1, x0 + cw + 1, y0 + ch + 1], outline=border, width=2)
        draw.text((x0 + 4, y0 + ch + 8), f"t={fm['t_sec']:.2f}s · {fm['act']}", fill=(255, 255, 255), font=f_meta)
        eng_short = "ArcFace" if "insightface" in str(fm.get("identity_engine", "")) else "ProxyEst"
        draw.text(
            (x0 + 4, y0 + ch + 28),
            f"Poros: {fm['pore_texture_energy']} | {eng_short}: {fm['identity_similarity']}%",
            fill=(170, 220, 170),
            font=f_meta,
        )

    contact_sheet_path = out_dir / "CONTACT_SHEET_PERSONAJE.jpg"
    sheet.save(contact_sheet_path, quality=94)
    shutil.rmtree(sample_dir, ignore_errors=True)

    verdict = "FAIL" if errors else ("WARN" if warnings else "PASS")
    report = {
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "stream_info": info,
        "loudness": loudness,
        "cue_sec": round(cue_sec, 3),
        "frame_metrics": [
            {k: v for k, v in fm.items() if k != "image"} for fm in frame_metrics
        ],
        "contact_sheet": str(contact_sheet_path),
    }
    (out_dir / "QC_REPORT.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report


def run_personaje_pipeline(
    script_text: Optional[str] = None,
    out_dir: Optional[Path] = None,
    external_audio_file: Optional[Path] = None,
    input_video: Optional[Path] = None,
    cue_sec_override: Optional[float] = None,
    prefer_edge: bool = False,
    prefer_elevenlabs: bool = False,
    studio_lipsync: str = "none",
    framing: str = "close",
    public_audio_url: Optional[str] = None,
    include_music: bool = True,
    include_subtitles: bool = True,
    export_i2v_only: bool = False,
    preflight_only: bool = False,
) -> Dict[str, Any]:
    """Ejecuta de principio a fin el pipeline de Candidato C sin errores."""
    cfg = load_character_config()
    target_dir = (out_dir or (VIDEO_DIR / "PRUEBA_01_GENJUTSU")).resolve()
    preflight = run_preflight_checks(cfg, target_dir)
    if preflight_only:
        return {"preflight": preflight, "out_dir": str(target_dir)}

    pcfg = cfg["personaje"]
    vcfg = cfg["video"]
    s_cfg = cfg.get("studio_apis", {})
    kf1_path = resolve_project_path(pcfg["kf1_normal"])
    kf2_path = resolve_project_path(pcfg["kf2_genjutsu"])
    kf3_path = resolve_project_path(pcfg["kf3_plano_medio"]) if pcfg.get("kf3_plano_medio") else None
    dna_npy_path = resolve_project_path(pcfg["adn_embedding"])

    script = script_text or cfg["default_test_script"]

    # 1. Locución bi-fase + timestamps reales
    speech = synthesize_actor_speech(
        script,
        target_dir,
        config=cfg,
        external_audio_file=external_audio_file,
        prefer_edge=prefer_edge,
        prefer_elevenlabs=prefer_elevenlabs,
    )
    cue_sec = float(cue_sec_override) if cue_sec_override is not None else float(speech["genjutsu_cue_sec"])

    # 2. Mezcla Genjutsu + 2-pass loudnorm (-14.0 LUFS)
    mix = mix_genjutsu_soundscape(
        Path(speech["voice_wav"]),
        target_dir / "AUDIO_MASTER.wav",
        cue_sec=cue_sec,
        config=cfg,
        include_music=include_music,
    )

    # 3. Subtítulos Kinetic ASS opcionales
    ass_path: Optional[Path] = None
    if include_subtitles:
        wb = json.loads(Path(speech["word_boundaries_path"]).read_text(encoding="utf-8"))
        ass_path = generate_personaje_ass(wb, target_dir / "SUBTITULOS_PERSONAJE.ass", cue_sec, cfg)

    # 4. Paquete I2V / Lip-Sync listo para Flow, fal.ai, HeyGen o GPU
    source_keyframe = kf3_path if (framing == "medium" and kf3_path and kf3_path.exists()) else kf1_path
    i2v_pack_dir = export_i2v_lipsync_pack(
        out_dir=target_dir,
        kf1_path=source_keyframe,
        kf2_path=kf2_path,
        clean_voice_wav=Path(speech["voice_wav"]),
        master_audio_wav=Path(mix["master_wav"]),
        script_text=script,
        cue_sec=cue_sec,
        total_duration_sec=float(mix["duration_sec"]),
    )

    result: Dict[str, Any] = {
        "preflight": preflight,
        "out_dir": str(target_dir),
        "speech": speech,
        "mix": mix,
        "subtitles_ass": str(ass_path) if ass_path else None,
        "i2v_pack_dir": str(i2v_pack_dir),
        "framing": framing,
        "source_keyframe": str(source_keyframe),
    }

    if export_i2v_only:
        return result

    # 5A. Generación opcional de Lip-Sync vía API de estudio
    effective_input_video = Path(input_video).resolve() if input_video is not None else None
    if effective_input_video is None and studio_lipsync and studio_lipsync != "none":
        raw_studio_mp4 = target_dir / f"_studio_{studio_lipsync}.mp4"
        if studio_lipsync in ("fal_omnihuman", "fal_kling_avatar"):
            fal_client = FalStudioAvatarClient()
            fal_client.generate_talking_avatar(
                image_source=source_keyframe,
                audio_source=Path(speech["voice_wav"]),
                out_mp4=raw_studio_mp4,
                model=studio_lipsync,
                resolution=str(s_cfg.get("fal_omnihuman_resolution", "")) or None,
            )
            effective_input_video = raw_studio_mp4
        elif studio_lipsync == "heygen_avatar_iv":
            hg_client = HeyGenAvatarIVClient(default_avatar_id=str(s_cfg.get("heygen_avatar_id", "")))
            hg_client.generate_avatar_iv_video(
                audio_url=str(public_audio_url or ""),
                out_mp4=raw_studio_mp4,
            )
            effective_input_video = raw_studio_mp4
        else:
            raise ValueError(f"Proveedor --studio-lipsync desconocido: {studio_lipsync}")

    # 5B. Renderizado de vídeo (I2V restaurado sin texture sticking o Preview local sincronizado)
    maxrate = str(vcfg.get("maxrate", "12M"))
    bufsize = str(vcfg.get("bufsize", "24M"))
    if effective_input_video is not None:
        final_mp4 = target_dir / "CANDIDATO_C_GENJUTSU_I2V_FINAL.mp4"
        process_i2v_video_with_pore_restoration(
            input_video=effective_input_video,
            kf1_path=source_keyframe,
            kf2_path=kf2_path,
            out_mp4=final_mp4,
            cue_sec=cue_sec,
            audio_path=Path(mix["master_wav"]),
            subtitle_path=ass_path,
            fps=int(vcfg["fps"]),
            crf=int(vcfg["crf"]),
            preset=str(vcfg["preset"]),
            grain_sigma=float(vcfg["temporal_grain_sigma"]),
            pore_strength=float(vcfg["pore_restoration_strength"]),
            transition_window_sec=float(vcfg["transition_window_sec"]),
            maxrate=maxrate,
            bufsize=bufsize,
        )
        mode = f"studio_{studio_lipsync}" if studio_lipsync != "none" else "i2v_restore"
    else:
        final_mp4 = target_dir / "PRUEBA_01_LOCAL_PREVIEW.mp4"
        render_genjutsu_master_video(
            kf1_path=source_keyframe,
            kf2_path=kf2_path,
            out_mp4=final_mp4,
            duration_sec=float(mix["duration_sec"]),
            fps=int(vcfg["fps"]),
            cue_sec=cue_sec,
            transition_window_sec=float(vcfg["transition_window_sec"]),
            audio_path=Path(mix["master_wav"]),
            subtitle_path=ass_path,
            crf=int(vcfg["crf"]),
            preset=str(vcfg["preset"]),
            grain_sigma=float(vcfg["temporal_grain_sigma"]),
            pore_strength=0.0,
            maxrate=maxrate,
            bufsize=bufsize,
        )
        mode = "local_preview"

    # 6. Auditoría QC + Contact Sheet
    qc = audit_personaje_video(
        final_mp4,
        dna_npy_path=dna_npy_path,
        cue_sec=cue_sec,
        out_dir=target_dir,
        config=cfg,
        has_audio=True,
        master_image_path=source_keyframe,
    )

    result.update(
        {
            "mode": mode,
            "final_mp4": str(final_mp4),
            "qc": qc,
        }
    )
    (target_dir / "METADATA_PRUEBA.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline Completo Candidato C · Voz + SFX Genjutsu + Hiperrealismo")
    parser.add_argument("--script", type=str, default=None, help="Guion con marcador [GENJUTSU]")
    parser.add_argument("--audio-file", type=str, default=None, help="Audio externo de voz")
    parser.add_argument("--input-video", type=str, default=None, help="Vídeo crudo de Flow/Hallo2/LivePortrait para restaurar poros y muxeado")
    parser.add_argument("--cue-sec", type=float, default=None, help="Forzar segundo exacto de fractura Genjutsu")
    parser.add_argument("--out-dir", type=str, default=str(VIDEO_DIR / "PRUEBA_01_GENJUTSU"))
    parser.add_argument("--prefer-edge", action="store_true", help="Usar Edge-TTS en lugar de Gemini/ElevenLabs")
    parser.add_argument("--prefer-elevenlabs", action="store_true", help="Priorizar ElevenLabs TTS con timestamps")
    parser.add_argument(
        "--studio-lipsync",
        type=str,
        default="none",
        choices=["none", "fal_omnihuman", "fal_kling_avatar", "heygen_avatar_iv"],
        help="Motor API de estudio para Lip-Sync/actuación real",
    )
    parser.add_argument(
        "--framing",
        type=str,
        default="close",
        choices=["close", "medium"],
        help="Encuadre base: close (KF1 85mm) o medium (KF3 50mm explicando)",
    )
    parser.add_argument("--public-audio-url", type=str, default=None, help="URL HTTPS pública del audio (requerida para HeyGen)")
    parser.add_argument("--no-music", action="store_true", help="Omitir cama musical")
    parser.add_argument("--no-subtitles", action="store_true", help="No quemar subtítulos ASS en el vídeo")
    parser.add_argument("--export-i2v-only", action="store_true", help="Generar audio + I2V_PACK sin renderizar preview")
    parser.add_argument("--preflight-only", action="store_true", help="Solo comprobar requisitos y salir")
    args = parser.parse_args()

    res = run_personaje_pipeline(
        script_text=args.script,
        out_dir=Path(args.out_dir),
        external_audio_file=Path(args.audio_file) if args.audio_file else None,
        input_video=Path(args.input_video) if args.input_video else None,
        cue_sec_override=args.cue_sec,
        prefer_edge=args.prefer_edge,
        prefer_elevenlabs=args.prefer_elevenlabs,
        studio_lipsync=args.studio_lipsync,
        framing=args.framing,
        public_audio_url=args.public_audio_url,
        include_music=not args.no_music,
        include_subtitles=not args.no_subtitles,
        export_i2v_only=args.export_i2v_only,
        preflight_only=args.preflight_only,
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
