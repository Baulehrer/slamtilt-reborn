# Slamtilt - Reborn

Neo-90s Premium main menu and options, optional Classic menu, four playable tables. Combined Debian12-built package: `build/compat/releases/slamtilt-reborn-linux-x86_64-rc3.tar.gz`; launch `./slamtilt-reborn`. All four tables import from supported Windows DAT files only: no EXE is needed, even on first import. See [required data](docs/dat-only-import.md), [release and controls](docs/reborn-release.md), [review](docs/reborn-review.md) and [playtest scope](docs/reborn-playtest.md).

**Start all four tables:** `tools/slamtilt-reborn` (`tools/slamtilt` stays compatible). Original menu art, keyboard/mouse table selection, shared options and F2 data import. In a table: F10 or Options → Main Menu returns to selection. Standalone bundle: `build/releases/slamtilt-four-tables-064.tar.gz`. See [shared frontend](docs/frontend.md).

C++17, SDL3 and CMake. Mean has native ball physics, collision, flippers, finite single-player games, rules, DMD and audio. Complete table equivalence is still under verification; see [remaining work](analysis/mean-completion.json). Four original Windows/Amiga playfields are supported.

The Pirate now has a playable single-player Linux RC: `build/compat/releases/slamtilt-pirate-rc1/slampirate`. First start imports your own supported Windows Retail data through the native folder chooser. Shift controls flippers, Enter launches, Left Ctrl uses the earned Magnasaver, and Escape opens options. The program archive contains no original assets. See [Pirate release](docs/pirate-release.md) and the [bounded rule acceptance map](analysis/pirate-completion-contract.json).

Ace of Space now has a playable Linux RC1: `build/compat/releases/space-private-053/play-space --fullscreen` starts the prepared local game. The asset-free `slamtilt-space-rc1.tar.gz` imports your supported Windows Retail data natively. Shift controls flippers, Enter launches, Left/Right Ctrl invoke loop direction/Magnasaver, Escape opens display/shader/audio/controls options. All24 handbook contracts have bounded evidence; isolated package, Debian12 and real-time GPU/audio acceptance pass. See [Space release](docs/space-release.md). `tools/slamspace` remains the development launcher.

Night of the Demon RC1: `build/compat/releases/slamtilt-demon-rc1/slamdemon`. Native Retail data selection/import, fullscreen/shader/DMD options and audio are included. Shift controls flippers, Enter launches, Escape opens options. Twenty bounded handbook contracts cover36 Original-backed fixtures; the archive contains no original assets. See [Demon release](docs/demon-release.md) and [completion contract](analysis/demon-completion-contract.json).

The local relocatable Linux RC starts with `build/releases/mean-private-data/play-mean`. Program and private data are separate; see [release packaging](docs/release.md).

Start the prepared local game with `tools/slamplay`. Escape opens persistent options: desktop/exclusive fullscreen, resolution, aspect ratio, zoom, filtering, controls, music/SFX levels and DMD placement/colors. Default DMD placement is above the table, using original amber colors. Select overlay and drag the DMD while options are open. Default controls: Shift flippers, Enter launch/Mode Lock, Alt/Space nudge, R new game.

The arcade menu groups options into Display, Visual Effects, DMD, Audio and Controls.
Six shader presets range from Original/Clean HD to Neon Arcade and CRT Deluxe;
Soft Glow is the default. Hold V in the menu to preview the table. Apply saves,
Cancel restores. GPU effects use optional SDL >=3.4/Vulkan and `glslc` at build time;
the classic SDL renderer remains available. See [presentation](docs/presentation.md)
for controls, dependencies and verification commands.

Natural Pit Stop full65M route: `tools/slamplay --natural-mode-preview pit-stop` (includes two right nudges).

Natural Kickstart full60M route: `tools/slamplay --natural-mode-preview kickstart`.

Natural Cliff route/result: `tools/slamplay --natural-mode-preview cliff` (finite game; keyboard actions only).

Cliff result preview: `tools/slamplay --short-mode-preview cliff-jumper` (diagnostic state; original animation/30M award).

Diagnostic display previews: `tools/slamplay --short-mode-preview speed-jackpot`, `--short-mode-preview stock-car` or `--short-mode-preview pit-jackpot`. These seed known rule states and pause on an original DMD frame.

The bounded original collision decoder is generated locally from your executable with `build/venv/bin/python tools/lift_mean_normal.py EXE build/generated/mean_normal_lift.cpp`, then rebuild. Generated original code and user assets stay under `build/`.

```sh
cmake -S . -B build/native -DCMAKE_BUILD_TYPE=Debug
cmake --build build/native -j4
ctest --test-dir build/native --output-on-failure
tools/slamview 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT'
```

Use your original DAT directly, or extract corpus archives with `python tools/corpus_extract.py` (7z and `amitools` in `build/venv` required for ADFs). Amiga: `python tools/slamdecode.py ORIGINAL/Mean.Raw build/Mean.Raw`, then `tools/slamview build/Mean.Raw --amiga`. Up/Down or wheel scroll; Home/End jump; Escape quits. `--export image.bmp` exports a full table. No original assets belong in the source tree; user corpus and generated files are ignored.

Start with [ARCHITECTURE](docs/ARCHITECTURE.md), [STATUS](docs/STATUS.md), [formats](docs/file-formats.md), [evidence](docs/EVIDENCE.md) and [verification](docs/verification.md). Machine map: [analysis/map.json](analysis/map.json).

# Slamtilt-Corpus

Zusammenstellung aller auffindbaren Versionen und Varianten von **Slam Tilt**
(Liquid Dezign HB / 21st Century Entertainment, Amiga 1996, Windows 1997).

Stand: 07.10.2026 - 65 Dateien. 1.047.209.613 Bytes.

## Struktur

* **68040-DigitalCorruption** - 1 Datei(en). 901.120 Bytes
* **ADF v1.224 (TOSEC)** - 2 Datei(en). 1.802.240 Bytes
* **Amiga Action #83** - 3 Datei(en). 2.703.360 Bytes
* **Amiga Power #60** - 2 Datei(en). 1.802.240 Bytes
* **Aminet-Demo** - 1 Datei(en). 878.835 Bytes
* **Aminet-Readme** - 1 Datei(en). 7.113 Bytes
* **BTTR-v1.224-ADF (rekonstruiert)** - 4 Datei(en). 3.604.480 Bytes
* **DLM** - 6 Datei(en). 4.519.035 Bytes
* **DLM-alt** - 1 Datei(en). 901.120 Bytes
* **Dokumente** - 4 Datei(en). 27.094.468 Bytes
* **Extra** - 2 Datei(en). 9.257 Bytes
* **HD-Ninja** - 5 Datei(en). 4.505.600 Bytes
* **JoinSlamtilt** - 1 Datei(en). 6.506 Bytes
* **SPS-1151-IPF** - 5 Datei(en). 5.245.900 Bytes
* **SlamTilt_Join** - 1 Datei(en). 3.721 Bytes
* **SlamtiltJudge-1.4** - 1 Datei(en). 28.742 Bytes
* **cd32-master-2015** - 3 Datei(en). 12.854.335 Bytes
* **das-original-1999** - 1 Datei(en). 637.224.960 Bytes
* **demo-1.0** - 2 Datei(en). 1.767.561 Bytes
* **demo-1997** - 1 Datei(en). 2.407.597 Bytes
* **earok-2014** - 3 Datei(en). 8.271.855 Bytes
* **full-3.6** - 3 Datei(en). 7.270.942 Bytes
* **germany-1996** - 2 Datei(en). 201.874.914 Bytes
* **nts-patch-2000** - 1 Datei(en). 1.756 Bytes
* **nts_slamtiltcd-1.0** - 2 Datei(en). 3.542 Bytes
* **old-2003** - 1 Datei(en). 68.496 Bytes
* **old-2006** - 1 Datei(en). 49.089 Bytes
* **old-2009** - 1 Datei(en). 49.759 Bytes
* **pcaction-11-98** - 1 Datei(en). 65.460.188 Bytes
* **slampch-1.0** - 1 Datei(en). 41.419 Bytes
* **uk-1997** - 1 Datei(en). 36.188.160 Bytes
* **usa-expert-1997** - 1 Datei(en). 19.661.303 Bytes

## Inhalt nach Ordnern


### amiga/_extras/

* `Slam-HI.lha` - 1.161 Bytes - Aminet-Extra: Slam Tilt Highscore-Tool
* `SlamMan.lha` - 8.096 Bytes - Aminet-Extra: SlamMan

### amiga/demo/amiga-action-83/

* `Amiga Action #83 (1996-05)(IDG Media)(GB)(Disk 1 of 3)[Jun 1996].adf` - 901.120 Bytes - Amiga Action #83 Coverdisk (Disk 3 = Slam Tilt)
* `Amiga Action #83 (1996-05)(IDG Media)(GB)(Disk 2 of 3)[Jun 1996].adf` - 901.120 Bytes - Amiga Action #83 Coverdisk (Disk 3 = Slam Tilt)
* `Amiga Action #83 (1996-05)(IDG Media)(GB)(Disk 3 of 3)[Jun 1996][Slam Tilt].adf` - 901.120 Bytes - Amiga Action #83 Coverdisk (Disk 3 = Slam Tilt)

### amiga/demo/amiga-power-60/

* `Amiga Power #60 (1996-03-28)(Future Publishing)(GB)(Disk 1 of 2)[Apr 1996].adf` - 901.120 Bytes - Amiga Power #60 Coverdisk (Slam Tilt AGA Preview)
* `Amiga Power #60 (1996-03-28)(Future Publishing)(GB)(Disk 2 of 2)[Apr 1996].adf` - 901.120 Bytes - Amiga Power #60 Coverdisk (Slam Tilt AGA Preview)

### amiga/demo/aminet-slamdemo/

* `rview_slamtilt.txt` - 7.113 Bytes - Aminet-Readme (Versionshistorie v1.224)
* `slamdemo.lha` - 878.835 Bytes - Aminet game/demo/slamdemo

### amiga/historical-mods/68040-DigitalCorruption/

* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 1 of 5)[f 68040 Digital Corruption][h DLM].adf` - 901.120 Bytes - 68040-Fix von 'Digital Corruption' + DLM-Hack, Disk 1

### amiga/historical-mods/DLM-alt/

* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 1 of 5)[h DLM][a].adf` - 901.120 Bytes - DLM-Hack, alternative Fassung (a) von Disk 1

### amiga/historical-mods/DLM/

* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 1 of 5)[h DLM].adf` - 901.120 Bytes - DLM-Hack/Crack, Disk 1/5
* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 2 of 5)[h DLM].adf` - 901.120 Bytes - DLM-Hack/Crack, Disk 2/5
* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 3 of 5)[h DLM].adf` - 901.120 Bytes - DLM-Hack/Crack, Disk 3/5
* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 4 of 5)[h DLM].adf` - 901.120 Bytes - DLM-Hack/Crack, Disk 4/5
* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 5 of 5)[h DLM].adf` - 901.120 Bytes - DLM-Hack/Crack, Disk 5/5
* `dlm-slamtilt.lha` - 13.435 Bytes - DLM-Patch (Archiv)

### amiga/historical-mods/HD-Ninja/

* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 1 of 5)[m HD Ninja][HD].adf` - 901.120 Bytes - HD-Installation von Ninja, Disk 1/5
* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 2 of 5)[m HD Ninja][HD].adf` - 901.120 Bytes - HD-Installation von Ninja, Disk 2/5
* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 3 of 5)[m HD Ninja][HD].adf` - 901.120 Bytes - HD-Installation von Ninja, Disk 3/5
* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 4 of 5)[m HD Ninja][HD].adf` - 901.120 Bytes - HD-Installation von Ninja, Disk 4/5
* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 5 of 5)[m HD Ninja][HD].adf` - 901.120 Bytes - HD-Installation von Ninja, Disk 5/5

### amiga/patches/JoinSlamtilt/

* `JoinSlamtilt.lha` - 6.506 Bytes - Aminet game/patch/JoinSlamtilt

### amiga/patches/SlamTilt_Join/

* `SLAMTILT_Join.lha` - 3.721 Bytes - Aminet game/patch/SlamTilt_Join

### amiga/patches/SlamtiltJudge-1.4/

* `SlamtiltJudge.lha` - 28.742 Bytes - Aminet game/patch/SlamtiltJudge v1.4

### amiga/patches/nts_slamtiltcd-1.0/

* `nts_slamtiltcd.lzh` - 1.756 Bytes - Aminet game/patch/nts_slamtiltcd - CD32-Pad-Support
* `nts_slamtiltcd.readme` - 1.786 Bytes - Readme zum nts-Patch (Aminet)

### amiga/patches/slampch-1.0/

* `slampch.lha` - 41.419 Bytes - Aminet game/patch/slampch - Patch (v1.2xx)

### amiga/retail/ADF-v1.224-TOSEC/

* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 1 of 5).adf` - 901.120 Bytes - TOSEC-ADF Diskettenimage 1/5 (unveraenderter Dump)
* `Slam Tilt v1.224 (1996)(21st Century)(AGA)(Disk 4 of 5).adf` - 901.120 Bytes - TOSEC-ADF Diskettenimage 4/5 (unveraenderter Dump)

### amiga/retail/BTTR-v1.224-ADF/

* `SlamTil2.adf` - 901.120 Bytes - BTTR-Image Disk 2/5 - bit-identisch mit dem DLM-Image (SHA1 b343d9d598dc0fcfbb42a1e7148346d6df0ca6c1)
* `SlamTil3.adf` - 901.120 Bytes - BTTR-Image Disk 3/5 - bit-identisch mit dem DLM-Image (SHA1 1da32b049b70ed81e6d9b92bd5b3cd3ce1c62c64)
* `SlamTil4.adf` - 901.120 Bytes - BTTR-Image Disk 4/5 - bit-identisch mit dem DLM-Image (SHA1 5015b7c024da10b293b7659ea8e67a0c74594b08)
* `SlamTil5.adf` - 901.120 Bytes - BTTR-Image Disk 5/5 - bit-identisch mit dem DLM-Image (SHA1 bd439d08a55c2127acae2904b6cb04522e6f7cf9)

### amiga/retail/SPS-1151-IPF/

* `Slamtilt_Disk1.ipf` - 1.049.180 Bytes - SPS/CAPS-IPF-Image (MASTER)
* `Slamtilt_Disk2.ipf` - 1.049.180 Bytes - SPS/CAPS-IPF-Image (MASTER)
* `Slamtilt_Disk3.ipf` - 1.049.180 Bytes - SPS/CAPS-IPF-Image (MASTER)
* `Slamtilt_Disk4.ipf` - 1.049.180 Bytes - SPS/CAPS-IPF-Image (MASTER)
* `Slamtilt_Disk5.ipf` - 1.049.180 Bytes - SPS/CAPS-IPF-Image (MASTER)

### amiga/whdload/demo-1.0/

* `SlamTiltDemo_v1.0_AGA.lha` - 888.726 Bytes - Retroplay-WHDLoad-Pack der Demo v1.0
* `slamdemo.lha` - 878.835 Bytes - Demo (Aminet-Quelle)

### amiga/whdload/full-3.6/

* `SlamTilt_v3.6_AGA_1151.lha` - 3.597.543 Bytes - Retroplay-WHDLoad-Pack v3.6 (SPS 1151)
* `SlamTilt_v3.6_AGA_2MB_1151.lha` - 3.597.634 Bytes - Retroplay-WHDLoad-Pack v3.6 (SPS 1151)
* `whd_SlamTilt.lha` - 75.765 Bytes - WHDLoad-Slave, aktuelle Revision (2013)

### amiga/whdload/old-2003/

* `whd_SlamTilt-20031019.lha` - 68.496 Bytes - WHDLoad-Slave, historische Revision

### amiga/whdload/old-2006/

* `whd_SlamTilt-20060329.lha` - 49.089 Bytes - WHDLoad-Slave, historische Revision

### amiga/whdload/old-2009/

* `whd_SlamTilt-20090515.lha` - 49.759 Bytes - WHDLoad-Slave, historische Revision

### cd32/cd32-master-2015/

* `Slam Tilt v1.224 (2015-05-24)(21st Century)[f www.cd32.co.uk].7z` - 5.299.136 Bytes - CD32-Fassung 2015-05-24 (TOSEC-ISO, enthaelt ISO+CUE)
* `Slam Tilt v1.224 (2015-05-24)(21st Century)[f www.cd32.co.uk].cue` - 127 Bytes - aus dem TOSEC-ISO-7z entpackt
* `Slam Tilt v1.224 (2015-05-24)(21st Century)[f www.cd32.co.uk].iso` - 7.555.072 Bytes - aus dem TOSEC-ISO-7z entpackt

### cd32/earok-2014/

* `Slam Tilt v1.224 (2014-09-17)(21st Century)[f www.cd32.co.uk].7z` - 3.874.672 Bytes - CD32-Konversion von Earok, 2014-09-17 (TOSEC-ISO, enthaelt ISO+CUE)
* `Slam Tilt v1.224 (2014-09-17)(21st Century)[f www.cd32.co.uk].cue` - 127 Bytes - aus dem TOSEC-ISO-7z entpackt
* `Slam Tilt v1.224 (2014-09-17)(21st Century)[f www.cd32.co.uk].iso` - 4.397.056 Bytes - aus dem TOSEC-ISO-7z entpackt

### cd32/nts-patch-2000/

* `nts_slamtiltcd.lzh` - 1.756 Bytes - nts_slamtiltcd 1.0 (Aminet, 2000): CD32-Pad-Support fuer Slam Tilt CD

### win95/_dokumente/

* `Slam Tilt - Windows Handbuch (EN).pdf` - 346.875 Bytes - Offizielles Handbuch (Windows, EN, PDF)
* `Slam_Tilt_Fix_Win_EN.zip` - 207.360 Bytes - Offizieller Fix/Patch (Windows)
* `Slam_Tilt_Win_RIP_EN.zip` - 7.459.400 Bytes - Windows-Fassung als RIP (installiert, EN)
* `Slam_Tilt_Win_ROM_EN.zip` - 19.080.833 Bytes - Windows-Fassung (ROM/Dateien, EN)

### win95/das-original-1999/

* `SlamTilt Resurrection (Genios budget) - STR Demon.iso` - 637.224.960 Bytes - SlamTilt Resurrection (3D-Remake 1999, Budget-Neuauflage), ISO

### win95/demo-1997/

* `Slam Tilt Demo (Windows. 1996) - SLAMTILT.rar` - 2.407.597 Bytes - Windows-Demo (1996), RAR-Archiv

### win95/germany-1996/

* `SlamTilt (EU release. multilingual) - SLAMTILT.bin` - 201.874.512 Bytes - EU-/Multilanguage-CD (BIN), Track-Image
* `SlamTilt (EU release. multilingual) - SLAMTILT.cue` - 402 Bytes - Cue-Sheet zur BIN

### win95/pcaction-11-98/

* `PC Action 11-98 (Heftscan) - PCAction9811.rar` - 65.460.188 Bytes - Heftscan der Ausgabe 11/98 (PDF im RAR); Heft-CD selbst nicht beschaffbar

### win95/uk-1997/

* `Slam Tilt Pinball (Windows CD. EN) - SLAM_TILT.ISO` - 36.188.160 Bytes - Windows-CD-ROM-Fassung (EN), ISO, Disc-ID SLAM_TILT

### win95/usa-expert-1997/

* `Slam Tilt Pinball (PC. 1996) - Slam_Tilt_Pinball_1996.7z` - 19.661.303 Bytes - PC-Fassung (US-Vertrieb Expert Software, 1997), 7z

## Nicht beschaffbar

Siehe die `_NICHT-BESCHAFFBAR.md`-Dateien in den jeweiligen Ordnern:
* `amiga/retail/BTTR-v1.224-ADF/` (Fuenf-Disketten-Satz von Back to the Roots)
* `win95/pcaction-11-98/` (Magazin-CD) - nur Heftscan enthalten
* `win95/pcgamesplus-03-99/` (Magazin-CD)
* `win95/japan-1997/` (keine JP-Version nachweisbar)
* `win95/budget-2001/` (keine 2001 datierte Ausgabe verifizierbar)

## Pruefsummen

Vollstaendige SHA256-/SHA1-Pruefsummen aller Dateien: `inventory.json`.
Detailquellen je Datei: `QUELLEN.md`.

## RE-Artefakte

Priorisierte Artefaktliste fürs Reverse Engineering (inkl. Abgleich mit diesem Corpus
und offenen Beschaffungslücken): `RE-Artefakte.md`.

## Nachbeschaffung 07.10.2026

Neu aufgenommene Artefakte (u. a. `slamtilthd.lha` v2.0, `DC-STFIX.DMS`, vollständiger
BTTR-Fünf-Disketten-Satz inkl. `SlamTil1.adf`, Win95-Demo vom CD-Gamer-Träger) sowie
Quellen und Prüfsummen: `NACHBESCHAFFUNG-2026-10-07.md`,
`inventory-nachbeschaffung-2026-10-07.json`.

Priorisierte Artefaktliste fürs Reverse Engineering: `RE-Artefakte.md`.


Natural Stock Car75M completion preview: `tools/slamplay --natural-mode-preview stock-car` (legal-input replay, paused original NO CARS LEFT DMD page).

Natural SPEED eightball/triplelock40M preview: `tools/slamplay --natural-mode-preview speed` (fresh legal-input replay through Formula1win and fiveletters; paused original40M DMD).

Natural Monster Car sixshot125M preview: `tools/slamplay --natural-mode-preview monster` (fresh Returnlock/input replay, paused original final50M DMD page).

Natural Liquid Rally preview: `tools/slamplay --natural-mode-preview rally` (six correct targets/two wrong turns; original22.5M finalbonus,112.5M subtotal).

Natural Offroad multiball preview: `tools/slamplay --natural-mode-preview offroad` (original15M reward; Windows3additional/fourtotal balls, handbook says3).

Natural Chicken Race preview: `tools/slamplay --natural-mode-preview chicken` (three real timed races,140.208M subtotal, original56.078M finalaward).

Natural fifth-gear / extra-ball-ready preview: `tools/slamplay --natural-mode-preview gears`. Replays legal inputs; shows original colored DMD animation.

Natural KICK / left-lane rescue preview: `tools/slamplay --natural-mode-preview kickback` (legal-input activation and actual fourth-ball rescue, original KICK BACK animation).

Natural GOAL-bonus → LaneSaver fence preview: `tools/slamplay --natural-mode-preview laps`. This route earns GOAL after three lap captures; complete lap-built goals remain partial. Diagnostic fence/upper-reward preview: `tools/slamplay --lane-saver-preview`.

Full natural goal ladder and extra-ball preview: `tools/slamplay --natural-mode-preview goals` (GOAL-bonus firstgoal, lap-built goals2/3, both extra credits earned).

Natural Million Skull preview: `tools/slamplay --natural-mode-preview skull` (original15M frame; complete fixture also checks expiry and restart at5M).
