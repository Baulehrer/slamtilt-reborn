#!/usr/bin/env python3
"""Handbook-guided event chains; individual steps share the original oracle."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1];image=(r/'build/mean-prepared/pe-data.bin').read_bytes();probe=sys.argv[1]
def run(c):return json.loads(subprocess.check_output([probe],input=json.dumps([c]),text=True))[0]
def w(f,o,v):struct.pack_into('<H',f,o,v&65535)
def get(f,o):return struct.unpack_from('<H',bytes(f),o)[0]
def initial(selected):
 f=bytearray(0x3c0);w(f,0x1e6,selected);w(f,0x39c,2000)
 for j in range(6):w(f,0x044+j*2,1)
 return f
chains=[]
# Six distinct car shots, then a duplicate: no seventh award after completion.
f=initial(1);mode=5;events=[]
for event_id in [0,1,2,3,4,5,5]:
 out=run(dict(fields=list(f),mode=mode,id=event_id,returned=123));f=bytearray(out['fields']);mode=out['mode'];events.append(dict(id=event_id,**out))
assert [e['scores'] for e in events]==[[5000000],[10000000],[15000000],[20000000],[25000000],[50000000],[]]
assert mode==2 and get(f,0x372)==6
chains.append(dict(name='monster_car_six_distinct_shots',total_score=125000000,events=events))
# Target depends on PE table + engine clock. Always hit the selected target.
directory=list(struct.unpack('<6I',image[0x38ddc:0x38df4]));targets=list(struct.unpack('<19I',image[0x38df4:0x38e40]))
f=initial(2);mode=5;events=[]
for tick in range(6):
 event_id=get(f,0x38c);out=run(dict(fields=list(f),mode=mode,id=event_id,returned=321));f=bytearray(out['fields']);mode=out['mode']
 if out['services'][3]:
  selection=run(dict(fields=list(f),mode=mode,target_only=True,engine38=tick*16,directory=directory,targets=targets));assert selection['valid'];f=bytearray(selection['fields'])
 events.append(dict(id=event_id,**out,target_after=get(f,0x38c)))
assert mode==2 and get(f,0x386)==6 and get(f,0x39c)==12000
assert [e['scores'] for e in events]==[[15000000]]*5+[[15000000,90000000]]
chains.append(dict(name='rally_six_targets_and_remaining_time',total_score=180000000,events=events))
f=initial(4);mode=5;events=[]
for event_id in [1,1,2,2,3]:
 out=run(dict(fields=list(f),mode=mode,id=event_id,returned=456));f=bytearray(out['fields']);events.append(dict(id=event_id,**out))
assert [e['scores'] for e in events]==[[15000000],[],[15000000],[],[15000000]]
chains.append(dict(name='offroad_repeated_shots_do_not_award',total_score=45000000,events=events))
(r/'analysis/traces/mean-manual-reward-chains.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),scope='bounded synthetic switch-event chains;not normal physical-play proof;external completion services reported',chains=chains),separators=(',',':'))+'\n')
print('3 handbook-guided chains, 18 events PASS')
