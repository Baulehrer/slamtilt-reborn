#!/bin/sh
set -eu
out=/workspace/build/arm64-release
app="$out/slamtilt-reborn-linux-aarch64"
export SDL_VIDEO_DRIVER=dummy SDL_AUDIO_DRIVER=dummy SDL_RENDER_DRIVER=software
export LD_LIBRARY_PATH="$app/lib:/usr/aarch64-linux-gnu/lib:/usr/lib/aarch64-linux-gnu"
export QEMU_LD_PREFIX=/usr/aarch64-linux-gnu
mkdir -p "$out/smoke-home"
export HOME="$out/smoke-home" XDG_CONFIG_HOME="$out/smoke-home/config" XDG_DATA_HOME="$out/smoke-home/data"
qemu-aarch64 "$app/bin/slamtilt" --help
qemu-aarch64 "$app/slamimport" --help
qemu-aarch64 "$app/bin/slamtilt" --windowed --frames 3 --capture "$out/menu-qemu.bmp" --trace "$out/menu-qemu.json"
