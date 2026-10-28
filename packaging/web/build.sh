#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$ROOT"
python3 packaging/web/patch_sdl.py build/arm64-release/sources/SDL3-3.4.18
mkdir -p build/web-release/meta build/web-release/headers/include build/web-release/headers/lib/cmake/nlohmann_json
if [ ! -f build/web-release/headers/include/nlohmann/json.hpp ]; then
  cp -R /usr/include/nlohmann build/web-release/headers/include/
fi
cat > build/web-release/headers/lib/cmake/nlohmann_json/nlohmann_jsonConfig.cmake <<'EOF'
if(NOT TARGET nlohmann_json::nlohmann_json)
  add_library(nlohmann_json::nlohmann_json INTERFACE IMPORTED)
  get_filename_component(_json_prefix "${CMAKE_CURRENT_LIST_DIR}/../../.." ABSOLUTE)
  set_target_properties(nlohmann_json::nlohmann_json PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${_json_prefix}/include")
endif()
EOF
cp analysis/import/*-startup.json packaging/*data.sha256 analysis/table-profiles.json build/web-release/meta/
cp packaging/mean-initial.json build/web-release/meta/initial-state.json
exec docker run --rm --user "$(id -u):$(id -g)" -v "$ROOT:/workspace" -w /workspace emscripten/emsdk:4.0.20@sha256:460fff8f8ac87e11b16447fbd66538a686eafa0e4fb977aa0989ed19fe2079f7 sh /workspace/packaging/web/inside-build.sh
