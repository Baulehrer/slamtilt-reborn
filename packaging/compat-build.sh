#!/bin/sh
set -eu
cmake -S /workspace -B /output/native -G Ninja \
    -DCMAKE_BUILD_TYPE=Release '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -DNDEBUG' \
    -DCMAKE_PREFIX_PATH=/opt/mean -DXMP_INCLUDE_DIR=/opt/mean/include \
    -DXMP_LIBRARY=/opt/mean/lib/libxmp.so -DSLAM_GLSLC=/usr/bin/glslc
cmake --build /output/native --target slamview slamsetup slamimport sha256_tests mean_mode_marathon -j "${SLAM_COMPAT_JOBS:-3}"
python3 /workspace/tools/slampack --build /output/native \
    --output "/output/releases/$SLAM_COMPAT_RELEASE_NAME" \
    --data-output "/output/releases/$SLAM_COMPAT_RELEASE_NAME-data" \
    --sdl-license /opt/mean/licenses/SDL3.txt --xmp-license /opt/mean/licenses/libxmp.txt
cp /opt/mean/packages.txt /output/toolchain-packages.txt
ldd --version > /output/toolchain-libc.txt
c++ --version > /output/toolchain-compiler.txt
