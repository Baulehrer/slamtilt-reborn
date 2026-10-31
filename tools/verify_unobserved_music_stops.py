#!/usr/bin/env python3
"""Bounded direct-reference survey of unobserved Retail music-stop functions.

A negative result is not proof of unreachability: indirect targets can be
computed at runtime. No original code or audio is stored in the report.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
BUILD = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
RANGES = [
    ('pirate',0x435134,0x43515a,0x435149),('pirate',0x4365c0,0x4365e2,0x4365db),
    ('space',0x44172c,0x441770,0x441743),('space',0x4440bc,0x4440de,0x4440d7),
    ('space',0x4440e0,0x444124,0x4440f7),('space',0x44650c,0x446532,0x446521),
    ('demon',0x41761c,0x417642,0x417631),
]
DAT_HASH = {'pirate':'6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6',
            'space':'18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b',
            'demon':'0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d'}
def sha(data): return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'build/music-audit/unobserved-stops.json')
    args=p.parse_args(); raw=(GAME/'SLAMTILT.EXE').read_bytes(); assert sha(raw)==BUILD
    image=pefile.PE(data=raw).get_memory_mapped_image()
    dats={t:(GAME/'DAT'/f'{t.upper()}.DAT').read_bytes() for t in DAT_HASH}
    for t in dats: assert sha(dats[t])==DAT_HASH[t]
    cs=Cs(CS_ARCH_X86,CS_MODE_32); rows=[]
    for table,start,end,call in RANGES:
        code=image[start-0x400000:end-0x400000]
        ins=list(cs.disasm(code,start)); assert ins and ins[0].address==start
        site=next(x for x in ins if x.address==call)
        assert site.mnemonic=='call' and '[eax + 0x80]' in site.op_str
        incoming=[]
        # Search every byte in the mapped code range for rel32 CALL/JMP, so
        # a negative result does not depend on a chosen disassembly alignment.
        for offset in range(0x1000,0x54000-5):
            if image[offset] not in (0xe8,0xe9):continue
            source=0x400000+offset
            target=(source+5+struct.unpack_from('<i',image,offset+1)[0])&0xffffffff
            if start<=target<end and not start<=source<end:incoming.append([hex(source),hex(target)])
        literal=[]
        for target in range(start,end):
            word=struct.pack('<I',target)
            for name,blob in [('image',image),('dat',dats[table])]:
                off=0
                while (off:=blob.find(word,off))!=-1:
                    # Search all byte offsets; accidental data coincidences are not claimed xrefs.
                    literal.append([name,hex(off),hex(target)]);off+=1
        rows.append({'table':table,'function_start':hex(start),'end_exclusive':hex(end),
                     'music_stop':hex(call),'service':'0x80','code_sha256':sha(code),
                     'raw_external_rel32_candidates':incoming,'little_endian_address_occurrences':literal})
    report={'status':'BOUNDED_SURVEY','original_build_sha256':BUILD,'dat_sha256':DAT_HASH,'functions':rows,
            'scope':'Raw byte candidates only: rel32 E8/E9 in mapped code 0x401000..0x453ffa, and little-endian 32-bit literals anywhere in mapped EXE and that table DAT. Not a full control-flow proof; indirect, computed, compressed, relocated or differently encoded references remain UNKNOWN.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    for row in rows: print(row['table'],row['function_start'],'rel32',len(row['raw_external_rel32_candidates']),'literals',len(row['little_endian_address_occurrences']))
if __name__=='__main__':main()
