#!/usr/bin/env python3
"""Generate a developer-only instrumented lift; production sources stay untouched."""
import argparse,hashlib,json,re
from pathlib import Path
def write_changed(path,text):
 if not path.exists()or path.read_text()!=text:path.write_text(text)
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);header=a.root/'src/physics/pirate_step_lift.h';source=a.root/'build/generated/pirate_step.cpp'
h=header.read_text();needle='  PirateStepLift():runtime(0x10000) {}';assert needle in h
h=h.replace(needle,'''  std::function<void(std::uint32_t,std::uint32_t,unsigned,bool)> audit_access;
  std::uint32_t audit_rd(std::uint32_t pc,std::uint32_t address,unsigned count) {
    if(address>=0x1100000&&address-0x1100000<dat.size()&&audit_access)audit_access(pc,address,count,false);
    return rd(address,count);
  }
  void audit_wr(std::uint32_t pc,std::uint32_t address,std::uint32_t value,unsigned count) {
    if(address>=0x1100000&&address-0x1100000<dat.size()&&audit_access)audit_access(pc,address,count,true);
    wr(address,value,count);
  }
'''+needle)
(a.output/'physics').mkdir(exist_ok=True);write_changed(a.output/'physics/pirate_step_lift.h',h)
session=a.root/'src/physics/pirate_session.h';text=session.read_text();assert 'private:'in text
text=text.replace('private:','  PirateStepLift& asset_audit_machine(){return machine_;}\nprivate:',1)
write_changed(a.output/'physics/pirate_session.h',text)
write_changed(a.output/'pirate_session_audit.cpp',(a.root/'src/physics/pirate_session.cpp').read_text())

lines=[];counts={'rd':0,'wr':0}
for line in source.read_text().splitlines(True):
 m=re.match(r'L([0-9a-f]+):',line)
 for kind in ['rd','wr']:
  if 'm.'+kind+'('in line:
   assert m,('Unlabelled memory operation',line[:100]);counts[kind]+=line.count('m.'+kind+'(')
   line=line.replace('m.'+kind+'(','m.audit_'+kind+'(0x'+m[1]+',')
 lines.append(line)
write_changed(a.output/'pirate_step_audit.cpp',''.join(lines));(a.output/'instrumentation.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'header_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),'generated_source_sha256':hashlib.sha256((a.output/'pirate_step_audit.cpp').read_bytes()).hexdigest(),'memory_operations':counts,'scope':'RD/WR wrapper only; instruction PCs retained; production sources and binaries untouched'},indent=2)+'\n')
