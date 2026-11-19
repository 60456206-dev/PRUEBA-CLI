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


class TestPersonajeV2Upgrade(unittest.TestCase):
    def test_moving_i2v_has_zero_texture_sticking(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            # KF1 con patrón de tablero de alto contraste en la esquina superior izquierda (donde NO debe pegarse)
            kf1_arr = np.full((320, 180, 3), 120, dtype=np.uint8)
            for y in range(20, 100):
                for x in range(20, 100):
                    if ((x // 4) + (y // 4)) % 2 == 0:
                        kf1_arr[y, x] = [245, 245, 245]
                    else:
                        kf1_arr[y, x] = [15, 15, 15]
            kf1 = td / "kf1.jpg"
            kf2 = td / "kf2.jpg"
            Image.fromarray(kf1_arr).resize((540, 960)).save(kf1, quality=95)
            Image.fromarray(kf1_arr).resize((540, 960)).save(kf2, quality=95)

            # Vídeo sintético con cielo liso en esquina superior izquierda y un círculo en movimiento horizontal
            frames_dir = td / "mov_frames"
            frames_dir.mkdir()
            for idx in range(12):
                arr = np.full((640, 360, 3), 128, dtype=np.uint8)
                cx = 80 + idx * 14
                cy = 380
                yy, xx = np.ogrid[:640, :360]
                mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= 40 ** 2
                arr[mask] = [215, 175, 145]
                Image.fromarray(arr).save(frames_dir / f"f_{idx:04d}.jpg", quality=96)

            in_mp4 = td / "moving_raw.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-y", "-framerate", "24", "-i", str(frames_dir / "f_%04d.jpg"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(in_mp4),
                ],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )

            out_mp4 = td / "moving_out.mp4"
            process_i2v_video_with_pore_restoration(
                input_video=in_mp4,
                kf1_path=kf1,
                kf2_path=kf2,
                out_mp4=out_mp4,
                cue_sec=99.0,
                fps=24,
                crf=18,
                grain_sigma=0.8,
                pore_strength=0.45,
                maxrate="12M",
                bufsize="24M",
            )
            self.assertTrue(out_mp4.exists())

            qc = audit_personaje_video(
                out_mp4,
                dna_npy_path=resolve_project_path(load_character_config()["personaje"]["adn_embedding"]),
                cue_sec=99.0,
                out_dir=td,
                config=load_character_config(),
                has_audio=False,
                master_image_path=kf1,
            )
            self.assertGreater(qc["stream_info"]["bitrate_kbps"], 0.0)
            self.assertLessEqual(qc["stream_info"]["bitrate_kbps"], 14000.0)

            chk_jpg = td / "chk_f8.jpg"
            subprocess.run(
                ["ffmpeg", "-y", "-ss", "0.33", "-i", str(out_mp4), "-frames:v", "1", str(chk_jpg)],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            chk_arr = np.asarray(Image.open(chk_jpg).convert("L"), dtype=np.float32)
            # Esquina superior izquierda (cielo liso) NO hereda el tablero de KF1 (std baja vs >80 si hubiera texture sticking)
            top_left_std = float(np.std(chk_arr[60:240, 60:240]))
            self.assertLess(top_left_std, 12.0)

    def test_structural_face_similarity_survives_crimson_shift(self):
        from unittest import mock
        from PERSONAJE_HIPERREALISTA.tools import motor_personaje
        from PERSONAJE_HIPERREALISTA.tools.motor_personaje import (
            measure_frame_biometrics,
        )

        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            # Crear retrato sintético con rasgos faciales estructurados en zona central
            arr = np.full((640, 360, 3), 90, dtype=np.uint8)
            arr[140:420, 95:265] = [195, 160, 138]  # rostro
            arr[210:230, 125:165] = [38, 28, 24]    # ojo izq
            arr[210:230, 195:235] = [38, 28, 24]    # ojo der
            arr[250:320, 170:190] = [160, 120, 100] # nariz
            arr[345:365, 145:215] = [130, 75, 70]   # boca

            ref_img = td / "kf1_ref.jpg"
            Image.fromarray(arr).resize((540, 960)).save(ref_img, quality=96)
            with mock.patch.object(motor_personaje, "DNA_DIR", td):
                dna = motor_personaje.extract_biometric_dna_signature(ref_img, "TEST_CHAR")
            dna_npy = Path(dna["embedding_file"])

            # Versión teñida de carmesí Genjutsu (canal R alto, G/B muy reducidos) + ligero desplazamiento
            crimson = arr.astype(np.float32)
            crimson[:, :, 0] = np.clip(crimson[:, :, 0] * 1.25 + 35, 0, 255)
            crimson[:, :, 1] = np.clip(crimson[:, :, 1] * 0.28, 0, 255)
            crimson[:, :, 2] = np.clip(crimson[:, :, 2] * 0.30, 0, 255)
            shifted = np.roll(crimson.astype(np.uint8), shift=4, axis=1)
            cur_img = td / "kf2_crimson.jpg"
            Image.fromarray(shifted).resize((540, 960)).save(cur_img, quality=96)

            metrics = measure_frame_biometrics(cur_img, dna_npy, master_image_path=ref_img)
            self.assertIn(metrics["identity_engine"], ("structural_gradient_proxy", "insightface_arcface_512d"))
            if metrics["identity_engine"] == "structural_gradient_proxy":
                self.assertGreaterEqual(metrics["structural_face_similarity"], 75.0)
            else:
                self.assertGreaterEqual(metrics["identity_similarity"], 75.0)

    def test_studio_api_clients_mocked(self):
        import base64
        from unittest import mock
        from PERSONAJE_HIPERREALISTA.tools import studio_api_client

        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            img_p = td / "kf1.jpg"
            aud_p = _write_test_speech_wav(td / "voz.wav", duration_sec=0.8)
            img_p.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 512)
            seed_mp3 = td / "seed.mp3"
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(aud_p), "-b:a", "64k", str(seed_mp3)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )

            # 1) ElevenLabsClient mocked
            el = studio_api_client.ElevenLabsStudioClient(api_key="el-key")
            out_wav = td / "el.wav"
            el_resp = {
                "audio_base64": base64.b64encode(seed_mp3.read_bytes()).decode("ascii"),
                "alignment": {
                    "characters": list("Hola tú."),
                    "character_start_times_seconds": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
                    "character_end_times_seconds": [0.09, 0.19, 0.29, 0.39, 0.49, 0.59, 0.69, 0.79],
                },
            }
            with mock.patch.object(studio_api_client, "_http_json", return_value=el_resp):
                ok_el, wb_data = el.synthesize_with_timestamps("Hola tú.", out_wav, voice_id="voice_test")
            self.assertTrue(ok_el)
            self.assertTrue(out_wav.exists())
            self.assertEqual([w["text"] for w in wb_data], ["Hola", "tú."])

            # 2) fal.ai OmniHuman v1.5 & Kling Avatar v2 Pro queue submit -> poll -> result -> download
            fal = studio_api_client.FalStudioAvatarClient(api_key="fal-key")
            for model_name in ("fal_omnihuman", "fal_kling_avatar"):
                out_fal = td / f"{model_name}.mp4"
                queue_calls = [
                    {"status_url": "https://queue.fal.run/status/1", "response_url": "https://queue.fal.run/res/1"},
                    {"status": "COMPLETED"},
                ]
                final_payload = {"video": {"url": "https://cdn.fal.run/avatar.mp4"}}

                def fake_download(url, dest, timeout=120.0):
                    dest.write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 4000)
                    return dest

                with mock.patch.object(studio_api_client, "_http_json", side_effect=[queue_calls[0], queue_calls[1], final_payload]), \
                     mock.patch.object(studio_api_client, "_download_binary", side_effect=fake_download), \
                     mock.patch.object(studio_api_client, "_verify_video_file", return_value=True), \
                     mock.patch.object(studio_api_client, "_probe_duration_safe", return_value=12.0), \
                     mock.patch("time.sleep", return_value=None):
                    got = fal.generate_talking_avatar(img_p, aud_p, out_fal, model=model_name)
                self.assertEqual(got, out_fal)
                self.assertTrue(out_fal.exists())

            # 3) HeyGen Avatar IV v3 mocked
            hg = studio_api_client.HeyGenAvatarIVClient(api_key="hg-key", default_avatar_id="avatar_123")
            out_hg = td / "heygen.mp4"
            with mock.patch.object(
                studio_api_client,
                "_http_json",
                side_effect=[
                    {"data": {"video_id": "vid_999"}},
                    {"data": {"status": "completed", "video_url": "https://cdn.heygen.com/v999.mp4"}},
                ],
            ), \
                 mock.patch.object(studio_api_client, "_download_binary", side_effect=lambda u, p, timeout=120.0: (p.write_bytes(b"mp4data" * 300), p)[1]), \
                 mock.patch.object(studio_api_client, "_verify_video_file", return_value=True), \
                 mock.patch("time.sleep", return_value=None):
                got_hg = hg.generate_avatar_iv_video("https://example.com/voz.mp3", out_hg)
            self.assertEqual(got_hg, out_hg)
            self.assertTrue(out_hg.exists())


if __name__ == "__main__":
    unittest.main()
