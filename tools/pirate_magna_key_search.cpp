// Bounded native search: frozen diagnostic admission, legal keys only after release.
#include "physics/pirate_session.h"
#include "core/pirate_input_replay.h"
#include "core/pirate_shot_replay.h"
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <cmath>
#include <limits>
using nlohmann::json;
static unsigned rd(const std::vector<std::uint8_t>&image,unsigned address,unsigned count=4){unsigned v=0;for(unsigned i=0;i<count;++i)v|=unsigned(image.at(address-0x400000+i))<<(8*i);return v;}
struct Policy{std::string kind;int a,b;};
int main(int argc,char**argv){try{
 if(argc!=6)return 2;
 std::ifstream in(argv[3]);json source;in>>source;
 unsigned release=0;for(const auto&m:source.at("milestones"))if(m.at("label")=="field_released")release=m.at("tick");
 if(!release)throw std::runtime_error("No release marker");
 json prefix={{"inputs",json::array()},{"diagnostic_shots",json::array()}};
 for(const auto&e:source.at("inputs"))if(e.at("tick").get<unsigned>()<release)prefix["inputs"].push_back(e);
 for(const auto&e:source.at("diagnostic_shots"))if(e.at("tick").get<unsigned>()<release)prefix["diagnostic_shots"].push_back(e);
 const std::filesystem::path output=argv[4];std::filesystem::create_directories(output);
 const auto prefix_path=output/"entry-prefix.json";std::ofstream(prefix_path)<<prefix.dump()<<'\n';
 slam::PirateInputReplay input;slam::PirateShotReplay shots;input.load(prefix_path);shots.load(prefix_path);
 const auto profile=slam::load_table_profile(slam::default_table_profiles(),"pirate");
 slam::PirateSession session(argv[1],argv[2],slam::PirateTickMode::Full);session.enable_lamps(true);
 std::vector<Policy> policies;
 for(int mask=0;mask<4;++mask)policies.push_back({"fixed",mask,0});
 for(int mask=0;mask<4;++mask)for(int delay:{20,50,100,160,240,360,500,750,1000,1500,2200})policies.push_back({"delayed",mask,delay});
 for(int a=0;a<4;++a)for(int b=0;b<4;++b)if(a!=b)for(int period:{25,60,120,240,500,900})policies.push_back({"alternate",a*4+b,period});
 for(int center:{90,100,110,120,130,140})for(int dead:{0,4,10,20})for(int polarity:{0,1})policies.push_back({"feedback",center,dead+100*polarity});
 for(int center:{90,100,110,120,130,140})for(int height:{20,35,50,65})for(int polarity:{0,1})policies.push_back({"vertical",center,height+100*polarity});
 json report={{"source",argv[3]},{"field_released_tick",release},{"policies",json::array()},{"status","NO_REWARD"}};
 double global_best=std::numeric_limits<double>::infinity();int index=0;bool found=false;
 const int limit=std::min(300,std::stoi(argv[5]));
 for(const auto&p:policies){if(index>=limit)break;
  session.reset();input.reset();shots.reset();bool left=false,right=false;
  for(unsigned tick=0;tick<release;++tick){input.apply(session,tick,left,right);shots.apply(session,profile);session.step();}
  json events=prefix["inputs"];double best=1e9;json closest,trail=json::array();unsigned reward=0,returned=0;int used=0;
  for(int step=0;step<5000;++step){
   const auto&image=session.executable_image();
   const double x=double(std::int32_t(rd(image,0x46c15c)))/65536.0,y=double(std::int32_t(rd(image,0x46c160)))/65536.0;
   const auto state=rd(image,0x46c1b4,2),capture=rd(image,0x46c1b6,2),active=rd(image,0x46e542,2);
   const double distance=std::hypot(x-120.0,y-14.0);
   if(distance<best){best=distance;closest={{"tick",session.ticks()},{"x",x},{"y",y},{"state",state},{"capture",capture},{"layer",rd(image,0x46c1a4,2)}};}
   if(step%100==0)trail.push_back({session.ticks(),x,y,state,active});
   if(state==3&&capture==6&&!reward){reward=session.ticks();std::cout<<"REWARD policy "<<index<<" tick "<<reward<<'\n'<<std::flush;}
   if(reward&&state==2&&!active){returned=session.ticks();used=step;break;}
   if(!active&&!reward){used=step;break;}
   int mask=3;
   if(reward)mask=0;
   else if(p.kind=="fixed")mask=p.a;
   else if(p.kind=="delayed")mask=step<p.b?3:p.a;
   else if(p.kind=="alternate")mask=(step/p.b)%2?p.a%4:p.a/4;
   else if(p.kind=="feedback"){
    const int dead=p.b%100;const bool reverse=p.b>=100;
    mask=x<p.a-dead?(reverse?2:1):x>p.a+dead?(reverse?1:2):3;
   }else{
    const int height=p.b%100;const bool reverse=p.b>=100;
    mask=y<height?0:(x<p.a?(reverse?2:1):(reverse?1:2));
   }
   const bool next_left=mask&1,next_right=mask&2;
   if(next_left!=left)events.push_back({{"tick",session.ticks()},{"action","left"},{"down",next_left}});
   if(next_right!=right)events.push_back({{"tick",session.ticks()},{"action","right"},{"down",next_right}});
   session.flippers(next_left,next_right);left=next_left;right=next_right;session.step();used=step+1;
  }
  json row={{"index",index},{"kind",p.kind},{"a",p.a},{"b",p.b},{"steps",used},{"closest_distance",best},{"closest",closest},{"reward_tick",reward},{"return_tick",returned}};
  report["policies"].push_back(row);
  if(best<global_best||reward){global_best=best;json candidate={{"inputs",events},{"diagnostic_shots",prefix["diagnostic_shots"]},{"policy",row},{"trail",trail},{"tick_count",session.ticks()}};std::ofstream(output/"best-candidate.json")<<candidate.dump(2)<<'\n';}
  if(index%20==0)std::cout<<"policy "<<index<<" best "<<best<<" global "<<global_best<<'\n'<<std::flush;
  ++index;
  if(reward){found=true;report["status"]=returned?"NATIVE_REWARD_AND_RETURN":"NATIVE_REWARD";report["candidate"]=row;break;}
 }
 report["tested_policies"]=index;report["post_entry_inputs"]="Left/right original game-action edges only; no diagnostic/state writes after field_released";
 report["verification"]="Native search only; independent original/reset/SDL proof pending";
 std::ofstream(output/"search.json")<<report.dump(2)<<'\n';
 json summary=report;summary.erase("policies");summary["best_distance"]=global_best;
 std::ofstream("analysis/pirate-magna-key-search.json")<<summary.dump(2)<<'\n';
 return found?0:3;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
