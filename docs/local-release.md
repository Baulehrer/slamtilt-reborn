# Local release candidate

Local staging: `build/github-release/v0.1.0-rc1/`. Nothing is published.

- `assets/`: unsigned Windows installer + portable ZIP, Linux AppImage, ARM64 preview and self-contained playable HTML.
- `README.md`, `RELEASE-NOTES.md`: audience-facing descriptions.
- `screenshots/`: six actual menu/options/table captures.
- `verification/`: exact test scope and reports; hardware limitations are explicit.
- `release.json`, `assets/SHA256SUMS`: final artifact inventory, generated after acceptance.

Original game data is excluded from runtime downloads. Browser import stays local. ARM64 physical Pi/Batocera operation and actual Windows hardware are not verified by QEMU/Wine.

Build recipes: [packaging](../packaging/README.md). Browser acceptance: `node tools/verify_web_release.cjs --html build/github-release/v0.1.0-rc1/assets/Slamtilt-Reborn.html`. Seal only after final artifacts pass: `python3 tools/seal_local_release.py build/github-release/v0.1.0-rc1`.

Final acceptance:18 browser checks with Windows DATs and18 with the supported five-ADF set, including real ball movement, options, persistent data reload and page fullscreen. Browser target uses JSPI/native Wasm exceptions and requires a compatible browser (verified Chromium155). Native application targets and4 focused regression tests pass. All5 artifact hashes are matched to their acceptance proofs by the sealing tool. Windows/browser builds use compatible rendering; advanced GPU filters are unavailable in those packages.
