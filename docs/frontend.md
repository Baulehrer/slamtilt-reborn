# Shared original-style frontend — 064

Current frontend: **Slamtilt - Reborn**, Neo-90s Premium by default. Options → General selects Classic or reduced motion. See [Reborn release](reborn-release.md) and [review](reborn-review.md). Existing data paths and standalone aliases are retained.

RC3: F2 now imports all four tables directly from supported Windows DAT files, with no EXE required. Choose the DAT folder or its parent. See [current data requirements](dat-only-import.md). Earlier milestones below are retained for reference.

RC2: a supported Windows Retail import now configures all four tables, including Mean. Demo remains optional for Mean; EXE is required only during import. See [data requirements](data-import.md). The following064 section records the earlier frontend milestone.

Start `tools/slamtilt`, or extract `build/releases/slamtilt-four-tables-064.tar.gz`
and run `./slamtilt`. The combined package contains no original assets; native
import and play need no Python, Wine, emulator or checkout. This combined build
is verified on the current Linux host; older-ABI individual RCs remain frozen.

The main screen uses the actual supported Windows Retail `MENU.DAT`: metal logo,
four gold table buttons, Options and Quit. Art is aspect-preserved, with native
selection outlines and a small help/status footer. Arrow keys/Enter or mouse
select a table; O opens shared display/shader/DMD/audio/control options.
The native hit areas follow decoded artwork; original input rectangles are not
claimed. Before art is available a functional native fallback is shown.

F2 selects an original game folder. A supported Retail selection imports Pirate,
Space and Demon together. Mean gameplay uses the separately supported Windows
Demo; Retail Mean is deliberately not routed to the Demo engine. Imports use the
existing SHA-bound native decoders. Original menu art is read from user data.

Each table runs in its existing native frontend as a child process. The hidden
menu returns when the table exits. In a table, Escape opens options; **Main Menu**
or **F10** returns to selection. Pause, new-game, scoring and independent highscore
stores keep their existing table behavior. The extra exit action is enabled only
for shared-frontend sessions; standalone RC controls are unchanged.

`frontend.json` under the existing SDL preference directory stores data locations,
menu-art path and last table; shared `options.json` remains the display/input
settings store. `--config`, `--menu`, `--import` permit explicit paths.

Checks: `main_menu_flow`, `original_menu_pixels`, `port_options`; isolated archive
check `tools/verify_main_menu_package.py`. Four actual finite native children
start and return; source import/files, artwork pixels, options entry, missing-art
fallback and failed-import preservation are checked. Pixel proof/PE addresses:
`analysis/menu-layout.json`. No physical keyboard/mouse/listening claim.
