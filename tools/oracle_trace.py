#!/usr/bin/env python3
"""Capture original Mean demo state at original single-ball step boundaries via WineDbg."""
import argparse, hashlib,json,os,re,struct,time
from pathlib import Path
import pexpect
ROOT=Path(__file__).resolve().parents[1]
ANSI=re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07')
class Debugger:
 def __init__(self,pid):
  env=dict(os.environ,WINEPREFIX=str(ROOT/'build/oracle/prefix'),WINEDEBUG='-all',TERM='dumb')
  wine=Path.home()/'.local/share/lutris/runners/wine/wine-staging-11.16-x86_64/bin/winedbg'
  self.child=pexpect.spawn(str(wine),[hex(pid)],env=env,encoding='utf8',timeout=180)
  self.log=(ROOT/'build/oracle/trace-debugger.log').open('w');self.child.logfile=self.log
  self.child.expect('Wine-dbg>')
  self.child.delaybeforesend=0.005
 def cmd(self,s):
  self.child.send(s+'\r');self.child.expect('Wine-dbg>');return ANSI.sub('',self.child.before).replace('\r','')
 def words(self,address,count):
  out=self.cmd(f'x/{max(count,4)}x 0x{address:x}');words=[]
  for line in out.splitlines():
   if re.match(r'0x[0-9a-f]+ .*:',line):words.extend(int(v,16) for v in line.split(':',1)[1].split() if re.fullmatch('[0-9a-fA-F]{8}',v))
  if len(words)<count:raise RuntimeError('memory read failed: '+out)
  return words[:count]
 def close(self):
  self.cmd('detach');self.child.send('quit\r');self.child.expect(pexpect.EOF);self.log.close()
def state(words):
 def signed(v):return v if v<0x80000000 else v-0x100000000
 return dict(x=signed(words[0]),y=signed(words[1]),previous_x=signed(words[2]),previous_y=signed(words[3]),
             vx=signed(words[5]),vy=signed(words[6]),field_58=words[22]&65535,raw_words=words)
def main():
 p=argparse.ArgumentParser();p.add_argument('--pid',type=lambda s:int(s,0),default=0x20);p.add_argument('--steps',type=int,default=100);p.add_argument('--output',type=Path,default=ROOT/'analysis/traces/mean-ball-100.json');p.add_argument('--wait-contact',action='store_true',help='Wait for active ball0 entering lower-flipper approach before capture');a=p.parse_args()
 d=Debugger(a.pid)
 try:
  d.cmd('break *0x4088f0');d.cmd('cont');d.cmd('condition 1 $eax == 0')
  if a.wait_contact:
   for attempt in range(10000):
    pointer=d.words(0x4298c8,1)[0];w=d.words(pointer,25)
    current=state(w)
    if current['field_58']==2 and 160*65536<=current['x']<=240*65536 and 510*65536<=current['y']<=535*65536 and current['vy']>0:
     print('Lower-flipper approach reached; capturing100steps',flush=True);break
    d.cmd('cont')
   else:raise RuntimeError('No lower-flipper approach within10000steps')
  samples=[]
  for i in range(a.steps+1):
   ball_address=d.words(0x4298c8,1)[0]
   w=d.words(ball_address,25)
   samples.append(dict(step=i,**state(w),oracle_context=dict(
     ball_address=ball_address,
     flipper_words=d.words(0x43e850,27),
     engine_global_words=d.words(0x43e700,40))))
   if i<a.steps:d.cmd('cont')
  exe=ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/SLAMTILT.EXE'
  artifact=dict(schema_version=1,method='live WineDbg capture at original single-ball step entry; no native/guessed physics',
    build_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),addresses=dict(ball_pointer_table='0x4298c8',ball_state='0x43e568',step='0x4088f0',outer_step='0x408874',integration='0x40a010',x_writer='0x40a0d2',y_writer='0x40a0dd'),
    layout=dict(x=0,y=4,previous_x=8,previous_y=12,vx=20,vy=24,coordinate_format='signed16.16',screen_x_word=16,screen_y_word=18),tick_count=a.steps,tick_hz=200,
    tick_hz_note='4036b8 timeGetTime →4048cc accumulator →408874 each5ms; context sampled at4088f0 entry before ball step',
    initial_state=samples[0],final_state=samples[-1],samples=samples)
  a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(artifact,indent=2)+'\n')
  print(json.dumps(dict(output=str(a.output),initial_xy=[samples[0]['x']/65536,samples[0]['y']/65536],final_xy=[samples[-1]['x']/65536,samples[-1]['y']/65536],steps=a.steps)))
 finally:d.close()
if __name__=='__main__':main()
