#!/usr/bin/env python3
"""Suite de pruebas automatizadas para PERSONAJE_HIPERREALISTA."""

import json
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PERSONAJE_HIPERREALISTA.tools.audio_personaje import (  # noqa: E402
    mix_genjutsu_soundscape,
    parse_two_act_script,
    probe_audio_duration,
    synthesize_genjutsu_illusion_sfx,
)
from PERSONAJE_HIPERREALISTA.tools.genjutsu_video_engine import (  # noqa: E402
    escape_ffmpeg_filter_path,
    process_i2v_video_with_pore_restoration,
    restore_high_frequency_pores,
)
from PERSONAJE_HIPERREALISTA.tools.motor_personaje import (  # noqa: E402
    load_character_config,
    resolve_project_path,
)
from PERSONAJE_HIPERREALISTA.tools.pipeline_personaje import (  # noqa: E402
    audit_personaje_video,
    export_i2v_lipsync_pack,
    generate_personaje_ass,
    run_preflight_checks,
)


def _write_test_speech_wav(path: Path, duration_sec: float = 3.6, sr: int = 48000) -> Path:
    """Genera una señal modulada tipo voz sintética (sin depender de red) para tests offline."""
    n = int(round(duration_sec * sr))
    t = np.linspace(0.0, duration_sec, n, endpoint=False)
    env = np.where((t > 0.2) & (t < 1.5), 1.0, 0.0) + np.where((t > 2.0) & (t < 3.2), 1.0, 0.0)
    sig = (0.35 * np.sin(2 * np.pi * 165.0 * t) + 0.18 * np.sin(2 * np.pi * 330.0 * t)) * env
    pcm = np.stack([sig, sig], axis=1)
    pcm_i16 = np.clip(pcm * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm_i16.tobytes())
    return path


class TestPersonajePipeline(unittest.TestCase):
    def test_preflight_checks_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_preflight_checks(load_character_config(), Path(tmp))
        self.assertTrue(report["ready"])
        self.assertEqual(report["errors"], [])

    def test_parse_two_act_script(self) -> None:
        a1, a2 = parse_two_act_script("Hola mundo. [GENJUTSU] Ahora estás en mi ilusión.")
        self.assertEqual(a1, "Hola mundo.")
        self.assertEqual(a2, "Ahora estás en mi ilusión.")

        b1, b2 = parse_two_act_script("Primera frase científica. Segunda frase con giro.")
        self.assertEqual(b1, "Primera frase científica.")
        self.assertEqual(b2, "Segunda frase con giro.")

        with self.assertRaises(ValueError):
            parse_two_act_script("   ")

    def test_synthesize_genjutsu_illusion_sfx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sfx = synthesize_genjutsu_illusion_sfx(Path(tmp) / "sfx.wav", duration_sec=1.2)
            self.assertTrue(sfx.exists())
            dur = probe_audio_duration(sfx)
            self.assertGreater(dur, 1.1)

    def test_mix_genjutsu_soundscape_ebur128(self) -> None:
        cfg = load_character_config()
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            voice = _write_test_speech_wav(td / "voice.wav", duration_sec=3.6)
            mix = mix_genjutsu_soundscape(voice, td / "master.wav", cue_sec=1.75, config=cfg, include_music=True)
            self.assertTrue(Path(mix["master_wav"]).exists())
            self.assertGreaterEqual(mix["integrated_lufs"], -15.5)
            self.assertLessEqual(mix["integrated_lufs"], -12.5)
            self.assertLessEqual(mix["true_peak_dbtp"], -0.5)

    def test_generate_personaje_ass_and_path_escape(self) -> None:
        cfg = load_character_config()
        words = [
            {"act": 1, "text": "¿Crees", "start": 0.2, "end": 0.55},
            {"act": 1, "text": "que", "start": 0.55, "end": 0.75},
            {"act": 1, "text": "ves?", "start": 0.75, "end": 1.1},
            {"act": 2, "text": "Así", "start": 2.1, "end": 2.35},
            {"act": 2, "text": "despiertas.", "start": 2.35, "end": 2.8},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            ass_path = Path(tmp) / "sub dir:1" / "SUBS.ass"
            generate_personaje_ass(words, ass_path, cue_sec=1.6, config=cfg)
            self.assertTrue(ass_path.exists())
            txt = ass_path.read_text(encoding="utf-8")
            self.assertIn("Montserrat Black", txt)
            self.assertIn("&H005A5CFF", txt)
            self.assertNotIn("VES? {\\c&H005A5CFF&}ASÍ", txt)
            self.assertNotIn("VES? ASÍ", txt)
            esc = escape_ffmpeg_filter_path(ass_path)
            self.assertIn("\\:", esc)

    def test_restore_high_frequency_pores_recovers_detail(self) -> None:
        cfg = load_character_config()
        kf1 = resolve_project_path(cfg["personaje"]["kf1_normal"])
        ref_img = Image.open(kf1).convert("RGB").resize((540, 960), Image.Resampling.LANCZOS)
        blurred = ref_img.filter(ImageFilter.GaussianBlur(radius=2.6))

        ref_arr = np.asarray(ref_img, dtype=np.float32)
        blur_arr = np.asarray(blurred, dtype=np.float32)
        restored = restore_high_frequency_pores(blur_arr, ref_arr, strength=0.5)

        def _hf_energy(arr: np.ndarray) -> float:
            face = arr[180:520, 120:420]
            gray = 0.299 * face[:, :, 0] + 0.587 * face[:, :, 1] + 0.114 * face[:, :, 2]
            return float(np.mean(np.abs(np.diff(gray, axis=1))))

        self.assertGreater(_hf_energy(restored), _hf_energy(blur_arr) * 1.4)

    def test_i2v_restore_end_to_end_and_qc(self) -> None:
        cfg = load_character_config()
        kf1 = resolve_project_path(cfg["personaje"]["kf1_normal"])
        kf2 = resolve_project_path(cfg["personaje"]["kf2_genjutsu"])
        dna_npy = resolve_project_path(cfg["personaje"]["adn_embedding"])

        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            # Simular clip I2V 720x1280 suavizado por VAE (peor caso real)
            blur_jpg = td / "blur_kf1.jpg"
            Image.open(kf1).convert("RGB").resize((720, 1280), Image.Resampling.LANCZOS).filter(
                ImageFilter.GaussianBlur(radius=1.8)
            ).save(blur_jpg, quality=90)
            raw_i2v = td / "raw_i2v.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-y", "-loop", "1", "-i", str(blur_jpg),
                    "-t", "2.4", "-r", "24", "-vf", "scale=720:1280,format=yuv420p",
                    "-c:v", "libx264", "-crf", "24", str(raw_i2v),
                ],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )

            voice = _write_test_speech_wav(td / "voice.wav", duration_sec=2.4)
            mix = mix_genjutsu_soundscape(voice, td / "master.wav", cue_sec=1.2, config=cfg, include_music=False)
            ass = generate_personaje_ass(
                [{"text": "PRUEBA", "start": 0.2, "end": 0.9}, {"text": "GENJUTSU", "start": 1.4, "end": 2.1}],
                td / "subs.ass",
                cue_sec=1.2,
                config=cfg,
            )
            out_mp4 = process_i2v_video_with_pore_restoration(
                input_video=raw_i2v,
                kf1_path=kf1,
                kf2_path=kf2,
                out_mp4=td / "restored.mp4",
                cue_sec=1.2,
                audio_path=Path(mix["master_wav"]),
                subtitle_path=ass,
                preset="veryfast",
            )
            qc = audit_personaje_video(
                out_mp4,
                dna_npy_path=dna_npy,
                cue_sec=1.2,
                out_dir=td,
                config=cfg,
                has_audio=True,
            )
            self.assertNotEqual(qc["verdict"], "FAIL", msg=f"QC errors: {qc['errors']}")
            self.assertTrue(Path(qc["contact_sheet"]).exists())
            self.assertEqual(qc["stream_info"]["video"]["width"], 1080)
            self.assertEqual(qc["stream_info"]["video"]["height"], 1920)
            self.assertAlmostEqual(qc["stream_info"]["fps"], 24.0, places=1)

            pack = export_i2v_lipsync_pack(
                td, kf1, kf2, voice, Path(mix["master_wav"]), "Hola [GENJUTSU] Mundo", 1.2, 2.4
            )
            manifest = json.loads((pack / "05_PROMPTS_FLOW_Y_LIPSYNC.json").read_text(encoding="utf-8"))
            self.assertIn("google_flow_veo3_first_last_frame", manifest)


if __name__ == "__main__":
    unittest.main()
