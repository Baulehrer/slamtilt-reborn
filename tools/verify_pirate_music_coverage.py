#!/usr/bin/env python3
"""Inventory SHA-bound Pirate Retail music requests; no whole-game claim."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_OP_MEM, X86_OP_IMM, X86_OP_REG, X86_REG_EAX, X86_REG_EDX
import re
from verify_space_demon_music_coverage import scan as scan_retail_calls

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / 'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
BUILD = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
DAT = '6050b576678ec9b1878c203c057089b1c2499cdfd4a1ebdd7220f9d665fac7d6'
FILES = ('pirate-audio-events.json', 'pirate-knife-auto-audio.json',
         'pirate-mermaid-audio.json', 'pirate-extra-use-audio.json',
         'pirate-window-audio.json')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'build/music-audit/pirate/music-coverage.json')
    p.add_argument('--native-report', type=Path, help='Successful pirate_audio_probe report to link')
    p.add_argument('--native-probe', type=Path, default=ROOT/'build/native/pirate_audio_probe')
    a = p.parse_args()
    exe, dat = GAME/'SLAMTILT.EXE', GAME/'DAT/PIRATE.DAT'
    assert sha(exe) == BUILD and sha(dat) == DAT
    image = pefile.PE(data=exe.read_bytes()).get_memory_mapped_image()
    # Exact original access sites and table extents, not names inferred from order.
    cs = Cs(CS_ARCH_X86, CS_MODE_32)
    lookups = []
    for start, end, address, expected in (
        (0x42d844, 0x42d85c, 0x465b30, [30, 29, 28, 31]),
        (0x43035f, 0x43037a, 0x465b74, [4, 5, 46, 6]),
    ):
        insn = list(cs.disasm(image[start-0x400000:end-0x400000], start))
        assert insn and insn[-1].mnemonic == 'call' and '[ebx + 0x88]' in insn[-1].op_str
        assert any(hex(address) in i.op_str for i in insn)
        import struct
        values = list(struct.unpack_from('<4I', image, address-0x400000))
        assert values == expected
        lookups.append({'entry': hex(start), 'call': hex(insn[-1].address),
                        'data': hex(address), 'bank': 1, 'orders': values,
                        'instruction_sha256': hashlib.sha256(image[start-0x400000:end-0x400000]).hexdigest()})
    entries = collections.defaultdict(lambda: {'count': 0, 'cases': set()})
    files = []
    for name in FILES:
        path = ROOT/'analysis/traces'/name
        fixture = json.loads(path.read_text())
        assert fixture['build_sha256'] == BUILD and fixture['dat_sha256'] == DAT
        for case in fixture['cases']:
            replay = (ROOT/case['replay']).resolve()
            assert replay.is_relative_to(ROOT.resolve()) and sha(replay) == case['replay_sha256']
            events = case['events']
            assert events and events[0] == [0, 0x90, 0, 0, 0], (name, case['case'])
            for tick, service, bank, order, descriptor in events[1:]:
                if service not in (0x80, 0x84, 0x88, 0x8c, 0x90):
                    continue
                assert descriptor == 0
                if service in (0x84, 0x88, 0x90):
                    assert bank in (0, 1) and 0 <= order < (68, 55)[bank]
                entry = entries[(service, bank, order)]
                entry['count'] += 1
                entry['cases'].add(case['case'])
        files.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                      'case_count': len(fixture['cases']),
                      'steps': sum(c['tick_count'] for c in fixture['cases'])})
    verified = [{'service': hex(s), 'bank': b, 'order': o, 'events': info['count'],
                 'case_count': len(info['cases']), 'cases': sorted(info['cases'])}
                for (s, b, o), info in sorted(entries.items())]
    observed = {(row['service'], row['bank'], row['order']) for row in verified}
    for lut in lookups:
        assert all(('0x88', lut['bank'], order) in observed for order in lut['orders'])
    # Bounded straight-line inventory. Linear decoding is not a proof that no
    # alternate/unaligned code or shared-engine caller exists.
    cs.detail = True
    cs.skipdata = True
    instructions = list(cs.disasm(image[0x2b390:0x39ae0], 0x42b390))
    candidate = [(i, inst) for i, inst in enumerate(instructions)
                 if inst.mnemonic == 'call' and inst.operands and
                 inst.operands[0].type == X86_OP_MEM and
                 inst.operands[0].mem.disp in (0x84, 0x88, 0x90)]
    assert len(candidate) == 18, 'Unexpected decoded table music-call inventory'
    generated = (ROOT/'build/generated/pirate_step.cpp').read_text()
    calls = []
    for index, inst in candidate:
        base = inst.operands[0].mem.base
        regs = {}
        found_vtable = False
        for prev in reversed(instructions[max(0, index-24):index]):
            if prev.mnemonic in ('call', 'ret', 'jmp') or prev.mnemonic.startswith('j'):
                break
            try:
                _, writes = prev.regs_access()
            except Exception:
                break
            if (base in writes and prev.mnemonic == 'mov' and len(prev.operands) > 1 and
                prev.operands[1].type == X86_OP_MEM and prev.operands[1].mem.disp == 0x46e2b4):
                found_vtable = True
            for reg in (X86_REG_EAX, X86_REG_EDX):
                if reg not in writes or reg in regs:
                    continue
                if prev.mnemonic == 'mov' and len(prev.operands) > 1 and prev.operands[1].type == X86_OP_IMM:
                    regs[reg] = prev.operands[1].imm
                elif (prev.mnemonic == 'xor' and len(prev.operands) > 1 and
                      prev.operands[0].type == X86_OP_REG and prev.operands[1].type == X86_OP_REG and
                      prev.operands[0].reg == prev.operands[1].reg):
                    regs[reg] = 0
                else:
                    regs[reg] = None
        assert found_vtable, hex(inst.address)
        assert re.search(r'^L%x:' % inst.address, generated, re.MULTILINE), hex(inst.address)
        row = {'address': hex(inst.address), 'service': hex(inst.operands[0].mem.disp),
               'bank': regs.get(X86_REG_EDX), 'native_lift_label_present': True}
        value = regs.get(X86_REG_EAX)
        if value is None:
            match = [lut for lut in lookups if lut['call'] == hex(inst.address)]
            assert len(match) == 1 and row['bank'] == match[0]['bank']
            row['orders'] = match[0]['orders']
        else:
            row['orders'] = [value]
        assert all((row['service'], row['bank'], order) in observed for order in row['orders']), row
        calls.append(row)
    labels = {int(v,16) for v in re.findall(r'^L([0-9a-fA-F]+):', generated, re.MULTILINE)}
    all_table_calls = scan_retail_calls(image, {'start': 0x42b390, 'end': 0x439ae0,
                                        'api_global': 0x46e2b4}, observed, labels)
    stops = [row for row in all_table_calls if row['service_offset'] in ('0x80','0x8c')]
    startup = json.loads((ROOT/'docs/verification/retail-music-start-2026-10-30.json').read_text())
    assert startup['original_build_sha256'] == BUILD
    pirate = next(row for row in startup['tables'] if row['table'] == 'pirate')
    assert all((r['bank'], r['order']) == (0, 34) for r in pirate['runs'])
    report = {'status': 'VERIFIED_BOUNDED', 'build_sha256': BUILD, 'dat_sha256': DAT,
              'startup': {'bank': 0, 'order': 34,
                          'evidence': 'docs/verification/retail-music-start-2026-10-30.json',
                          'historical_synthetic_first_event_excluded': True},
              'fixture_files': files, 'observed_music_requests': verified,
              'original_lookup_instructions': lookups, 'table_music_calls': calls,
              'table_music_stop_candidates': stops,
              'table_music_call_scan': {'start': '0x42b390', 'end_exclusive': '0x439ae0',
                 'method': 'Capstone linear x86 decoding; same-block vtable producer and constants, or executed lookup tables; generated lift label existence only',
                 'resolved_calls': len(calls), 'all_orders_in_observed_request_fixtures': True},
              'scope': 'SHA-bound previously captured Original service-entry requests from bounded gameplay and diagnostic fixtures. Repeated cases across files are included separately in event counts. Startup is verified separately; linear decoded table range only; stop-service observation does not prove the individual candidate site ran; no claim of exhaustive execution, unaligned/hidden code, shared-engine callers, tracker PCM, live device mix, or actual Amiga sequencing.'}
    if a.native_report:
        native = json.loads(a.native_report.read_text())
        primary = json.loads((ROOT/'analysis/traces'/FILES[0]).read_text())
        assert len(native['cases']) == len(primary['cases']) == 81
        for result, original in zip(native['cases'], primary['cases']):
            assert result['case'] == original['case'] and result['ticks'] == original['tick_count']
            assert result['frames'] == result['ticks'] * 44100 // 200
            assert result['music_nonzero'] > 0 and result['sfx_nonzero'] > 0
        report['native_replay'] = {'report_sha256': sha(a.native_report),
            'probe_sha256': sha(a.native_probe), 'cases': len(native['cases']),
            'steps_per_pass': sum(c['ticks'] for c in native['cases']),
            'stereo_frames_per_pass': sum(c['frames'] for c in native['cases']),
            'passes': 2, 'original_mono_pcm_cases': native['pcm_cases'],
            'scope': 'Probe compared each original request after the independently established startup correction, checked both passes for deterministic native PCM and compared bounded mono SFX to original. Does not compare music PCM or original final mix.'}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print('Pirate original requests:', len(verified), 'distinct entries,', sum(f['case_count'] for f in files), 'bounded fixture cases; static LUT orders covered')

if __name__ == '__main__':
    main()
