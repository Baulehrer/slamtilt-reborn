#!/bin/sh
# Optional maintainer check using private, already verified local data.
set -eu
root=/workspace
out="${SLAM_ARM64_OUT:-$root/build/arm64-release}"
app=$out/slamtilt-reborn-linux-aarch64
export SDL_VIDEO_DRIVER=dummy SDL_AUDIO_DRIVER=dummy SDL_RENDER_DRIVER=software
export LD_LIBRARY_PATH="$app/lib:/usr/aarch64-linux-gnu/lib:/usr/lib/aarch64-linux-gnu" QEMU_LD_PREFIX=/usr/aarch64-linux-gnu
export SLAM_TABLE_PROFILES="$app/share/slamtilt/table-profiles.json" XDG_DATA_HOME="$out/smoke-home/private"
dat="$root/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT"
qemu-aarch64 "$app/bin/slamview" "$root/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" --play "$root/build/mean-prepared" --trace "$root/analysis/traces/mean-flight-100.json" --frames 3 --trace-output "$out/mean-qemu.json"
qemu-aarch64 "$app/bin/slamview" "$dat/PIRATE.DAT" --pirate-play "$root/build/oracle/pirate-complete-game-lamps-ready" --frames 3 --trace-output "$out/pirate-qemu.json"
for table in space demon; do
 upper=$(printf '%s' "$table" | tr '[:lower:]' '[:upper:]')
 qemu-aarch64 "$app/bin/slamslice" "$table" "$root/build/oracle/$table-full-game" "$dat/$upper.DAT" --frames 3 --trace "$out/$table-qemu.json" --audio
 done
