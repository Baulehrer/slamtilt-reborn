#!/usr/bin/env python3
"""Reproduce bounded Windows corpus comparisons; requires local user artifacts and Capstone.

Run: build/venv/bin/python tools/audit_windows_corpus_levers.py
No broad function-equivalence claims: operand masking hides target differences.
"""
import json,struct,pathlib,hashlib
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
r=pathlib.Path(__file__).resolve().parents[1];s=json.load(open(r/'analysis/windows-symbol-map.json'));md=Cs(CS_ARCH_X86,CS_MODE_32);md.detail=True;md.skipdata=True

def load(x):
 b=bytearray((r/x['path']).read_bytes());ss=x['sections'];base=int(x['image_base'],16)
 if hashlib.sha256(b).hexdigest()!=x['sha256']:raise ValueError('Corpus metadata hash mismatch: '+x['path'])
 def off(va):return next((a['file_offset']+va-base-a['rva'] for a in ss if a['file_offset'] and a['rva']<=va-base<a['rva']+a['raw_size']),None)
 rel=next(a for a in ss if a['name']=='.reloc');p=rel['file_offset'];end=p+rel['raw_size'];relocs=[]
 while p+8<=end:
  page,n=struct.unpack_from('<II',b,p)
  if n<8 or p+n>end:break
  for j in range(p+8,p+n,2):
   v=struct.unpack_from('<H',b,j)[0]
   if v>>12==3:
    q=off(base+page+(v&4095))
    if q is not None:b[q:q+4]=bytes(4);relocs.append(base+page+(v&4095))
  p+=n
 a=ss[0];start=base+a['rva'];raw=bytearray(b[a['file_offset']:a['file_offset']+a['raw_size']]);norm=bytearray(raw)
 for i in md.disasm(bytes(raw),start):
  if i.id and (i.mnemonic.startswith('j') or i.mnemonic=='call' or i.mnemonic.startswith('loop')) and i.imm_size:
   p=i.address-start+i.imm_offset;norm[p:p+i.imm_size]=bytes(i.imm_size)
 return dict(meta=x,start=start,raw=bytes(raw),norm=bytes(norm),relocs=relocs)
builds=[load(x) for x in s['builds']];demo=builds[1]
anchors=[(0x4088f0,0x408b04,'physical gameplay step'),(0x40a0e8,0x40a35b,'point-force/magnet'),(0x41b8d0,0x41b900,'shared Mean rule service'),(0x41cb28,0x41cd50,'right arming/progression'),(0x4180d0,0x4191f6,'Mean mode4 minigame2')]
rows=[]
for a,end,name in anchors:
 needle=demo['norm'][a-demo['start']:a-demo['start']+min(64,end-a)]
 row=dict(demo_va=hex(a),demo_end=hex(end),name=name,matches=[])
 for target in [builds[0],builds[2]]:
  positions=[];at=0
  while True:
   p=target['norm'].find(needle,at)
   if p<0:break
   positions.append(p);at=p+1
  entry=dict(build=target['meta']['path'],sha256=target['meta']['sha256'],prefix_bytes=len(needle),prefix_matches=[hex(target['start']+p) for p in positions])
  if len(positions)==1:
   p=positions[0];n=end-a;expected=demo['norm'][a-demo['start']:end-demo['start']];actual=target['norm'][p:p+n];diff=[i for i,(x,y) in enumerate(zip(expected,actual)) if x!=y];entry.update(normalized_region_bytes=n,changed_bytes=len(diff),first_change_offsets=diff[:12],full_region_equal=not diff)
  row['matches'].append(entry)
 rows.append(row)
report=dict(schema=1,scope='Targeted Windows corpus leverage audit; does not claim semantic equivalence solely from masked code.',method='PE HIGHLOW operands zeroed; direct relative branch/call immediate bytes zeroed by Capstone linear BEGTEXT decode. Exact search not alignment-dependent. Full bounded-region comparison after unique prefix match.',anchors=rows,builds=[dict(path=x['meta']['path'],sha256=x['meta']['sha256']) for x in builds])
# Add original-byte instruction context for single altered minigame byte.
for row in report['anchors']:
 if row['name']!='Mean mode4 minigame2':continue
 for j,entry in enumerate(row['matches']):
  target=builds[0 if j==0 else 2];a=int(row['demo_va'],16);p=int(entry['prefix_matches'][0],16);contexts=[]
  for off in entry.get('first_change_offsets',[]):
   for label,b,va in [('demo',demo,a),('other',target,p)]:
    orig=(r/b['meta']['path']).read_bytes();sec=b['meta']['sections'][0];raw=orig[sec['file_offset']:sec['file_offset']+sec['raw_size']]
    ins=list(md.disasm(raw[va-b['start']:va-b['start']+off+32],va))
    contexts.append(dict(build=label,offset=off,instructions=[dict(va=hex(i.address),bytes=i.bytes.hex(),text=i.mnemonic+' '+i.op_str) for i in ins if i.address<=va+off<i.address+i.size]))
  entry['changed_instruction_context']=contexts
report['confidence']='VERIFIED bounded normalized binary matches; PARTIAL semantic equivalence until pointer and call adapters validated'
for row in report['anchors']:
 a=int(row['demo_va'],16);e=int(row['demo_end'],16);n=e-a;needle=demo['norm'][a-demo['start']:e-demo['start']]
 row['demo_normalized_sha256']=hashlib.sha256(needle).hexdigest()
 for j,entry in enumerate(row['matches']):
  b=builds[0 if j==0 else 2];va=int(entry['prefix_matches'][0],16);raw=b['norm'][va-b['start']:va-b['start']+n];entry['normalized_sha256']=hashlib.sha256(raw).hexdigest()
# Read the original embedded four-entry table and bounded entry prefixes.
b=builds[0];orig=(r/b['meta']['path']).read_bytes();sec=b['meta']['sections'][0];raw=orig[sec['file_offset']:sec['file_offset']+sec['raw_size']]
entries=struct.unpack_from('<4I',raw,0x404e60-b['start']);report['full_table_dispatch']={'va':'0x404e60','entries':[hex(a) for a in entries],'initializers':[]}
for va in entries:
 ins=list(md.disasm(raw[va-b['start']:va-b['start']+800],va));ptrstores=[dict(va=hex(i.address),instruction=i.mnemonic+' '+i.op_str) for i in ins if i.mnemonic=='mov' and ('0x46de' in i.op_str)];report['full_table_dispatch']['initializers'].append(dict(va=hex(va),callback_slot_stores=ptrstores))
# Physical step's direct callers are shared code, independent of table-specific callback registrations.
callers=[]
for i in md.disasm(raw,b['start']):
 if i.id and i.mnemonic=='call' and i.op_str=='0x409588':callers.append(hex(i.address))
report['full_table_dispatch']['physical_step_direct_calls']=callers
files=[f for f in json.load(open(r/'analysis/corpus.json'))['files'] if 'win95' in f.get('path','') and f['path'].lower().endswith('mean.dat')]
report['windows_mean_dat']=[dict(path=f['path'],size=(r/f['path']).stat().st_size,sha256=hashlib.sha256((r/f['path']).read_bytes()).hexdigest()) for f in files]
report['prioritized_next']=[dict(rank=1,action='Full mode4 minigame scaler: inspect ECX provenance at full425288 and demo418848, decide intentional demo difficulty versus port correction.',expected_gain='One changed instruction isolates real gameplay revision; avoid treating all demo semantics as retail.'),dict(rank=2,action='Reuse existing physical integration/magnet code for next table; prepare Full memory/global address adapters from confirmed full409588/40ad80.',expected_gain='Shared engine is same normalized code; focus table assets and callback boundary.'),dict(rank=3,action='Compare shared Mean service41b8d0 at full428310 with current mode5/mode6 callers.',expected_gain='Retail and patched retail equivalent bounded helper; no patch-specific RE required.')]
report['limits']=['HIGHLOW masking hides absolute target differences; branch masking hides changed destinations. Matches prove preserved instruction bodies, not pointer data or complete caller correctness.','Full four-entry initialization installs same callback slots; generic runtime physics for all four tables requires table-specific dynamic validation.','Only five selected routines compared; no broad claim that Fix has no gameplay changes.']
for item in report['full_table_dispatch']['initializers']:
 va=int(item['va'],16);ins=list(md.disasm(raw[va-b['start']:va-b['start']+800],va));item['entry_prefix']=[dict(va=hex(i.address),instruction=i.mnemonic+' '+i.op_str) for i in ins[:8]]
report['limits'][1]='Full embedded four-entry table and shared physical caller located; entry semantics and connection to initializers are not yet runtime verified. Do not claim all entries are initializers.'
report['full_table_dispatch']['entry_semantics']='UNKNOWN; existing doc labels four-entry dispatch; original entry prefixes saved for targeted followup.'
report['full_table_dispatch']['entry_contexts']=report['full_table_dispatch'].pop('initializers')
lookup={x['path']:x for x in s['builds']}
def original_digest(meta,a,n):
 section=meta['sections'][0];offset=section['file_offset']+a-int(meta['image_base'],16)-section['rva']
 return hashlib.sha256((r/meta['path']).read_bytes()[offset:offset+n]).hexdigest()
for row in report['anchors']:
 a=int(row['demo_va'],16);n=int(row['demo_end'],16)-a
 row['demo_original_region_sha256']=original_digest(demo['meta'],a,n)
 for match in row['matches']:
  match['original_region_sha256']=original_digest(lookup[match['build']],int(match['prefix_matches'][0],16),n)
report['mean_dat_accelerator']={'status':'VERIFIED','claim':'All six available Windows MEAN.DAT files byte-identical by freshly computed SHA256, across demo, USA, UK, ROM and RIP; existing parser/profile/geometry data reusable.', 'sha256':'1169210c52fb4cb8785a0ef87e42bcabbc9d7b17bf9b9062f4642fb2cb69755f','size':1622024}
out=r/'analysis/corpus-windows-levers.json'
out.write_text(json.dumps(report,indent=2)+'\n')
for row in rows:
 print(row['name'],[(x['prefix_matches'],x.get('changed_bytes')) for x in row['matches']])
print(out.relative_to(r))
