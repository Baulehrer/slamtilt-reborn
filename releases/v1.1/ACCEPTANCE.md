# Version 1.1 acceptance

- Six native regressions pass, plus the actual menu/four-table virtual-gamepad frontend flows. The feeder waits for the real frontend polling point rather than device-open time; analog visibility assertions remain enabled.
- Clean source export builds all three frontends without original data; four public unit tests pass. Local export check has no libxmp dependency installed; release toolchains include it.
- Debian 12 isolated DAT-only first import and four child sessions pass. The packaged Linux code also preserves 4,000-step state vectors and full BMPs for every table. Actual AppImage extract-and-run passes checkout-hidden, network-disabled import/cycle tests.
- Windows 1.1 unsigned solid-LZMA installer passes install, shortcut/registry, launch, uninstall and profile-retention checks under Wine. Packaged DAT-only import/four-table cycle and file/highscore smoke pass. Physical Windows hardware remains unverified.
- Exact final HTML hash passes 19 checks each in Chromium, Vivaldi and Brave; Chromium additionally passes the five-ADF import path. Includes ball motion, options, fullscreen, offline operation and persistence. Physical audio and Firefox/Safari remain unverified.
- ARM64 package passes QEMU menu, virtual-pad/backend, isolated DAT-only import and bounded direct sessions of all four tables. Physical Raspberry Pi/Batocera hardware remains unverified.
- Standard downloads use the static engine; shared-engine and LTO experiments stay opt-in. No original DAT/ADF/EXE/media assets are bundled. Original-data screenshots are documentation only.

Runtime artifacts and release.json are covered by SHA256SUMS. The 1.0 tag and artifacts are preserved.
