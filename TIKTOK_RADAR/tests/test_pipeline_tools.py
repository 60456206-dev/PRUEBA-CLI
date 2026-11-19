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
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH01", "Mapa Editorial 2.5D", has_geo=True), "Editorial25DMap")
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH01", "Mapa Editorial 2.5D", has_geo=False), "Editorial25DFactSheet")
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH03", "Dato Clave 2.5D", has_geo=True), "Editorial25DFactSheet")
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH10", "Diagrama Progresivo 2.5D"), "Editorial25DDiagram")
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH11", "Evidencia Documental 2.5D"), "Editorial25DFactSheet")
        self.assertEqual(remotion_renderer.get_composition_for_shot(genre, "SH13", "Cierre Documental 2.5D"), "Editorial25DOutro")

    def test_disaster_genre_maps_away_from_aircraft_diagram(self):
        self.assertEqual(remotion_renderer.get_composition_for_genre("G1_CATASTROFES"), "Editorial25DFactSheet")
        self.assertEqual(remotion_renderer.get_composition_for_genre("G1_AVIACION"), "Editorial25DMap")
        props = remotion_renderer.build_category_props(
            "G3_IA_HARDWARE",
            title="Chip de 2nm",
            composition_id="Editorial25DDiagram",
        )
        self.assertEqual(props["diagramKind"], "chip")
        self.assertNotIn("VERITASIUM", json.dumps(props).upper())

    def test_genre_mapping_avoids_ia_substring_false_positives_and_fake_metrics(self):
        self.assertEqual(remotion_renderer.get_composition_for_genre("G4_ESPACIO_CIENCIA"), "Editorial25DMap")
        self.assertEqual(
            remotion_renderer.get_composition_for_shot("G4_ESPACIO_CIENCIA", "SH10", "Diagrama de Sonda"),
            "Editorial25DDiagram",
        )
        props_space = remotion_renderer.build_category_props(
            "G4_ESPACIO_CIENCIA",
            title="Telescopio detecta señal en órbita",
            composition_id="Editorial25DFactSheet",
        )
        self.assertNotIn("$4.2B", json.dumps(props_space))
        self.assertNotIn("VERITASIUM", json.dumps(props_space).upper())
        self.assertNotIn("35,000", json.dumps(props_space))

        self.assertEqual(remotion_renderer.get_composition_for_genre("G3_IA_ROBOTICA"), "Editorial25DDiagram")
        props_ai = remotion_renderer.build_category_props(
            "G3_IA_ROBOTICA",
            title="Nuevo chip autónomo",
            composition_id="Editorial25DDiagram",
        )
        self.assertEqual(props_ai["diagramKind"], "chip")

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
            # CapCutBouncing MarginV=560 & MarginR=170 (Safe Zone derecha); sin HookPill invasivo
            self.assertIn(",65,170,560,1", content)
            self.assertNotIn("HookPill", content)
            self.assertNotIn("ÚLTIMA HORA", content)
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
            composition_id="Editorial25DDiagram",
            extra_props={**metrics_av, "diagramKind": "chip"},
        )
        self.assertEqual(props_chip["diagramKind"], "chip")
        self.assertNotIn("flightNumber", props_chip)

        props_fact = remotion_renderer.build_category_props(
            "G3_IA_HARDWARE",
            title="Nuevo procesador TSMC 2nm supera el 40%",
            composition_id="Editorial25DFactSheet",
            extra_props={"nodeSize": "2 NM"},
        )
        self.assertEqual(props_fact["mode"], "metric")
        self.assertEqual(props_fact["heroValue"], "2 NM")

    def test_geo_resolver_and_story_aware_prompts_avoid_recycled_florida_boats(self):
        import editorial_director

        geo_div = editorial_director.resolve_geo_context(
            "Un Airbus A350 de Thai Airways volando de Múnich a Bangkok se desvía de emergencia a Nueva Delhi.",
            "G1_AVIACION",
        )
        self.assertTrue(geo_div["has_geo"])
        self.assertEqual(geo_div["mapMode"], "diversion")
        self.assertEqual(geo_div["origin"]["code"], "MUC")
        self.assertEqual(geo_div["plannedDest"]["code"], "BKK")
        self.assertEqual(geo_div["diversionDest"]["code"], "DEL")

        geo_none = editorial_director.resolve_geo_context(
            "Nuevo algoritmo de compresión reduce el consumo energético de centros de datos.",
            "G3_IA_HARDWARE",
        )
        self.assertFalse(geo_none["has_geo"])

        shots = pipeline_autonomo.build_shot_prompts(
            is_aviation=True,
            title="Thai Airways Airbus A350 flight TG925 from Munich to Bangkok diverts safely to New Delhi",
            summary="Precautionary diversion with safe runway landing.",
            genre_label="G1_AVIACION",
        )
        joined = json.dumps(shots, ensure_ascii=False).lower()
        self.assertIn("airbus a350", joined)
        self.assertNotIn("florida", joined)
        self.assertNotIn("rescue boats", joined)
        self.assertNotIn("twin-engine private jet", joined)
        self.assertNotIn("veritasium", joined)

    def test_dynamic_story_visuals_gemini_merges_into_storyboard(self):
        import io
        long_script = " ".join([f"palabra{i}." if i % 14 == 0 else f"palabra{i}" for i in range(1, 141)])
        mock_visuals = {
            "flow_shots": {
                "SH02": {
                    "action": "Airbus A350 sobre nubes al atardecer",
                    "visual_en": "Airbus A350 widebody cruising over warm dusk clouds",
                    "fallback_en": "Commercial airliner over dusk clouds",
                }
            },
            "editorial_graphics": {
                "SH01": {
                    "has_geo": True,
                    "mapMode": "diversion",
                    "kicker": "CORREDOR AÉREO",
                    "headline": "DESVÍO PREVENTIVO DEL VUELO TG925",
                    "origin": {"name": "MÚNICH", "code": "MUC", "lon": 11.582, "lat": 48.135},
                    "plannedDest": {"name": "BANGKOK", "code": "BKK", "lon": 100.502, "lat": 13.756},
                    "diversionDest": {"name": "NUEVA DELHI", "code": "DEL", "lon": 77.209, "lat": 28.614},
                    "highlightCountries": ["Germany", "India", "Thailand"],
                    "stampText": "DESVÍO EN VUELO",
                    "cardKicker": "THAI AIRWAYS",
                    "cardHeadline": "VUELO TG925 · A350",
                    "cardLines": ["RUTA MÚNICH A BANGKOK", "ATERRIZAJE SEGURO EN DELHI"],
                },
                "SH10": {
                    "diagramKind": "aircraft",
                    "headline": "¿POR QUÉ DESVIAR ANTES DE UN FALLO?",
                },
            },
        }
        payload = json.dumps({"candidates": [{"content": {"parts": [{"text": json.dumps(mock_visuals)}]}}]}).encode("utf-8")
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}), \
             mock.patch.object(pipeline_autonomo, "generate_dynamic_news_script", return_value=long_script), \
             mock.patch("urllib.request.urlopen", return_value=io.BytesIO(payload)):
            sb = pipeline_autonomo.generate_monetizable_storyboard({
                "title": "Thai Airways A350 TG925 Munich to Bangkok diverts to New Delhi",
                "source_name": "Aviation24 Global",
                "link": "https://example.com/tg925",
                "genre": "G1_AVIACION_CATASTROFES",
            })
        sh02 = next(s for s in sb["shots"] if s["id"] == "SH02")
        sh01 = next(s for s in sb["shots"] if s["id"] == "SH01")
        self.assertIn("Airbus A350 widebody cruising", sh02["prompt"])
        self.assertEqual(sh01["remotion_props"]["headline"], "DESVÍO PREVENTIVO DEL VUELO TG925")
        self.assertEqual(sh01["remotion_props"]["diversionDest"]["code"], "DEL")

    def test_remotion_batch_worker_payload_and_crf(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_mp4 = Path(tmp) / "SH01.mp4"

            def fake_run(cmd, **kwargs):
                batch_json = Path(cmd[2])
                data = json.loads(batch_json.read_text(encoding="utf-8"))
                self.assertEqual(data["jobs"][0]["crf"], 14)
                self.assertEqual(data["jobs"][0]["compositionId"], "Editorial25DFactSheet")
                out_mp4.write_bytes(b"0" * 15_000)
                return mock.Mock(returncode=0, stdout="[REMOTION-BATCH] ✅ SH01.mp4")

            with mock.patch("subprocess.run", side_effect=fake_run):
                res = remotion_renderer.render_remotion_batch([{
                    "compositionId": "Editorial25DFactSheet",
                    "outputLocation": str(out_mp4),
                    "inputProps": {"headline": "TEST"},
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
                 mock.patch.object(flow_generator, "generate_story_style_anchor", return_value=None), \
                 mock.patch.object(flow_generator, "verify_mp4", side_effect=fake_verify), \
                 mock.patch.object(flow_generator, "_run_single_profile_session", side_effect=fake_session), \
                 mock.patch("asyncio.sleep", new=mock.AsyncMock()):
                ok = flow_generator.asyncio.run(flow_generator.run_flow_generator(delivery))

            self.assertTrue(ok)
            self.assertEqual(calls, [("p1", ["SH02", "SH04"]), ("p2", ["SH04"])])
            st = flow_generator.load_flow_profile_state(state_file)
            self.assertEqual(st[str(p1.resolve())]["reason"], "quota_exhausted")
            self.assertEqual(st[str(p2.resolve())]["reason"], "ok")

    def test_flow_tile_detection_handles_identical_play_circle_text_and_credit_prompts(self):
        before = [
            {
                "idx": 0,
                "isGridTile": True,
                "isGenerating": False,
                "isReady": True,
                "isError": False,
                "videoSrc": "",
                "imgSrc": "https://flow.google.com/asb/OLD_TILE",
                "ariaLabel": "Artificial horizon indicator",
                "imgAlt": "Miniatura de video generada",
                "preview": "play_circle",
            },
            {
                "idx": 1,
                "isGridTile": False,
                "isGenerating": False,
                "isReady": True,
                "isError": False,
                "videoSrc": "",
                "imgSrc": "https://storage.googleapis.com/ai-sandbox-videofx/image/OLD_CHAT",
                "ariaLabel": "Galería de opciones de contenido multimedia",
                "imgAlt": "Prompt viejo",
                "preview": "play_circle",
            },
        ]
        current = [
            {
                "idx": 0,
                "isGridTile": True,
                "isGenerating": False,
                "isReady": True,
                "isError": False,
                "videoSrc": "",
                "imgSrc": "https://flow.google.com/asb/NEW_SH07_TILE",
                "ariaLabel": "Twin-engine jet descending",
                "imgAlt": "Miniatura de video generada",
                "preview": "play_circle",
            },
            *[{**t, "idx": t["idx"] + 1} for t in before],
            {
                "idx": 3,
                "isGridTile": False,
                "isGenerating": False,
                "isReady": True,
                "isError": False,
                "videoSrc": "",
                "imgSrc": "https://storage.googleapis.com/ai-sandbox-videofx/image/NEW_CHAT",
                "ariaLabel": "Galería de opciones de contenido multimedia",
                "imgAlt": "Prompt nuevo",
                "preview": "play_circle",
            },
        ]
        new_tiles = flow_generator._select_new_or_changed_tiles(before, current)
        self.assertEqual([t["idx"] for t in new_tiles], [0, 3])
        self.assertEqual(flow_generator._pick_ready_tile_idx(new_tiles, current), 0)

        # Even if two tiles had identical empty signatures, multiplicity still exposes the excess tile
        dup_before = [{"idx": 0, "isGridTile": True, "isGenerating": False, "isReady": True, "isError": False, "videoSrc": "", "imgSrc": "", "ariaLabel": "", "imgAlt": "", "preview": "play_circle"}]
        dup_current = [
            {"idx": 0, "isGridTile": True, "isGenerating": False, "isReady": True, "isError": False, "videoSrc": "", "imgSrc": "", "ariaLabel": "", "imgAlt": "", "preview": "play_circle"},
            {"idx": 1, "isGridTile": True, "isGenerating": False, "isReady": True, "isError": False, "videoSrc": "", "imgSrc": "", "ariaLabel": "", "imgAlt": "", "preview": "play_circle"},
        ]
        dup_new = flow_generator._select_new_or_changed_tiles(dup_before, dup_current)
        self.assertEqual(len(dup_new), 1)
        self.assertEqual(flow_generator._pick_ready_tile_idx(dup_new, dup_current), 0)

        self.assertEqual(
            flow_generator.classify_flow_body_status(
                "Generating this video requires 7 credits, but you currently have 3 credits remaining (refreshes on 2026-11-29 19:44 UTC)."
            ),
            "quota_limit",
        )
        self.assertEqual(
            flow_generator.classify_flow_body_status("Upgrade / Top up credits\nWait for credits to refresh"),
            "quota_limit",
        )
        self.assertIsNone(
            flow_generator.classify_flow_body_status("Te quedan pocos puntos de Google Flow. Tus puntos se restablecerán cada mes.")
        )

    def test_generate_kinetic_ass_silencedetect_avoids_one_frame_flashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            voice = d / "voice.mp3"
            voice.write_bytes(b"fake")
            ass_path = d / "SUBTITULOS_KINETIC.ass"
            script = " ".join([f"palabra{i}" for i in range(1, 31)])
            fake_blocks = [(0.10, 4.02), (4.50, 8.95), (9.45, 14.00)]
            with mock.patch.object(ensamblador_final, "extract_acoustic_speech_blocks", return_value=fake_blocks):
                ensamblador_final.generate_kinetic_ass(
                    script,
                    total_duration=14.2,
                    ass_path=ass_path,
                    source_name="Aviation24",
                    voice_audio=voice,
                )
            lines = [ln for ln in ass_path.read_text(encoding="utf-8").splitlines() if "CapCutBouncing" in ln and ln.startswith("Dialogue:")]
            self.assertGreaterEqual(len(lines), 10)
            def _to_sec(ts: str) -> float:
                h, m, s = ts.split(":")
                return int(h) * 3600 + int(m) * 60 + float(s)
            for ln in lines:
                parts = ln.split(",", 4)
                dur = _to_sec(parts[2]) - _to_sec(parts[1])
                self.assertGreaterEqual(dur, 0.30, f"Subtitle flash too short: {ln}")

    def test_costa_rican_locucion_config_and_active_loop_tts(self):
        import asyncio
        cfg = json.loads((TOOLS_DIR.parent / "config_produccion.json").read_text(encoding="utf-8"))
        loc = cfg["locucion"]
        self.assertEqual(loc["motor_principal"], "edge_tts")
        self.assertEqual(loc["voz_edge"], "es-CR-JuanNeural")
        self.assertEqual(loc["rate_edge"], "-4%")
        self.assertEqual(loc["pitch_edge"], "+0Hz")
        self.assertFalse(loc["tighten_silencios"])

        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            out_mp3 = d / "LOCUCION_NOTICIERO_62S.mp3"
            stale_wb = d / "WORD_BOUNDARIES.json"
            stale_wb.write_text('[{"text":"viejo","start":0,"end":1}]', encoding="utf-8")
            calls = []

            async def fake_edge(text, output_path, voice="es-CR-JuanNeural", rate="-4%", pitch="+0Hz"):
                calls.append((voice, rate, pitch))
                audio_generator._clear_stale_boundaries(output_path)
                output_path.write_bytes(b"mp3")
                (output_path.parent / "WORD_BOUNDARIES.json").write_text("[]", encoding="utf-8")
                return True

            async def call_from_loop():
                return await pipeline_autonomo.synthesize_voiceover("Texto de prueba tico.", out_mp3)

            with mock.patch.object(audio_generator, "_generate_speech_edge_async", side_effect=fake_edge), \
                 mock.patch.object(audio_generator, "generate_speech_gemini") as m_gem, \
                 mock.patch.object(audio_generator, "tighten_audio_dead_air") as m_tight, \
                 mock.patch.object(audio_generator, "probe_duration", return_value=62.5), \
                 mock.patch.object(pipeline_autonomo, "probe_duration", return_value=62.5):
                dur = asyncio.run(call_from_loop())

            self.assertEqual(dur, 62.5)
            self.assertEqual(calls, [("es-CR-JuanNeural", "-4%", "+0Hz")])
            m_gem.assert_not_called()
            m_tight.assert_not_called()
            self.assertEqual(stale_wb.read_text(encoding="utf-8"), "[]")

            # Si Edge-TTS falla, cae automáticamente a Gemini con dirección costarricense
            with mock.patch.object(audio_generator, "_generate_speech_edge_async", return_value=False), \
                 mock.patch.object(audio_generator, "generate_speech_gemini", return_value=True) as m_gem_fb, \
                 mock.patch.object(audio_generator, "probe_duration", return_value=62.1), \
                 mock.patch.object(audio_generator, "extract_word_boundaries_whisper"):
                (d / "WORD_BOUNDARIES.json").unlink(missing_ok=True)
                dur_fb = audio_generator.generate_speech("Texto fallback.", out_mp3)
            self.assertEqual(dur_fb, 62.1)
            m_gem_fb.assert_called_once()
            self.assertEqual(m_gem_fb.call_args.kwargs["voice"], "Orus")
            self.assertIn("costarricense", m_gem_fb.call_args.kwargs["style"].lower())

    def test_generate_dynamic_news_script_condenses_overlong_output(self):
        import io
        long_text = " ".join([f"palabra{i}" for i in range(185)])
        condensed_text = " ".join([f"palabra{i}" for i in range(136)])
        responses = [
            io.BytesIO(json.dumps({"candidates": [{"content": {"parts": [{"text": long_text}]}}]}).encode("utf-8")),
            io.BytesIO(json.dumps({"candidates": [{"content": {"parts": [{"text": condensed_text}]}}]}).encode("utf-8")),
        ]
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}), \
             mock.patch("urllib.request.urlopen", side_effect=responses) as m_open:
            out = pipeline_autonomo.generate_dynamic_news_script(
                {"title": "Prueba vuelo TG925", "source_name": "Aviation24", "summary": "Alerta en cabina."},
                "G1_AVIACION",
            )
        self.assertEqual(m_open.call_count, 2)
        self.assertEqual(len(out.split()), 136)


class TestVeritasiumBroadcastUpgrade(unittest.TestCase):
    def test_news_radar_extracts_html_text_and_verified_receipt_facts(self):
        html_doc = """
        <html><body>
          <nav>Inicio | Suscríbete ahora | Cookies</nav>
          <script>var secret = "ignore me";</script>
          <article>
            <p>Boeing 787 flight BA117 carrying 242 passengers diverted to Reykjavik after sensors reported a 35% hydraulic pressure drop.</p>
            <p>FAA investigators confirmed the precautionary diversion occurred due to a faulty bypass valve seal in the right manifold.</p>
          </article>
          <footer>Copyright 2026</footer>
        </body></html>
        """
        extracted = news_radar.extract_article_text_from_html(html_doc, max_chars=2000)
        self.assertNotIn("Suscríbete", extracted)
        self.assertNotIn("ignore me", extracted)
        self.assertIn("242 passengers", extracted)
        self.assertIn("faulty bypass valve seal", extracted)

        facts = news_radar.extract_verified_receipt_facts(
            extracted,
            title="Boeing 787 flight BA117 diverts over hydraulic alert",
            source="AeroTime",
        )
        self.assertTrue(any("242" in n or "35%" in n or "Boeing 787" in n for n in facts["numbers"]))
        self.assertTrue(facts["receipt_quote"])
        self.assertTrue(facts["highlight_phrase"])
        self.assertIn(facts["highlight_phrase"].lower(), facts["receipt_quote"].lower())

    def test_veritasium_beat_sheet_and_audio_first_alignment(self):
        import editorial_director

        sentences = [
            "Todos asumimos que perder un sensor obliga al piloto a aterrizar de inmediato.",
            "En realidad, el Boeing 787 del vuelo BA117 siguió volando con total control manual.",
            "Según AeroTime, los 242 pasajeros cruzaban el Atlántico cuando cayó la presión hidráulica.",
            "El sistema derecho perdió 35% de presión en pleno ascenso sobre el océano.",
            "Pero los ingenieros diseñan tres circuitos hidráulicos independientes desde el principio.",
            "Cada circuito alimenta superficies de control críticas sin compartir el mismo fluido.",
            "Cuando una válvula falla, una compuerta mecánica aísla la fuga en milisegundos.",
            "Así evita que una sola pérdida vacíe el resto de los acumuladores del avión.",
            "Sin embargo, las listas de verificación prohíben ignorar una degradación múltiple.",
            "Si aparece una segunda anomalía en ruta oceánica, el margen legal cambia por completo.",
            "Ahí está el verdadero motivo del desvío: no fue pánico, fue redundancia preventiva.",
            "Incluso con dos sistemas sanos, cruzar sin alternativa cercana reduce el margen de seguridad.",
            "Por eso el comandante viró hacia Islandia aunque la cabina mostraba estabilidad total.",
            "Los reportes de la FAA confirman que la válvula de desvío activó el aviso preventivo.",
            "Ese equilibrio entre autonomía y prudencia separa un susto de una emergencia real.",
            "Cuando un sistema complejo avisa antes del fallo, ese desvío en calma es el diseño funcionando.",
        ]
        script = " ".join(sentences)
        shots = [{"id": f"SH{i:02d}", "shot_type": "Escena"} for i in range(1, 14)]
        beats = editorial_director.build_narrative_beat_sheet(script, shots, genre_label="AVIACIÓN")

        self.assertGreaterEqual(len(beats), 14)
        self.assertLessEqual(len(beats), 20)
        hard_cuts = sum(1 for b in beats[1:] if b.get("transition_in") == "cut")
        self.assertGreaterEqual(hard_cuts / max(1, len(beats) - 1), 0.75)
        for idx in range(1, len(beats)):
            if beats[idx]["transition_in"] == "dissolve":
                self.assertNotEqual(beats[idx]["act"], beats[idx - 1]["act"])
        self.assertEqual(sum(1 for b in beats if b.get("music_drop")), 1)
        self.assertTrue(any(b.get("variant") == "punch_in" for b in beats))

        words = script.split()
        total_dur = 64.0
        dt = total_dur / len(words)
        wb = [
            {"text": w, "start": round(i * dt, 3), "end": round((i + 1) * dt - 0.01, 3)}
            for i, w in enumerate(words)
        ]
        aligned = ensamblador_final.align_beats_to_audio(beats, wb, [], total_dur, script=script)
        self.assertEqual(len(aligned), len(beats))
        self.assertLessEqual(max(b["sync_delta_sec"] for b in aligned), 0.15)
        self.assertAlmostEqual(aligned[-1]["end_sec"], total_dur, places=2)

    def test_music_drop_window_attenuates_music_at_least_20db(self):
        import math
        import shutil
        import struct
        import subprocess
        import wave

        if shutil.which("ffmpeg") is None:
            self.skipTest("ffmpeg no disponible")

        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            voice_wav = d / "voice_ref.wav"
            sr = 48000
            total_dur = 7.5
            n_samples = int(sr * total_dur)
            # Pulso de referencia breve solo al inicio (0.15-0.35s) y silencio después para medir la caída limpia de música
            with wave.open(str(voice_wav), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                frames = bytearray()
                for i in range(n_samples):
                    t = i / sr
                    val = int(12000 * math.sin(2.0 * math.pi * 440.0 * t)) if (0.15 <= t <= 0.35) else 0
                    frames.extend(struct.pack("<h", val))
                wf.writeframes(bytes(frames))

            master_m4a = d / "master.m4a"
            ensamblador_final.synthesize_broadcast_audio_master(
                voice_mp3=voice_wav,
                total_dur=total_dur,
                transition_times=[],
                master_m4a=master_m4a,
                genre="G1",
                sfx_events=[],
                music_drop_window=(2.6, 5.4),
            )
            self.assertTrue(master_m4a.exists())

            decoded_wav = d / "decoded.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(master_m4a), "-ac", "1", "-ar", "48000", str(decoded_wav)],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            with wave.open(str(decoded_wav), "rb") as wf:
                raw = wf.readframes(wf.getnframes())
            samples = struct.unpack(f"<{len(raw) // 2}h", raw)

            def rms_db(t0: float, t1: float) -> float:
                seg = samples[int(t0 * sr):int(t1 * sr)]
                mean_sq = sum(s * s for s in seg) / max(1, len(seg))
                return 10.0 * math.log10(max(1e-12, mean_sq / (32768.0 ** 2)))

            normal_db = rms_db(0.9, 2.2)
            drop_db = rms_db(3.1, 4.9)
            self.assertGreaterEqual(normal_db - drop_db, 20.0)

    def test_editorial_receipt_routing_and_factsheet_no_fake_ratios(self):
        comp_receipt = remotion_renderer.get_composition_for_shot(
            genre="G1", shot_id="SH03", shot_type="Recibo Documental 2.5D", has_geo=True, has_receipt=True
        )
        self.assertEqual(comp_receipt, "Editorial25DReceipt")

        receipt_props = remotion_renderer.build_category_props(
            genre="G1",
            title="Vuelo BA117 desviado a Islandia",
            subtitle="Alerta de sensor hidráulico confirmada",
            duration_frames=108,
            composition_id="Editorial25DReceipt",
            extra_props={
                "sourceName": "AeroTime",
                "receiptQuote": "El sensor reportó caída de presión en el circuito hidráulico derecho.",
                "highlightPhrase": "presión en el circuito hidráulico",
                "keyMetricBadge": "35% PRESIÓN",
            },
        )
        self.assertEqual(receipt_props["sourceName"], "AeroTime")
        self.assertIn("presión", receipt_props["highlightPhrase"].lower())

        fact_props = remotion_renderer.build_category_props(
            genre="G2",
            title="Incidente en nodo de red",
            subtitle="Aislamiento preventivo confirmado",
            duration_frames=108,
            composition_id="Editorial25DFactSheet",
        )
        self.assertNotIn("leftRatio", fact_props)
        self.assertNotIn("rightRatio", fact_props)
        tsx_src = (
            Path(__file__).resolve().parent.parent / "motion_engine" / "src" / "Editorial25DFactSheet.tsx"
        ).read_text(encoding="utf-8")
        self.assertIn("hasNumericPair", tsx_src)

    def test_minimalist_cover_and_elevenlabs_timestamps_mocked(self):
        from PIL import Image, ImageDraw

        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "metadata.json").write_text(json.dumps({
                "title": "El fallo silencioso que obligó a desviar un Boeing 787",
                "genre": "G1",
                "source": "AeroTime",
            }), encoding="utf-8")
            drawn_texts = []
            orig_draw_text = ImageDraw.ImageDraw.text

            def spy_text(self_draw, xy, text, *args, **kwargs):
                drawn_texts.append(str(text))
                return orig_draw_text(self_draw, xy, text, *args, **kwargs)

            dark_bg = Image.new("RGBA", (1080, 1920), (14, 18, 28, 255))
            with mock.patch.object(generador_portada, "generate_ai_cover_background", return_value=dark_bg), \
                 mock.patch.object(ImageDraw.ImageDraw, "text", spy_text):
                out_cover = generador_portada.generate_tiktok_cover(d)

            self.assertTrue(out_cover.exists())
            joined = " | ".join(drawn_texts).upper()
            self.assertNotIn("INFORME EN 60S", joined)
            self.assertNotIn("FUENTE ·", joined)
            self.assertNotIn("ÚLTIMA HORA", joined)

            # ElevenLabs /with-timestamps mockeado -> WORD_BOUNDARIES.json y SENTENCE_BOUNDARIES.json
            import base64
            text_tts = "Hola mundo."
            chars = list(text_tts)
            starts = [round(i * 0.12, 3) for i in range(len(chars))]
            ends = [round(i * 0.12 + 0.10, 3) for i in range(len(chars))]
            fake_resp = {
                "audio_base64": base64.b64encode(b"\xff\xfb\x90\x00" * 260).decode("ascii"),
                "alignment": {
                    "characters": chars,
                    "character_start_times_seconds": starts,
                    "character_end_times_seconds": ends,
                },
            }

            class FakeCtxResp:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

            out_mp3 = d / "LOCUCION_VOZ.mp3"
            with mock.patch.object(audio_generator.urllib.request, "urlopen", return_value=FakeCtxResp()), \
                 mock.patch.object(audio_generator.json, "load", return_value=fake_resp):
                ok = audio_generator.generate_speech_elevenlabs(
                    text_tts, out_mp3, voice_id="voice123", api_key="test-key"
                )
            self.assertTrue(ok)
            wb = json.loads((d / "WORD_BOUNDARIES.json").read_text(encoding="utf-8"))
            sb = json.loads((d / "SENTENCE_BOUNDARIES.json").read_text(encoding="utf-8"))
            self.assertEqual([w["text"] for w in wb], ["Hola", "mundo."])
            self.assertEqual(len(sb), 1)

    def test_flow_style_anchor_reuse_and_attach_reference_mocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            portada_ai = d / "PORTADA_AI_BASE.jpg"
            portada_ai.write_bytes(b"\xff\xd8\xff" + b"\x00" * 30_000)

            anchor = flow_generator.generate_story_style_anchor(d, "Título prueba", "G1")
            self.assertIsNotNone(anchor)
            self.assertTrue(anchor.exists())
            self.assertEqual(anchor.name, "FLOW_STYLE_ANCHOR.jpg")

            fake_input = mock.MagicMock()
            fake_input.count = mock.AsyncMock(return_value=1)
            fake_input.set_input_files = mock.AsyncMock()
            fake_page = mock.MagicMock()
            fake_locator = mock.MagicMock()
            fake_locator.first = fake_input
            fake_page.locator = mock.MagicMock(return_value=fake_locator)

            with mock.patch("asyncio.sleep", new=mock.AsyncMock()):
                attached = flow_generator.asyncio.run(flow_generator.attach_reference_image_to_flow(fake_page, anchor))
            self.assertTrue(attached)
            fake_input.set_input_files.assert_awaited_once_with(str(anchor))


if __name__ == "__main__":
    unittest.main(verbosity=2)
