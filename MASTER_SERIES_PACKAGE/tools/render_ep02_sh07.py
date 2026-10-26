"""Render an editorial focus shift from the accepted S2 still, without scene motion."""
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image, ImageFilter

root = Path(__file__).resolve().parents[1]
source = root / 'SHOT_REFERENCES/EP02_SH07_START_S2.png'
output = root / 'shots/EP02_SH07_FINAL.mp4'
im = Image.open(source).convert('RGB')
w, h = im.size
sharp = np.asarray(im, dtype=np.float32)
soft = np.asarray(im.filter(ImageFilter.GaussianBlur(3.0)), dtype=np.float32)
y, x = np.mgrid[:h, :w]
# Soft-edged mask over the consumed patch. Keep adjacent dry salt and background intact.
mask = np.exp(-2.0 * (((x - 330) / 150) ** 2 + ((y - 615) / 105) ** 2))
mask = mask[..., None].astype(np.float32)
proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-n', '-f', 'rawvideo',
    '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-r', '24', '-i', '-', '-an',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart', str(output)], stdin=subprocess.PIPE)
for frame in range(144):
    t = frame / 24
    phase = min(1.0, max(0.0, (t - 1.0) / 3.0))
    strength = phase * phase * (3 - 2 * phase)
    pixels = sharp + (soft - sharp) * mask * strength
    proc.stdin.write(np.clip(pixels, 0, 255).round().astype(np.uint8).tobytes())
proc.stdin.close()
if proc.wait():
    raise SystemExit('Encoding failed')
print(output)
