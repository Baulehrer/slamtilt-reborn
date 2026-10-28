# Local-only toolchain: no original game data or project source in this image.
FROM rust@sha256:9a73a5088750b4c95158ab26629c854c3d6fc4b173cb7bc8079ad252d8ed7bfa
RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    cmake ninja-build pkg-config python3 glslc nlohmann-json3-dev \
    libasound2-dev libpulse-dev libx11-dev libxext-dev libxrandr-dev \
    libxcursor-dev libxfixes-dev libxi-dev libxss-dev libxtst-dev libwayland-dev \
    libxkbcommon-dev libdecor-0-dev libdrm-dev libgbm-dev libudev-dev \
    libdbus-1-dev libegl-dev libgl-dev libgles2-mesa-dev wayland-protocols \
    libpipewire-0.3-dev libvulkan-dev libusb-1.0-0-dev libfribidi-dev \
    libthai-dev libibus-1.0-dev liburing-dev \
    && rm -rf /var/lib/apt/lists/*
COPY SDL3-3.4.18.tar.gz libxmp.tar.gz /sources/
RUN tar -xzf /sources/SDL3-3.4.18.tar.gz -C /sources && \
    tar -xzf /sources/libxmp.tar.gz -C /sources && \
    cmake -S /sources/SDL3-3.4.18 -B /sources/sdl-build -G Ninja \
      -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/mean \
      -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TEST_LIBRARY=OFF \
      -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF && \
    cmake --build /sources/sdl-build -j 3 && cmake --install /sources/sdl-build && \
    cmake -S /sources/libxmp -B /sources/xmp-build -G Ninja \
      -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/mean \
      -DBUILD_SHARED=ON -DBUILD_STATIC=OFF && \
    cmake --build /sources/xmp-build -j 3 && cmake --install /sources/xmp-build && \
    mkdir -p /opt/mean/licenses && \
    cp /sources/SDL3-3.4.18/LICENSE.txt /opt/mean/licenses/SDL3.txt && \
    cp /sources/libxmp/docs/COPYING /opt/mean/licenses/libxmp.txt && \
    dpkg-query -W > /opt/mean/packages.txt && \
    rm -rf /sources
ENV CMAKE_PREFIX_PATH=/opt/mean
ENV LD_LIBRARY_PATH=/opt/mean/lib
WORKDIR /workspace
