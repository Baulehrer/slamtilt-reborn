// Native discovery only. All candidates require fresh Original/reset/SDL proof.
#include "pirate_session_search.h"
#include "core/pirate_input_replay.h"
#include <nlohmann/json.hpp>
#include <chrono>
#include <fstream>
#include <iostream>
#include <cmath>
using nlohmann::json;
struct Policy {int a,b,period,offset;};
struct Pulse {unsigned mask,onset,duration;int direction=0;unsigned nudge_tick=0;bool nudge=false;};
static int inspect(char**argv){
  const std::filesystem::path out=argv[3];std::filesystem::create_directories(out);
  slam::PirateSession s(argv[1],argv[2],slam::PirateTickMode::Full);s.enable_lamps(true);
  slam::PirateInputReplay replay;replay.load(argv[5]);bool l=false,r=false;
  const unsigned begin=std::stoul(argv[6]),end=std::stoul(argv[7]);
  json rows=json::array();unsigned old_phase=99,old_hits=99,old_state=99,old_layer=99;
  const auto get=[&](unsigned a,unsigned n=4){return slam::PirateSessionSearch::read(s,a,n);};
  for(unsigned t=0;t<end;++t){
    replay.apply(s,t,l,r);s.step();
    const unsigned state=get(0x46c1b4,2),layer=get(0x46c1a4,2);
    json ropes=json::array();unsigned hits=0;for(unsigned i=0;i<5;++i){const auto v=get(0x46e564+i,1);ropes.push_back(v);hits+=v==0;}
    if(t>=begin&&(t%8==0||s.phase()!=old_phase||state!=old_state||layer!=old_layer||hits!=old_hits)){
      const auto fixed=[&](unsigned a){return std::int32_t(get(a))/65536.0;};
      rows.push_back({{"tick",s.ticks()},{"phase",s.phase()},{"x",fixed(0x46c15c)},{"y",fixed(0x46c160)},{"vx",fixed(0x46c170)},{"vy",fixed(0x46c174)},{"layer",layer},{"state",state},{"guide",get(0x46c1b8,2)},{"ropes",ropes},{"timer",get(0x46e546,2)},{"left",l},{"right",r}});
    }
    old_phase=s.phase();old_hits=hits;old_state=state;old_layer=layer;
  }
  std::ofstream(out/"flight.json")<<rows.dump(2)<<'\n';return 0;
}
static int branch(int argc,char**argv){
  const std::filesystem::path out=argv[3];std::filesystem::create_directories(out);
  slam::PirateSession s(argv[1],argv[2],slam::PirateTickMode::Full);s.enable_lamps(true);
  std::ifstream file(argv[4]);json src;file>>src;
  const unsigned begin=std::stoul(argv[5]), span=argc>6?std::stoul(argv[6]):1000;
  const unsigned goal=argc>7?std::stoul(argv[7]):5;
  if(goal<1||goal>5)throw std::runtime_error("Rope goal must be1..5");
  json prefix=json::array();for(const auto&e:src.at("inputs"))if(e.at("tick").get<unsigned>()<begin)prefix.push_back(e);
  slam::PirateInputReplay replay;replay.load(argv[4]);bool l=false,r=false;
  for(unsigned t=0;t<begin;++t){replay.apply(s,t,l,r);s.step();}
  const auto state=slam::PirateSessionSearch::capture(s);
  const auto get=[&](unsigned a,unsigned n=4){return slam::PirateSessionSearch::read(s,a,n);};
  const bool armed=get(0x46e2de,2)!=0,plank=s.phase()==5;double best=-1e30;
  if(plank&&get(0x46e2c0,2)!=0)throw std::runtime_error("Expected Walk the Plank checkpoint");
  const auto clock=std::chrono::steady_clock::now();
  const auto elapsed=[&]{return std::chrono::duration<double>(std::chrono::steady_clock::now()-clock).count();};
  unsigned trials=0,steps=0;bool found=false;json rows=json::array();
  std::vector<Pulse> probes;
  if(argc>8&&std::string(argv[8])=="nudge"){
    // Prioritize contact-time requests; early transient waves preceded arrival.
    for(unsigned dt:{140,160,180})for(int direction:{-1,1,0})for(unsigned mask:{2,1,3})
      for(unsigned onset=begin+120;onset<=begin+220;onset+=4)for(unsigned duration:{8,24,64})
        probes.push_back({mask,onset,duration,direction,begin+dt,true});
  }else{
    for(unsigned mask:{1,2,3,0})for(unsigned onset=begin;onset<=begin+300;onset+=4)for(unsigned duration:{8,24,64,128}){
      if(mask==0&&(onset!=begin||duration!=8))continue;
      probes.push_back({mask,onset,duration});
    }
  }
  for(const auto&p:probes){
    if(found||elapsed()>=60)break;
    const auto mask=p.mask,onset=p.onset,duration=p.duration;
    slam::PirateSessionSearch::restore(s,state);l=state.left;r=state.right;json inputs=prefix;
    double score=-1e30;std::string error;unsigned maxlayer=0;
    const auto edge=[&](bool nl,bool nr){if(nl!=l)inputs.push_back({{"tick",s.ticks()},{"action","left"},{"down",nl}});if(nr!=r)inputs.push_back({{"tick",s.ticks()},{"action","right"},{"down",nr}});s.flippers(nl,nr);l=nl;r=nr;};
    try{for(unsigned t=begin;t<begin+span;++t){
      const bool on=t>=onset&&t<onset+duration;edge(on&&(mask&1),on&&(mask&2));
      if(p.nudge&&(t==p.nudge_tick||t==p.nudge_tick+1)){
        const auto action=p.direction<0?"nudge_left":p.direction>0?"nudge_right":"nudge_up";
        inputs.push_back({{"tick",s.ticks()},{"action",action},{"down",t==p.nudge_tick}});
        if(t==p.nudge_tick)s.nudge(p.direction);
      }
      s.step();++steps;
      const auto b=s.ball();const auto i32=[&](unsigned a){unsigned v=0;for(unsigned j=0;j<4;++j)v|=unsigned(b[a+j])<<(8*j);return std::int32_t(v);};
      const unsigned layer=get(0x46c15c+0x48,2);maxlayer=std::max(maxlayer,layer);
      const double x=i32(0)/65536.0,y=i32(4)/65536.0;
      if(layer==1&&!armed)score=std::max(score,1000-std::hypot(x-227,y-44.5));
      if(layer==0&&armed)score=std::max(score,1000-std::hypot(x-40,y-84));
      if(plank){
        if(s.phase()!=5)break;
        unsigned hits=0;for(unsigned i=0;i<5;++i)hits+=get(0x46e564+i,1)==0;
        score=std::max(score,double(hits)*100000);
        if(hits>=goal){found=true;break;}
      }else if((!armed&&get(0x46e2de,2))||(s.phase()==5&&get(0x46e2c0,2)==0)){found=true;score=100000;break;}
      if(s.phase()==0||s.phase()==3)break;
    }}catch(const std::exception&e){error=e.what();}
    ++trials;json policy={{"mask",mask},{"onset",onset},{"duration",duration},{"start_tick",begin},{"armed_at_start",armed},{"found",found},{"phase",s.phase()},{"selected",get(0x46e2c0,2)},{"max_layer",maxlayer},{"error",error}};rows.push_back(policy);
    if(p.nudge){policy["nudge_tick"]=p.nudge_tick;policy["nudge_direction"]=p.direction;rows.back()=policy;}
    if(score>best){best=score;std::ofstream(out/"best-candidate.json")<<json({{"inputs",inputs},{"diagnostic_shots",json::array()},{"tick_count",s.ticks()},{"policy",policy},{"score",score},{"scope","Native reachable-state branching; fresh original/reset/SDL proof pending"}}).dump(2)<<'\n';std::cout<<"best "<<trials<<" score "<<score<<" mask "<<mask<<" onset "<<onset<<" duration "<<duration<<" tick "<<s.ticks()<<'\n'<<std::flush;}
  }
  std::ofstream(out/"search.json")<<json({{"status",found?"NATIVE_TARGET":"BOUNDED_NO_TARGET"},{"policies",rows},{"wall_seconds",elapsed()},{"simulated_steps",steps}}).dump(2)<<'\n';
  return found?0:3;
}
int main(int argc,char**argv){try {
  if(argc==8&&std::string(argv[4])=="--inspect")return inspect(argv);
  if(argc>=6)return branch(argc,argv);
  if(argc!=4)return 2;
  const std::filesystem::path out=argv[3];std::filesystem::create_directories(out);
  slam::PirateSession s(argv[1],argv[2],slam::PirateTickMode::Full);s.enable_lamps(true);
  const auto get=[&](unsigned a,unsigned n=4){return slam::PirateSessionSearch::read(s,a,n);};
  const auto start=std::chrono::steady_clock::now();
  const auto elapsed=[&]{return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();};
  std::vector<Policy> policies;
  for(int a=0;a<4;++a)policies.push_back({a,a,1,0});
  for(int p:{16,25,40,60,90,120,180,240,360,500,750})
    for(int a=0;a<4;++a)for(int b=0;b<4;++b)if(a!=b)policies.push_back({a,b,p,0});
  json rows=json::array();unsigned total=0,best=0;bool found=false;
  for(unsigned index=0;index<policies.size()&&elapsed()<60&&!found;++index){
    const auto p=policies[index];s.reset();bool left=false,right=false;json inputs=json::array(),marks=json::array();
    unsigned stage=0,arm_tick=0;std::string error;
    try{for(unsigned t=0;t<10000;++t){
      if(t%256==0&&elapsed()>=60)break;
      const unsigned mask=((t+p.offset)/p.period)%2?p.b:p.a;
      if(s.phase()==1&&(t==0||t%200==0)){s.launch();inputs.push_back({{"tick",t},{"action","enter"},{"down",true}});inputs.push_back({{"tick",t},{"action","enter"},{"down",false}});}
      const bool l=mask&1,r=mask&2;
      if(l!=left)inputs.push_back({{"tick",t},{"action","left"},{"down",l}});
      if(r!=right)inputs.push_back({{"tick",t},{"action","right"},{"down",r}});
      s.flippers(l,r);left=l;right=r;s.step();++total;
      if(get(0x46e2de,2)&&stage<1){stage=1;arm_tick=s.ticks();marks.push_back({{"event","armed"},{"tick",s.ticks()},{"selected",get(0x46e2c0,2)}});}
      if(s.phase()==5&&get(0x46e2c0,2)==0){stage=2;found=true;marks.push_back({{"event","adventure"},{"tick",s.ticks()},{"selected",get(0x46e2c0,2)}});}
      if(stage>best){best=stage;json c={{"inputs",inputs},{"diagnostic_shots",json::array()},{"tick_count",s.ticks()},{"policy",{{"index",index},{"a",p.a},{"b",p.b},{"period",p.period},{"offset",p.offset}}},{"milestones",marks},{"scope","Native-only legal key discovery; no verification claim"}};std::ofstream(out/"best-candidate.json")<<c.dump(2)<<'\n';std::cout<<"stage "<<stage<<" policy "<<index<<" tick "<<s.ticks()<<'\n'<<std::flush;}
      if(found||s.game_over()||s.initials_active())break;
    }}catch(const std::exception&e){error=e.what();}
    rows.push_back({{"index",index},{"a",p.a},{"b",p.b},{"period",p.period},{"offset",p.offset},{"steps",s.ticks()},{"arm_tick",arm_tick},{"stage",stage},{"error",error}});
  }
  std::ofstream(out/"search.json")<<json({{"status",found?"NATIVE_ADVENTURE_ENTRY":"BOUNDED_NO_ENTRY"},{"policies",rows},{"wall_seconds",elapsed()},{"simulated_steps",total}}).dump(2)<<'\n';
  return found?0:3;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
