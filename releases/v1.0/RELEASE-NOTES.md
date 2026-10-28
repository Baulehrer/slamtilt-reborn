# Slamtilt - Reborn 1.0

Four playable tables: **Mean Machines, The Pirate, Ace of Space and Night of the Demon**. New arcade menu, configurable controls, fullscreen/zoom/aspect options and a movable, colored DMD.

## Downloads

- **Windows x86_64:** installer or portable ZIP. Unsigned; SmartScreen may warn.
- **Linux x86_64:** AppImage (glibc2.34+). Make executable; `--appimage-extract-and-run` also works without FUSE.
- **Browser preview:** one playable HTML file. Open locally and choose your game files. Requires WebAssembly JSPI; tested in Chromium155.
- **ARM64 preview:** Linux archive with Raspberry Pi/Batocera instructions. Keyboard controls; physical hardware remains untested.

## Your original game files

Windows: `MAIN.DAT` plus the desired table DATs. No original Windows EXE needed. Amiga: the complete supported retail v1.224 DLM five-ADF set. Game data is not included or uploaded; import stays local. Amiga artwork/sound use the shared native engine, with original Amiga gameplay parity unverified.

**Shift:** flippers · **Enter:** launch · **Esc:** options · **F10:** table menu. Native import: F2. Browser import: Choose game files.

Windows installer/import/table-cycle checks pass under Wine; ARM64 checks pass under QEMU. Actual Windows and Raspberry Pi/Batocera hardware remain unverified. Browser DAT and ADF acceptance each passes18 checks, including real ball movement, options, fullscreen/table switching and saved-data reload offline. Windows/browser use compatible rendering rather than advanced GPU filters.

Verify downloads against **SHA256SUMS**. Source build and screenshots are in the repository README.

## Screenshots

![Main menu](https://raw.githubusercontent.com/Baulehrer/slamtilt-reborn/v1.0/docs/screenshots/main-menu.png)

![Options](https://raw.githubusercontent.com/Baulehrer/slamtilt-reborn/v1.0/docs/screenshots/options-menu.png)

![Mean Machines](https://raw.githubusercontent.com/Baulehrer/slamtilt-reborn/v1.0/docs/screenshots/mean-machines.png)

![The Pirate](https://raw.githubusercontent.com/Baulehrer/slamtilt-reborn/v1.0/docs/screenshots/the-pirate.png)

![Ace of Space](https://raw.githubusercontent.com/Baulehrer/slamtilt-reborn/v1.0/docs/screenshots/ace-of-space.png)

![Night of the Demon](https://raw.githubusercontent.com/Baulehrer/slamtilt-reborn/v1.0/docs/screenshots/night-of-the-demon.png)
