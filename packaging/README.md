# Building release packages

Run commands from the repository root on a Linux host with Docker. These are packaging workflows for an existing development checkout: generated physics sources under `build/generated`, the libxmp checkout under `build/libxmp`, and the pinned SDL/libxmp archives under `build/compat-context` must already be present. Original game data is private and must stay out of distributable packages. Use new output names rather than overwriting frozen release candidates.

## Linux x86_64

Build the compatibility image from the pinned archives, then build an asset-free runtime:

```sh
docker build -t slamtilt-mean-toolchain:bookworm \
  -f packaging/compat.Dockerfile build/compat-context
mkdir -p build/linux-release
docker run --rm -v "$PWD:/workspace:ro" -v "$PWD/build/linux-release:/output" \
  -e SLAM_REBORN_NAME=slamtilt-reborn-linux-x86_64-candidate \
  slamtilt-mean-toolchain:bookworm sh /workspace/packaging/reborn-compat-build.sh
python3 packaging/linux/build-appimage.py \
  --runtime build/linux-release/releases/slamtilt-reborn-linux-x86_64-candidate \
  --output build/linux-release/Slamtilt-Reborn-linux-x86_64.AppImage
```

The runtime builder bundles SDL3/libxmp and records required ABI versions. The AppImage wrapper downloads appimagetool and records its source and hash under `build/appimage-release`. See [source pins](compat-sources.json).

## Windows x86_64

```sh
docker build -t slamtilt-windows-toolchain:bookworm packaging/windows
docker run --rm -v "$PWD:/workspace" slamtilt-windows-toolchain:bookworm \
  sh -c 'sh packaging/windows/build.sh && sh packaging/windows/verify.sh'
```

Outputs: portable ZIP, per-user NSIS installer and checksums under `build/windows-release/artifacts`. Packages are unsigned. Wine checks do not establish physical Windows hardware acceptance. See [Windows packaging](windows/README.md) for runtime and installer checks.

## Linux ARM64 preview

Build the compatibility base above first, then:

```sh
docker build -t slamtilt-arm64-toolchain:bookworm \
  -f packaging/arm64/Dockerfile packaging/arm64
docker run --rm -v "$PWD:/workspace" slamtilt-arm64-toolchain:bookworm \
  /workspace/packaging/arm64/build.sh
```

The asset-free tar, ELF architecture proof, toolchain inventory and QEMU checks go to `build/arm64-release`. SDL includes ALSA, Wayland and KMSDRM/GLES2 backends. Physical Raspberry Pi/Batocera acceptance remains untested. See [ARM64 instructions](arm64/README.md) and the [Batocera launcher](batocera/Slamtilt-Reborn.sh).

## Experimental browser build

```sh
sh packaging/web/build.sh
```

This uses the pinned Emscripten Docker image and writes to `build/web-release`. In addition to the shared generated sources and libxmp checkout, it currently expects SDL sources at `build/arm64-release/sources/SDL3-3.4.18` and host nlohmann-json headers (copied automatically into `build/web-release/headers`). See [the build script](web/inside-build.sh) for exact paths. The output is one self-contained HTML file with embedded WebAssembly. Run `packaging/web/finalize.py` to add dependency notices; see [browser instructions](web/README.md). This command alone does not establish browser acceptance.

Before publishing, inspect the staged manifest and checksums, confirm no original DAT/ADF/EXE/cache files entered the package, and run the platform's acceptance checks. Screenshots can be reproduced with `python3 tools/release-screenshots.py` using private supported local data; its proof records software rendering and exact capture commands.
