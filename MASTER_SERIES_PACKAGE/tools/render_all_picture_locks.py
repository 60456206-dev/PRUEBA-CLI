#!/usr/bin/env python3
"""Renderiza los Picture Locks (1080x1920, 24 fps, sin audio) de EP02 a EP06."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "shots"
FINAL = ROOT / "FINAL"
FINAL.mkdir(exist_ok=True)

EPISODES = {
    "EP02": [
        ("EP02_SH01_FLOW_5S.mp4", 5),
        ("EP02_SH02_FLOW_7S.mp4", 7),
        ("EP02_SH03_FLOW_5S.mp4", 5),
        ("EP02_SH04_FINAL.mp4", 8),
        ("EP02_SH05_FINAL.mp4", 6),
        ("EP02_SH06_FINAL.mp4", 7),
        ("EP02_SH07_FINAL.mp4", 6),
        ("EP02_SH08_FINAL.mp4", 8),
    ],
    "EP03": [
        ("EP03_SH01_FINAL.mp4", 5),
        ("EP03_SH02_FINAL.mp4", 7),
        ("EP03_SH03_FINAL.mp4", 6),
        ("EP03_SH04_FINAL.mp4", 8),
        ("EP03_SH05_FINAL.mp4", 5),
        ("EP03_SH06_FINAL.mp4", 8),
        ("EP03_SH07_FINAL.mp4", 6),
        ("EP03_SH08_FINAL.mp4", 8),
    ],
    "EP04": [
        ("EP04_SH01_FINAL.mp4", 5),
        ("EP04_SH02_FINAL.mp4", 8),
        ("EP04_SH03_FINAL.mp4", 7),
        ("EP04_SH04_FINAL.mp4", 8),
        ("EP04_SH05_FINAL.mp4", 5),
        ("EP04_SH06_FINAL.mp4", 8),
        ("EP04_SH07_FINAL.mp4", 6),
        ("EP04_SH08_FINAL.mp4", 8),
    ],
    "EP05": [
        ("EP05_SH01_FINAL.mp4", 5),
        ("EP05_SH02_FINAL.mp4", 7),
        ("EP05_SH03_FINAL.mp4", 6),
        ("EP05_SH04_FINAL.mp4", 8),
        ("EP05_SH05_FINAL.mp4", 5),
        ("EP05_SH06_FINAL.mp4", 8),
        ("EP05_SH07_FINAL.mp4", 6),
        ("EP05_SH08_FINAL.mp4", 8),
    ],
    "EP06": [
        ("EP06_SH01_FINAL.mp4", 8),
        ("EP06_SH02_FINAL.mp4", 7),
        ("EP06_SH03_FINAL.mp4", 6),
        ("EP06_SH04_FINAL.mp4", 7),
        ("EP06_SH05_FINAL.mp4", 5),
        ("EP06_SH06_FINAL.mp4", 7),
        ("EP06_SH07_FINAL.mp4", 6),
        ("EP06_SH08_FINAL.mp4", 8),
    ],
}


def render_episode(ep: str, clips: list[tuple[str, int]]) -> None:
    out_path = FINAL / f"{ep}_PICTURE_LOCK.mp4"
    inputs = []
    filt_parts = []
    for i, (fname, dur) in enumerate(clips):
        fpath = SHOTS / fname
        if not fpath.exists():
            raise FileNotFoundError(f"Missing clip: {fpath}")
        inputs.extend(["-t", str(dur), "-i", str(fpath)])
        filt_parts.append(
            f"[{i}:v]scale=1080:1920:flags=lanczos,setsar=1,fps=24,trim=duration={dur},setpts=PTS-STARTPTS[v{i}];"
        )
    concat_inputs = "".join(f"[v{i}]" for i in range(len(clips)))
    filt = "".join(filt_parts) + f"{concat_inputs}concat=n={len(clips)}:v=1:a=0[out]"
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-y",
        *inputs,
        "-filter_complex",
        filt,
        "-map",
        "[out]",
        "-an",
        "-c:v",
        "libx264",
        "-crf",
        "16",
        "-preset",
        "medium",
        "-pix_fmt",
        "yuv420p",
        "-r",
        "24",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    print(f"Rendering {out_path.name} ...", flush=True)
    subprocess.run(cmd, check=True)
    print(f"OK {out_path.name}", flush=True)


def main() -> None:
    for ep, clips in EPISODES.items():
        render_episode(ep, clips)


if __name__ == "__main__":
    main()
