# 1.2 acceptance

- STIM timing: four adapted original first ticks, 20 manually clocked windows, four synthetic five-second loops, and 10 seconds of deterministic native playback per table; complete songs/effects and physical output remain unverified.
- Non-STIM isolation: 88,200 frames of a non-STIM MOD match the unmodified libxmp.
- Pirate music plus two SFX: bounded original comparison correlation 0.999925; not sample-identical.
- Linux: Debian 12 compatibility build; AppImage first import and all four child launches pass in a network-isolated sandbox. Real GPU/audio and FUSE mounting were not tested in that check.
- Browser: offline Chromium check, 19 checks including real gameplay input, storage and fullscreen.
- Windows: Wine smoke and silent installer/uninstaller test; actual Windows hardware unverified.
- ARM64: cross-build and QEMU smoke; physical Pi/Batocera unverified.
- Runtime packages contain no original DAT/ADF game data. The user must supply supported original files.
