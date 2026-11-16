#!/usr/bin/env python3
"""
Tests unitarios offline para las correcciones críticas de TIKTOK_RADAR/tools/.
"""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import whatsapp_monitor
import news_radar
import audio_generator
import flow_generator
import remotion_renderer
import pipeline_autonomo
import ensamblador_final
import ejecutar_todo
from video_qc_inspector import VideoQCInspector
import generador_portada


class TestWhatsAppMonitor(unittest.TestCase):
    def test_parse_webhook_payload_twilio_and_generic(self):
        msg, sender = whatsapp_monitor.parse_webhook_payload("Body=%21estado&From=whatsapp%3A%2B34600111222")
        self.assertEqual(msg, "!estado")
        self.assertEqual(sender, "whatsapp:+34600111222")

        msg2, sender2 = whatsapp_monitor.parse_webhook_payload("text=hola+radar&phone=34699888777")
        self.assertEqual(msg2, "hola radar")
        self.assertEqual(sender2, "34699888777")

        self.assertEqual(whatsapp_monitor.parse_webhook_payload(""), ("", ""))

    def test_scan_delivery_state_resets_on_new_folder_and_respects_notify_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d1 = root / "2026-11-13_0800_G1"
            (d1 / "shots").mkdir(parents=True)
            (d1 / "metadata.json").write_text(
                json.dumps({"storyboard": [{"id": f"SH{i:02d}"} for i in range(1, 10)]}),
                encoding="utf-8",
            )
            sh1 = d1 / "shots" / "SH01.mp4"
            sh1.write_bytes(b"x" * 60_000)

            d2 = root / "2026-11-13_1300_G3"
            (d2 / "shots").mkdir(parents=True)
            sh2 = d2 / "shots" / "SH01.mp4"
            sh2.write_bytes(b"x" * 60_000)

            state = {"active_dir": None, "reported_shots": set(), "reported_final": False}
            with mock.patch.object(whatsapp_monitor, "send_whatsapp") as m_send, \
                 mock.patch.object(whatsapp_monitor, "send_whatsapp_delivery") as m_deliv:
                # Initial scan with notify=False seeds without spamming
                whatsapp_monitor.scan_delivery_state(d1, state, notify=False)
                self.assertEqual(state["active_dir"], d1.name)
                self.assertIn("SH01", state["reported_shots"])
                m_send.assert_not_called()
                m_deliv.assert_not_called()

                # Switching to d2 resets reported_shots and notifies for new SH01
                whatsapp_monitor.scan_delivery_state(d2, state, notify=True)
                self.assertEqual(state["active_dir"], d2.name)
                self.assertEqual(state["reported_shots"], {"SH01"})
                m_send.assert_called_once()
                self.assertIn("1/13 planos", m_send.call_args[0][0])

    def test_get_planned_shots_count_supports_shots_and_storyboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            d_shots = root / "shots_meta"
            d_shots.mkdir()
            (d_shots / "metadata.json").write_text(
                json.dumps({"shots": [{"id": f"SH{i:02d}"} for i in range(1, 10)]}),
                encoding="utf-8",
            )
            self.assertEqual(whatsapp_monitor._get_planned_shots_count(d_shots), 9)

            d_legacy = root / "storyboard_meta"
            d_legacy.mkdir()
            (d_legacy / "metadata.json").write_text(
                json.dumps({"storyboard": [{"id": f"SH{i:02d}"} for i in range(1, 12)]}),
                encoding="utf-8",
            )
            self.assertEqual(whatsapp_monitor._get_planned_shots_count(d_legacy), 11)


class TestNewsRadar(unittest.TestCase):
    def test_clean_rss_text_strips_tags_and_entities(self):
        raw = "<p>Breaking &amp; Critical &#8217;Mayday&#x2019; alert &mdash; Live</p>"
        cleaned = news_radar.clean_rss_text(raw)
        self.assertNotIn("<", cleaned)
        self.assertIn("& Critical", cleaned)
        self.assertIn("’Mayday’", cleaned)

    def test_kw_match_prevents_substring_false_positives(self):
        self.assertFalse(news_radar.kw_match("cure", "secure cloud architecture updated"))
        self.assertFalse(news_radar.kw_match("stall", "install latest driver update"))
        self.assertFalse(news_radar.kw_match("grant", "immigrant workforce policy"))
        self.assertTrue(news_radar.kw_match("mayday", "Pilot declares Mayday after engine fire"))
        self.assertTrue(news_radar.kw_match("cure", "Scientists discover a cure for rare disease"))

    def test_g1_incident_scores_far_above_commercial_regulation(self):
        now = time.time()
        incident = {
            "title": "Boeing 737 declares Mayday and performs emergency landing after severe engine fire",
            "summary": "200 passengers evacuated safely after cabin smoke and hydraulic failure triggered an emergency.",
            "timestamp": now - 3600,
            "source_weight": 1.6,
            "is_aviation": True,
            "genre": "G1_AVIACION_CATASTROFES",
        }
        regulation = {
            "title": "FAA proposes new airworthiness rules for commercial eVTOL airline quarterly earnings route",
            "summary": "Airline unveils new lounge schedule and quarterly profit forecast under FAA regulatory proposal.",
            "timestamp": now - 1800,
            "source_weight": 1.7,
            "is_aviation": True,
            "genre": "G1_AVIACION_CATASTROFES",
        }
        s_inc = news_radar.score_article(incident, now)
        s_reg = news_radar.score_article(regulation, now)
        self.assertTrue(incident["is_aviation_incident"])
        self.assertFalse(regulation["is_aviation_incident"])
        self.assertGreater(s_inc, s_reg + 30.0)

    def test_rerank_by_human_impact_preserves_g1_incidents(self):
        candidates = [
            {"title": "FAA updates eVTOL draft", "summary": "Policy schedule.", "source_name": "AeroTime", "score": 10.0, "timestamp": 200, "is_aviation_incident": False},
            {"title": "Cargo flight declares Mayday", "summary": "Engine fire.", "source_name": "AVweb", "score": 32.0, "timestamp": 100, "is_aviation_incident": True},
        ]
        mock_payload = json.dumps({
            "candidates": [{"content": {"parts": [{"text": '{"ranked_indices": [0, 1], "top_reason": "test"}'}]}}]
        }).encode("utf-8")

        class _FakeResp:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return mock_payload

        # json.load reads .read(), mock urllib.request.urlopen cleanly
        import io
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}), \
             mock.patch("urllib.request.urlopen", return_value=io.BytesIO(mock_payload)):
            out = news_radar.rerank_by_human_impact_gemini(candidates, genre_key="G1_AVIACION_CATASTROFES")
        self.assertEqual(out[0]["title"], "Cargo flight declares Mayday")


class TestRemotionRenderer(unittest.TestCase):
    def test_truncate_clean_respects_word_boundaries(self):
        out = remotion_renderer.truncate_clean("ARQUITECTURA DE SILICIO NANOSCÓPICA ULTRA COMPACTA", 26)
        self.assertLessEqual(len(out), 26)
        self.assertFalse(out.endswith("NANOSC"))
        self.assertEqual(out, "ARQUITECTURA DE SILICIO")

    def test_composition_selection_disambiguates_infographics_by_shot(self):
        genre = "G1_AVIACION_CATASTROFES"
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH01", "Infografía Táctica 3D"), "VeritasiumAltimeter")
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH03", "Infografía Táctica 3D"), "VeritasiumAltimeter")
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH10", "Infografía Táctica 3D"), "VeritasiumBlueprint")
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH11", "Infografía Táctica 3D"), "VeritasiumStatComparison")
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH13", "Infografía Táctica 3D"), "VeritasiumDocumentaryOutro")

    def test_disaster_genre_maps_away_from_altimeter(self):
        self.assertEqual(remotion_renderer.get_composition_for_genre("G1_CATASTROFES"), "VeritasiumStatComparison")
        self.assertEqual(remotion_renderer.get_composition_for_genre("G1_AVIACION"), "VeritasiumAltimeter")
        props = remotion_renderer.build_category_props(
            "G3_IA_HARDWARE",
            title="Chip de 2nm",
            composition_id="VeritasiumBlueprint",
        )
        self.assertEqual(props["theme"], "hardware")
        self.assertIn("2 NM", props["metricA"])

    def test_genre_mapping_avoids_ia_substring_false_positives(self):
        self.assertEqual(remotion_renderer.get_composition_for_genre("G4_ESPACIO_CIENCIA"), "VeritasiumStatComparison")
        self.assertEqual(
            remotion_renderer.get_composition_for_shot("G4_ESPACIO_CIENCIA", "SH03", "Telemetría de Descenso"),
            "VeritasiumBlueprint",
        )
        props_space = remotion_renderer.build_category_props(
            "G4_ESPACIO_CIENCIA",
            title="Telescopio detecta señal en órbita",
            composition_id="VeritasiumStatComparison",
        )
        self.assertEqual(props_space["theme"], "space")
        self.assertNotIn("$4.2B", json.dumps(props_space))

        self.assertEqual(remotion_renderer.get_composition_for_genre("G3_IA_ROBOTICA"), "VeritasiumTechChip")
        props_ai = remotion_renderer.build_category_props(
            "G3_IA_ROBOTICA",
            title="Nuevo chip autónomo",
            composition_id="VeritasiumTechChip",
        )
        self.assertEqual(props_ai["theme"], "hardware")

    def test_verified_source_card_renders_cleanly_across_genres(self):
        with tempfile.TemporaryDirectory() as tmp:
            for genre in ("G1_AVIACION", "G2_CIBERSEGURIDAD", "G3_IA_HARDWARE", "G4_ESPACIO_CIENCIA"):
                out_png = Path(tmp) / f"{genre}.png"
                generated = ensamblador_final.generate_verified_source_card(
                    source_name="Reuters",
                    genre=genre,
                    out_png=out_png,
                )
                self.assertIsNotNone(generated)
                self.assertTrue(out_png.exists() and out_png.stat().st_size > 1000)


class TestPipelineAndSubtitles(unittest.TestCase):
    def test_flow_primario_keeps_hybrid_render_mode(self):
        cfg = json.loads((TOOLS_DIR.parent / "config_produccion.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["modo_produccion"]["activo"], "flow_primario")
        with mock.patch.object(pipeline_autonomo, "generate_dynamic_news_script", return_value="Frase uno. Frase dos. Frase tres."):
            sb = pipeline_autonomo.generate_monetizable_storyboard({
                "title": "Avión realiza aterrizaje de emergencia por falla hidráulica",
                "source_name": "AeroTime",
                "link": "https://example.com/av",
                "genre": "G1_AVIACION_CATASTROFES",
            })
        modes = [s["render_mode"] for s in sb["shots"]]
        self.assertEqual(modes.count("flow"), 8)
        self.assertEqual(modes.count("infographic"), 5)
        excerpts = {s["narrative_excerpt"] for s in sb["shots"]}
        self.assertGreaterEqual(len(excerpts), 2)

    def test_rescale_sentence_boundaries_scales_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "LOCUCION_GEMINI.mp3"
            bounds = Path(tmp) / "SENTENCE_BOUNDARIES.json"
            bounds.write_text(json.dumps([
                {"text": "Uno.", "start": 0.0, "end": 10.0},
                {"text": "Dos.", "start": 10.0, "end": 30.0},
            ]), encoding="utf-8")
            pipeline_autonomo._rescale_sentence_boundaries(audio, factor=0.95)
            scaled = json.loads(bounds.read_text(encoding="utf-8"))
            self.assertAlmostEqual(scaled[0]["end"], 10.526, places=3)
            self.assertAlmostEqual(scaled[1]["start"], 10.526, places=3)
            self.assertAlmostEqual(scaled[1]["end"], 31.579, places=3)

    def test_generate_kinetic_ass_uses_sentence_boundaries_and_safezone(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            bounds = d / "SENTENCE_BOUNDARIES.json"
            bounds.write_text(json.dumps([
                {"text": "Primera frase breve.", "start": 0.0, "end": 2.0},
                {"text": "Segunda frase final.", "start": 30.0, "end": 32.0},
            ]), encoding="utf-8")
            ass_path = d / "SUBTITULOS_KINETIC.ass"
            ensamblador_final.generate_kinetic_ass(
                "Primera frase breve. Segunda frase final.",
                total_duration=35.0,
                ass_path=ass_path,
                source_name="AeroTime",
                sentence_boundaries_file=bounds,
            )
            content = ass_path.read_text(encoding="utf-8")
            # CapCutBouncing MarginV=560 & HookPill MarginV=175
            self.assertIn(",560,1", content)
            self.assertIn(",175,1", content)
            # Second sentence starts near 0:00:30.00, not linearly compressed
            self.assertIn("0:00:30.00", content)


class TestVideoQCAndCover(unittest.TestCase):
    def test_qc_inspector_never_fakes_lufs_and_flags_bad_safezone(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            fake_mp4 = d / "NOTICIERO_FINAL_62S.mp4"
            fake_mp4.write_bytes(b"not a real video")
            (d / "metadata.json").write_text(json.dumps({
                "genre": "G1_AVIACION",
                "script": "Texto sin cierre",
                "storyboard": [{"id": "SH01", "render_mode": "flow"}],
            }), encoding="utf-8")
            (d / "SUBTITULOS_KINETIC.ass").write_text(
                "Style: CapCutBouncing,Montserrat Black,78,&H00FFFFFF,&H0000EAFF,&H00000000,&H00000000,-1,0,0,0,100,100,1.2,0,1,7,0,2,80,80,140,1\n",
                encoding="utf-8",
            )
            qc = VideoQCInspector(fake_mp4)
            qc.results["stream_info"] = {"width": 1080, "height": 1920, "fps": 24.0, "duration": 62.0}
            with mock.patch("subprocess.run", side_effect=OSError("no ffmpeg")):
                audio = qc.inspect_audio()
            self.assertIsNone(audio["integrated_lufs"])
            self.assertIsNone(audio["true_peak_dbfs"])
            sz = qc.inspect_safezone_and_editorial()
            self.assertFalse(sz["capcut_safezone_ok"])
            self.assertEqual(sz["capcut_y_est"], 1920 - 140)
            self.assertFalse(sz["cover_present"])
            verdict = qc.evaluate_verdict()
            self.assertEqual(verdict["verdict"], "FAIL")

    def test_cover_non_aviation_disaster_badge(self):
        self.assertTrue(generador_portada._is_non_aviation_disaster("G1_CATASTROFES", "Terremoto magnitud 7.1 sacude zona urbana"))
        self.assertFalse(generador_portada._is_non_aviation_disaster("G1_AVIACION_CATASTROFES", "Boeing 737 declares Mayday"))
        is_cyber, is_ai, is_space = generador_portada._detect_category_flags("G3_IA_ROBOTICA", "Chip neuromórfico rompe récord")
        self.assertEqual((is_cyber, is_ai, is_space), (False, True, False))

    def test_cover_skips_unauthenticated_pollinations_watermark(self):
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.dict(os.environ, {"POLLINATIONS_API_KEY": ""}, clear=False), \
             mock.patch.object(generador_portada, "_try_gemini_image_cover", return_value=None), \
             mock.patch("urllib.request.urlopen") as m_urlopen:
            bg = generador_portada.generate_ai_cover_background("G4_ESPACIO", "Starship Flight 15", Path(tmp))
            m_urlopen.assert_not_called()
            self.assertEqual(bg.size, (1080, 1920))

    def test_synthesize_voiceover_guarantees_monetizable_duration(self):
        import asyncio
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            out_mp3 = Path(tmp) / "LOCUCION_NOTICIERO_62S.mp3"
            subprocess.run(
                ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "55.49", "-b:a", "64k", str(out_mp3)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            with mock.patch.object(pipeline_autonomo, "generate_speech", return_value=55.49):
                final_dur = asyncio.run(pipeline_autonomo.synthesize_voiceover("Guion de prueba.", out_mp3))
            self.assertGreaterEqual(final_dur, 61.1)


class TestEjecutarTodoQCGuard(unittest.TestCase):
    def test_qc_schema_and_fail_blocks_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            qc_file = d / "QC_AUDIT_REPORT.json"
            qc_file.write_text(json.dumps({
                "verdict": "FAIL",
                "score": 55,
                "errors": ["audio_clipping", "capcut_safezone_violation"],
                "warnings": ["missing_flow_shots"],
            }), encoding="utf-8")

            summary = ejecutar_todo._read_qc_summary(qc_file)
            self.assertTrue(summary["failed"])
            self.assertEqual(summary["score"], 55)
            self.assertEqual(len(summary["errors"]), 2)

            with mock.patch.object(whatsapp_monitor, "send_whatsapp") as m_alert, \
                 mock.patch.object(whatsapp_monitor, "send_whatsapp_delivery") as m_deliv:
                ejecutar_todo._dispatch_whatsapp_outcome(d, True, summary)
                m_deliv.assert_not_called()
                m_alert.assert_called_once()
                self.assertIn("BLOQUEO QC", m_alert.call_args[0][0])

    def test_qc_warn_still_allows_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            qc_file = d / "QC_AUDIT_REPORT.json"
            qc_file.write_text(json.dumps({
                "verdict": "WARN",
                "score": 88,
                "errors": [],
                "warnings": ["missing_flow_shots"],
            }), encoding="utf-8")

            summary = ejecutar_todo._read_qc_summary(qc_file)
            self.assertFalse(summary["failed"])
            with mock.patch.object(whatsapp_monitor, "send_whatsapp") as m_alert, \
                 mock.patch.object(whatsapp_monitor, "send_whatsapp_delivery") as m_deliv:
                ejecutar_todo._dispatch_whatsapp_outcome(d, True, summary)
                m_deliv.assert_called_once_with(d)
                m_alert.assert_not_called()


class TestRenderAndSyncUpgrades(unittest.TestCase):
    def test_word_boundaries_reconstruction_rescale_and_ass_sync(self):
        words = [
            {"text": "Cohete", "start": 0.20, "end": 0.65},
            {"text": "espacial", "start": 0.70, "end": 1.25},
            {"text": "despega.", "start": 1.30, "end": 1.95},
            {"text": "Misión", "start": 2.40, "end": 2.90},
            {"text": "crítica.", "start": 2.95, "end": 3.60},
        ]
        sentences = audio_generator._reconstruct_sentences_from_words(words)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0]["text"], "Cohete espacial despega.")
        self.assertAlmostEqual(sentences[0]["end"], 1.95, places=3)

        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            audio = d / "LOCUCION_NOTICIERO_62S.mp3"
            wb = d / "WORD_BOUNDARIES.json"
            sb = d / "SENTENCE_BOUNDARIES.json"
            wb.write_text(json.dumps(words), encoding="utf-8")
            sb.write_text(json.dumps(sentences), encoding="utf-8")

            pipeline_autonomo._rescale_sentence_boundaries(audio, factor=0.90)
            rescaled_wb = json.loads(wb.read_text(encoding="utf-8"))
            self.assertAlmostEqual(rescaled_wb[3]["start"], 2.40 / 0.90, places=2)

            ass_path = d / "SUBTITULOS_KINETIC.ass"
            ensamblador_final.generate_kinetic_ass(
                "Cohete espacial despega. Misión crítica.",
                total_duration=5.0,
                ass_path=ass_path,
                source_name="Space.com",
                word_boundaries_file=wb,
            )
            content = ass_path.read_text(encoding="utf-8")
            self.assertIn("0:00:02.67", content)

    def test_extract_story_metrics_pulls_real_identifiers_and_filters_props(self):
        metrics_av = pipeline_autonomo.extract_story_metrics(
            "British Airways BA431 A321neo goes around near Heathrow",
            "El vuelo BA431 descendió desde 12.000 ft hasta 3200 ft cerca de Heathrow.",
            "Aviation24",
            "G1_AVIACION",
        )
        self.assertEqual(metrics_av["flightNumber"], "BA431")
        self.assertEqual(metrics_av["initialAlt"], 12000)
        self.assertEqual(metrics_av["finalAlt"], 3200)

        metrics_sp = pipeline_autonomo.extract_story_metrics(
            "On this day in space! Nov. 13, 1971: NASA's Mariner 9",
            "En 1971, la humanidad alcanzó el planeta rojo en noviembre.",
            "Space.com",
            "G4_ESPACIO",
        )
        self.assertNotIn("flightNumber", metrics_sp)

        props_chip = remotion_renderer.build_category_props(
            "G3_IA_HARDWARE",
            title="Nuevo procesador TSMC 2nm supera el 40%",
            composition_id="VeritasiumTechChip",
            extra_props={**metrics_av, "nodeSize": "2 NM"},
        )
        self.assertEqual(props_chip["nodeSize"], "2 NM")
        self.assertNotIn("flightNumber", props_chip)

    def test_remotion_batch_worker_payload_and_crf(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_mp4 = Path(tmp) / "SH01.mp4"

            def fake_run(cmd, **kwargs):
                batch_json = Path(cmd[2])
                data = json.loads(batch_json.read_text(encoding="utf-8"))
                self.assertEqual(data["jobs"][0]["crf"], 14)
                self.assertEqual(data["jobs"][0]["compositionId"], "VeritasiumStatComparison")
                out_mp4.write_bytes(b"0" * 15_000)
                return mock.Mock(returncode=0, stdout="[REMOTION-BATCH] ✅ SH01.mp4")

            with mock.patch("subprocess.run", side_effect=fake_run):
                res = remotion_renderer.render_remotion_batch([{
                    "compositionId": "VeritasiumStatComparison",
                    "outputLocation": str(out_mp4),
                    "inputProps": {"title": "TEST"},
                }], crf=14)
            self.assertEqual(res[str(out_mp4)], out_mp4)

    def test_flow_select_prompt_for_attempt_respects_quota_vs_fallback(self):
        shot = {"prompt": "PRIMARY PROMPT", "fallback_prompt": "SAFE FALLBACK", "action": "acción"}
        p1, fb1 = flow_generator.select_prompt_for_attempt(shot, attempt=1, use_fallback=False)
        self.assertEqual((p1, fb1), ("PRIMARY PROMPT", False))
        p2_quota, fb2_quota = flow_generator.select_prompt_for_attempt(shot, attempt=2, use_fallback=False)
        self.assertEqual((p2_quota, fb2_quota), ("PRIMARY PROMPT", False))
        p2_policy, fb2_policy = flow_generator.select_prompt_for_attempt(shot, attempt=2, use_fallback=True)
        self.assertEqual((p2_policy, fb2_policy), ("SAFE FALLBACK", True))

    def test_render_two_pass_loudnorm_uses_linear_measurements(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_m4a = Path(tmp) / "master.m4a"
            calls = []

            def fake_run(cmd, **kwargs):
                calls.append(cmd)
                if len(calls) == 1:
                    fake_json = '{"input_i":"-18.50","input_tp":"-4.20","input_lra":"4.10","input_thresh":"-29.00","target_offset":"0.45"}'
                    return mock.Mock(returncode=0, stdout=fake_json)
                out_m4a.write_bytes(b"m4a" * 100)
                return mock.Mock(returncode=0, stdout="")

            with mock.patch("subprocess.run", side_effect=fake_run):
                ensamblador_final._render_two_pass_loudnorm(
                    inputs=["-i", "voice.mp3"],
                    fc_parts=["[0:a]anull[mixed]"],
                    raw_label="[mixed]",
                    total_dur=62.0,
                    master_m4a=out_m4a,
                )
            self.assertEqual(len(calls), 2)
            cmd2_str = " ".join(calls[1])
            self.assertIn("linear=true", cmd2_str)
            self.assertIn("measured_I=-18.50", cmd2_str)

    def test_flow_sequential_profile_discovery_and_cooldown_filtering(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            p1 = td / "flow-profile"
            p2 = td / "flow-profiles" / "cuenta_2"
            p3 = td / "flow-profiles" / "cuenta_3"
            for p in (p1, p2, p3):
                p.mkdir(parents=True, exist_ok=True)
            state_file = td / "state.json"

            env_val = f"{p1}:{p2}:{p3}:{p2}"
            with mock.patch.dict("os.environ", {"FLOW_PROFILE_DIRS": env_val, "FLOW_STATE_FILE": str(state_file)}):
                resolved = flow_generator.resolve_flow_profiles()
                self.assertEqual([p.resolve() for p in resolved], [p1.resolve(), p2.resolve(), p3.resolve()])

                flow_generator.mark_profile_state(p1, "quota_exhausted", cooldown_hours=12.0, state_file=state_file, now=1000.0)
                flow_generator.mark_profile_state(p2, "session_expired", cooldown_hours=24.0, state_file=state_file, now=1000.0)

                avail = flow_generator.select_available_profiles(resolved, state=flow_generator.load_flow_profile_state(state_file), now=1500.0)
                self.assertEqual([p.resolve() for p in avail], [p3.resolve()])

                # Tras vencer el cooldown de p1 (1000 + 12*3600 < 50000), p1 vuelve a estar disponible pero p2 sigue expirada
                avail_after = flow_generator.select_available_profiles(resolved, state=flow_generator.load_flow_profile_state(state_file), now=50000.0)
                self.assertEqual([p.resolve() for p in avail_after], [p1.resolve(), p3.resolve()])

    def test_flow_sequential_rotation_continues_pending_shots_on_second_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            p1 = td / "p1"
            p2 = td / "p2"
            p1.mkdir()
            p2.mkdir()
            state_file = td / "state.json"

            delivery = td / "delivery"
            shots_dir = delivery / "shots"
            shots_dir.mkdir(parents=True)
            (delivery / "metadata.json").write_text(json.dumps({
                "shots": [
                    {"id": "SH01", "render_mode": "remotion"},
                    {"id": "SH02", "render_mode": "flow", "prompt": "P2"},
                    {"id": "SH04", "render_mode": "flow", "prompt": "P4"},
                ]
            }), encoding="utf-8")

            calls = []

            async def fake_session(profile_dir, cdp_url, pending_shots, shots_dir, delivery_dir, chrome_exec):
                calls.append((profile_dir.name, [s["id"] for s in pending_shots]))
                if profile_dir.name == "p1":
                    (shots_dir / "SH02.mp4").write_bytes(b"ok" * 20000)
                    return "quota_exhausted", 1
                (shots_dir / "SH04.mp4").write_bytes(b"ok" * 20000)
                return "completed", 1

            def fake_verify(path: Path) -> bool:
                return path.exists() and path.stat().st_size > 25000

            with mock.patch.dict("os.environ", {"FLOW_PROFILE_DIRS": f"{p1}:{p2}", "FLOW_STATE_FILE": str(state_file)}), \
                 mock.patch.object(flow_generator, "async_playwright", new=object()), \
                 mock.patch.object(flow_generator, "verify_mp4", side_effect=fake_verify), \
                 mock.patch.object(flow_generator, "_run_single_profile_session", side_effect=fake_session), \
                 mock.patch("asyncio.sleep", new=mock.AsyncMock()):
                ok = flow_generator.asyncio.run(flow_generator.run_flow_generator(delivery))

            self.assertTrue(ok)
            self.assertEqual(calls, [("p1", ["SH02", "SH04"]), ("p2", ["SH04"])])
            st = flow_generator.load_flow_profile_state(state_file)
            self.assertEqual(st[str(p1.resolve())]["reason"], "quota_exhausted")
            self.assertEqual(st[str(p2.resolve())]["reason"], "ok")


if __name__ == "__main__":
    unittest.main(verbosity=2)
