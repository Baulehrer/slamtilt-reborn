#!/usr/bin/env python3
"""Accelerated comparisons only; GPU realtime is deliberately orchestrated separately."""
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for table in ['demon','space','pirate']:
 for case in ['primary','variant-1','variant-2']:
  subprocess.run([sys.executable,ROOT/'tools/verify_reborn_playtest.py','--table',table,'--case',case],check=True)
for case in ['primary','variant-1','variant-2']:
 subprocess.run([sys.executable,ROOT/'tools/verify_reborn_mean.py','--case',case],check=True)
