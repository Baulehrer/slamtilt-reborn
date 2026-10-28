#!/usr/bin/env python3
"""Bounded wall-clock/queued-SDL-input measurements; no physical latency claim."""
import argparse,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def percentile(xs,p):
    xs=sorted(xs);return xs[min(len(xs)-1,int((len(xs)-1)*p))]if xs else None

def main():
    p=argparse.ArgumentParser();p.add_argument('--launcher',type=Path,required=True);p.add_argument('--label',required=True);a=p.parse_args()
    out=ROOT/'build/oracle/pirate-realtime'/a.label;out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ);env.pop('SDL_VIDEODRIVER',None);env.pop('SDL_AUDIODRIVER',None);rows=[]
    for full in [False,True]:
        path=out/f'{full}.json'
        subprocess.run([a.launcher,'--data',ROOT/'build/imported/pirate-retail','--fullscreen'if full else'--windowed',
            '--realtime-ms','4000','--autoplay','--timing-inputs','--timing-output',path],env=env,check=True,timeout=30)
        t=json.loads(path.read_text());assert not t['error']and len(t['inputs'])==8,t['inputs']
        assert all('observed_ns'in e and e['observed_ns']>=e['handled_ns']>=e['queued_ns']for e in t['inputs'])
        f=t['frames'];assert f[-1][5]>=660
        warm=[r for r in f if r[0]>=1000000000]
        intervals=[(b[0]-a[0])/1e6 for a,b in zip(warm,warm[1:])]
        latencies=[(e['observed_ns']-e['queued_ns'])/1e6 for e in t['inputs']]
        row=dict(fullscreen=t['fullscreen'],video=t['video'],renderer=t['renderer'],frames=len(f),ticks=f[-1][5],
            frame_interval_p50_ms=percentile(intervals,.5),frame_interval_p95_ms=percentile(intervals,.95),
            render_phase_p95_ms=percentile([r[3]/1e6 for r in warm],.95),sim_audio_phase_p95_ms=percentile([r[2]/1e6 for r in warm],.95),
            present_phase_p95_ms=percentile([r[4]/1e6 for r in warm],.95),queued_to_pose_p95_ms=percentile(latencies,.95),
            input_samples=len(latencies),ball_file_reads=t['ball_file_reads'],texture_uploads=t['uploads'])
        if len(f[0])>=11:
            active_ns=sum(r[9]for r in f if r[7]);steps=sum(r[6]for r in f)
            row.update(active_ns=active_ns,steps=steps,tick_quantization_error_ns=abs(steps*5000000-active_ns),clamped_frames=sum(r[10]>100000000 for r in f))
            assert row['tick_quantization_error_ns']<5000000
        rows.append(row);print(row,flush=True)
    report=dict(status='MEASURED',label=a.label,cases=rows,scope='Two4second real-clock runs; firstsecond excluded from frame percentiles. 8queued synthetic SDL presses perrun; wall-time diagnostics around call groups, not physical input-to-photon or GPU timing. No general performance guarantee.')
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
