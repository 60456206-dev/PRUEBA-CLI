#!/usr/bin/env python3
"""Descarga activos reales en WAV (música por stems y efectos de estudio) desde Epidemic Sound MCP."""
import json
import os
import urllib.request
from pathlib import Path

API_KEY = os.environ["EPIDEMIC_SOUND"]
MCP_URL = "https://www.epidemicsound.com/a/mcp-service/mcp"
OUT_DIR = Path(__file__).resolve().parents[1] / "AUDIO" / "EPIDEMIC_SOUND"
MUSIC_DIR = OUT_DIR / "MUSIC"
SFX_DIR = OUT_DIR / "SFX"
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
SFX_DIR.mkdir(parents=True, exist_ok=True)


def mcp_call(payload: dict, session_id: str | None = None) -> tuple[str | None, dict]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "MasterSeries-MCP-Client/1.0",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    req = urllib.request.Request(
        MCP_URL, data=json.dumps(payload).encode(), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        sid = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
        body = resp.read().decode()
        for line in body.splitlines():
            if line.startswith("data: {"):
                return sid, json.loads(line[6:])
        return sid, {"raw": body}


def download_file(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [SKIP] {dest.name} ({dest.stat().st_size // 1024} KB)")
        return
    req = urllib.request.Request(url, headers={"User-Agent": "MasterSeries-MCP-Client/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())
    print(f"  [OK] {dest.name} ({dest.stat().st_size // 1024} KB)")


def main() -> None:
    sid, _ = mcp_call(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "antigravity", "version": "1.0.0"},
            },
        }
    )
    print("Conectado a Epidemic Sound MCP. Session ID:", sid)

    music_assets = [
        ("ORO_INSTRUMENTS", "55900695-564d-45bd-bde7-672cca5e827e", "INSTRUMENTS", "Oro - Hanna Ekström & Anna Dager"),
        ("ORO_BASS", "55900695-564d-45bd-bde7-672cca5e827e", "BASS", "Oro (Bass) - Hanna Ekström & Anna Dager"),
        ("CREEPING_ANXIETY_INSTRUMENTS", "98451bbf-902f-4139-a264-a239c0308f2f", "INSTRUMENTS", "Creeping Anxiety - Anna Dager & Hanna Ekström"),
        ("CREEPING_ANXIETY_BASS", "98451bbf-902f-4139-a264-a239c0308f2f", "BASS", "Creeping Anxiety (Bass) - Anna Dager & Hanna Ekström"),
        ("DONT_TURN_AROUND_INSTRUMENTS", "a749c9fc-4e51-434b-a43d-22e8bad3184b", "INSTRUMENTS", "Don't Turn Around - Belladonna Strings"),
        ("SHIFTING_GROUND_INSTRUMENTS", "87893ebf-9476-46ff-9cc1-f1227748c791", "INSTRUMENTS", "Shifting Ground - Luba Hilman"),
        ("SHIFTING_GROUND_BASS", "87893ebf-9476-46ff-9cc1-f1227748c791", "BASS", "Shifting Ground (Bass) - Luba Hilman"),
        ("DARK_PUZZLE_INSTRUMENTS", "8baa12a3-6028-40b4-b57c-a091b687d041", "INSTRUMENTS", "Dark Puzzle - Anna Dager & Hanna Ekström"),
        ("DISTURBING_EVIDENCE_INSTRUMENTS", "84db60d5-46d4-4869-a573-b2ec46ad0b53", "INSTRUMENTS", "Disturbing Evidence - Stefan Ekström"),
    ]

    sfx_assets = [
        ("ROOM_BASEMENT", "f090dfcc-b464-4493-b32f-706ed02d4a95", "Ambience, Room Tone, Corporate Building, Dark, Basement"),
        ("FOLEY_COAT_THICK", "d693ef10-2841-4d51-8e5c-364e49c4d599", "Cloth, Movement, Jacket, Thick, Fast, Slow"),
        ("FOLEY_COAT_FLAP", "6bc04bea-5b48-469f-8ea7-462927f68a88", "Cloth, Flap, Foley Set Fabric, Jacket, Flap 01"),
        ("SFX_WATER_DROP_SINGLE", "da7885a5-2746-4edd-855a-790cebf94cd7", "Water, Drip, Drop, Single"),
        ("SFX_WATER_DROP_CLOTH", "df3e9964-f498-4666-9b5e-079dbcc134f2", "Cloth, Impact, Wet Cloth, Drop On Glass, Soft"),
        ("FOLEY_KEYS_HAND", "11eaca16-49f3-45c6-8405-1bba085b8060", "Objects, Keys, Handling, Lock Clicks"),
        ("SFX_FLOODGATE_HIT", "b848b9f3-665b-4205-9df4-99487a6237ad", "Metal, Impact, Hit Door, Heavy Impact, Rattle, Reverberant"),
        ("SFX_FLOODGATE_BOOM", "778b3f1c-bccb-4138-bd90-defb8fcf26fa", "Doors, Dungeon, Impact, Metal Door, Close, Deep, Big, Boom 01"),
        ("SFX_FLOODGATE_SCRAPE", "b7e222f9-5feb-4967-88be-fcb5235f9a2b", "Objects, Furniture, Dragging, Scrape, Metal, Heavy"),
        ("SFX_RECORDER_BUTTONS", "6c41c582-e514-4e50-9279-b3e5c7b06fca", "Mechanical, Click, Portable Cassette, Sun Ace Portable BOT 450"),
        ("FOLEY_PAPER_TURN", "3e3e1af7-6d5b-4f09-a227-97575f34af7a", "Paper, Handle, Thick, Turn Page"),
        ("SFX_RISER_LOW", "e705e6f7-6b2b-4083-99de-2ef6327a6771", "Designed, Riser, Low Risers"),
        ("SFX_RUMBLE_RISING", "bfaede35-d903-46d5-9c01-548e591177d3", "Designed, Rumble, Bass, Low, Rising 01"),
        ("SFX_DARK_BOOM", "582229d4-ce16-4e09-8c9e-6b0d9ecace82", "Designed, Boom, Impact, Dark, Cinematic, Low Passed"),
        ("SFX_UI_CONFIRM", "998fe887-42ea-4d38-9fd2-f430d8475bb1", "User Interface, Click, UI Buttons, Confirm, Menu"),
    ]

    manifest = {"music": [], "sfx": []}

    for name, rec_id, stem, desc in music_assets:
        dest = MUSIC_DIR / f"{name}.wav"
        _, res = mcp_call(
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": "DownloadRecording",
                    "arguments": {"id": rec_id, "options": {"fileType": "WAV", "stemType": stem}},
                },
            },
            sid,
        )
        data = json.loads(res["result"]["content"][0]["text"])
        asset_url = data["data"]["recordingDownload"]["assetUrl"]
        download_file(asset_url, dest)
        manifest["music"].append({"name": name, "id": rec_id, "stem": stem, "description": desc, "file": str(dest.relative_to(OUT_DIR))})

    for name, sfx_id, desc in sfx_assets:
        dest = SFX_DIR / f"{name}.wav"
        _, res = mcp_call(
            {
                "jsonrpc": "2.0",
                "id": 20,
                "method": "tools/call",
                "params": {
                    "name": "DownloadSoundEffect",
                    "arguments": {"id": sfx_id, "options": {"fileType": "WAV"}},
                },
            },
            sid,
        )
        data = json.loads(res["result"]["content"][0]["text"])
        asset_url = data["data"]["soundEffectDownload"]["assetUrl"]
        download_file(asset_url, dest)
        manifest["sfx"].append({"name": name, "id": sfx_id, "description": desc, "file": str(dest.relative_to(OUT_DIR))})

    (OUT_DIR / "catalog_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print("Descarga completa y registrada en catalog_manifest.json")


if __name__ == "__main__":
    main()
