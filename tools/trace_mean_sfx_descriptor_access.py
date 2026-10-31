#!/usr/bin/env python3
"""Watch selected Mean Demo descriptor accesses during bounded DMD callbacks.

Actual Demo callback code and drawing services run with synthetic initialized
display state; sound and two external display services are stubbed. This is
not a full original game or a proof of unreachability. No asset bytes are saved.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_HOOK_BLOCK, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDX
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESP
from verify_mean_sample_pcm_original import DEMO_SHA, DAT_SHA, IMAGE_SHA

ROOT = Path(__file__).resolve().parents[1]
CALLBACKS = ((0x4133d4,99),(0x413518,139),(0x4131cc,129),(0x4132d4,104),
             (0x412fa8,156),(0x411824,80),(0x41041c,118),(0x410158,88),
             (0x4102c0,113),(0x411c60,101),(0x411db4,226),(0x413490,81),
             (0x413770,128),(0x4107c8,149),(0x41086c,149),(0x410504,42))
TARGETS = (0x437f54,0x437f78,0x437f9c)
MAIN_SHA = 'e82addadc9b40b172615983034825ebf3e077c3ff3c167531520c50dd8c9188c'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    builds = json.loads((ROOT/'analysis/windows-symbol-map.json').read_text())['builds']
    exe = (ROOT/next(x['path'] for x in builds if x['sha256'] == DEMO_SHA)).read_bytes()
    directory = next((ROOT/'build/corpus/win95/demo-1997').rglob('MEAN.DAT')).parent
    mean, main_dat = (directory/'MEAN.DAT').read_bytes(), (directory/'MAIN.DAT').read_bytes()
    image = (ROOT/'build/mean-prepared/pe-data.bin').read_bytes()
    assert (sha(exe),sha(mean),sha(main_dat),sha(image)) == (DEMO_SHA,DAT_SHA,MAIN_SHA,IMAGE_SHA)
    pe = pefile.PE(data=exe)
    u = Uc(UC_ARCH_X86, UC_MODE_32)
    for address,size in ((0x400000,0x100000),(0x1000000,0x100000),(0x1100000,0x200000)):
        u.mem_map(address,size)
    u.mem_write(0x400000,image)
    u.mem_write(0x1100000,mean)
    u.mem_write(0x1010000,main_dat)
    blocks, accesses, calls = set(), [], []
    current = {'callback':None,'tick':None}

    def put(address,value):
        u.mem_write(address,struct.pack('<I',value & 0xffffffff))
    def get(address):
        return struct.unpack('<I',u.mem_read(address,4))[0]
    def run(address):
        u.reg_write(UC_X86_REG_ESP,0x10ff000)
        put(0x10ff000,0x10ffff0)
        u.emu_start(address,0x10ffff0,count=100000)
        assert u.reg_read(UC_X86_REG_EIP) == 0x10ffff0, hex(address)
    def remember_block(_uc,address,size,_):
        if 0x401000 <= address < 0x440000:
            blocks.add((address,size))
    def watch(uc,kind,address,size,value,_):
        accesses.append({'callback':current['callback'],'tick':current['tick'],
                         'pc':hex(uc.reg_read(UC_X86_REG_EIP)),
                         'address':hex(address),'size':size,'access':kind})
    def external(uc,address,_size,_):
        if address == 0x1004000:
            calls.append({'callback':current['callback'],'tick':current['tick'],
                          'eax':uc.reg_read(UC_X86_REG_EAX),
                          'edx':uc.reg_read(UC_X86_REG_EDX),
                          'ebx':uc.reg_read(UC_X86_REG_EBX)})
            sp = uc.reg_read(UC_X86_REG_ESP)
            uc.reg_write(UC_X86_REG_EIP,get(sp))
            uc.reg_write(UC_X86_REG_ESP,sp+4)
    u.hook_add(UC_HOOK_BLOCK,remember_block)
    u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,watch,begin=0x437e10,end=0x437fbf)
    u.hook_add(UC_HOOK_CODE,external,begin=0x1004000,end=0x1004000)
    run(0x40af14)
    for address,value in ((0x43e3e8,0x1000000),(0x43e82c,0x1010000),
                          (0x43efd8,0x1100000),(0x43f068,0x1002000),
                          (0x43f0d0,0x1003000)):
        put(address,value)
    for off,target in ((0x3c,0x406680),(0x4c,0x4060a4),(0x50,0x40607c),
                       (0x40,0x406280),(0x38,0x406574),(0x48,0x4060f8),
                       (0x44,0x40617c),(0x70,0x1004000),(0x68,0x1004000),
                       (0x5c,0x1004000)):
        put(0x1003000+off,target)
    clean_image = bytes(u.mem_read(0x400000,0x100000))
    clean_runtime = bytes(u.mem_read(0x1000000,0x100000))
    per_callback = []
    for callback,frames in CALLBACKS:
        u.mem_write(0x400000,clean_image)
        u.mem_write(0x1000000,clean_runtime)
        put(0x1002014,callback)
        put(0x100201c,0)
        put(0x43f050,15000000)
        u.mem_write(0x43f1dc,bytes(4))
        u.mem_write(0x1000000,bytes(i%4 for i in range(1920)))
        put(0x43efdc,1)
        put(0x43efcc,0)
        put(0x43efd0,0x1005000)
        u.mem_write(0x1005000,bytes(480))
        current['callback'] = hex(callback)
        before = len(calls)
        for tick in range(frames):
            current['tick'] = tick
            run(callback)
        per_callback.append({'callback':hex(callback),'frames':frames,
                             'adapted_external_calls':len(calls)-before})
    target_reads = [x for x in accesses if any(base <= int(x['address'],16) < base+36 for base in TARGETS)]
    controls = [x for x in accesses if 0x437e10 <= int(x['address'],16) < 0x437e58]
    sound_calls = [x for x in calls if x['eax'] in (0x437e10,0x437e34)]
    assert controls and sound_calls, 'positive controls did not fire'
    assert not target_reads, target_reads
    for address,size in blocks:
        off = pe.get_offset_from_rva(address-0x400000)
        assert image[address-0x400000:address-0x400000+size] == exe[off:off+size]
    report = {'status':'BOUNDED_NO_TARGET_ACCESSES','scope':__doc__,'demo_sha256':DEMO_SHA,
              'mean_dat_sha256':DAT_SHA,'main_dat_sha256':MAIN_SHA,'prepared_image_sha256':IMAGE_SHA,
              'targets':[hex(x) for x in TARGETS], 'callback_count':len(CALLBACKS),
              'frames':sum(x[1] for x in CALLBACKS),'callbacks':per_callback,
              'target_accesses':target_reads,'positive_control_accesses':len(controls),
              'positive_control_service_calls':len(sound_calls),'executed_original_blocks':len(blocks)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(CALLBACKS)} original DMD callbacks, {report["frames"]} frames; '
          f'{len(controls)} positive-control accesses, no watched target accesses')


if __name__ == '__main__':
    main()
