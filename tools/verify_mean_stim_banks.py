#!/usr/bin/env python3
"""Verify original Windows Mean STIM extraction and eight proved event/initial orders."""
import argparse, ctypes, hashlib, json
from pathlib import Path
from extract_mean_stim import extract

def main():
    p=argparse.ArgumentParser();p.add_argument('--dat',type=Path,required=True);p.add_argument('--libxmp',type=Path,required=True);p.add_argument('--out-dir',type=Path,default=Path('build/mean-audio'));p.add_argument('--report',type=Path);a=p.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True);data=a.dat.read_bytes()
    l=ctypes.CDLL(str(a.libxmp.resolve()));P=ctypes.c_void_p;l.xmp_create_context.restype=P
    for f,args in [('xmp_load_module',[P,ctypes.c_char_p]),('xmp_start_player',[P,ctypes.c_int,ctypes.c_int]),('xmp_set_position',[P,ctypes.c_int]),('xmp_play_buffer',[P,P,ctypes.c_int,ctypes.c_int]),('xmp_end_player',[P]),('xmp_release_module',[P]),('xmp_free_context',[P])]:getattr(l,f).argtypes=args
    records=[]
    for bank,orders in [(0,[0,4,23,73]),(1,[0,49,53,56])]:
        raw,_=extract(data,bank);target=a.out_dir/f'mean-bank-{bank}.stim';target.write_bytes(raw)
        for order in orders:
            c=l.xmp_create_context();load=l.xmp_load_module(c,str(target).encode());assert load==0
            start=l.xmp_start_player(c,44100,0);assert start==0
            position=l.xmp_set_position(c,order) if order else None
            assert order==0 or position==order
            buf=ctypes.create_string_buffer(44100*4);play=l.xmp_play_buffer(c,buf,len(buf),0);assert play==0
            nonzero=sum(x!=0 for x in buf.raw);assert nonzero>0
            records.append(dict(bank=bank,order=order,load=load,start=start,position=position,play=play,nonzero_bytes=nonzero,pcm_sha256=hashlib.sha256(buf.raw).hexdigest()))
            l.xmp_end_player(c);l.xmp_release_module(c);l.xmp_free_context(c)
    if a.report:a.report.write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps({'cases':len(records),'banks':2,'load_start_render_exact':True}))
if __name__=='__main__':main()
