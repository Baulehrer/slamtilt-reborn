#!/usr/bin/env python3
"""Compare original Space/Demon nudges/Tilt and music with actual SDL key events.

The retained original snapshot uses a keyboard configuration adapter and the
separately verified original base music fields. No ball/rule/score writes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pefile
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDX
from pirate_adventure_oracle import Original
from reborn_retail_oracle import sample

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT'
BUILD_SHA = '185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6'
TABLES = {
    'space': {'dat':'18a308bdfa9fe141f57d4462a44dc4dd69cb32c35f9e6f83462fce770600115b', 'base':32, 'tilt':54, 'callback':0x444a64, 'ranges':[(0x444a64,0x444ac8),(0x43a484,0x43a4da)]},
    'demon': {'dat':'0d78f5dbc069c5082cecce06f9620385288f615c03c83696483a43f272069c4d', 'base':25, 'tilt':0, 'callback':0x416d6c, 'ranges':[(0x416d6c,0x416dd8),(0x410600,0x41065a)]},
}
SERVICES = {0x406600:0x5c, 0x406268:0x80, 0x406240:0x84, 0x40621c:0x88,
            0x4061f8:0x8c, 0x4061c4:0x90}

def sha(data): return hashlib.sha256(data).hexdigest()
def signed(value): return value if value < 0x80000000 else value - 0x100000000

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--table', choices=TABLES, default='space')
    p.add_argument('--native', type=Path, default=ROOT/'build/native/slamslice')
    p.add_argument('--output', type=Path)
    p.add_argument('--amiga-root', type=Path, help='Also test a prepared native Amiga asset adapter')
    a = p.parse_args()
    table, cfg = a.table, TABLES[a.table]
    if a.output is None: a.output = ROOT/'build/music-audit'/f'{table}-tilt'
    a.output.mkdir(parents=True, exist_ok=True)
    dat_path = GAME/'DAT'/f'{table.upper()}.DAT'
    exe = (GAME/'SLAMTILT.EXE').read_bytes(); dat = dat_path.read_bytes()
    assert sha(exe) == BUILD_SHA and sha(dat) == cfg['dat']
    prepared = ROOT/'build/oracle'/f'{table}-full-game'
    summary = json.loads((prepared/'summary.json').read_text())
    assert summary['build_sha256'] == BUILD_SHA and summary['dat_sha256'] == cfg['dat']
    image = (prepared/'human-image.bin').read_bytes()
    pe = pefile.PE(data=exe).get_memory_mapped_image()
    ranges = (*cfg['ranges'], (0x405eec,0x405fac))
    for start,end in ranges:
        assert image[start-0x400000:end-0x400000] == pe[start-0x400000:end-0x400000], hex(start)
    m = Original(prepared, table=table)
    # The isolated initialized context predates original keyboard setup and
    # base music selection. These documented bindings are configuration only.
    m.put(0x46c5ec,0x38); m.put(0x46c5f0,0xb8)
    descriptor = m.get(0x46c644); config = m.get(descriptor+0xc)
    bank, order = m.get(config+8), m.get(config+12)
    assert (bank,order) == (0,cfg['base'])
    for address,value in ((0x454a64,order),(0x454a3c,order),
                          (0x454a68,bank),(0x454a38,bank),(0x454a54,0)):
        m.put(address,value)
    tick = 0; callbacks = []; audio = [[0,0x90,bank,order,0]]; states = [m.ball()]; samples = []
    def observe(u, address, _size, _):
        if address == cfg['callback']:
            callbacks.append([tick,u.reg_read(UC_X86_REG_EAX),m.get(0x46c6e4)])
            return
        service = SERVICES[address]
        if service == 0x5c:
            event = [tick+1,service,signed(u.reg_read(UC_X86_REG_EDX)),
                     signed(u.reg_read(UC_X86_REG_EBX)),u.reg_read(UC_X86_REG_EAX)]
        elif service in (0x80,0x8c): event = [tick+1,service,0,0,0]
        else: event = [tick+1,service,signed(u.reg_read(UC_X86_REG_EDX)),
                       signed(u.reg_read(UC_X86_REG_EAX)),0]
        audio.append(event)
    for address in (cfg['callback'],*SERVICES):
        m.u.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
    keys = {200:(0x1c,True),204:(0x1c,False),600:(0x38,True),
            604:(0xb8,True),608:(0x39,True)}
    for tick in range(800):
        if tick in keys:
            scan,down = keys[tick]; m.run(0x40404c,0 if down else 1,scan)
        m.step(tick); states.append(m.ball()); samples.append(sample(m))
    assert callbacks == [[604,0,79],[608,1,118]], callbacks
    assert [609,0x84,2,cfg['tilt'],0] in audio and m.get(0x46b764) == 1
    ui = [dict(frame=i,type='focus_gained') for i in range(200)]
    for frame,key,down in [(50,'Return',True),(51,'Return',False),
                           (150,'Left Alt',True),(151,'Left Alt',False),
                           (151,'Right Alt',True),(152,'Right Alt',False),
                           (152,'Space',True),(153,'Space',False)]:
        ui.append(dict(frame=frame,type='key',key=key,down=down))
    ui.sort(key=lambda e:e['frame'])
    ui_path, replay, trace, sound = [a.output/name for name in ('ui.json','empty-replay.json','native.json','audio.json')]
    ui_path.write_text(json.dumps({'events':ui})); replay.write_text('{"inputs":[]}')
    native = a.native.resolve(); native_hash = sha(native.read_bytes())
    command = [str(native),table,str(prepared),str(dat_path),
               '--frames','200','--presentation','--windowed','--audio',
               '--audio-trace',str(sound),'--ui-events',str(ui_path),
               '--trace',str(trace),'--replay',str(replay)]
    env = dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',
               XDG_DATA_HOME=str(a.output.resolve()/'profile'))
    result = subprocess.run(command,env=env,capture_output=True,text=True,timeout=120)
    assert result.returncode == 0, (result.returncode,result.stderr)
    assert sha(native.read_bytes()) == native_hash
    native_trace,native_audio = json.loads(trace.read_text()),json.loads(sound.read_text())
    assert native_trace['tick_count'] == 800 and native_trace['states'] == states
    for key in ('globals','poses','lifecycle','highscore_sha256','lamp_sha256','ball_pool_sha256'):
        assert native_trace[key] == [row[key] for row in samples], key
    if table == 'demon':
        assert native_trace['raw_state_sha256'] == [row['raw_state_sha256'] for row in samples]
    assert native_audio['enabled'] and native_audio['queued_bytes'] > 0 and native_audio['events'] == audio
    delivered = {int(t):events for t,events in native_trace['physical_inputs']}
    for at,action in [(600,'nudge_left'),(604,'nudge_right'),(608,'nudge_up')]:
        assert {'action':action,'down':True} in delivered[at]
    report = {'status':'VERIFIED_BOUNDED','original_build_sha256':BUILD_SHA,
              'table':table,'dat_sha256':cfg['dat'],'native_sha256':native_hash,'steps':800,
              'callbacks':callbacks,'tilt_music':[609,0x84,2,cfg['tilt'],0],
              'audio_requests':len(audio),'ball_states':len(states),
              'compared_vectors':['ball','globals including DMD hash','poses','lifecycle','highscores','lamps','ball pool'] + (['Demon raw state'] if table == 'demon' else []),
              'scope':'Actual original x86 default keyboard handler vs actual native SDL events and fresh reset/replay; original snapshot keyboard/base-music initialization adapted; no ball or rule injection. Audio requests and gameplay/display state, not mixed PCM or physical listening.'}
    if a.amiga_root:
        amiga = a.amiga_root.resolve()
        amiga_dat = amiga/f'{table.upper()}.DAT'
        amiga_prepared = amiga/f'{table}-prepared'
        amiga_trace, amiga_sound = a.output/'amiga-native.json', a.output/'amiga-audio.json'
        amiga_command = [str(native),table,str(amiga_prepared),str(amiga_dat),
                         '--frames','200','--presentation','--windowed','--audio',
                         '--audio-trace',str(amiga_sound),'--ui-events',str(ui_path),
                         '--trace',str(amiga_trace),'--replay',str(replay)]
        result = subprocess.run(amiga_command,env=env,capture_output=True,text=True,timeout=120)
        assert result.returncode == 0, (result.returncode,result.stderr)
        assert sha(native.read_bytes()) == native_hash
        adapted, adapted_audio = json.loads(amiga_trace.read_text()),json.loads(amiga_sound.read_text())
        for key in ('states','globals','poses','lifecycle','highscore_sha256','lamp_sha256','ball_pool_sha256'):
            assert adapted[key] == native_trace[key], ('amiga adapter',key)
        if table == 'demon': assert adapted['raw_state_sha256'] == native_trace['raw_state_sha256']
        assert adapted_audio['enabled'] and adapted_audio['queued_bytes'] > 0 and adapted_audio['events'] == audio
        report['amiga_adapter'] = {'dat_sha256':sha(amiga_dat.read_bytes()),
            'image_sha256':sha((amiga_prepared/'human-image.bin').read_bytes()),
            'steps':800,'events_exact':True,
            'scope':'Native Amiga data adapter compared with native Windows gameplay; not original Amiga gameplay or music.'}
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'{table}: warning/Tilt, 800 original/native steps, 801 ball states, music bank 2 order {cfg["tilt"]} exact')

if __name__ == '__main__': main()
