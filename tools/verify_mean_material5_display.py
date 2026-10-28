#!/usr/bin/env python3
import argparse,json,struct,hashlib,subprocess,os
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=argparse.ArgumentParser();p.add_argument('--native',required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];directory=next((root/'build/corpus/win95/demo-1997').rglob('MEAN.DAT')).parent;mean=(directory/'MEAN.DAT').read_bytes();main=(directory/'MAIN.DAT').read_bytes();image=(root/'build/mean-prepared/pe-data.bin').read_bytes()
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x400000,0x100000);u.mem_write(0x400000,image);u.mem_map(0x1000000,0x100000);u.mem_map(0x1100000,0x200000);u.mem_write(0x1100000,mean);u.mem_write(0x1010000,main)
def put(ad,v):u.mem_write(ad,struct.pack('<I',v&0xffffffff))
def get(ad):return struct.unpack('<I',u.mem_read(ad,4))[0]
def call(ad):u.reg_write(UC_X86_REG_ESP,0x10ff000);put(0x10ff000,0x10ffff0);u.emu_start(ad,0x10ffff0,count=100000);assert u.reg_read(UC_X86_REG_EIP)==0x10ffff0
call(0x40af14);put(0x43e3e8,0x1000000);put(0x43e82c,0x1010000);put(0x43efd8,0x1100000);put(0x43f068,0x1002000);put(0x43f0d0,0x1003000)
for offset,target in [(0x3c,0x406680),(0x4c,0x4060a4),(0x50,0x40607c),(0x40,0x406280),(0x38,0x406574),(0x48,0x4060f8),(0x44,0x40617c),(0x70,0x1004000),(0x68,0x1004000),(0x5c,0x1004000)]:put(0x1003000+offset,target)
def hook(uc,address,n,data):
 if address==0x1004000:
  sp=uc.reg_read(UC_X86_REG_ESP);uc.reg_write(UC_X86_REG_EIP,get(sp));uc.reg_write(UC_X86_REG_ESP,sp+4)
u.hook_add(UC_HOOK_CODE,hook)
def fnv(data):
 h=14695981039346656037
 for v in data:h=((h^v)*1099511628211)&0xffffffffffffffff
 return str(h)
specs=[dict(callback=0x413a2c,score=0,flags=[(mask>>i)&1 for i in range(4)],steps=51) for mask in range(16)]
specs += [dict(callback=0x413958,score=0,flags=[0]*4,steps=106)]
specs += [dict(callback=0x41062c,score=score,flags=[0]*4,steps=156) for score in [0,12345,4294967294]]
specs += [dict(callback=callback,score=0,flags=[0]*4,steps=steps) for callback,steps in [(0x4107c8,149),(0x41086c,149),(0x410504,42)]]
specs += [dict(callback=0x410e4c,score=0,flags=[0]*4,steps=123,restore=restore) for restore in [0,1]]
specs += [dict(callback=0x40fdec,score=score,flags=[0]*4,steps=155,field358=cash,field362=selector,field1fe=index,field1f2=index) for cash in [0,1] for selector in range(8) for index in range(3) for score in [0,12345]]
specs += [dict(callback=cb,score=score,flags=[0]*4,steps=steps) for cb,steps in [(0x412fa8,156),(0x41041c,118),(0x410158,88)] for score in [0,15000000,50000000,4294967294]]
specs += [dict(callback=0x411c60,score=score,flags=[0]*4,steps=101) for score in [0,15000000,50000000,4294967294]]
specs += [dict(callback=0x411db4,score=score,flags=[0]*4,steps=226,restore=restore) for score in [0,15000000,50000000,4294967294] for restore in [0,1]]
specs += [dict(callback=0x411824,score=0,flags=[0]*4,steps=80,restore=restore) for restore in [0,1]]
if os.environ.get('SLAM_SHARED_DISPLAY_ONLY'): specs=[c for c in specs if c['callback'] in (0x412fa8,0x41041c,0x410158)]
if os.environ.get('SLAM_RALLY_DISPLAY_ONLY'): specs=[c for c in specs if c['callback'] in (0x411c60,0x411db4,0x411824)]
if os.environ.get('SLAM_UPPER_DISPLAY_ONLY'): specs=[dict(callback=0x411fdc,score=0,flags=[0]*4,steps=156,restore=restore) for restore in [0,1]]
if os.environ.get('SLAM_UPPER_MODES_ONLY'): specs=[dict(callback=cb,score=0,flags=[0]*4,steps=steps,restore=restore) for cb,steps in [(0x412d24,149),(0x411f10,172),(0x412af8,175),(0x412c58,153)] for restore in [0,1]]
if os.environ.get('SLAM_REWARD_PIXELS_ONLY'): specs=[dict(callback=cb,score=0,flags=[0]*4,steps=steps,restore=restore) for cb,steps in [(0x410a34,169),(0x410910,160),(0x410d34,198),(0x410b00,268)] for restore in [0,1]]
if os.environ.get('SLAM_RETURN_PASS_DISPLAY_ONLY'): specs=[dict(callback=0x41163c,score=score,flags=[0]*4,steps=81) for score in [0,5000000,10000000,4294967294]]
if os.environ.get('SLAM_MINIGAME2_TERMINAL_ONLY'): specs=[dict(callback=cb,score=score,flags=[0]*4,steps=steps,restore=restore,field_43efcc=value) for cb,steps in [(0x41210c,239),(0x4122cc,214)] for value in [0,8000,65535] for score in [30000000,45000000] for restore in [0,1]]
if os.environ.get('SLAM_MINIGAME1_TERMINAL_ONLY'): specs=[dict(callback=cb,score=0,flags=[0]*4,steps=steps,field_43efdc=value) for cb,steps in [(0x40f994,168),(0x40fb78,301)] for value in [1,2,3,5,7,20]]
if os.environ.get('SLAM_MINIGAME_RETAIL_TERMINAL_ONLY'):
 # These two parameter changes are proved in the actual Retail/Fix DMD bodies.
 u.mem_write(0x40fb51,struct.pack('<I',40000000));u.mem_write(0x40fd79,struct.pack('<I',40000000))
 specs=[dict(callback=cb,score=0,flags=[0]*4,steps=steps,field_43efdc=value,minigame_lap_points=40000000) for cb,steps in [(0x40f994,168),(0x40fb78,301)] for value in [1,2,4]]
if os.environ.get("SLAM_NUDGE_WARNING_ONLY"):specs=[dict(callback=0x40f93c,score=0,flags=[0]*4,steps=51)]
if os.environ.get("SLAM_MODE5_LEFT_AWARD_ONLY"): specs=[dict(callback=0x412908,score=score,flags=[0]*4,steps=163,restore=restore) for score in [0,12345,15000000,4294967294] for restore in [0,1]]
if os.environ.get("SLAM_MODE_LOCK_ONLY"): specs=[dict(callback=cb,score=0,flags=[0]*4,steps=steps,restore=restore) for cb,steps in [(0x411908,110),(0x41265c,160)] for restore in [0,1]]
if os.environ.get("SLAM_MODE4_EXIT_INPUT_ONLY"): specs=[dict(callback=0x4114cc,score=0,flags=[0]*4,steps=76,restore=restore) for restore in [0,1]]
if os.environ.get("SLAM_PIT_STOP_PIXELS_ONLY"): specs=[dict(callback=cb,score=0,flags=[0]*4,steps=steps,field1d8=remain) for cb,steps in [(0x4131cc,129),(0x4132d4,104),(0x413518,139),(0x4133d4,99)] for remain in ([0,1,2,3,4] if cb==0x4133d4 else [4])]
if os.environ.get("SLAM_STOCK_CAR_PIXELS_ONLY"): specs=[dict(callback=cb,score=0,flags=[0]*4,steps=steps,field38a=remain) for cb,steps in [(0x413490,81),(0x413770,128)] for remain in ([0,1,2,5,15,30] if cb==0x413770 else [0])]
if os.environ.get("SLAM_SPEED_JACKPOT_PIXELS_ONLY"): specs=[dict(callback=0x410158,score=score,flags=[0]*4,steps=88) for score in [10000000,20000000,30000000,40000000]]+[dict(callback=0x410b00,score=0,flags=[0]*4,steps=268,restore=restore) for restore in [0,1]]
if os.environ.get("SLAM_LEFT_SPEED_PIXELS_ONLY"): specs=[dict(callback=0x412df0,score=0,flags=[0]*4,steps=158,field1f2=index,restore=restore) for index in range(6) for restore in [0,1]]
if os.environ.get("SLAM_KICKSTART_PIXELS_ONLY"): specs=[dict(callback=cb,score=score,flags=[0]*4,steps=steps,restore=restore) for cb,steps in [(0x4102c0,113),(0x4130cc,158)] for score in [0,25000000,12345,4294967294] for restore in [0,1]]
expected=[]
for c in specs:
 put(0x1002014,c['callback']);put(0x100201c,0);put(0x43f050,c['score']);u.mem_write(0x43f1dc,bytes(c['flags']));u.mem_write(0x1000000,bytes(i%4 for i in range(1920)));frames=[]
 for offset,key in [(0x358,'field358'),(0x362,'field362'),(0x1fe,'field1fe'),(0x1f2,'field1f2'),(0x1d8,'field1d8'),(0x38a,'field38a')]:u.mem_write(0x43f000+offset,struct.pack('<H',c.get(key,0)))
 put(0x43efdc,c.get('field_43efdc',1))
 put(0x43efcc,c.get('field_43efcc',0))
 put(0x43efd0,0x1005000)
 source=bytes((i%4 if c.get('restore',0) else 0) for i in range(1920))
 packed=bytearray(480)
 for i,v in enumerate(source):
  packed[i//8] |= (v&1)<<(7-i%8)
  packed[240+i//8] |= ((v>>1)&1)<<(7-i%8)
 u.mem_write(0x1005000,bytes(packed))
 for n in range(c['steps']):

  try: call(c['callback'])
  except Exception as exc: raise RuntimeError((hex(c['callback']),n,hex(u.reg_read(UC_X86_REG_EIP)))) from exc
  frames.append(dict(active=get(0x1002014)!=0,counter=get(0x100201c),fnv=fnv(bytes(u.mem_read(0x1000000,1920)))))
 expected.append(frames)
actual=json.loads(subprocess.run([a.native,str(directory/'MEAN.DAT'),str(directory/'MAIN.DAT')],input=json.dumps(specs),capture_output=True,text=True,check=True).stdout)
for series,(original,native) in enumerate(zip(expected,actual)):
 assert len(original)==len(native)
 for frame,(x,y) in enumerate(zip(original,native)):assert x==y,(series,frame,x,y)
assert len(actual)==len(expected)
report=dict(image_sha256=hashlib.sha256(image).hexdigest(),mean_dat_sha256=hashlib.sha256(mean).hexdigest(),scope='Original callback pixel/counter/active states with actual bitmap, font, clear and invert services; external engine70/68 lamp and5c audio adapters skipped, original shared scheduler excluded',series=specs,expected=expected)
if os.environ.get('SLAM_MINIGAME_RETAIL_TERMINAL_ONLY'): report['scope']='Normalized Demo callbacks with two proven Retail/Fix20M-to40M immediate substitutions; original Demo font/render services, shape matched across actual Retail/Fix callback bodies; shared scheduler excluded'
(root/('analysis/traces/mean-kickstart-pixels-original.json' if os.environ.get('SLAM_KICKSTART_PIXELS_ONLY') else 'analysis/traces/mean-left-speed-pixels-original.json' if os.environ.get('SLAM_LEFT_SPEED_PIXELS_ONLY') else 'analysis/traces/mean-speed-jackpot-pixels-original.json' if os.environ.get('SLAM_SPEED_JACKPOT_PIXELS_ONLY') else 'analysis/traces/mean-pit-stop-pixels-original.json' if os.environ.get('SLAM_PIT_STOP_PIXELS_ONLY') else 'analysis/traces/mean-stock-car-pixels-original.json' if os.environ.get('SLAM_STOCK_CAR_PIXELS_ONLY') else 'analysis/traces/mean-mode4-exit-input-pixels-original.json' if os.environ.get('SLAM_MODE4_EXIT_INPUT_ONLY') else 'analysis/traces/mean-mode-lock-pixels-original.json' if os.environ.get('SLAM_MODE_LOCK_ONLY') else 'analysis/traces/mean-mode5-left-award-pixels-original.json' if os.environ.get('SLAM_MODE5_LEFT_AWARD_ONLY') else 'analysis/traces/mean-nudge-warning-pixels-original.json' if os.environ.get('SLAM_NUDGE_WARNING_ONLY') else 'analysis/traces/mean-minigame-retail-terminal-pixels.json' if os.environ.get('SLAM_MINIGAME_RETAIL_TERMINAL_ONLY') else 'analysis/traces/mean-minigame1-terminal-pixels-original.json' if os.environ.get('SLAM_MINIGAME1_TERMINAL_ONLY') else 'analysis/traces/mean-minigame2-terminal-pixels-original.json' if os.environ.get('SLAM_MINIGAME2_TERMINAL_ONLY') else 'analysis/traces/mean-return-pass-dmd-original.json' if os.environ.get('SLAM_RETURN_PASS_DISPLAY_ONLY') else 'analysis/traces/mean-reward-mode6-pixels-original.json' if os.environ.get('SLAM_REWARD_PIXELS_ONLY') else 'analysis/traces/mean-upper-modes-original.json' if os.environ.get('SLAM_UPPER_MODES_ONLY') else 'analysis/traces/mean-upper-announcement-original.json' if os.environ.get('SLAM_UPPER_DISPLAY_ONLY') else 'analysis/traces/mean-rally-dmd-original.json' if os.environ.get('SLAM_RALLY_DISPLAY_ONLY') else 'analysis/traces/mean-shared-reward-dmd-original.json' if os.environ.get('SLAM_SHARED_DISPLAY_ONLY') else 'analysis/traces/mean-material5-dmd-original.json')).write_text(json.dumps(report,separators=(',',':'))+'\n')
print(f'{sum(c["steps"] for c in specs)} original/native callback pixel/state cases exact')
