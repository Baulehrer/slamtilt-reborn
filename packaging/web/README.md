# Single-file browser build

Run `packaging/web/build.sh` from the repository. It uses the pinned Emscripten4.0.20 Docker image, SDL3 3.4.18 sources prepared by the ARM64 build, libxmp sources in `build/libxmp`, and the nlohmann/json development headers prepared in `build/web-release/headers`. No game data is embedded.

The result is `build/web-release/native/Slamtilt-Reborn.html`. Add the bundled dependency notices with:

```sh
python3 packaging/web/finalize.py build/web-release/native/Slamtilt-Reborn.html build/github-release/v0.1.0-rc1/assets/Slamtilt-Reborn.html
```

Open that single file locally in a desktop browser. Import your own DAT files or supported complete ADF set. The native gameplay is compiled to WebAssembly; imported data and saves use local browser storage. Some browsers restrict persistence for local files. Keep a backup of your game files.

Browser rendering uses the compatible SDL renderer; native GPU effects are unavailable. Keyboard controls are required. Audio starts after user interaction. Gameplay objects are optimized at compile time. Link-time optimization is disabled for quick builds. The browser build also compiles libxmp setjmp/longjmp for native Wasm exceptions. JSPI and native WebAssembly exceptions preserve C++ stack state across browser waits. This build requires WebAssembly.Suspending and WebAssembly.promising; unsupported browsers show a capability message.

Acceptance: `node tools/verify_web_release.cjs --html PATH`. The runner requires Chromium and Playwright Core, checks offline loading, actual first import, all four table sessions and storage reload. It uses private local game data only for testing, never for the output HTML.

The build applies `patch_sdl.py` to SDL's Emscripten backend. It prevents SDL canvas teardown from exiting fullscreen owned by the persistent HTML document. Native backends are unaffected. The original SDL archive remains unchanged.
