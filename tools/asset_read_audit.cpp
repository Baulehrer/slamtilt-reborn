#include "physics/pirate_step_lift.h"
#include "core/sha256.h"
#include "physics/pirate_session.h"
#include "core/pirate_input_replay.h"
#include <memory>
#include <nlohmann/json.hpp>
#include <fstream>
#include <algorithm>
#include <iostream>
#include <map>
using nlohmann::json;
using Bytes=std::vector<std::uint8_t>;
Bytes read(const std::string& p){std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("Missing "+p);return {std::istreambuf_iterator<char>(f),{}};}
struct Access{unsigned reads=0,writes=0,pc=0,tick=0;bool initialized=false;};
int main(int argc,char**argv){try{
 if(argc!=8)throw std::runtime_error("Usage: audit TABLE PREPARED DAT PC_DAT FIXTURE TICKS REPORT");
 const std::string table=argv[1],dir=argv[2];const unsigned ticks=std::stoul(argv[6]);if(!ticks||ticks>60000)throw std::runtime_error("Bounded audit requires1..60000ticks");
 slam::PirateStepLift retail;std::unique_ptr<slam::PirateSession> session;
 if(table=="pirate"){session=std::make_unique<slam::PirateSession>(dir,argv[3],slam::PirateTickMode::Full);session->enable_lamps(true);}
 else{retail.image=read(dir+"/human-image.bin");retail.runtime=read(dir+"/human-runtime.bin");retail.dat=read(argv[3]);}
 auto&m=session?session->asset_audit_machine():retail;const auto initial_dat=m.dat;const auto pc_dat=read(argv[4]);if(pc_dat.size()!=m.dat.size())throw std::runtime_error("Reference DAT size mismatch");
 json fixture;{std::ifstream f(argv[5]);f>>fixture;}
 std::map<unsigned,std::vector<json>> inputs;for(const auto&e:fixture.at("inputs"))inputs[e.at("tick")].push_back(e);
 slam::PirateInputReplay replay;bool left=false,right=false;if(session)replay.load(argv[5]);
 std::map<unsigned,json> objects;
 std::vector<Access> access(m.dat.size());unsigned tick=0;std::uint64_t reads=0,writes=0;
 m.call_observer=[&](slam::PirateStepLift& state,unsigned address){
  if(address!=0x407020||state.r[0]<0x1100000)return;
  const auto offset=state.r[0]-0x1100000;
  if(offset>initial_dat.size()||initial_dat.size()-offset<480||objects.count(offset))return;
  unsigned diff=0;for(unsigned i=0;i<480;++i)diff+=initial_dat[offset+i]!=pc_dat[offset+i];
  objects[offset]={{"offset",offset},{"size",480},{"reader",address},{"first_tick",tick},{"caller_return",state.rd(state.r[4],4)},{"pc_different_bytes",diff}};
 };
 m.audit_access=[&](unsigned pc,unsigned address,unsigned count,bool write){
  const auto offset=address-0x1100000;if(count>access.size()-offset)throw std::runtime_error("Asset audit range");
  for(unsigned i=0;i<count;++i){auto&a=access[offset+i];if(write){++a.writes;a.initialized=true;++writes;}else if(!a.initialized){if(!a.reads){a.pc=pc;a.tick=tick;}++a.reads;++reads;}}
 };
 for(tick=0;tick<ticks;++tick){
  if(session)replay.apply(*session,tick,left,right);else for(const auto&e:inputs[tick]){const std::string action=e.at("action");unsigned scan=action=="key"?e.at("scan").get<unsigned>():action=="new_game"?0x3b:action=="enter"?0x1c:action=="left"?0x2a:action=="right"?0x36:throw std::runtime_error("Unsupported audit input");m.r[2]=scan;m.invoke(0x40404c,e.at("down").get<bool>()?0:1);}
  if(session)session->step();else{m.invoke(0x405234,(tick+1)*5);if((tick+1)%4==0){m.invoke(0x408da8);m.invoke(0x408674);}}
  const auto base=table=="pirate"?0x46c15c:m.rd(0x454b68,4);Bytes state(100);for(unsigned i=0;i<100;++i)state[i]=m.rd(base+i,1);
  if(state!=fixture.at("states").at(tick+1).get<Bytes>())throw std::runtime_error("Audit trajectory differs at "+std::to_string(tick));
 }
 json ranges=json::array();unsigned unique=0,different=0;
 for(std::size_t i=0;i<access.size();){if(!access[i].reads){++i;continue;}
  if(initial_dat[i]==pc_dat[i]){++i;continue;}
  const auto start=i;const auto pc=access[i].pc,first=access[i].tick;unsigned total=0;
  do{total+=access[i].reads;++different;++i;}while(i<access.size()&&access[i].reads&&initial_dat[i]!=pc_dat[i]&&access[i].pc==pc&&access[i].tick==first);
  ranges.push_back({{"offset",start},{"size",i-start},{"first_pc",pc},{"first_tick",first},{"reads",total}});
 }
 unique=std::count_if(access.begin(),access.end(),[](const auto&a){return a.reads!=0;});
 json object_list=json::array();for(const auto& entry:objects)object_list.push_back(entry.second);
 std::ofstream(argv[7])<<json{{"status","VERIFIED_BOUNDED_NATIVE_READS"},{"table",table},{"ticks",ticks},{"trajectory_exact",true},{"source_read_bytes",reads},{"write_bytes",writes},{"unique_read_bytes",unique},{"pc_different_read_bytes",different},{"ranges",ranges},{"dmd_objects",object_list},{"source_sha256",slam::sha256(initial_dat)},{"pc_source_sha256",slam::sha256(pc_dat)},{"scope","Shared native lifted instructions only; reads after DAT writes excluded; SDL file loaders not observed; differences can be legitimate Amiga artwork"}}.dump(2)<<'\n';
 std::cout<<table<<" ticks="<<ticks<<" differences="<<different<<" ranges="<<ranges.size()<<'\n';
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
