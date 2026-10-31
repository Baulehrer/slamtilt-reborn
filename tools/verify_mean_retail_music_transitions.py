#!/usr/bin/env python3
"""Bounded original Retail Mean startup and Mode4 music service sequences."""
import hashlib
import json
import struct
from pathlib import Path
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_EDX, UC_X86_REG_EBX,
                               UC_X86_REG_ESI, UC_X86_REG_EIP, UC_X86_REG_ESP)

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE'
SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
blob = EXE.read_bytes()
assert hashlib.sha256(blob).hexdigest() == SHA
image = pefile.PE(data=blob).get_memory_mapped_image()
u = Uc(UC_ARCH_X86, UC_MODE_32)
u.mem_map(0x400000, 0x100000)
u.mem_write(0x400000, image)
u.mem_map(0x1000000, 0x10000)
def put(address, value, size=4):
    u.mem_write(address, int(value).to_bytes(size, 'little'))
def get(address):
    return int.from_bytes(u.mem_read(address, 4), 'little')
put(0x46dbe0, 0x1001000)
for offset, entry in [(0x84, 0x1002000), (0x88, 0x1005000), (0x8c, 0x1003000), (0x90, 0x1004000)]:
    put(0x1001000 + offset, entry)
events = []
def hook(uc, pc, _size, _):
    services = {0x1002000: 0x84, 0x1005000: 0x88, 0x1003000: 0x8c, 0x1004000: 0x90}
    if pc not in services:
        return
    service = services[pc]
    events.append([service, uc.reg_read(UC_X86_REG_EDX) if service != 0x8c else 0,
                   uc.reg_read(UC_X86_REG_EAX) if service != 0x8c else 0])
    sp = uc.reg_read(UC_X86_REG_ESP)
    uc.reg_write(UC_X86_REG_EIP, get(sp))
    uc.reg_write(UC_X86_REG_ESP, sp + 4)
u.hook_add(UC_HOOK_CODE, hook)
def run(start, end):
    events.clear()
    u.reg_write(UC_X86_REG_ESP, 0x100f000)
    u.emu_start(start, end, count=100)
    assert u.reg_read(UC_X86_REG_EIP) == end
    return list(events)
# Mean's table descriptor independently identifies the Retail base track.
config = get(0x464b98 + 0x0c)
assert config == 0x464240 and (get(config+8), get(config+12)) == (0, 4)
base = run(0x4267c8, 0x4267db)
assert base == [[0x90, 0, 4]]
put(0x46deba, 0xffff, 2)
phase1 = run(0x420bfd, 0x420c2a)
assert phase1 == [[0x84, 1, 50], [0x8c, 0, 0]]
# Each range executes the actual immediate arguments and table-service call.
# These cases establish selectors, not the conditions that reach each branch.
selectors = [
    (0x42212b, 0x422156, 0x84, 0, 29),
    (0x42239c, 0x4223af, 0x84, 0, 51),
    (0x4224f9, 0x42250c, 0x84, 0, 46),
    (0x4225b6, 0x4225c9, 0x84, 0, 40),
    (0x422687, 0x42269a, 0x88, 1, 53),
    (0x42269a, 0x4226ad, 0x84, 0, 23),
    (0x4227ed, 0x422800, 0x84, 0, 2),
    (0x423074, 0x42308a, 0x88, 1, 56),
    (0x42308a, 0x42309d, 0x84, 0, 73),
    (0x4234ea, 0x4234fd, 0x84, 0, 62),
    (0x424574, 0x42458a, 0x84, 1, 52),
    (0x425e0b, 0x425e21, 0x88, 1, 46),
    (0x425fa1, 0x425fbc, 0x88, 1, 49),
]
selector_results = []
for start, end, service, bank, order in selectors:
    u.reg_write(UC_X86_REG_EBX, 1)
    u.reg_write(UC_X86_REG_ESI, 0x1001000)
    try:
        result = run(start, end)
    except Exception as error:
        raise RuntimeError(hex(start)) from error
    assert result == [[service, bank, order]], (hex(start), result)
    selector_results.append({'start': hex(start), 'end_exclusive': hex(end),
                             'service': service, 'bank': bank, 'order': order})
report = {'status':'VERIFIED_BOUNDED', 'original_build_sha256':SHA,
          'scope':'Original Retail x86 table config and selected service call sequences; services hooked; no tracker PCM or whole-game coverage.',
          'table':'mean', 'config':hex(config), 'base':base, 'phase1':phase1,
          'original_addresses':['0x4267c8..0x4267da','0x420bfd..0x420c29'],
          'individually_executed_selectors':selector_results}
out = ROOT/'build/mean-retail-music-transitions.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2)+'\n')
print('Retail Mean: base 90/0/4; phase1 84/1/50 then 8c; 13 additional selectors')
