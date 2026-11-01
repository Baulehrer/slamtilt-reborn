#!/bin/sh
set -eu
OUT=/workspace/build/web-release
PREFIX=$OUT/prefix
emcmake cmake -S /workspace/build/arm64-release/sources/SDL3-3.4.18 -B "$OUT/sdl" -DCMAKE_INSTALL_PREFIX="$PREFIX" -DCMAKE_BUILD_TYPE=Release -DSDL_SHARED=OFF -DSDL_STATIC=ON -DSDL_TESTS=OFF -DSDL_EMSCRIPTEN_PERSISTENT_PATH=/user/prefs
cmake --build "$OUT/sdl" -j2
cmake --install "$OUT/sdl"
python3 /workspace/tools/prepare_stim_libxmp.py --source /workspace/build/libxmp --output "$OUT/stim-xmp-v4-source"
emcmake cmake -S "$OUT/stim-xmp-v4-source" -B "$OUT/stim-xmp-v4" -DCMAKE_INSTALL_PREFIX="$PREFIX" -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED=OFF -DBUILD_STATIC=ON '-DCMAKE_C_FLAGS_RELEASE=-O2 -DNDEBUG -sSUPPORT_LONGJMP=wasm'
cmake --build "$OUT/stim-xmp-v4" -j2
cmake --install "$OUT/stim-xmp-v4"
emcmake cmake -S /workspace -B "$OUT/native" -DCMAKE_BUILD_TYPE=Release '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -DNDEBUG -fwasm-exceptions' -DCMAKE_PREFIX_PATH="$PREFIX;$OUT/headers" -DSDL3_DIR="$PREFIX/lib/cmake/SDL3" -Dnlohmann_json_DIR="$OUT/headers/lib/cmake/nlohmann_json" -DSLAM_ENABLE_GPU_EFFECTS=OFF -DXMP_INCLUDE_DIR="$PREFIX/include" -DXMP_LIBRARY="$PREFIX/lib/libxmp.a"
cmake --build "$OUT/native" --target slamtilt-web -j2
