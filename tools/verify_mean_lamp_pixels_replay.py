#!/usr/bin/env python3
"""Native mask/parser/palette patches vs actual original on/off canvas hashes."""
import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
dat=next((root/'build/corpus/win95/demo-1997').rglob('MEAN.DAT'))
b=dat.read_bytes();base=b[0x1594c8:0x1594c8+320*600]
a=json.loads(subprocess.check_output([sys.argv[1],str(dat)]))
assert len(a)==63
for on,name in [(1,'mean-lamp-pixels-fixture.json'),(0,'mean-lamp-off-pixels-fixture.json')]:
 fixture=json.loads((root/'analysis/traces'/name).read_text())['cases']
 for frame,c in zip(a,fixture):
  canvas=bytearray(base)
  for y in range(frame['h']):
   for x in range(frame['w']):
    i=y*frame['w']+x;p=(frame['y']+y)*320+frame['x']+x
    if frame['mask'][i]:canvas[p]=(canvas[p]&127) if on else (canvas[p]|128)
    rgba=frame['rgba'][on][i*4:i*4+4]
    color=(base[p]&127) if on else (base[p]|128)
    assert rgba[:3]==list(b[0x1590c8+color*4+1:0x1590c8+color*4+4])
    assert rgba[3]==(255 if frame['mask'][i] else 0)
  assert hashlib.sha256(canvas).hexdigest()==c['on_canvas_sha256'],c['id']
print('126 native lamp patches/palettes exact')
