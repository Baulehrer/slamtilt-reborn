# Scoring

Saved highscores use six bytes of packed BCD, big decimal digit first, followed by three initials. This is directly supported by two independent bundled utility sources and observed nontrivial scores. The same nine-byte payload survives in Windows CFG, despite different record stride and surrounding format. See `highscore-format.md` and executable `tools/slamscores.py`.

Status: saved-score representation UNDERSTOOD; native reader IMPLEMENTED and verified against 66 corpus files. Runtime score representation remains UNKNOWN. A save format does not establish the format used while playing.

BCD supports 12 digits (0..999,999,999,999). No overflow policy has been established. No claims yet about bonus, multiplier, jackpot arithmetic or DMD glyph conversion. UNPK/PACK or BCD arithmetic in game code must be tied to actual game state before assigning runtime semantics.

Port strategy: use an explicit integer score type with validated packed-BCD import/export; retain original score granularity until runtime traces establish arithmetic and caps. Next high-value step is tracing the original save routine to the live score storage, then following callers of score updates and the DMD formatter. Saved-score interoperability needs no further utility reverse engineering.
