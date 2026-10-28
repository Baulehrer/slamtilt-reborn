#!/usr/bin/env python3
"""Validate local decoded STIM using locally built libxmp; render five seconds."""
import ctypes,pathlib,json,wave,hashlib,os
root=pathlib.Path(__file__).resolve().parents[1];os.chdir(root)
lib=ctypes.CDLL(str(root/'build/libxmp-build/libxmp.so'));lib.xmp_create_context.restype=ctypes.c_void_p
for f,args in [('xmp_load_module',[ctypes.c_void_p,ctypes.c_char_p]),('xmp_start_player',[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('xmp_play_buffer',[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),('xmp_end_player',[ctypes.c_void_p]),('xmp_release_module',[ctypes.c_void_p]),('xmp_free_context',[ctypes.c_void_p])]:getattr(lib,f).argtypes=args
records=[]
paths=[*pathlib.Path('build/decoded').glob('*Music.Bin')]
for p in sorted(paths):
 b=p.read_bytes();c=lib.xmp_create_context();load=lib.xmp_load_module(c,str(p).encode());rec={'path':str(p),'size':len(b),'magic':b[:4].decode('ascii',errors='replace'),'sha256':hashlib.sha256(b).hexdigest(),'load_result':load}
 if load==0:
  start=lib.xmp_start_player(c,44100,0);rec['start_result']=start
  if start==0:
   size=44100*2*2*5;buf=ctypes.create_string_buffer(size);play=lib.xmp_play_buffer(c,buf,size,0);pcm=buf.raw;out=pathlib.Path('build/validation')/(p.stem+'.wav');out.parent.mkdir(exist_ok=True)
   with wave.open(str(out),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(pcm)
   rec.update(play_result=play,pcm_bytes=len(pcm),nonzero_bytes=sum(x!=0 for x in pcm),pcm_sha256=hashlib.sha256(pcm).hexdigest(),wav=str(out),duration_seconds=5,sample_rate=44100,channels=2,sample_bits=16);lib.xmp_end_player(c)
  lib.xmp_release_module(c)
 lib.xmp_free_context(c);records.append(rec)
previous=json.loads(pathlib.Path('analysis/audio-load-results.json').read_text()) if pathlib.Path('analysis/audio-load-results.json').exists() else []
records=[r for r in previous if not r['path'].startswith('build/decoded/')]+records
pathlib.Path('analysis/audio-load-results.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
assert len(paths)>=2 and all(r.get('load_result')==0 and r.get('start_result')==0 and r.get('play_result')==0 and r.get('nonzero_bytes',0)>0 for r in records if r['path'].startswith('build/decoded/'))
