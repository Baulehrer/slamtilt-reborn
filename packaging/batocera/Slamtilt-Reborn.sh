#!/bin/bash
set -eu
# Extract the ARM64 bundle here (or override SLAMTILT_HOME).
SLAMTILT_HOME="${SLAMTILT_HOME:-/userdata/system/slamtilt-reborn-linux-aarch64}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-/userdata/saves}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-/userdata/system/configs}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/userdata/system/cache}"
cd "$SLAMTILT_HOME"
exec ./slamtilt-reborn "$@"
