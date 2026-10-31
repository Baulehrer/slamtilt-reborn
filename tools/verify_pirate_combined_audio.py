#!/usr/bin/env python3
"""Bounded Pirate music + two SFX comparison, with adapted timing and voices.

The actual Retail tracker first tick and real simultaneous SFX requests are
combined at a synthetic common start. Tests native SFX over identical original
music, and measures (does not assert away) the real native tracker PCM gap.
No complete-game timing, device output or auditory equivalence is established.
"""
import argparse, hashlib, json, math, struct, subprocess, sys
from pathlib import Path
from extract_mean_stim import extract
from verify_retail_final_mix import original_mix
from verify_retail_tracker_pcm import GAME, TABLES, EXE_SHA

ROOT=Path(__file__).resolve().parents[1]
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--native',type=Path,required=True)
 p.add_argument('--sfx',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--min-correlation',type=float)
 a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
 exe=(GAME/'SLAMTILT.EXE').read_bytes(); dat_path=GAME/'DAT/PIRATE.DAT'; dat=dat_path.read_bytes()
 assert sha(exe)==EXE_SHA and sha(dat)==TABLES['pirate'][0]
 subprocess.run([sys.executable,str(ROOT/'tools/verify_retail_tracker_pcm.py'),'--table','pirate','--output',str(a.output)],check=True)
 subprocess.run([sys.executable,str(ROOT/'tools/verify_pirate_overlap_pcm.py'),'--native',str(a.sfx),'--output',str(a.output/'overlap.json')],check=True)
 stim,_=extract(dat,0,(TABLES['pirate'][1],)); stim_file=a.output/'pirate.stim';stim_file.write_bytes(stim)
 orig_music=(a.output/'pirate-first-tick.s16le').read_bytes(); music=struct.unpack('<1764h',orig_music)
 assert music[::2]==music[1::2]
 samples=subprocess.check_output([str(a.sfx.resolve()),str(dat_path),str(0x59fe9),'4490','226','64',str(0x5b173),'4012','226','64','882'])
 sfx=struct.unpack('<882h',samples)
 rows=[(m,s,s) for m,s in zip(music[::2],sfx)]
 assert all(-32768 <= m+s <= 32767 for m,s,_ in rows)
 orig,blocks=original_mix(exe,rows)
 def call(mode,input=None):
  return subprocess.check_output([str(a.native.resolve()),str(stim_file),str(dat_path),mode],input=input)
 injected=call('original-input',orig_music); actual=call('native-tracker')
 injected_samples=struct.unpack('<1764h',injected); actual_samples=struct.unpack('<1764h',actual)
 assert list(zip(injected_samples[::2],injected_samples[1::2]))==orig
 ref=[x for pair in orig for x in pair]; aa=sum(x*x for x in ref);bb=sum(x*x for x in actual_samples)
 corr=sum(x*y for x,y in zip(ref,actual_samples))/math.sqrt(aa*bb)
 exact=sum(x==y for x,y in zip(ref[::2],actual_samples[::2]))
 assert aa and bb and any(x!=y for x,y in zip(ref,actual_samples))
 if a.min_correlation is not None: assert corr >= a.min_correlation, corr
 report={'status':'VERIFIED_BOUNDED_WITH_TRACKER_PCM_GAP','scope':__doc__,'exe_sha256':sha(exe),'dat_sha256':sha(dat),'native_sha256':sha(a.native.read_bytes()),'sfx_probe_sha256':sha(a.sfx.read_bytes()),'frames':882,'sfx_descriptors':['0x464f60','0x464f84'],'shared_input_original_native_exact':True,'final_mix_original_blocks':blocks,'native_music_plus_sfx_exact_frames':exact,'native_music_plus_sfx_correlation':round(corr,6),'native_over_original_rms':round(math.sqrt(bb/aa),6),'original_combined_pcm_sha256':sha(struct.pack('<1764h',*ref)),'native_combined_pcm_sha256':sha(actual)}
 (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: same-input mixed PCM exact; actual tracker + SFX differs on',882-exact,'frames, correlation',round(corr,6))
if __name__=='__main__':main()
