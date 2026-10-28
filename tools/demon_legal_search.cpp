// Bounded feedback search: only real Enter/Shift edges, never gameplay writes.
#include "physics/pirate_step_lift.h"
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <chrono>
using nlohmann::json;
static std::vector<std::uint8_t> read(const std::string& p){std::ifstream f(p,std::ios::binary);return {std::istreambuf_iterator<char>(f),{}};}
int main(int argc,char**argv){try{
 if(argc!=3)return 2;
 slam::PirateStepLift initial;const std::string dir=argv[1];initial.image=read(dir+"/human-image.bin");initial.runtime=read(dir+"/human-runtime.bin");initial.dat=read(dir+"/human-dat.bin");
 const auto start=std::chrono::steady_clock::now();unsigned runs=0,total=0;json rows=json::array();
 for(int threshold:{440,460,480,490,500,510,520,530,540,550})for(int duration:{4,8,16,24,40,80})for(int side:{0,1}){
  if(std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>60)throw std::runtime_error("Bounded search time limit");
  auto m=initial;bool left=false,right=false;int lt=0,rt=0;json events=json::array();unsigned score_tick=0;
  auto key=[&](unsigned t,const char* action,unsigned scan,bool down){m.r[2]=scan;m.invoke(0x40404c,down?0:1);events.push_back({{"tick",t},{"action",action},{"down",down}});};
  for(unsigned t=0;t<4000;++t){
   if(t==200||t==201)key(t,"enter",0x1c,t==200);
   const auto b=0x46c15c;const int x=std::int32_t(m.rd(b,4))/65536,y=std::int32_t(m.rd(b+4,4))/65536,vy=std::int32_t(m.rd(b+24,4));
   if(m.rd(b+88,2)==2&&y>=threshold&&y<580&&vy>0){if(x<(side?180:160)&&lt==0)lt=duration;if(x>(side?140:160)&&rt==0)rt=duration;}
   const bool nl=lt>0,nr=rt>0;if(nl!=left)key(t,"left",0x2a,nl);if(nr!=right)key(t,"right",0x36,nr);left=nl;right=nr;if(lt)--lt;if(rt)--rt;
   m.invoke(0x405234,(t+1)*5);if((t+1)%4==0){m.invoke(0x408da8);m.invoke(0x408674);}++total;
   const auto p=m.rd(0x46b758,4);bool scored=false;for(unsigned i=0;i<6;++i)scored|=m.rd(p+i,1)!=0;
   if(scored){score_tick=t+1;break;}
   if(t>800&&m.rd(0x46c6ac,4)!=2)break;
  }
  ++runs;rows.push_back({{"threshold",threshold},{"duration",duration},{"overlap",side},{"score_tick",score_tick}});
  if(score_tick){json out={{"status","NATIVE_CANDIDATE"},{"policy",rows.back()},{"inputs",events},{"diagnostic_shots",json::array()},{"tick_count",score_tick},{"runs",runs},{"total_search_steps",total},{"scope","Ball-observed policy drives actual Enter/Shift keys only; no game state writes; Original/reset proof pending"}};std::ofstream(argv[2])<<out.dump(2)<<'\n';std::cout<<out.at("policy")<<" runs="<<runs<<" steps="<<total<<'\n';return 0;}
 }
 std::ofstream(argv[2])<<json({{"status","NEGATIVE_BOUNDED"},{"runs",runs},{"steps",total},{"policies",rows}}).dump(2)<<'\n';return 3;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
