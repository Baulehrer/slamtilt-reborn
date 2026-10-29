#!/bin/bash
set -eu
# The user supplies the runtime and original data; this launcher bundles neither.
SLAMTILT_HOME="${SLAMTILT_HOME:-/userdata/system/slamtilt-reborn-linux-aarch64}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-/userdata/saves}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-/userdata/system/configs}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/userdata/system/cache}"
SLAMTILT_CONFIG="${SLAMTILT_CONFIG:-$XDG_DATA_HOME/SlamTiltNative/SlamTilt/frontend.json}"
SLAMTILT_DATA="${SLAMTILT_DATA-/userdata/roms/ports/slamtilt-data}"
# Honor native CLI overrides before choosing the import destination.
args=("$@")
explicit_import=0
for ((i=0; i<${#args[@]}; ++i)); do
    if [ "${args[i]}" = --import ]; then
        explicit_import=1
    elif [ "${args[i]}" = --config ]; then
        if ((i+1 >= ${#args[@]})); then
            echo "Slamtilt: --config requires a file" >&2
            exit 2
        fi
        SLAMTILT_CONFIG="${args[i+1]}"
        ((i+=1))
    fi
done
marker="$SLAMTILT_CONFIG.batocera-imported"

if [ -n "${SLAMTILT_GAMEPAD_DB:-}" ]; then
    if [ ! -r "$SLAMTILT_GAMEPAD_DB" ]; then
        echo "Slamtilt: controller mapping file is not readable: $SLAMTILT_GAMEPAD_DB" >&2
        exit 2
    fi
    export SDL_GAMECONTROLLERCONFIG_FILE="$(cd -- "$(dirname -- "$SLAMTILT_GAMEPAD_DB")" && pwd)/$(basename -- "$SLAMTILT_GAMEPAD_DB")"
elif [ -z "${SDL_GAMECONTROLLERCONFIG_FILE:-}" ]; then
    for candidate in "$XDG_CONFIG_HOME/slamtilt/gamecontrollerdb.txt" "$SLAMTILT_HOME/gamecontrollerdb.txt"; do
        if [ -r "$candidate" ]; then
            export SDL_GAMECONTROLLERCONFIG_FILE="$candidate"
            break
        fi
    done
fi

cd "$SLAMTILT_HOME"
if [ ! -x ./slamtilt-reborn ]; then
    echo "Slamtilt: runtime is missing or not executable in $SLAMTILT_HOME" >&2
    exit 2
fi
imported_path=''
if [ -f "$marker" ]; then
    IFS= read -r imported_path < "$marker" || true
fi
if [ "$explicit_import" = 0 ] && [ -n "$SLAMTILT_DATA" ] && [ -d "$SLAMTILT_DATA" ] &&
   { [ "${SLAMTILT_REIMPORT:-0}" = 1 ] || [ ! -s "$SLAMTILT_CONFIG" ] ||
     { [ -f "$marker" ] && [ "$imported_path" != "$SLAMTILT_DATA" ]; }; }; then
    # The native importer saves frontend.json transactionally even with --frames.
    # Commit the marker only on success; a failed import cannot skip the next try.
    ./slamtilt-reborn --config "$SLAMTILT_CONFIG" --import "$SLAMTILT_DATA" --windowed --frames 1
    if [ ! -s "$SLAMTILT_CONFIG" ]; then
        echo "Slamtilt: import completed without creating $SLAMTILT_CONFIG" >&2
        exit 2
    fi
    printf '%s\n' "$SLAMTILT_DATA" > "$marker"
fi
exec ./slamtilt-reborn --config "$SLAMTILT_CONFIG" "$@"
