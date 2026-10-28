#!/usr/bin/env python3
"""Renderer optimization must preserve original established scene and gameplay."""
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    f=json.loads((ROOT/'analysis/traces/pirate-render-cache.json').read_text());work=ROOT/'build/oracle/pirate-render-cache'
    trace=work/'verified.json';capture=work/'verified.bmp';timing=work/'verified-timing.json'
    subprocess.run([ROOT/'tools/slampirate','--data',ROOT/'build/imported/pirate-retail','--frames','1000','--no-audio',
        '--replay',ROOT/'analysis/traces/pirate-acceptance-multiball.json','--full-state-trace','--trace-output',trace,
        '--capture',capture,'--timing-output',timing],check=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
    t=json.loads(trace.read_text());assert not t['error']and t['tick_count']==4000
    for key,digest in f['vectors'].items():assert hashlib.sha256(json.dumps(t[key],separators=(',',':')).encode()).hexdigest()==digest,key
    assert hashlib.sha256(capture.read_bytes()).hexdigest()==f['screenshot_sha256']
    m=json.loads(timing.read_text());assert m['ball_file_reads']==0 and m['uploads']==f['optimized_uploads']
    print('4000steps/10vectors/camera/full BMP exact;0per-ball file reads;',m['uploads'],'uploads')
if __name__=='__main__':main()
