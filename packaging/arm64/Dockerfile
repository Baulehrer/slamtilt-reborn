FROM slamtilt-mean-toolchain:bookworm
RUN dpkg --add-architecture arm64 && apt-get update -qq && apt-get install -y --no-install-recommends g++-aarch64-linux-gnu qemu-user libasound2-dev:arm64 libwayland-dev:arm64 libxkbcommon-dev:arm64 libdrm-dev:arm64 libgbm-dev:arm64 libudev-dev:arm64 libegl-dev:arm64 libgles2-mesa-dev:arm64 && rm -rf /var/lib/apt/lists/*
ENV PKG_CONFIG_LIBDIR=/usr/lib/aarch64-linux-gnu/pkgconfig:/usr/share/pkgconfig
ENV LD_LIBRARY_PATH=
