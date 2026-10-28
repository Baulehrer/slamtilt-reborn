import pathlib,struct,subprocess,json,hashlib,sys,runpy
root=pathlib.Path(__file__).resolve().parents[1];import os;os.chdir(root);pathlib.Path('build/validation').mkdir(parents=True,exist_ok=True);uk=next(pathlib.Path('build/corpus/win95/uk-1997').rglob('GAME'));out=pathlib.Path('build/validation');results={'method':'Independent Python raw DAT palette indexing vs native exported BMP pixels; no original screenshot comparison','tables':[],'negative_cases':[]}
profiles={'MEAN':0x1590c8,'PIRATE':0x14605c,'SPACE':0x14c035,'DEMON':0x146830}
for n,palette in profiles.items():
 dat=uk/'DAT'/f'{n}.DAT';bmp=out/f'{n}.bmp';r=subprocess.run(['tools/slamview',str(dat),'--export',str(bmp)],capture_output=True,text=True);assert r.returncode==0,r.stderr
 b=bmp.read_bytes();off=struct.unpack_from('<I',b,10)[0];w,h=struct.unpack_from('<ii',b,18);bits=struct.unpack_from('<H',b,28)[0];assert w==320 and abs(h)==600 and bits==32,(w,h,bits)
 data=dat.read_bytes();expected=bytes(channel for index in data[palette+1024:palette+1024+320*600] for channel in data[palette+4*index+1:palette+4*index+4]);actual=bytearray()
 for y in range(600):
  row=off+(599-y if h>0 else y)*320*4
  for x in range(320):
   p=row+4*x;actual.extend([b[p+2],b[p+1],b[p]])
 mismatches=sum(expected[i:i+3]!=actual[i:i+3] for i in range(0,len(expected),3));assert mismatches==0
 results['tables'].append({'table':n,'dat':str(dat),'dat_sha256':hashlib.sha256(data).hexdigest(),'bmp':str(bmp),'width':w,'height':abs(h),'compared_pixels':192000,'mismatched_pixels':mismatches,'rgb_sha256':hashlib.sha256(expected).hexdigest()})
mean=(uk/'DAT/MEAN.DAT').read_bytes()
cases={'empty':b'','unsupported':b'unknown format','truncated':mean[:0x1590c8+1030],'bad_palette_same_size':mean[:0x1590c8]+bytes([255])+mean[0x1590c8+1:]}
for name,data in cases.items():
 p=out/(name+'.dat');p.write_bytes(data);r=subprocess.run(['tools/slamview',str(p),'--export',str(out/(name+'.bmp'))],capture_output=True,text=True);assert r.returncode!=0
 results['negative_cases'].append({'case':name,'exit_code':r.returncode,'diagnostic':r.stderr.strip()})
# Demo table asset identity and exports.
demo=next(pathlib.Path('build/corpus/win95/demo-1997').rglob('MEAN.DAT'));r=subprocess.run(['tools/slamview',str(demo),'--export',str(out/'DEMO_MEAN.bmp')],capture_output=True,text=True)
results['demo']={'path':str(demo),'sha256':hashlib.sha256(demo.read_bytes()).hexdigest(),'identical_to_retail_mean':demo.read_bytes()==mean,'export_exit_code':r.returncode};assert r.returncode==0 and demo.read_bytes()==mean
# Independent STTF parser comparison.
inspect=runpy.run_path('tools/slaminfo')['inspect'];sys.path.insert(0,'tools');from slamscores import inspect as scores
count=0
for p in pathlib.Path('build/corpus').rglob('*.Dat'):
 if not p.is_file() or p.read_bytes()[:4]!=b'STTF':continue
 a=inspect(p);b=scores(p);hs=next(s for s in a['structures'] if s['kind']=='highscores');assert hs['offset']==b['score_offset'];assert [(v['score'],v['initials']) for v in hs['records']]==[(v['score'],v['initials']) for v in b['highscores']];count+=1
results['sttf_cross_check']={'files_compared':count,'mismatches':0}
results['cli_cases']=[]
for options in [['--frames','0'],['--frames','-1'],['--frames','2x'],['--export'],['--unknown']]:
 r=subprocess.run(['tools/slamview',str(uk/'DAT/MEAN.DAT'),*options],capture_output=True,text=True);assert r.returncode!=0
 results['cli_cases'].append({'options':options,'exit_code':r.returncode,'diagnostic':r.stderr.strip()})
r=subprocess.run(['tools/slamview',str(uk/'DAT/MEAN.DAT'),'--frames','3'],env={**dict(__import__('os').environ),'SDL_VIDEODRIVER':'dummy'},capture_output=True,text=True);assert r.returncode==0
results['headless_window_smoke']={'frames':3,'exit_code':r.returncode,'output':r.stdout.strip(),'limitation':'dummy video driver; interactive scrolling and physical display not validated'}
# Deliberately malformed but correct-sized data demonstrates recognition limitation.
forged=out/'same_size_zero.dat';forged.write_bytes(bytes(len(mean)));r=subprocess.run(['tools/slamview',str(forged),'--export',str(out/'same_size_zero.bmp')],capture_output=True,text=True)
results['recognition_limitation']={'case':'all-zero file of known MEAN size','exit_code':r.returncode,'accepted':r.returncode==0,'implication':'native identification checks size and palette shape; it does not authenticate revision or general DAT structure'}
# Cross-check native Amiga planar exports against independent Python decoder.
from slamamiga import playfield
results['amiga_tables']=[]
for name in ['Mean','Pirate','Space','Demon']:
 raw=pathlib.Path('build/decoded/full')/(name+'.Raw');data=raw.read_bytes();bmp=out/(name+'_AMIGA.bmp')
 r=subprocess.run(['tools/slamview',str(raw),'--amiga','--export',str(bmp)],capture_output=True,text=True);assert r.returncode==0,r.stderr
 b=bmp.read_bytes();off=struct.unpack_from('<I',b,10)[0];w,h=struct.unpack_from('<ii',b,18);bits=struct.unpack_from('<H',b,28)[0];assert w==320 and abs(h)==600 and bits==32
 actual=bytearray()
 for y in range(600):
  row=off+(599-y if h>0 else y)*320*4
  for x in range(320):
   q=row+4*x;actual.extend([b[q+2],b[q+1],b[q]])
 expected=playfield(data);differences=sum(actual[j:j+3]!=expected[j:j+3] for j in range(0,len(expected),3));assert differences==0
 results['amiga_tables'].append({'table':name,'raw':str(raw),'raw_sha256':hashlib.sha256(data).hexdigest(),'compared_pixels':192000,'mismatched_pixels':differences,'rgb_sha256':hashlib.sha256(expected).hexdigest(),'bmp':str(bmp)})
source=pathlib.Path('build/decoded/full/Mean.Raw').read_bytes();section=int.from_bytes(source[:4],'big');palette=section+int.from_bytes(source[section+4:section+8],'big')
cases={'empty':b'','truncated_header':source[:23],'invalid_section_pointer':bytes.fromhex('ffffffff')+source[4:],'unsupported_pixels_pointer':source[:section]+bytes.fromhex('00000019')+source[section+4:],'truncated_palette':source[:palette+1000],'invalid_palette':source[:palette]+b'\xff'+source[palette+1:],'compressed_magic':b'SLAM'+source[4:]}
results['amiga_negative_cases']=[]
for name,data in cases.items():
 path=out/('amiga_'+name+'.raw');path.write_bytes(data);r=subprocess.run(['tools/slamview',str(path),'--amiga','--export',str(out/('amiga_'+name+'.bmp'))],capture_output=True,text=True);assert r.returncode!=0
 results['amiga_negative_cases'].append({'case':name,'exit_code':r.returncode,'diagnostic':r.stderr.strip()})
pathlib.Path('analysis/renderer-validation.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
