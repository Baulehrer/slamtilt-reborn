#!/usr/bin/env python3
"""Bounded Retail flipper intermediate; original-derived output stays under build/."""
from pathlib import Path
import lift_mean_flippers as lift
R=Path(__file__).resolve().parents[1]
exe=R/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
lift.RANGES=[(a+0xc98,b+0xc98) for a,b in lift.RANGES]
code,image=lift.generate(exe,'185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6')
out=R/'build/generated/retail_flippers.cpp';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(code)
print('Generated bounded Retail C++:',len(code),'bytes')
