# Changelog

## 1.2 — 2026-10-31

- Corrected table music startup positions and expanded checks of music transitions and sound effects against the Windows original.
- Improved STIM sample timing for all four tables with a Slam Tilt-specific libxmp correction.
- Improved Mean sound handling and several table-specific gameplay and audio paths.
- Expanded original-data import, display options and controller-related checks.

Original game data is not included. Audio and gameplay comparisons cover tested scenarios; complete original parity has not been established. Windows and ARM64 validation uses Wine and QEMU rather than physical hardware.

## 1.1 — 2026-10-29

- Main menu returns to the original metal logo and table switches, with a Reborn subtitle and table preview. Options use matching colors and controls.
- Native gamepad support across the menu and all four tables, saved button mappings, trigger pull/release and safer focus/hotplug handling. Keyboard controls remain available.
- Batocera launcher bootstrap and controller documentation. ARM64 remains a preview; physical Raspberry Pi/Batocera hardware is not yet verified.
- Browser download reduced to about 3 MB through internal compression, still one offline HTML file. Fixed Vivaldi's collapsed 4×4 gameplay canvas. Tested in Chromium, Vivaldi and Brave.
- Space and Demon upload lamp textures only when their visible frame changes; verified states and screenshots remain identical.
- Smaller Windows installer using solid LZMA compression; installation remains unsigned and per-user.
- Optional XZ native archives and developer profiling tools. Shared-engine/LTO experiments are opt-in and are not enabled in standard downloads.

No original game data is included. Existing imported data and settings remain supported. Windows checks use Wine; ARM64 checks use QEMU, not physical hardware. Firefox and Safari are unverified.

## 1.0 — 2026-10-28

Initial public release: all four native tables, user DAT/ADF import, configurable display/DMD/audio/input, Windows packages, Linux AppImage, ARM64 preview and single-file browser preview.
