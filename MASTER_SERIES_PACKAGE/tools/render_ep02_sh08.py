"""Rebuild EP02 SH08 from the report still with a bounded, smooth 10% push-in."""
from pathlib import Path
import subprocess
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / 'SHOT_REFERENCES/REPORT_TOP.png'
output = root / 'shots/EP02_SH08_FINAL.mp4'
im = Image.open(source).convert('RGB')
w, h = im.size
fps, count = 24, 192
# Zoom around the center of the evacuation line; keep all lettering inside the frame.
anchor_x, anchor_y = w / 2, h * 0.335
proc = subprocess.Popen([
    'ffmpeg', '-v', 'error', '-n', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
    '-s', '720x1280', '-r', str(fps), '-i', '-', '-an', '-c:v', 'libx264',
    '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart', str(output)
], stdin=subprocess.PIPE)
for n in range(count):
    phase = min(1.0, n / (fps * 7.0))
    ease = phase * phase * (3.0 - 2.0 * phase)
    zoom = 1.0 + 0.10 * ease
    crop_w, crop_h = w / zoom, h / zoom
    left = anchor_x * (1.0 - 1.0 / zoom)
    top = anchor_y * (1.0 - 1.0 / zoom)
    frame = im.resize((720, 1280), Image.Resampling.LANCZOS,
                      box=(left, top, left + crop_w, top + crop_h))
    proc.stdin.write(frame.tobytes())
proc.stdin.close()
if proc.wait():
    raise SystemExit('Encoding failed')
print(output)
