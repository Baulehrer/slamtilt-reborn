#!/usr/bin/env python3
"""Ensure all three source-identity checks reject changed local music inputs."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'tools/verify_amiga_music_banks.py'
DECODED=ROOT/'build/decoded/full'
AMIGA=ROOT/'build/amiga-read-verified-data'
WINDOWS=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT'

def flip(path):
 data=bytearray(path.read_bytes());data[len(data)//2]^=1;path.write_bytes(data)

def main():
 with tempfile.TemporaryDirectory(prefix='slam-music-integrity-') as name:
  tmp=Path(name);decoded=tmp/'decoded';decoded.mkdir()
  for table in ('Mean','Pirate','Space','Demon'):
   for ext in ('Raw','Bin'):shutil.copy2(DECODED/f'{table}.{ext}',decoded/f'{table}.{ext}')
  flip(decoded/'Space.Raw')
  cases=[['--decoded',str(decoded)]]
  amiga=tmp/'amiga';amiga.mkdir();shutil.copy2(AMIGA/'amiga-import.json',amiga/'amiga-import.json')
  for table in ('mean','pirate','space','demon'):
   (amiga/table).mkdir()
   for filename in (f'{table.upper()}.DAT','data.json'):
    shutil.copy2(AMIGA/table/filename,amiga/table/filename)
  flip(amiga/'space/SPACE.DAT');cases.append(['--amiga-root',str(amiga)])
  windows=tmp/'windows';windows.mkdir()
  for table in ('MEAN','PIRATE','SPACE','DEMON'):
   shutil.copy2(WINDOWS/f'{table}.DAT',windows/f'{table}.DAT')
  flip(windows/'SPACE.DAT');cases.append(['--windows-dat',str(windows)])
  for case in cases:
   result=subprocess.run([sys.executable,str(TOOL),*case,'--output',str(tmp/'report.json')],
                         capture_output=True,text=True,env=dict(os.environ,PYTHONOPTIMIZE='0'))
   if result.returncode==0 or 'AssertionError' not in result.stderr:
    raise RuntimeError(f'Changed input was not rejected as expected: {case}: {result.stderr}')
 print('Changed decoded source, Amiga adapter and Windows DAT each rejected')
if __name__=='__main__':main()
