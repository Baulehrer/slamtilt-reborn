# Version1.0 acceptance

- Clean public source export builds all three native programs without original game data. Public options, highscore and frontend-safety tests pass3/3.
- Windows1.0 unsigned NSIS installer: install, launch, shortcut/registry checks, uninstall and profile retention pass under Wine. Physical Windows hardware/GPU unverified. Runtime payload unchanged from prior four-table DAT import/cycle proof.
- Linux AppImage: isolated, network-disabled DAT first import and all four child sessions pass.
- Browser: exact HTML hash in both reports; Windows DAT and five-ADF import each pass18 checks, including all four simulation traces, actual ball motion, options, F10, persistent storage and fullscreen. Headless Chromium155 with JSPI; physical speakers/other browsers unverified.
- ARM64: AArch64 binaries, QEMU menu/import/four-table/backend probes pass. Physical Raspberry Pi/Batocera graphics, sound and controller testing remains open.
- No original game DAT/ADF/EXE/media files are distributed. Windows/browser advanced GPU filters are unavailable.

All runtime artifacts match SHA256SUMS. Windows installer bootstrap carries1.0.0.0 version metadata; the game payload is unchanged. Native package and browser proof hashes are checked by tools/seal_local_release.py before publication.
