#!/bin/sh
set -eu
export PKG_CONFIG_LIBDIR=/usr/lib/aarch64-linux-gnu/pkgconfig:/usr/share/pkgconfig
unset LD_LIBRARY_PATH
python3 - <<'PYHASH'
import hashlib,json
from pathlib import Path
spec=json.loads(Path('/workspace/packaging/compat-sources.json').read_text())
for filename,expected in [('SDL3-3.4.18.tar.gz',spec['sdl']['sha256']),('libxmp.tar.gz',spec['libxmp']['git_archive_sha256'])]:
 assert hashlib.sha256((Path('/workspace/build/compat-context')/filename).read_bytes()).hexdigest()==expected, filename
PYHASH
out="${SLAM_ARM64_OUT:-/workspace/build/arm64-release}"
export SLAM_ARM64_OUT="$out"
mkdir -p "$out/sources"
tar -xzf /workspace/build/compat-context/SDL3-3.4.18.tar.gz -C "$out/sources"
tar -xzf /workspace/build/compat-context/libxmp.tar.gz -C "$out/sources"
cmake -S "$out/sources/SDL3-3.4.18" -B "$out/sdl" -G Ninja -DCMAKE_TOOLCHAIN_FILE=/workspace/packaging/arm64/toolchain.cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/arm64 -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TEST_LIBRARY=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF -DSDL_X11=OFF -DSDL_ALSA=ON -DALSA_INCLUDE_DIR=/usr/include -DALSA_LIBRARY=/usr/lib/aarch64-linux-gnu/libasound.so -DSDL_WAYLAND=ON -DSDL_KMSDRM=ON
cmake --build "$out/sdl" -j 4
cmake --install "$out/sdl"
for feature in SDL_AUDIO_DRIVER_ALSA SDL_VIDEO_DRIVER_KMSDRM SDL_VIDEO_DRIVER_WAYLAND SDL_VIDEO_OPENGL_ES2 SDL_JOYSTICK_LINUX SDL_JOYSTICK_HIDAPI SDL_JOYSTICK_VIRTUAL; do
 grep -q "#define $feature 1" "$out/sdl/include-config-release/build_config/SDL_build_config.h"
done
cmake -S "$out/sources/libxmp" -B "$out/xmp" -G Ninja -DCMAKE_TOOLCHAIN_FILE=/workspace/packaging/arm64/toolchain.cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/arm64 -DBUILD_SHARED=ON -DBUILD_STATIC=OFF
cmake --build "$out/xmp" -j 4
cmake --install "$out/xmp"
cmake -S /workspace -B "$out/native" -G Ninja -DCMAKE_TOOLCHAIN_FILE=/workspace/packaging/arm64/toolchain.cmake -DCMAKE_BUILD_TYPE=Release '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -DNDEBUG' -DCMAKE_PREFIX_PATH=/opt/arm64 -DSDL3_DIR=/opt/arm64/lib/cmake/SDL3 -DXMP_INCLUDE_DIR=/opt/arm64/include -DXMP_LIBRARY=/opt/arm64/lib/libxmp.so
cmake --build "$out/native" --target slamtilt slamview slamslice slamimport slamsetup -j 4
if [ -f /workspace/tests/gamepad_input_test.cpp ]; then
 cmake --build "$out/native" --target gamepad_input_test -j 4
 SDL_VIDEO_DRIVER=dummy SDL_AUDIO_DRIVER=dummy SDL_RENDER_DRIVER=software LD_LIBRARY_PATH=/opt/arm64/lib:/usr/aarch64-linux-gnu/lib:/usr/lib/aarch64-linux-gnu qemu-aarch64 -L /usr/aarch64-linux-gnu "$out/native/gamepad_input_test" "$out/gamepad-input-qemu.json" > "$out/gamepad-input-qemu.log" 2>&1
fi
dpkg-query -W > "$out/toolchain-packages.txt"
aarch64-linux-gnu-g++ --version > "$out/compiler.txt"
cp "$out/sdl/include-config-release/build_config/SDL_build_config.h" "$out/SDL_build_config.h"
python3 /workspace/packaging/arm64/pack.py
/workspace/packaging/arm64/smoke.sh > "$out/qemu-smoke.log" 2>&1
aarch64-linux-gnu-g++ -I/opt/arm64/include /workspace/packaging/arm64/backend_probe.cpp -L/opt/arm64/lib -lSDL3 -o "$out/backend-probe"
SDL_AUDIO_DRIVER=dummy LD_LIBRARY_PATH=/opt/arm64/lib:/usr/aarch64-linux-gnu/lib:/usr/lib/aarch64-linux-gnu qemu-aarch64 -L /usr/aarch64-linux-gnu "$out/backend-probe" > "$out/backends-qemu.txt"
