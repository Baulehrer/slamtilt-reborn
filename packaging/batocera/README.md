# Batocera / Raspberry Pi ARM64 preview

Use a **64-bit** Batocera installation. Extract the ARM64 runtime to
`/userdata/system/slamtilt-reborn-linux-aarch64`, copy `Slamtilt-Reborn.sh` to
`/userdata/roms/ports/`, make it executable, and refresh the game list.

For keyboard-free first import, create `/userdata/roms/ports/slamtilt-data` and
put your original `MAIN.DAT` plus the table DATs there, or all five supported
retail v1.224 DLM ADFs. The launcher performs one native import, then opens the
menu. No Python, Wine, emulator or EXE is required by this launcher. The data
folder is not supplied with the port.

Settings, imported data and highscores remain in `/userdata/saves/SlamTiltNative/SlamTilt`.
An import marker next to `frontend.json` prevents repeated copies. Existing
nonempty frontend configurations, including partial table collections, are
preserved when no launcher marker exists; the native frontend validates them. A failed
import writes no marker and is retried next time. To deliberately refresh data,
set `SLAMTILT_REIMPORT=1`, or change `SLAMTILT_DATA` when a launcher marker
exists. Deleting or emptying
`frontend.json` also causes a new import. Corrupt/incomplete configurations are
not parsed or silently replaced by this shell script; use the explicit refresh
setting after reviewing the native frontend warning. With no data folder, the menu opens
normally and can still import through its existing data picker.

Default controls: **LB/RB** flippers, **South/A** launch, **Start** options,
**Back/Select** table menu, and D-pad/stick menu navigation. **RT** is a pull-and-
release launch gesture using the original digital launch force, not a newly
invented variable-strength physics model. Action buttons can be rebound in the
native Controls options. Release held controls after reconnecting or closing a
modal menu before they become active again. In menus, **West/X** switches the
PC/Amiga source, **North/Y** opens the native data picker, and **LB/RB** change
options categories. External desktop folder dialogs may still need a keyboard;
the data-folder bootstrap avoids them on Batocera.

Recognized SDL gamepads use the port's native mapping. The launcher preserves
Batocera's existing `SDL_GAMECONTROLLERCONFIG`/`SDL_GAMECONTROLLERCONFIG_FILE`.
Optional additional SDL mappings can be stored in
`/userdata/system/configs/slamtilt/gamecontrollerdb.txt`, or in the runtime
folder as `gamecontrollerdb.txt`. `SLAMTILT_GAMEPAD_DB` explicitly overrides that
file selection. No controller XML or pad2key layer is generated; duplicate
keyboard emulation can otherwise trigger actions twice.

Overrides: `SLAMTILT_HOME`, `SLAMTILT_DATA` (empty disables automatic import),
`SLAMTILT_CONFIG`, `SLAMTILT_GAMEPAD_DB`, `SLAMTILT_REIMPORT`; normal XDG variables
are respected. Arguments passed to the launcher reach the interactive game. A native `--config`
override also controls the first-import destination; an explicit `--import`
bypasses automatic preflight and is handled directly by the native frontend.

This remains a preview. QEMU can validate ARM code and virtual input, not a
physical Pi's graphics, ALSA output, Bluetooth latency, controller mappings or
Batocera board image. Those hardware checks remain open.
