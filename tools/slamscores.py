#!/usr/bin/env python3
"""Read original Slam Tilt STTF highscore records or 332-byte Windows CFG.
Never writes input. Preserve unknown bytes when implementing an eventual writer.
"""
import argparse,json,struct
from pathlib import Path

def bcd_score(raw):
 if len(raw)!=6 or any((v>>4)>9 or (v&15)>9 for v in raw):raise ValueError('invalid six-byte packed BCD score')
 return int(raw.hex())
def records(data,start,stride):
 if start<0 or start+5*stride>len(data):raise ValueError('highscore records exceed input')
 return [{'offset':start+i*stride,'score':bcd_score(data[start+i*stride:start+i*stride+6]),'initials':data[start+i*stride+6:start+i*stride+9].decode('latin1'),'raw':data[start+i*stride:start+(i+1)*stride].hex()} for i in range(5)]
def inspect(path):
 data=Path(path).read_bytes()
 if data[:4]==b'STTF':
  if len(data)<34:raise ValueError('truncated STTF header')
  start=int.from_bytes(data[30:34],'big')
  return {'format':'STTF','score_offset':start,'record_size':14,'highscores':records(data,start,14)}
 if len(data)==332 and Path(path).suffix.lower()=='.cfg':
  return {'format':'windows-cfg','record_size':10,'highscores':{name:records(data,0x68+i*50,10) for i,name in enumerate(['mean','pirate','space','demon'])},'leading_doubles':list(struct.unpack('<7d',data[:56])),'unknown_header_hex':data[56:104].hex(),'unknown_trailer_hex':data[304:].hex()}
 raise ValueError('unrecognized highscore file')
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('file');args=parser.parse_args()
 try:print(json.dumps(inspect(args.file),indent=2))
 except (OSError,ValueError) as e:parser.exit(1,f'{e}\n')
