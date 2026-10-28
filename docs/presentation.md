# Native presentation

Escape opens the English arcade options menu. Tab / Shift-Tab select categories;
Up/Down navigate; Left/Right edit; Enter activates the selected control or footer
button. Mouse hover, click, wheel and slider dragging are supported. Apply saves;
Cancel / Escape / Backspace restore the settings present when the menu opened.
Hold V for an unobstructed preview of the paused table. All original options remain.

## Effects

| Preset | Look |
|---|---|
| Original | Unprocessed table and DMD |
| Clean HD | Sharp bilinear scaling and bounded sharpening |
| Soft Glow | Subtle bloom and color enhancement; default |
| Neon Arcade | Stronger bloom and saturation |
| CRT Classic | Scanlines, RGB mask and glow |
| CRT Deluxe | CRT plus mild curvature, vignette and color fringe |

Changing an individual table-effect slider selects Custom. DMD glow is independent;
CRT geometry, mask, fringes, saturation and sharpening never affect the DMD. The
Original preset or zero global strength bypasses all effects. Filtering, camera,
zoom and DMD layout remain ordinary presentation settings.

Low/Balanced/High use bloom targets at 1/8, 1/4 and 1/2 displayed size (capped at
2048 pixels per axis). Bright extraction and two separable blur passes feed a
composite shader; zero bloom skips those passes. Menus and highscores are drawn
AFTER effects. Simulation coordinates and the 200Hz gameplay tick are unchanged.

## Build and fallback

SDL >=3.4 and `glslc` enable the optional Vulkan/SPIR-V GPU renderer. CMake embeds
compiled shaders and the licensed Inter UI fonts; no compiler, network or system
fonts are needed at runtime. `-DSLAM_ENABLE_GPU_EFFECTS=OFF` builds the classic path.
SDL versions/backends without GPU support retain the standard renderer and menu;
the menu reports shader availability. Existing version-one options files receive
new visual defaults, while preserving their existing settings.

Font and dependency provenance: `assets/fonts/README.md`, `assets/fonts/OFL.txt`,
`third_party/stb/README.md`; stb's dual MIT/public-domain license is in its header.
No original game assets or generated original code were added.

## Reproducible checks

- `ctest --test-dir build/native --output-on-failure`: includes menu input,
  persistence, malformed settings, old-file migration and renderer fallback.
- `build/native/presentation_probe --require-gpu build/arcade-acceptance/gpu-contract.json`:
  real GPU checks for all 18 preset/quality combinations, pixel identity for
  Original/zero strength, DMD isolation, repeated frames, clipping and target resize.
- `tools/slamplay --visual-preset 5 --require-gpu --no-audio --frames 180 --capture build/crt.bmp --presentation-report build/crt.json`
- `tools/slamplay --menu-category 1 --visual-preset 2 --frames 6 --capture build/menu.bmp`
- `--preview-size 1366x768` changes preview window dimensions. Reports record actual
  drawable pixels; compositor tiling/HiDPI can override the requested window size.

Frame reports include renderer, actual output dimensions and median/p95 CPU frame
wall times including presentation. Runs longer than 60 frames exclude 30 warmup
frames from quantiles. These are local observations, not GPU timestamp profiling
or a guarantee for other hardware. Test screenshots/reports stay under `build/`.
