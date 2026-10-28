#!/usr/bin/env python3
"""Reuse the actual Original camera verifier without overwriting its frozen artifact."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'tools/verify_mean_camera.py'
text=source.read_text().replace('analysis/traces/mean-camera-original.json','analysis/traces/reborn-mean-camera-original.json')
sys.argv=[str(source),str(ROOT/'build/native/mean_camera_probe')]
exec(compile(text,str(source),'exec'),{'__file__':str(source),'__name__':'__main__'})
