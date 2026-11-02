# 1.4 acceptance

- Source: tag `v1.4`, commit `cf14efc290326477512c098dd0c4da09a71e8817`. Release artifacts contain no original game files.
- Audio: bounded original/native tracker, sound and final-mixer comparisons cover all four tables. Full gameplay cadence, physical audio output and Amiga audio parity remain unverified.
- Linux x86-64: Debian 12 compatibility build; actual AppImage extract-and-run, isolated first import and four table child launches passed. FUSE mounting and real GPU/audio were not checked in this run. The packaged ABI ceiling is GLIBC 2.34, GLIBCXX 3.4.29 and CXXABI 1.3.9.
- Browser: Chromium passed 19 offline checks each for Windows DAT and five Amiga ADF inputs, including all four tables, interaction, persistence and fullscreen. Vivaldi was not verified in this run.
- Windows: unsigned per-user installer and portable ZIP; Wine first import, four table launches, installation and uninstallation passed. Physical Windows is unverified.
- ARM64: QEMU menu, virtual controller, audio backend and four short table launches passed. Physical Raspberry Pi/Batocera is unverified.
- Checksums in `SHA256SUMS` identify the published artifacts; GitHub upload digests were compared against the local files.
