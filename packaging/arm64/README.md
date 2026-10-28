# Linux ARM64 / Raspberry Pi candidate

This is an asset-free aarch64 Linux package built with the Debian 12 cross compiler. It includes the four-table frontend, native importer, SDL3 3.4.18 and libxmp 4.7.3. Original DAT/ADF files are supplied privately by the user through F2 in the frontend. Demon Amiga V3 and all runtime import profiles installed by the common Runtime component are included.

Extract and run `./slamtilt-reborn`. Requires 64-bit ARM Linux, glibc 2.36 or newer and compatible libstdc++; inspect frontend-bundle.json for symbol requirements. SDL was built with ALSA, Wayland, KMSDRM/GBM/EGL/OpenGL ES. These dynamically loaded platform libraries and a working graphics/audio session must be provided by the target OS. SDL may select its driver automatically; `SDL_VIDEO_DRIVER=kmsdrm` or `SDL_VIDEO_DRIVER=wayland` can select an available backend. A compositor generally owns DRM while running, so do not force KMSDRM in that session.

For Batocera, extract to `/userdata/system/slamtilt-reborn-linux-aarch64`, copy `batocera/Slamtilt-Reborn.sh` to `/userdata/roms/ports/`, make it executable, and refresh the game list. Settings and saves use persistent /userdata paths. The launcher uses SDL's controller detection; no Batocera controller configuration is converted automatically. Keyboard access is required for initial import if the chosen controller lacks the relevant controls.

QEMU CPU smoke results are recorded separately in the build report. Physical Raspberry Pi GPU, display, controller, audio and Batocera compatibility have not been validated; this is an optional candidate, not a supported Batocera board image.

Rebuild from the repository root: `docker build -t slamtilt-arm64-toolchain:bookworm -f packaging/arm64/Dockerfile packaging/arm64`, then `docker run --rm -v "$PWD:/workspace" slamtilt-arm64-toolchain:bookworm /workspace/packaging/arm64/build.sh`. The existing pinned SDL/libxmp archives must be in build/compat-context. The base image is built with packaging/compat.Dockerfile. Build output is isolated in build/arm64-release.
