# Amiga ADF import

Select the folder containing all five retail v1.224 DLM ADFs in the main menu (F2), or run:

```
slamimport --adf /path/to/five-adfs /path/to/new-private-output
```

The importer reads the disks without modifying them. No Windows DAT/EXE files, Python, Kickstart, Wine or emulator are required. Shared fonts are data inside the Amiga executable **on the disks**; the importer reads its DATA hunk and never executes it. Consequently the disk set must include that file. Ball graphics come from Matrix.Dat.

The main menu retains PC and Amiga sources separately for each table; F3 switches available sources. Options are shared, highscores are separated. The standalone chooser also accepts the disk folder. Private imported data must not be distributed with the port.

Scope: original Amiga playfields, ball, flippers, lamps, mapped scenes and audio feed the existing shared native engine. This is not verified original-Amiga physics/rule equivalence. The adapter now expands 1,732 original compressed DMD bank frames and all twelve Mean contact-animation frames. Thirteen additional Pirate frames preserve the original overlapping streams. A seven-frame Amiga tire-repair sequence retains its original artwork and “TIRE” spelling versus PC “TYRE”. Some remaining individual scene fragments are unmapped. Original contact palette indices are retained; full Amiga mask/transparency semantics remain unverified. These limitations are not replaced with PC assets.

Verified: DLM five-disk import, overwrite/missing-set rejection, four native 4,000-step sessions, persisted menu reload and four child sessions. The independent reader/SLAM comparison also passes the HD-Ninja disk set; **full HD-Ninja import is rejected** because its shared graphics revision differs. Other ADF revisions remain unverified.

New imports use asset revision2 forMean/Pirate/Space and revision3 forDemon. Older RC4/RC5 private imports remain supported. Demon revision3 restores two complete DMD frames identified by observed reads. RC4 introduced the ADF adapter; subsequent acceptance and remaining limits are recorded separately. Older archives/evidence remain unchanged.
