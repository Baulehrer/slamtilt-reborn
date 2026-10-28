// Offline branching from a complete reachable state; candidates are frozen legal
// actions and must be independently replayed from reset in original/native/SDL.
#include "pirate_session_search.h"
#include "core/pirate_input_replay.h"
#include <chrono>
#include <fstream>
#include <iostream>
#include <cmath>
using nlohmann::json;
static int signed_word(const std::array<std::uint8_t,100>& b,unsigned o) {
 unsigned x=0;for(unsigned i=0;i<4;++i)x|=unsigned(b.at(o+i))<<(i*8);return std::int32_t(x);
}
int main(int argc,char**argv){try{
 if(argc!=5)return 2;
 const std::filesystem::path out=argv[4];std::filesystem::create_directories(out);
 slam::PirateSession s(argv[1],argv[2],slam::PirateTickMode::Full);s.enable_lamps(true);
 slam::PirateInputReplay replay;replay.load(argv[3]);bool left=false,right=false;
 std::ifstream in(argv[3]);json src;in>>src;json prefix=json::array();
 constexpr unsigned start_tick=5400;
 for(const auto&e:src.at("inputs"))if(e.at("tick").get<unsigned>()<start_tick)prefix.push_back(e);
 for(unsigned tick=0;tick<start_tick;++tick){replay.apply(s,tick,left,right);s.step();}
 auto checkpoint=slam::PirateSessionSearch::capture(s);
 const auto get=[&](unsigned a,unsigned n=4){return slam::PirateSessionSearch::read(s,a,n);};
 if(get(0x46e2bc,2)!=2||s.phase()!=2)throw std::runtime_error("Expected two earned Cave locks");
 const auto begin=std::chrono::steady_clock::now();
 const auto seconds=[&]{return std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();};
 unsigned trials=0,steps=0;double best=-1e30;json rows=json::array();bool found=false;
 const auto save=[&](const json& events,const json& policy,double score){json c={{"inputs",events},{"diagnostic_shots",json::array()},{"tick_count",s.ticks()},{"policy",policy},{"score",score},{"scope","Native-only search: complete reachable checkpoint; only subsequent Enter/Shift actions. Fresh Original/reset/SDL proof pending."}};std::ofstream(out/"best-candidate.json")<<c.dump(2)<<'\n';};
 for(int mode=0;mode<3&&!found&&seconds()<60;++mode)for(int onset=5450;onset<=5610&&!found&&seconds()<60;onset+=4)for(int duration:{8,16,32,64,128,256}){
  if(found||seconds()>=60)break;
  slam::PirateSessionSearch::restore(s,checkpoint);left=checkpoint.left;right=checkpoint.right;json events=prefix;
  double score=-1e30;std::string error;bool cannon=false;unsigned entry=0;
  const auto edge=[&](bool l,bool r){if(l!=left)events.push_back({{"tick",s.ticks()},{"action","left"},{"down",l}});if(r!=right)events.push_back({{"tick",s.ticks()},{"action","right"},{"down",r}});s.flippers(l,r);left=l;right=r;};
  try{for(unsigned t=start_tick;t<start_tick+1400;++t){
   const bool l=mode==0?false:mode==1?bool((t/16)%2):t>=unsigned(onset)&&t<unsigned(onset+duration);
   const bool r=t>=unsigned(onset)&&t<unsigned(onset+duration);edge(l,r);s.step();++steps;
   const auto b=s.ball();const int state=unsigned(b[88])|(unsigned(b[89])<<8),layer=unsigned(b[72])|(unsigned(b[73])<<8);
   if(state==2&&layer==0){const double x=signed_word(b,0)/65536.0,y=signed_word(b,4)/65536.0;const double dist=std::hypot(x-86,y-10);score=std::max(score,1000-dist);}
   if(s.phase()==6){cannon=true;entry=s.ticks();break;}
   if(s.phase()==3||s.phase()==0)break;
  }
  if(cannon){edge(false,false);const unsigned entered=unsigned(s.ticks());
   while(s.phase()==6&&s.ticks()-entered<1600){
    if(get(0x465974)>=0x80000000u){const unsigned angle=get(0x465970)&4095;const auto sine=std::int16_t(get(get(0x46b778)+angle*2,2));if(std::abs(int(sine))<1000){edge(true,false);s.step();++steps;edge(false,false);break;}}
    s.step();++steps;
   }
   while(s.phase()!=4&&s.ticks()-entered<3600&&get(0x46e2bc,2)>=2){s.step();++steps;}
   found=s.phase()==4&&get(0x46e2be,2)>=1;
   if(found){score=1000000;for(unsigned n=0;n<1200;++n){s.step();++steps;}}
  }
  }catch(const std::exception&e){error=e.what();}
  ++trials;json policy={{"mode",mode},{"onset",onset},{"duration",duration},{"cannon",cannon},{"cannon_tick",entry},{"multiball",found},{"phase",s.phase()},{"ball_count",s.ball_count()},{"error",error}};rows.push_back(policy);
  if(score>best){best=score;save(events,policy,score);std::cout<<"best "<<trials<<" score "<<score<<" onset "<<onset<<" duration "<<duration<<" cannon "<<cannon<<" multi "<<found<<'\n'<<std::flush;}
 }
 json report={{"status",found?"NATIVE_CROCODILE":"BOUNDED_NO_ENTRY"},{"trials",trials},{"simulated_steps",steps},{"wall_seconds",seconds()},{"prefix_steps",start_tick},{"policies",rows}};std::ofstream(out/"search.json")<<report.dump(2)<<'\n';return found?0:3;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
