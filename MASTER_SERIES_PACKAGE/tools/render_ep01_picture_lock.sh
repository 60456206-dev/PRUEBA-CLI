#!/usr/bin/env bash
# Montaje de imagen EP01 (picture lock) según EPISODES/EP01/EP01_EDIT_PLAN.md.
# 1080x1920, 24 fps, cortes secos, sin audio (el audio se monta aparte en stems).
set -euo pipefail
cd "$(dirname "$0")/.."
S=shots
OUT=FINAL/EP01_PICTURE_LOCK.mp4
mkdir -p FINAL
# Orden y duración de montaje (s). Nombres: versiones elegidas por el usuario (EP01 conserva nombres previos al acuerdo _FINAL).
CLIPS=(
  "$S/EP01_SH01_PIXVERSE_SIN_MARCA_PREVIEW.mp4:5"
  "$S/EP01_SH02_FLOW_SIN_MARCA_6S.mp4:6"
  "$S/EP01_SH03_FLOW_5S.mp4:5"
  "$S/EP01_SH04_FLOW_8S.mp4:8"
  "$S/EP01_SH05_FLOW_6S.mp4:6"
  "$S/EP01_SH06_FLOW_7S.mp4:7"
  "$S/EP01_SH07_FLOW_6S.mp4:6"
  "$S/EP01_SH08_FLOW_8S.mp4:8"
)
inputs=(); filt=""; i=0
for c in "${CLIPS[@]}"; do
  f="${c%%:*}"; d="${c##*:}"
  inputs+=(-t "$d" -i "$f")
  filt+="[$i:v]scale=1080:1920:flags=lanczos,setsar=1,fps=24,trim=duration=$d,setpts=PTS-STARTPTS[v$i];"
  i=$((i+1))
done
for ((k=0;k<i;k++)); do filt+="[v$k]"; done
filt+="concat=n=$i:v=1:a=0[out]"
ffmpeg -v error -y "${inputs[@]}" -filter_complex "$filt" -map "[out]" -an \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -r 24 -movflags +faststart "$OUT"
echo "OK $OUT"
