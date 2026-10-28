# Windows release acceptance

Final artifacts: `artifacts/Slamtilt-Reborn-windows-x86_64-portable.zip` and
`artifacts/Slamtilt-Reborn-windows-x86_64-setup.exe`; hashes in `artifacts/SHA256SUMS`.
The earlier pre-import-fix candidate under `artifacts-before-import-fix` is not for distribution.

Passed:

- Cross-built shared launcher, Mean/Pirate and Space/Demon engines with MinGW GCC 12.2, SDL 3.4.18 and libxmp from the repository's source checkout.
- Native Windows smoke through Wine 8: overwrite existing preferences; create, overwrite and reload highscores; SDL process startup and captured exit code; `.exe` child paths.
- Portable first start through Wine with dummy SDL video/audio: imported all four Windows retail DAT tables without an original EXE. Original data was supplied separately from the workspace corpus, never bundled.
- Portable second invocation loaded saved preferences, launched Mean/Pirate/Space/Demon in sequence, rendered 16 frames each and returned exit code zero from all four child sessions.
- NSIS compiled an unsigned per-user installer with zero warnings.
- Actual unchanged NSIS installer passed under Wine 8 with Wine32 and Xvfb: silent per-user install, installed AMD64 launcher (three frames with software renderer), Start menu shortcut, correctly quoted uninstall registry entry, silent uninstall and retained user-profile sentinel. See `installer-acceptance.log`.
- Portable contents are limited to native executable/DLL files, import metadata, fonts/licenses and documentation. No original DAT/ADF/BIN or original game EXE is included.

Evidence: `import-fix-build.log`, `runtime-check.log`, `first-import.json`,
`table-cycle.json`, `artifacts/*/windows-bundle.json`.

Limits:

- Actual Windows desktop/hardware, audio playback and interactive folder dialogs have not been exercised.
- The initial Wine64-only installer probe failed because the NSIS bootstrap requires Wine32. After adding Wine32 the actual installation/uninstallation acceptance passed. Actual Windows desktop acceptance remains separate.
- Amiga imports use the same newly portable publication function but have not been exercised on Wine.

Reproduce build/package with packaging/windows/README.md, then run
`sh packaging/windows/runtime-check.sh` inside the toolchain container with the
same separate original-data corpus available. No certificate is required.

Final manifest verification also passed: all 39 recorded payload hashes match;
all three game programs are PE AMD64 (0x8664), and all programs and the NSIS
bootstrap have an empty PE certificate directory. The NSIS bootstrap is PE i386
(0x14c), launching the x86_64 payload. Toolchain versions are recorded in
`toolchain-versions.txt`.

Installer execution command: in Docker image
`slamtilt-windows-installer-toolchain:bookworm` (recorded digest in
`installer-toolchain-image.txt`), start Xvfb then run
`DISPLAY=:99 XAUTHORITY=/tmp/xvfb-run.YDM3tA/Xauthority sh packaging/windows/installer-check.sh`.
The initial installed-launcher attempt exposed a Wine vkd3d Vulkan extension
assertion; selecting SDL's software renderer for the headless acceptance made the
installed-launcher check pass. No executable or installer was changed.

Final license-notice repack: both nlohmann/json MIT and Ancient BSD-2-Clause notices are included. Every executable/DLL remains byte-identical to the prior accepted runtime. The exact new NSIS installer passed the full silent install, installed notices, launcher, shortcut/registry, uninstall and retained-profile check again; see `installer-notices-acceptance.log`. Final archive hashes are in `artifacts/SHA256SUMS`.
