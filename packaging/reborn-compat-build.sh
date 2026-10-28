#!/bin/sh
set -eu
cmake -S /workspace -B /output/native -G Ninja \
 -DCMAKE_BUILD_TYPE=Release '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -DNDEBUG' \
 -DCMAKE_PREFIX_PATH=/opt/mean -DXMP_INCLUDE_DIR=/opt/mean/include \
 -DXMP_LIBRARY=/opt/mean/lib/libxmp.so -DSLAM_GLSLC=/usr/bin/glslc
cmake --build /output/native --target slamtilt slamview slamslice slamimport slamsetup -j "${SLAM_COMPAT_JOBS:-3}"
python3 /workspace/tools/slamtilt-pack --build /output/native --output "/output/releases/$SLAM_REBORN_NAME" \
 --sdl-license /opt/mean/licenses/SDL3.txt --xmp-license /opt/mean/licenses/libxmp.txt
cp /opt/mean/packages.txt /output/reborn-toolchain-packages.txt
ldd --version > /output/reborn-toolchain-libc.txt
c++ --version > /output/reborn-toolchain-compiler.txt
