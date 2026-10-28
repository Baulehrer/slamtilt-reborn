#!/usr/bin/env python3
"""Bounded original ball-pair response; original-derived C++ stays local."""
from pathlib import Path
import lift_mean_flippers as g
r=Path(__file__).resolve().parents[1]
g.RANGES=[(0x408bfc,0x408e70),(0x40964c,0x40968c),(0x40968c,0x4096e8)]
code,_=g.generate(next((r/'build/corpus/win95/demo-1997').rglob('SLAMTILT.EXE')))
code=code.replace('physics/flipper_lift.h','physics/mean_minigame_lift.h').replace('FlipperLift','MeanMinigameLift').replace('flipper_','ball_pair_')
(r/'build/generated/mean_ball_pair.cpp').write_text(code)
print(len(code))
