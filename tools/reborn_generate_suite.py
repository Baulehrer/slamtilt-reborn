#!/usr/bin/env python3
"""Bounded legal Original/native suite, keeping public reports compact."""
import argparse,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--oracle-only',action='store_true');args=p.parse_args()
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for table in ['demon','space','pirate']:
 for variant,steps,case in [(0,60000,'primary'),(1,4000,'variant-1'),(2,4000,'variant-2')]:
  subprocess.run([ROOT/'build/venv/bin/python',ROOT/'tools/reborn_retail_oracle.py','--table',table,'--steps',str(steps),'--variant',str(variant),'--track'],check=True)
  if not args.oracle_only:subprocess.run([sys.executable,ROOT/'tools/verify_reborn_playtest.py','--table',table,'--case',case],check=True)
