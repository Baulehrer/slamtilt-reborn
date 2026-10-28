#!/usr/bin/env python3
"""Dependency-free PE/import/thunk map; offsets are NOT inferred functions."""
import struct, pathlib, json, hashlib, re, subprocess, collections, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
def analyze(p):
 b=p.read_bytes(); u16=lambda o:struct.unpack_from('<H',b,o)[0];u32=lambda o:struct.unpack_from('<I',b,o)[0]
 pe=u32(0x3c); opt=pe+24; base=u32(opt+28); secs=[]
 for i in range(u16(pe+6)):
  o=opt+u16(pe+20)+40*i;n=b[o:o+8].split(b'\0')[0].decode();vs,va,sz,raw=struct.unpack_from('<IIII',b,o+8);secs.append(dict(name=n,rva=va,virtual_size=vs,raw_size=sz,file_offset=raw))
 def off(r):
  for s in secs:
   if s['rva']<=r<s['rva']+max(s['raw_size'],s['virtual_size']):return s['file_offset']+r-s['rva']
  return r
 def cstr(r):return b[off(r):].split(b'\0')[0].decode('ascii','replace')
 imports=[];o=off(u32(opt+104))
 while any(b[o:o+20]):
  orig,_,_,name,iat=struct.unpack_from('<IIIII',b,o);dll=cstr(name);t=off(orig or iat);i=0
  while u32(t+4*i):
   v=u32(t+4*i);imports.append(dict(dll=dll,name=f'ordinal_{v&65535}' if v&0x80000000 else cstr(v+2),iat_va=hex(base+iat+4*i)));i+=1
  o+=20
 dis=subprocess.check_output(['objdump','-d','-Mintel',str(p)],text=True)
 ins=[]
 for line in dis.splitlines():
  m=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*(.*)',line)
  if m:ins.append((int(m[1],16),m[2]))
 for im in imports:
  addr=im['iat_va'];th=[a for a,t in ins if t.startswith('jmp') and 'ds:'+addr in t];im['thunks']=[hex(a) for a in th];im['call_sites']=[hex(a) for a,t in ins if t.startswith('call') and (any(re.search(r'0x'+format(x,'x')+r'\b',t) for x in th) or ':'+addr in t)]
 strings=[]
 for m in re.finditer(rb'[ -~]{5,}',b):
  if any(k in m[0].lower() for k in [b'.dat',b'watcom',b'pinball',b'gravity']):strings.append(dict(file_offset=hex(m.start()),text=m[0].decode()))
 return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),size=len(b),image_base=hex(base),entry_va=hex(base+u32(opt+16)),timestamp_utc=datetime.datetime.fromtimestamp(u32(pe+8),datetime.timezone.utc).isoformat(),linker=f'{b[opt+2]}.{b[opt+3]}',sections=secs,imports=imports,strings=strings)
paths=[ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE',ROOT/'build/corpus/win95/cd-gamer-03-1997/SLAMTILT/SLAMTILT/SLAMTILT.EXE',ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Fix_Win_EN/Game Files/Slam_Tilt_Fix/SLAMTILT.EXE']
result={'schema_version':1,'address_convention':'preferred PE virtual addresses; call_sites are instructions, not function starts','builds':[analyze(p) for p in paths]}
def blocks(x):
 b=bytearray((ROOT/x['path']).read_bytes());ss=x['sections'];base=int(x['image_base'],16)
 def offset(r):
  return next((s['file_offset']+r-s['rva'] for s in ss if s['rva']<=r<s['rva']+s['raw_size']),None)
 reloc=next(s for s in ss if s['name']=='.reloc');o=reloc['file_offset'];end=o+reloc['raw_size']
 while o+8<=end:
  page,n=struct.unpack_from('<II',b,o)
  if n<8 or o+n>end:break
  for j in range(o+8,o+n,2):
   v=struct.unpack_from('<H',b,j)[0];q=offset(page+(v&4095))
   if v>>12==3 and q is not None:b[q:q+4]=bytes(4)
  o+=n
 section=ss[0];raw=b[section['file_offset']:section['file_offset']+section['raw_size']]
 entries=collections.defaultdict(list)
 for i in range(0,len(raw)-63,64):entries[bytes(raw[i:i+64])].append(hex(base+section['rva']+i))
 return {k:v[0] for k,v in entries.items() if len(v)==1}
a=blocks(result['builds'][0]);comparisons=[]
for x in result['builds'][1:]:
 b=blocks(x);matches=[{'full_va':a[k],'other_va':b[k]} for k in sorted(a.keys()&b.keys())]
 comparisons.append({'other_build':x['path'],'method':'64-byte aligned code blocks, HIGHLOW relocation operands zeroed; unique blocks only; relative calls not normalized','matched_blocks':len(matches),'matches':matches})
result['block_comparisons']=comparisons
dis=subprocess.check_output(['objdump','-d','-Mintel',str(paths[0])],text=True)
regs={};callbacks=[]
for line in dis.splitlines():
 m=re.match(r'\s*([a-f0-9]+):.*?\t([^\t]+)$',line)
 if not m:continue
 addr=int(m[1],16);t=m[2]
 if not 0x41b9e0<=addr<0x41bc00:continue
 k=re.match(r'mov\s+(eax|ebx|ecx|edx|esi|edi|ebp),0x([0-9a-f]+)$',t)
 if k:regs[k[1]]=int(k[2],16)
 k=re.match(r'mov\s+DWORD PTR ds:0x(46de[0-9a-f]{2}),(\w+)$',t)
 if k and k[2] in regs and 0x401000<=regs[k[2]]<0x454000:callbacks.append({'slot_va':'0x'+k[1],'target_va':hex(regs[k[2]]),'store_va':hex(addr),'semantics':'unknown'})
 k=re.match(r'(?:lea|mov)\s+(\w+),',t)
 if k and not re.match(r'mov\s+\w+,0x',t):regs.pop(k[1],None)
result['mean_callback_candidates']=callbacks
out=ROOT/'analysis/windows-symbol-map.json';out.write_text(json.dumps(result,indent=2)+'\n');print(out)
for x in result['builds']:
 print(x['path'],x['size'],x['entry_va'],x['timestamp_utc'])
 for i in x['imports']:
  if i['name'] in ['ReadFile','CreateFileA','DirectDrawCreate','DirectSoundCreate','timeGetTime','SetTimer']:print(i)
