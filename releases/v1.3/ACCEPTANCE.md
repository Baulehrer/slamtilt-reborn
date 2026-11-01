# 1.3 acceptance

- Original/native tracker period checks: 2,000 manually clocked startup ticks per table, plus 32 selected 256-tick order samples. These do not prove full-game scheduling.
- Original/native tracker and mixer PCM: 512 manually clocked ticks (about 10.24 seconds) per table with changing voices. Overall correlations 0.999512–0.999793; samples are not identical and individual windows differ more. SFX, full songs and physical audio output are not covered.
- Non-STIM module isolation: 88,200 frames match unmodified libxmp exactly in the bounded test.
- Linux: Debian 12 build; AppImage first import and four table child launches under a network-isolated sandbox. Real GPU/audio and FUSE mounting are not covered.
- Browser: offline Chromium checks include real input, local import, persistence and fullscreen. Other browsers and hardware can differ.
- Windows: Wine smoke and silent installer/uninstaller tests; physical Windows unverified.
- ARM64: cross-build and QEMU smoke; physical Raspberry Pi/Batocera unverified.
- Runtime packages do not intentionally include original DAT/ADF game data.
