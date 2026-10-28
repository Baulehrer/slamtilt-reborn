# Gameplay accelerators from the corpus

Audit 2026-10-12. Machine-readable priorities: `analysis/corpus-accelerators.json`.

| Priority | Evidence | Practical saving | Limit |
|---|---|---|---|
| 1 | Original USA PDF, SHA `be23f47fba12a5749bacae511b41fd00a8f3f7b03c1abdc1edf9db0aecfcd869`; all four rule chapters | Use named shots, mode starts and awards as test expectations; analyze only missing event chains | Narrative/OCR is not a binary field map |
| 2 | Complete bounded Demo step and magnet ranges match Retail/Fix after address normalization | Address adapters and replay existing physics fixtures; spend next-table work on data and callbacks | Redirected callees/global layouts still need verification |
| 3 | Shared car-dispatcher variant1 differs in one semantic byte: Demo418848×2, Retail425288/Fix425658×4 | Inspect one scaler instead of reanalyzing4390bytes | 120 bounded arithmetic cases prove decrement; Drag Race variant2 bypasses this branch; port unchanged |
| 4 | Six Windows MEAN.DAT files freshly hash-identical | Reuse all existing Mean data decoders and geometry for retail | Other tables have different data |
| 5 | Four Amiga overlays share likely directory origin island+8 and slot-entry signatures | Validate shared ABI once, produce four entry maps | Directory consumers not yet proven |

The previously used nine-page Windows PDF is not the strongest rules source. The USA PDF has complete table chapters: zero-based pages6–11 Mean,12–17 Pirate,18–23 Space,24–31 Demon. Extracted text stays under ignored `build/manual-rules/`. Source/index: `analysis/table-rule-oracles.json`.

Mean's magnet/25M–10M–25M sequence strongly identifies the implemented phase1 as Kickstart. Video racing, repeated flipper acceleration and a progressively harder record strongly identify phase2 as Drag Race. Official main-mode numbers must not be confused with internal engine modes. Manual narrative is checked against binary behavior, not used to replace proven clock/input semantics.

No gameplay source shortcut was established in SlamMan or the patch collections. SlamMan is highscore management; the `demon-multiball` member name suggests a music module, not a gameplay modification. Resurrection remains a separate product. Avoid spending time on duplicate archives and already solved hardware patches.

Reproduce the Windows audit with `build/venv/bin/python tools/audit_windows_corpus_levers.py`. It checks hashes and records full bounded-region hashes, not only matching prefixes. Reports: `analysis/corpus-windows-levers.json`, `analysis/corpus-amiga-levers.json`, `analysis/corpus-amiga-table-entry-candidates.json`.

Mean shared41b8d0 event/reward dispatch has since been implemented and verified. Next primary action: descriptor-driven table profiles, then Pirate contact/flipper adapters.


## Second pass: direct gameplay shortcuts

| Lever | New proof | Saves |
|---|---|---|
| Shared table descriptor | All four full initializers executed to return, loader/allocation adapters only. Shared switch consumer409823..40983e uses descriptor+4 → engine+0 → callback[layer]. | Geometry and switch entry points extracted once for all tables; `analysis/table-profiles.json` is ready for a data-driven port adapter. |
| Same data across releases | Fresh24 DAT hashes: MAIN/MEAN sixcopies each, PIRATE/SPACE/DEMON fourcopies each; one hash family per basename. USA EXE=RIP; UK EXE=ROM. | Reuse each data parser/profile across tested releases; keep one retail oracle per actual code family. |
| Minigame revision isolated |120 original Demo/Retail/Fix arithmetic traces prove counter decrement×2 vs×4; two original dispatcher traces prove the changed block belongs to3a4==1. | Target a small version profile + trajectory comparison; do not modify Drag Race based on this byte. |

Correction to the first pass: the broad dispatcher range is shared by car variants. At418105,3a4==1 selects418113 (includes418848); variant2 (known Drag Race) selects418a81 and skips the scaler. Counter43effc remains an offset name; its highWORD feeds the20-marker draw loop, suggesting a resource display. The exact upstream projection/full trajectory still needs verification.

Additional address corrections: Demon initializer40febc (not40fec0); Pirate layer-switch callbacks437460/437bfc/438954 (not4364c4, which occupies engine+0c). Motion entry format remains PARTIAL; DWORDs are not uniformly pointers. Base geometry records do not imply all special callback-created layers are covered.

Windows USA Control.txt also provides practical oracle controls: Ctrl special actions, F12 toggle autozoom, P pause, Alt/Space nudge. These are textual control evidence, not a recovered input implementation. German SLAMTILT.EXE is an installercontainer, not another gameplay EXE; its inner payload was not inspected this pass.

Reproduce: `tools/audit_table_descriptors.py`, `tools/audit_table_data_families.py`, `tools/verify_corpus_minigame_scaler.py` (first/third use build/venv/bin/python). All passed. Source evidence stays in `analysis/corpus-{table-descriptor-levers,table-data-families,minigame-scaler}.json`; priorities `analysis/corpus-accelerators-v2.json`. No native gameplay changed during this audit.
