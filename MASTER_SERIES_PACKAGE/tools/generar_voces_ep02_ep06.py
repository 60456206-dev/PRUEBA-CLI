#!/usr/bin/env python3
"""Genera las voces TTS para EP02 a EP06 con registro persistente."""
import base64
import io
import json
import os
import shutil
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "AUDIO"

EPISODE_LINES = {
    "EP02": [
        ("L01", "INES", "Kore", "Mara. ¿Me oyes?", "Voz baja, contenida, tensa, esperando respuesta.", 2.5, "00:00.5–00:03.0"),
        ("L02", "ALBA", "Gacrux", "No vuelve. Ya no está.", "Grave, cansada, resignada pero firme, sin sollozar.", 3.0, "00:06.0–00:09.0"),
        ("L03", "MARA", "Vindemiatrix", "<breath> Son las seis y diez. Han cerrado. Seguimos aquí.", "Susurro cercano, respiración contenida, urgencia fría desde la tela.", 5.0, "00:18.0–00:23.0"),
        ("L04", "MARA", "Vindemiatrix", "REUSE:L03", "Misma toma L03 reproducida por altavoz de grabadora.", 5.0, "00:32.0–00:37.0"),
        ("L05", "INES", "Kore", "La tela se calla. La grabación no.", "Firme, analítica, contenida, voz baja.", 3.5, "00:38.5–00:42.0"),
        ("L06", "INES", "Kore", "Aquí pone que a las seis ya no quedaba nadie.", "Tensa, descubriendo la contradicción en el acta, voz contenida.", 5.0, "00:45.0–00:50.0"),
    ],
    "EP03": [
        ("L01", "INES", "Kore", "¿Por qué guardabas la llave de la compuerta?", "Directa, contenida, exigiendo una respuesta sin gritar.", 4.0, "00:06.0–00:10.0"),
        ("L02", "ALBA", "Gacrux", "Yo llevaba las llaves. Eso ya lo sabes.", "Seca, defensiva, voz grave y cansada.", 3.5, "00:12.5–00:16.0"),
        ("L03", "ALBA", "Gacrux", "No busques solo mi nombre.", "Advertencia grave, baja, contenida.", 3.0, "00:19.0–00:22.0"),
        ("L04", "MARA", "Vindemiatrix", "<breath> Mamá. Te oigo al otro lado. Abre.", "Susurro cercano, tenso, súplica contenida sin histeria.", 5.0, "00:32.0–00:37.0"),
        ("L05", "INES", "Kore", "La oíste.", "Voz muy baja, helada, certeza dolorosa.", 2.5, "00:46.0–00:49.0"),
        ("L06", "INES", "Kore", "Y no abriste.", "Seca, sentencia contenida, sin gritar.", 2.0, "00:50.0–00:52.0"),
    ],
    "EP04": [
        ("L01", "ALBA", "Gacrux", "El agua iba hacia la sala norte. Tú estabas allí.", "Grave, confesión cansada y contenida, peso de años.", 5.5, "00:05.5–00:11.5"),
        ("L02", "ALBA", "Gacrux", "Cerré para que no te alcanzara.", "Voz baja, firmeza dolorosa, sin sollozar.", 4.0, "00:13.5–00:18.0"),
        ("L03", "INES", "Kore", "¿Sabías que Mara seguía dentro?", "Temblor contenido, directa, voz baja.", 4.0, "00:21.0–00:25.0"),
        ("L04", "ALBA", "Gacrux", "Sí.", "Una sola palabra, grave, seca, honesta.", 1.2, "00:29.0–00:30.0"),
        ("L05", "ALBA", "Gacrux", "No podía perderos a las dos.", "Cansada, vulnerabilidad contenida, voz grave.", 3.0, "00:34.0–00:37.0"),
        ("L06", "INES", "Kore", "La perdiste tú. A mí me mentiste.", "Dura, herida, firme, voz baja sin gritar.", 2.5, "00:38.0–00:40.0"),
        ("L07", "ALBA", "Gacrux", "Yo cerré la puerta. Tú firmaste que no quedaba nadie.", "Grave, devolviendo la verdad compartida, sin crueldad.", 5.0, "00:48.0–00:53.0"),
    ],
    "EP05": [
        ("L01", "INES", "Kore", "Me dijiste que habías comprobado.", "Voz baja, mirando el documento, reproche contenido.", 2.5, "00:00.5–00:03.0"),
        ("L02", "INES", "Kore", "Y yo firmé. Sin mirar. Me acuerdo.", "Asumiendo su culpa, pausada, voz baja y clara.", 4.5, "00:05.5–00:10.5"),
        ("L03", "ALBA", "Gacrux", "Puedes mandar solo la grabación.", "Voz baja, intentando protegerla por última vez.", 3.0, "00:13.0–00:16.0"),
        ("L04", "MARA", "Vindemiatrix", "<breath> Somos siete. Si alguien oye esto, que no quite a ninguno.", "Susurro cercano y firme desde la tela, solemnidad serena.", 5.5, "00:31.5–00:37.0"),
        ("L05", "INES", "Kore", "La página entera. Y mi nombre.", "Decisión firme, serena, definitiva.", 3.0, "00:40.0–00:43.0"),
        ("L06", "MARA", "Vindemiatrix", "<breath> Voy a decir los nombres.", "Susurro cercano, respiración leve, preparación final.", 3.0, "00:46.0–00:49.0"),
    ],
    "EP06": [
        ("L01", "MARA", "Vindemiatrix", "<breath> Elena Ríos. Tomás Vera. Luz Arce. Bruno Sol.", "Susurro pausado, claro, nombrando a cada persona con dignidad.", 5.8, "00:00.5–00:06.5"),
        ("L02", "MARA", "Vindemiatrix", "Celia Paz. Samuel Costa. Y yo, Mara Vidal.", "Susurro sereno, cerrando la lista con calma definitiva.", 5.2, "00:08.5–00:14.0"),
        ("L03", "INES", "Kore", "Firmé sin comprobar. Adjuntaré mi declaración.", "Firme, oficial, asumiendo responsabilidad completa.", 4.2, "00:15.5–00:20.0"),
        ("L04", "INES", "Kore", "No voy a quitar tu nombre.", "Serena, directa hacia su madre, sin rencor.", 3.0, "00:22.0–00:25.0"),
        ("L05", "ALBA", "Gacrux", "Deja el mío también. ¿Puedo quedarme?", "Grave, aceptando su responsabilidad, humilde al final.", 4.0, "00:34.0–00:38.0"),
        ("L06", "MARA", "Vindemiatrix", "Y yo, Mara Vidal.", "Susurro sereno para reproducción en grabadora, claro y breve.", 3.0, "00:40.5–00:44.0"),
        ("L07", "INES", "Kore", "Si no apagas eso.", "Voz baja, cierre contenido y sobrio.", 2.2, "00:46.5–00:49.0"),
    ],
}

MODELS = ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts"]


def write_guion_md(ep: str, lines: list) -> None:
    ep_dir = AUDIO_DIR / ep
    ep_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for lid, person, voice, txt, style, secs, window in lines:
        disp_txt = txt.replace("<breath> ", "")
        rows.append(f"| {lid} | {window} | {person} ({voice}) | {disp_txt} | {style} |")
    content = (
        f"# {ep} · Guion de voces para TTS (Gemini TTS)\n\n"
        "Fuente: `AUDIO_TIMELINE.md`, `04_CHARACTER_BIBLE.md` y guion del episodio.\n"
        f"Formato de archivo: `{ep}_<PERSONAJE>_L<nn>_T<toma>.wav`.\n\n"
        "## Líneas\n"
        "| # | Ventana | Personaje | Texto | Dirección |\n"
        "|---|---|---|---|---|\n"
        + "\n".join(rows)
        + "\n"
    )
    (ep_dir / f"{ep}_GUION_VOCES_TTS.md").write_text(content, encoding="utf-8")


def generate_all() -> None:
    key = os.environ["GEMINI_API_KEY"]
    req_idx = 0

    for ep, lines in EPISODE_LINES.items():
        ep_dir = AUDIO_DIR / ep
        for sub in ("TAKES", "EDITADOS", "STEMS", "AJUSTE_V2"):
            (ep_dir / sub).mkdir(parents=True, exist_ok=True)
        write_guion_md(ep, lines)

        log_path = ep_dir / "generacion.json"
        records = json.loads(log_path.read_text()) if log_path.exists() else []

        for lid, person, voice, txt, style, secs, _window in lines:
            existing = [r for r in records if r["id"] == lid and r.get("file") and (ep_dir / r["file"]).exists()]
            if existing:
                print(f"[{ep} {lid}] Already exists: {existing[0]['file']}", flush=True)
                continue

            if txt.startswith("REUSE:"):
                ref_id = txt.split(":")[1]
                ref_rec = next(r for r in records if r["id"] == ref_id and r.get("file"))
                src_wav = ep_dir / ref_rec["file"]
                dst_wav = ep_dir / "TAKES" / f"{ep}_{person}_{lid}_T1.wav"
                shutil.copy2(src_wav, dst_wav)
                record = {
                    "id": lid,
                    "take": 1,
                    "model": "reuse_source:" + ref_id,
                    "voice": voice,
                    "text": ref_rec["text"],
                    "style": style,
                    "target_seconds": secs,
                    "seconds": ref_rec["seconds"],
                    "file": str(dst_wav.relative_to(ep_dir)),
                    "status": "reused_from_" + ref_id,
                }
                records.append(record)
                log_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
                print(f"[{ep} {lid}] Reused from {ref_id} ({record['seconds']:.2f}s)", flush=True)
                continue

            for attempt in range(1, 4):
                model = MODELS[req_idx % len(MODELS)]
                req_idx += 1
                record = {
                    "id": lid,
                    "take": attempt,
                    "model": model,
                    "voice": voice,
                    "text": txt,
                    "style": style,
                    "target_seconds": secs,
                    "status": "requested",
                }
                body = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": txt,
                                    "speech_metadata": {
                                        "style": f"{style} Interpretación cinematográfica natural en español neutro, sin música. Duración aproximada {secs} segundos."
                                    },
                                }
                            ],
                        }
                    ],
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {"voiceConfig": {"voice": voice}},
                    },
                }
                req = urllib.request.Request(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    data=json.dumps(body).encode("utf-8"),
                    headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                )
                try:
                    with urllib.request.urlopen(req, timeout=100) as resp:
                        data = json.load(resp)
                    parts = data["candidates"][0]["content"]["parts"]
                    inline = next(p["inlineData"] for p in parts if "inlineData" in p)
                    raw = base64.b64decode(inline["data"])
                    if raw[:4] != b"RIFF":
                        buf = io.BytesIO()
                        with wave.open(buf, "wb") as w:
                            w.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
                            w.writeframes(raw)
                        raw = buf.getvalue()
                    with wave.open(io.BytesIO(raw)) as w:
                        dur_s = w.getnframes() / w.getframerate()
                    out_wav = ep_dir / "TAKES" / f"{ep}_{person}_{lid}_T{attempt}.wav"
                    out_wav.write_bytes(raw)
                    record.update(
                        seconds=round(dur_s, 3),
                        file=str(out_wav.relative_to(ep_dir)),
                        status="generated_technical_review_pending",
                    )
                    records.append(record)
                    log_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
                    print(f"[{ep} {lid}] OK ({model}) -> {dur_s:.2f}s", flush=True)
                    time.sleep(11)
                    break
                except urllib.error.HTTPError as e:
                    err_body = e.read().decode("utf-8", errors="replace").replace(key, "[REDACTED]")
                    record.update(status="http_error", http=e.code, error=err_body[:300])
                    records.append(record)
                    log_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
                    print(f"[{ep} {lid}] HTTP {e.code} on {model}, waiting 25s...", flush=True)
                    time.sleep(25)
                except Exception as e:
                    record.update(status="error", error=type(e).__name__)
                    records.append(record)
                    log_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
                    print(f"[{ep} {lid}] ERR {type(e).__name__}, waiting 15s...", flush=True)
                    time.sleep(15)


if __name__ == "__main__":
    generate_all()
