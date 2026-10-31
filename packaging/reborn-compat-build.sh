#!/bin/sh
set -eu
python3 /workspace/tools/prepare_stim_libxmp.py --source /workspace/build/libxmp --output /output/stim-xmp-source
cmake -S /output/stim-xmp-source -B /output/stim-xmp-build -G Ninja \
 -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/output/stim-xmp -DBUILD_SHARED=ON -DBUILD_STATIC=OFF
cmake --build /output/stim-xmp-build -j "${SLAM_COMPAT_JOBS:-3}"
cmake --install /output/stim-xmp-build
export LD_LIBRARY_PATH="/output/stim-xmp/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
cmake -S /workspace -B /output/native -G Ninja \
 -DCMAKE_BUILD_TYPE=Release '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -DNDEBUG' \
 -DCMAKE_PREFIX_PATH=/opt/mean -DXMP_INCLUDE_DIR=/output/stim-xmp/include \
 -DXMP_LIBRARY=/output/stim-xmp/lib/libxmp.so -DSLAM_GLSLC=/usr/bin/glslc
cmake --build /output/native --target slamtilt slamview slamslice slamimport slamsetup -j "${SLAM_COMPAT_JOBS:-3}"
python3 /workspace/tools/slamtilt-pack --build /output/native --output "/output/releases/$SLAM_REBORN_NAME" \
 --sdl-license /opt/mean/licenses/SDL3.txt --xmp-license /opt/mean/licenses/libxmp.txt
cp /opt/mean/packages.txt /output/reborn-toolchain-packages.txt
ldd --version > /output/reborn-toolchain-libc.txt
c++ --version > /output/reborn-toolchain-compiler.txt
