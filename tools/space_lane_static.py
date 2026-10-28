#!/usr/bin/env python3
"""Export only the PE-backed direction and kickback code evidence used by050."""
import hashlib,json
from pathlib import Path
import capstone,pefile
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
b=p.read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha=='185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
pe=pefile.PE(data=b);cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
ranges=[(0x444810,0x444869),(0x449636,0x4496af),(0x44970a,0x449785),(0x44ac23,0x44ac90),(0x44aeb2,0x44af30),(0x44af98,0x44b034),(0x44b034,0x44b130),(0x44b40c,0x44b425)]
d=dict(build_sha256=sha,evidence_type='STATIC PE bytes/disassembly; execution established separately by Original trace fixtures',direction=dict(field='WORD0x46ed2c',key='Left Ctrl scan1d',callback='0x444810',lamps=['0x46ec74','0x46ec78'],source_branch='0x449636'),kickback=dict(grey_flags=['0x46e930','0x46e932','0x46e934','0x46e936'],charge='0x46ed34',timer='0x46ee58'),ranges=[])
for lo,hi in ranges:
 raw=pe.get_data(lo-pe.OPTIONAL_HEADER.ImageBase,hi-lo)
 d['ranges'].append(dict(start=hex(lo),end_exclusive=hex(hi),sha256=hashlib.sha256(raw).hexdigest(),instructions=[dict(address=hex(i.address),bytes=i.bytes.hex(),text=i.mnemonic+' '+i.op_str)for i in cs.disasm(raw,lo)]))
(ROOT/'analysis/space-lane-kickback-static.json').write_text(json.dumps(d,indent=2)+'\n');print('PE SHA and eight bounded ranges verified')
