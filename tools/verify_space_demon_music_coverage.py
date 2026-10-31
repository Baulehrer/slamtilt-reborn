#!/usr/bin/env python3
"""Inventory bounded Space/Demon music service sites and retained Original traces."""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_OP_MEM, X86_OP_IMM, X86_OP_REG, X86_REG_EAX, X86_REG_EDX

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
BUILD = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
TABLES = {
 'space': {'start': 0x439ae0, 'end': 0x44b640, 'api_global': 0x46ed24,
           'dat': '18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b',
           'bank_counts': [67,40,56]},
 'demon': {'start': 0x40febc, 'end': 0x41b9e0, 'api_global': 0x46d64c,
           'dat': '0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d',
           'bank_counts': [66,31,37]},
}

def sha(data): return hashlib.sha256(data).hexdigest()
def digest(value): return sha(json.dumps(value, separators=(',', ':')).encode())
def read(p): return json.loads(p.read_text())

def events(table, config):
    results = collections.defaultdict(lambda: {'events': 0, 'cases': set()})
    fixtures, missing = [], []
    for pin in sorted((ROOT/'analysis/traces').glob(table+'-*-rewards.json')):
        pinned = read(pin)
        if 'audio_events' not in pinned or 'sequence_sha256' not in pinned:
            continue
        source = ROOT/'build/oracle'/f'{table}-modes'/f"{pinned['case']}-rewards.json"
        if not source.exists():
            missing.append(str(source.relative_to(ROOT))); continue
        original = read(source)
        assert pinned['build_sha256'] == original['build_sha256'] == BUILD
        assert pinned['dat_sha256'] == original['dat_sha256'] == config['dat']
        for key in ('case','audio_events','table','tick_count','inputs','diagnostic_shots','milestones','payments','original_reset_exact'):
            assert original[key] == pinned[key], (pin.name, key)
        for key, expected in pinned['sequence_sha256'].items():
            assert digest(original[key]) == expected, (pin.name, key)
        sound = pinned['audio_events']
        assert sound and sound[0] == [0,0x90,0,0,0], pin
        for tick,service,bank,order,descriptor in sound[1:]:
            if service not in (0x80,0x84,0x88,0x8c,0x90): continue
            assert descriptor == 0
            if service in (0x84,0x88,0x90):
                assert bank in range(len(config['bank_counts']))
                assert 0 <= order < config['bank_counts'][bank], (pin.name, bank, order)
            row = results[(service,bank,order)]
            row['events'] += 1; row['cases'].add(pinned['case'])
        fixtures.append({'case':pinned['case'],'pinned_sha256':sha(pin.read_bytes()),
                         'source_sha256':sha(source.read_bytes()),
                         'steps':pinned['tick_count'],'sequences':len(pinned['sequence_sha256']),
                         'original_reset_exact':pinned['original_reset_exact']})
    assert fixtures
    result = [{'service':hex(s),'bank':b,'order':o,'events':r['events'],
               'case_count':len(r['cases'])} for (s,b,o),r in sorted(results.items())]
    return result, fixtures, missing

def scan(image, config, observed, labels):
    cs=Cs(CS_ARCH_X86,CS_MODE_32);cs.detail=True;cs.skipdata=True
    base = 0x400000
    ins=list(cs.disasm(image[config['start']-base:config['end']-base],config['start']))
    candidates=[]
    # Conservative same-straight-line register resolution; calls and branches
    # terminate the slice. Unknown is retained, never guessed.
    def value(reg, index, visited=()):
        if (reg,index) in visited:return None
        for j in range(index-1,max(-1,index-32),-1):
            p=ins[j]
            if p.mnemonic in ('call','ret','jmp') or p.mnemonic.startswith('j'):break
            try: _,writes=p.regs_access()
            except Exception:break
            if reg not in writes:continue
            if p.mnemonic=='mov' and len(p.operands)>1:
                operand=p.operands[1]
                if operand.type==X86_OP_IMM:return operand.imm
                if operand.type==X86_OP_REG:return value(operand.reg,j,visited+((reg,index),))
                if operand.type==X86_OP_MEM:
                    mem=operand.mem
                    return {'memory':hex(mem.disp & 0xffffffff), 'index_register':cs.reg_name(mem.index),
                            'base_register':cs.reg_name(mem.base), 'scale':mem.scale}
            if p.mnemonic=='xor' and len(p.operands)>1 and p.operands[0].type==X86_OP_REG and p.operands[1].type==X86_OP_REG and p.operands[0].reg==p.operands[1].reg:return 0
            return None
        return None
    for n,i in enumerate(ins):
        if i.mnemonic!='call' or not i.operands or i.operands[0].type!=X86_OP_MEM:continue
        mem=i.operands[0].mem
        if mem.disp not in (0x80,0x84,0x88,0x8c,0x90):continue
        bank,order=value(X86_REG_EDX,n),value(X86_REG_EAX,n)
        pointer=value(mem.base,n) if mem.base else None
        api_proven=isinstance(pointer,dict) and pointer['memory']==hex(config['api_global']) and not pointer['index_register'] and not pointer['base_register']
        if mem.disp in (0x80,0x8c):
            # Stop services do not consume EAX/EDX bank/order parameters.
            bank=order=None
            status=('observed_service' if any(s==hex(mem.disp) for s,_,_ in observed) else 'unobserved_service') if api_proven else 'unresolved'
        else:
            known=isinstance(bank,int) and isinstance(order,int)
            pair=(hex(mem.disp),bank,order) if known else None
            status=('observed_pair' if pair in observed else 'unobserved_pair') if known and api_proven else 'unresolved'
        candidates.append({'address':hex(i.address),'service_offset':hex(mem.disp),
                           'target_register':cs.reg_name(mem.base),'api_pointer_proven':api_proven,'api_source':pointer,
                           'bank':bank,'order':order,'status':status,
                           'instruction_hex':bytes(i.bytes).hex(), 'native_lift_label_present':i.address in labels})
    return candidates

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'build/music-audit/space-demon/coverage.json')
    p.add_argument('--tilt-dir',type=Path,help='Include separately verified native/original Tilt reports')
    a=p.parse_args()
    exe=(GAME/'SLAMTILT.EXE').read_bytes();assert sha(exe)==BUILD
    image=pefile.PE(data=exe).get_memory_mapped_image();tables={}
    lifted=(ROOT/'build/generated/pirate_step.cpp').read_text()
    labels={int(v,16) for v in re.findall(r'^L([0-9a-fA-F]+):', lifted, re.MULTILINE)}
    for table,config in TABLES.items():
        assert sha((GAME/'DAT'/f'{table.upper()}.DAT').read_bytes())==config['dat']
        observed,fixtures,missing=events(table,config)
        pairs={(x['service'],x['bank'],x['order'])for x in observed}
        calls=scan(image,config,pairs,labels)
        counts=collections.Counter(x['status'] for x in calls)
        tables[table]={'dat_sha256':config['dat'],'linear_range':[hex(config['start']),hex(config['end'])],
                       'bank_order_counts':config['bank_counts'],'fixture_count':len(fixtures),
                       'fixtures':fixtures,'missing_source_traces':missing,
                       'observed_requests':observed,'decoded_candidates':calls,
                       'candidate_counts':dict(counts),
                       'not_in_generated_lift':[x['address'] for x in calls if not x['native_lift_label_present']]}
        if a.tilt_dir:
            proof=a.tilt_dir/f'{table}-tilt-music-amiga'/'report.json'
            evidence=read(proof)
            assert evidence['status']=='VERIFIED_BOUNDED' and evidence['original_build_sha256']==BUILD
            assert evidence['table']==table and evidence['dat_sha256']==config['dat']
            assert evidence['tilt_music']==[609,0x84,2,54 if table=='space' else 0,0]
            tables[table]['additional_tilt_test']={'report_sha256':sha(proof.read_bytes()),
                'original_keyboard_steps':evidence['steps'],'original_music_request':evidence['tilt_music'],
                'scope':'Separate 800-step Original/native SDL proof; not included in historical fixture counts.'}
        print(table,len(fixtures),'SHA-checked fixtures,',len(calls),'candidate sites',dict(counts),flush=True)
    report={'status':'VERIFIED_BOUNDED','original_build_sha256':BUILD,'tables':tables,
            'scope':'Linear decoding of bounded original EXE ranges, conservative same-block register analysis and SHA-verified Original traces. Any target, bank, order or producer not resolved is explicitly UNKNOWN. Pair or stop service observed elsewhere does not prove this callsite ran; lift label absence is a static finding, not proof that a path is reachable. Counts exclude synthetic fixture startup. Does not prove whole-program reachability, complete original music PCM/mix or original Amiga sequencing.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
