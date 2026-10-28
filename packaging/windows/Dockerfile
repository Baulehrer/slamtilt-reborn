# Toolchain only: no original game data or source is copied into this image.
FROM rust:bookworm
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    g++-mingw-w64-x86-64-posix cmake ninja-build python3 nlohmann-json3-dev \
    nsis wine64 curl zip && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/windows && \
    curl -fL https://github.com/libsdl-org/SDL/releases/download/release-3.4.18/SDL3-devel-3.4.18-mingw.tar.gz -o /tmp/sdl.tar.gz && \
    tar -xf /tmp/sdl.tar.gz -C /opt/windows && rm /tmp/sdl.tar.gz
WORKDIR /workspace
