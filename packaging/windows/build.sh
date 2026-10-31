#!/bin/sh
set -eu
cd /workspace
prefix=/opt/windows/SDL3-3.4.18/x86_64-w64-mingw32
mkdir -p /opt/windows/prefix/share/cmake/nlohmann_json
cp /usr/share/cmake/nlohmann_json/* /opt/windows/prefix/share/cmake/nlohmann_json/
mkdir -p /opt/windows/prefix/include
cp -r /usr/include/nlohmann /opt/windows/prefix/include/
python3 tools/prepare_stim_libxmp.py --source build/libxmp --output build/windows-release/stim-xmp-source
cmake -S build/windows-release/stim-xmp-source -B build/windows-release/stim-xmp -G Ninja -DCMAKE_TOOLCHAIN_FILE=/workspace/packaging/windows/toolchain.cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/windows/prefix -DBUILD_SHARED=ON -DBUILD_STATIC=OFF
cmake --build build/windows-release/stim-xmp -j 3
cmake --install build/windows-release/stim-xmp
cmake -S . -B build/windows-release/native -G Ninja -DCMAKE_TOOLCHAIN_FILE=/workspace/packaging/windows/toolchain.cmake -DCMAKE_PREFIX_PATH="$prefix;/opt/windows/prefix" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O2 -DNDEBUG' -DXMP_INCLUDE_DIR=/opt/windows/prefix/include -DXMP_LIBRARY=/opt/windows/prefix/lib/libxmp.dll.a -DSLAM_ENABLE_GPU_EFFECTS=OFF
cmake --build build/windows-release/native --target slamtilt slamview slamslice -j 3
