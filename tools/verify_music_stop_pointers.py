#!/usr/bin/env python3
"""Bounded initialized-state and recorded-call survey of seven Retail stop paths.

Negative results do not prove unreachability: odd/encoded pointers, unobserved
states and computed branches remain outside the survey. Original binary/data
are never included in the output.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
BUILD = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
PREP = {'pirate':'pirate-full-tick','space':'space-full-game','demon':'demon-full-game'}
SURVEY = ROOT/'docs/verification/unobserved-music-stops-2026-10-30.json'
STARTUP = ROOT/'docs/verification/retail-music-start-2026-10-30.json'
EXE = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'

def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_text())
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build/music-stop-audit/stop-pointer-evidence.json')
    args=parser.parse_args(); assert sha(EXE.read_bytes())==BUILD
    prior=read(SURVEY); startup=read(STARTUP)
    assert prior['original_build_sha256']==startup['original_build_sha256']==BUILD
    functions=prior['functions']; assert len(functions)==7
    ranges={table:[(int(f['function_start'],0),int(f['end_exclusive'],0)) for f in functions if f['table']==table] for table in PREP}
    contexts={}
    for table,name in PREP.items():
        directory=ROOT/'build/oracle'/name; summary=read(directory/'summary.json')
        record=next(row for row in startup['tables'] if row['table']==table)
        assert summary['build_sha256']==BUILD
        blobs={key:(directory/filename).read_bytes() for key,filename in
               [('image','human-image.bin'),('runtime','human-runtime.bin'),('dat','human-dat.bin')]}
        for key,data in blobs.items():
            filename={'image':'human-image.bin','runtime':'human-runtime.bin','dat':'human-dat.bin'}[key]
            assert sha(data)==record[key+'_sha256']==summary['context_hashes'][filename]
        aligned=[]; literal=[]
        for key,blob in blobs.items():
            # Original code is not an aligned data table. Survey writable data
            # in the PE snapshot plus the whole initialized heap/table data.
            first=0x54000 if key=='image' else 0
            base={'image':0x400000,'runtime':0x1000000,'dat':0x1100000}[key]
            for offset in range(first,len(blob)-3,4):
                value=struct.unpack_from('<I',blob,offset)[0]
                if any(lo<=value<hi for lo,hi in ranges[table]):
                    aligned.append({'region':key,'address':hex(base+offset),'value':hex(value)})
            # Exact entry address at any byte alignment, independent of above.
            for lo,_ in ranges[table]:
                needle=struct.pack('<I',lo); offset=first
                while (offset:=blob.find(needle,offset))!=-1:
                    literal.append({'region':key,'address':hex(base+offset),'entry':hex(lo)});offset+=1
        contexts[table]={'image_sha256':record['image_sha256'], 'runtime_sha256':record['runtime_sha256'],
                         'dat_sha256':record['dat_sha256'],'aligned_pointer_candidates':aligned,
                         'unaligned_entry_candidates':literal}
    files=[];hits=[];edges=0
    for path in sorted((ROOT/'analysis').glob('*boundary*.json')):
        try: document=read(path)
        except (UnicodeDecodeError,json.JSONDecodeError):continue
        if not isinstance(document,dict) or not isinstance(document.get('executed_call_edges'),list):continue
        assert document.get('build_sha256')==BUILD, path
        count=0
        for edge in document['executed_call_edges']:
            if not isinstance(edge,dict) or 'target' not in edge:continue
            value=edge['target'];target=int(value,0) if isinstance(value,str) else int(value)
            count+=1
            for table,table_ranges in ranges.items():
                if any(lo<=target<hi for lo,hi in table_ranges):
                    hits.append({'file':str(path.relative_to(ROOT)), 'table':table,
                                 'target':hex(target),'edge':edge})
        edges+=count;files.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes()),'recorded_edges':count})
    assert files and edges
    report={'status':'BOUNDED_SURVEY','original_build_sha256':BUILD,'functions':functions,
            'original_initialized_contexts':contexts,'boundary_files':files,'recorded_edges':edges,'matching_edges':hits,
            'scope':'SHA-bound retained initialized Windows Retail contexts: aligned DWORDs in writable PE data, runtime and decoded table data, plus exact function-entry literals at every byte alignment. SHA-identified existing recorded call-edge files are searched for targets inside each function. No whole-game trace, no lifetime heap-write audit, no BE or relative/encoded/computed pointer equivalence, and no unreachability claim.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('Retail music-stop pointer survey:',len(files),'SHA-bound boundary files,',edges,'edges;',len(hits),'matching edges; context candidate counts', {k:(len(v['aligned_pointer_candidates']),len(v['unaligned_entry_candidates'])) for k,v in contexts.items()})
if __name__=='__main__':main()
