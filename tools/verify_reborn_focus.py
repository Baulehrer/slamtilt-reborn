#!/usr/bin/env python3
"""Real compositor Alt-Tab, pause/audio preservation and F10 return on owned windows."""
import argparse,atexit,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
keyboard_device=None
def read(p):return json.loads(p.read_text())
def active():return json.loads(subprocess.check_output(['hyprctl','activewindow','-j'],text=True)).get('pid',0)
def wait_active(pid,timeout=8):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  if active()==pid:return
  time.sleep(.05)
 raise AssertionError('Compositor did not activate owned test window '+str(pid)+'; active='+str(active()))
def key(pid,*args):
 assert active()==pid,'User focus changed; no keyboard input sent'
 if any(v in args for v in ['Alt_L','alt']):
  from evdev import ecodes as e
  backward=any(v in args for v in ['Shift_L','shift'])
  keyboard_device.write(e.EV_KEY,e.KEY_LEFTALT,1);keyboard_device.syn();time.sleep(.08)
  if backward:keyboard_device.write(e.EV_KEY,e.KEY_LEFTSHIFT,1);keyboard_device.syn();time.sleep(.05)
  keyboard_device.write(e.EV_KEY,e.KEY_TAB,1);keyboard_device.syn();time.sleep(.08)
  keyboard_device.write(e.EV_KEY,e.KEY_TAB,0);keyboard_device.syn();time.sleep(.2)
  if backward:keyboard_device.write(e.EV_KEY,e.KEY_LEFTSHIFT,0);keyboard_device.syn()
  keyboard_device.write(e.EV_KEY,e.KEY_LEFTALT,0);keyboard_device.syn()
 else:subprocess.run(['wtype',*args],check=True)
 time.sleep(.25)
def workspace_key(pid,index,move=False):
 assert active()==pid,'Workspace test lost owned focus'
 from evdev import ecodes as e
 keyboard_device.write(e.EV_KEY,e.KEY_LEFTMETA,1);keyboard_device.syn();time.sleep(.06)
 if move:keyboard_device.write(e.EV_KEY,e.KEY_LEFTSHIFT,1);keyboard_device.syn();time.sleep(.06)
 keyboard_device.write(e.EV_KEY,e.KEY_1+index-1,1);keyboard_device.syn();time.sleep(.08)
 keyboard_device.write(e.EV_KEY,e.KEY_1+index-1,0);keyboard_device.syn()
 if move:keyboard_device.write(e.EV_KEY,e.KEY_LEFTSHIFT,0);keyboard_device.syn()
 keyboard_device.write(e.EV_KEY,e.KEY_LEFTMETA,0);keyboard_device.syn();time.sleep(.4)
def children(pid):
 p=Path(f'/proc/{pid}/task/{pid}/children');return [int(x)for x in p.read_text().split()]if p.exists()else[]
def main():
 global keyboard_device
 from evdev import UInput,ecodes
 keyboard_device=UInput({ecodes.EV_KEY:list(range(1,249))},name='Slamtilt Reborn QA temporary keyboard')
 atexit.register(keyboard_device.close);time.sleep(1)
 p=argparse.ArgumentParser();p.add_argument('--app',type=Path,default=ROOT/'build/compat/releases/slamtilt-reborn-linux-x86_64-rc1');a=p.parse_args();app=a.app.resolve();work=ROOT/'build/reborn-focus';work.mkdir(exist_ok=True)
 original_workspace=int(json.loads(subprocess.check_output(['hyprctl','activeworkspace','-j'],text=True))['name']);assert 1<=original_workspace<=3
 used={x['id']for x in json.loads(subprocess.check_output(['hyprctl','workspaces','-j'],text=True))};qa_workspace=next(i for i in [3,2]if i not in used)
 raw=ROOT/'build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT';demo=ROOT/'build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT';rows=[]
 for index,table in enumerate(['mean','pirate','space','demon']):
  case=work/(table+'-'+str(time.time_ns()));case.mkdir();config=case/'frontend.json';reports=case/'reports';env=dict(os.environ,XDG_DATA_HOME=str(case/'profile'),LD_LIBRARY_PATH=str(app/'lib'));dummy=dict(env,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
  for folder in [raw,demo]:subprocess.run([app/'bin/slamtilt','--config',config,'--import',folder,'--frames','1'],env=dummy,check=True,capture_output=True,text=True)
  log=(case/'parent.log').open('w');parent=subprocess.Popen([app/'bin/slamtilt','--windowed','--config',config,'--session-reports',reports,'--trace',case/'parent.json'],env=env,stdout=log,stderr=log);helper=None
  try:
   wait_active(parent.pid);workspace_key(parent.pid,qa_workspace,move=True);wait_active(parent.pid)
   assert json.loads(subprocess.check_output(['hyprctl','activeworkspace','-j'],text=True))['id']==qa_workspace
   key(parent.pid,'-k',str(index+1),'-s','80','-k','Return')
   end=time.monotonic()+10;child=0
   while time.monotonic()<end:
    cs=children(parent.pid)
    if cs:child=cs[0];break
    time.sleep(.05)
   assert child,'No table child';wait_active(child);game_window=next(v for v in json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True))if v.get('pid')==child);assert game_window['fullscreen'];key(child,'-k','Return');time.sleep(.5)
   # Manual pause must survive a real compositor focus cycle.
   key(child,'-k','p');time.sleep(.4)
   helperlog=(case/'helper.log').open('w');helper=subprocess.Popen([app/'bin/slamtilt','--windowed','--config',case/'helper.json'],env=env,stdout=helperlog,stderr=helperlog)
   wait_active(helper.pid);print('LIVE_CHILD_HELPER',child,helper.pid,flush=True);print('OWN_WINDOWS',json.dumps([v for v in json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True))if v.get('pid')in[child,helper.pid]]),flush=True);time.sleep(.4);key(helper.pid,'-P','Alt_L','-P','Shift_L','-k','Tab','-s','250','-p','Shift_L','-p','Alt_L');wait_active(child);time.sleep(.4)
   key(child,'-k','p');time.sleep(.6)
   # A second actual Alt-Tab roundtrip exercises automatic audio suspension.
   key(child,'-P','Alt_L','-k','Tab','-s','250','-p','Alt_L');wait_active(helper.pid);print('LIVE_CHILD_HELPER',child,helper.pid,flush=True);print('OWN_WINDOWS',json.dumps([v for v in json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True))if v.get('pid')in[child,helper.pid]]),flush=True);time.sleep(.4);key(helper.pid,'-P','Alt_L','-P','Shift_L','-k','Tab','-s','250','-p','Shift_L','-p','Alt_L');wait_active(child);time.sleep(.6)
   key(child,'-k','F10');wait_active(parent.pid)
   # Close helper, then the actual parent via its Quit action.
   wait_active(parent.pid)
   key(parent.pid,'-k','1',*sum((['-k','Down']for _ in range(5)),[]),'-k','Return');parent.wait(timeout=8);assert parent.returncode==0
   wait_active(helper.pid);workspace_key(helper.pid,original_workspace);helper.terminate();helper.wait(timeout=5);helper=None
   paths=[p for p in reports.glob(table+'-*.json')if not p.name.endswith('-audio.json')];assert len(paths)==1
   t=read(paths[0]);frames=t['ui_frames'];assert frames
   assert any(not f['focused']and f['paused']for f in frames),'No real focus loss during manual pause'
   assert any(f['focused']and f['paused']for f in frames),'Manual pause lost on focus gain'
   assert any(not f['focused']and not f['paused']for f in frames),'No second automatic focus pause'
   assert all(f['audio_device_paused']for f in frames if not f['focused']or f['paused']),'Audio advancing while suspended'
   live=[f for f in frames if f['focused']and not f['paused']and not f['menu']and not f.get('game_over',False)];assert live and not live[-1]['audio_device_paused'],'Audio did not resume'
   for paused in [True,False]:
    blocks=[];block=[]
    for f in frames:
     if not f['focused']and f['paused']==paused:block.append(f['tick'])
     elif block:blocks.append(block);block=[]
    if block:blocks.append(block)
    assert blocks and all(min(b)==max(b)for b in blocks),'Simulation advanced without focus'
   parent_trace=read(case/'parent.json');assert parent_trace['events']==[dict(event='launched',table=table),dict(event='returned',table=table,exit_code=0)]
   rows.append(dict(table=table,actual_alt_tab=True,fullscreen_game_focus_case=True,temporary_owned_workspace=True,manual_pause_preserved=True,simulation_suspended=True,audio_suspend_resume=True,F10_return=True,table_pid=child,trace=str(paths[0].relative_to(ROOT))));print(table,'real Alt-Tab/pause/audio/F10 PASS',flush=True)
  finally:
   if helper and helper.poll()is None:
    if active()==helper.pid:workspace_key(helper.pid,original_workspace)
    helper.terminate();helper.wait(timeout=5)
   if parent.poll()is None:
    if active()==parent.pid:workspace_key(parent.pid,original_workspace)
    parent.terminate();parent.wait(timeout=8)
 import hashlib
 report=dict(status='VERIFIED_REAL_COMPOSITOR',archive_sha256=hashlib.sha256(Path(str(app)+'.tar.gz').read_bytes()).hexdigest(),cases=rows,scope='Actual temporary uinput-keyboard compositor forward/backward Alt-Tab between owned fullscreen games and a helper window, Hyprland PID assertions before every input; real SDL focus/audio/tick reports, no injected focus events. No physical keyboard/listening claim.')
 (ROOT/'analysis/traces/reborn-focus.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
