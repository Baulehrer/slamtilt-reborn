#!/bin/sh
set -eu
python3 /workspace/tools/prepare_stim_libxmp.py --source /workspace/build/libxmp --output /output/stim-xmp-v11-source
cmake -S /output/stim-xmp-v11-source -B /output/stim-xmp-v11-build -G Ninja \
 -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/output/stim-xmp-v11 -DBUILD_SHARED=ON -DBUILD_STATIC=OFF
cmake --build /output/stim-xmp-v11-build -j "${SLAM_COMPAT_JOBS:-3}"
cmake --install /output/stim-xmp-v11-build
export LD_LIBRARY_PATH="/output/stim-xmp-v11/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
cmake -S /workspace -B /output/native -G Ninja \
 -DCMAKE_BUILD_TYPE=Release '-DCMAKE_CXX_FLAGS_RELEASE=-O2 -DNDEBUG' \
 -DCMAKE_PREFIX_PATH=/opt/mean -DXMP_INCLUDE_DIR=/output/stim-xmp-v11/include \
 -DXMP_LIBRARY=/output/stim-xmp-v11/lib/libxmp.so -DSLAM_GLSLC=/usr/bin/glslc -DSLAM_STIM_CHANNEL_HISTORY=ON
cmake --build /output/native --target slamtilt slamview slamslice slamimport slamsetup -j "${SLAM_COMPAT_JOBS:-3}"
python3 /workspace/tools/slamtilt-pack --build /output/native --output "/output/releases/$SLAM_REBORN_NAME" \
 --sdl-license /opt/mean/licenses/SDL3.txt --xmp-license /opt/mean/licenses/libxmp.txt
cp /opt/mean/packages.txt /output/reborn-toolchain-packages.txt
ldd --version > /output/reborn-toolchain-libc.txt
c++ --version > /output/reborn-toolchain-compiler.txt
