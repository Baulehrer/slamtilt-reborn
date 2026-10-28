// Bounded native-only search from reset. Only Enter/Shift actions; no state writes.
#include "physics/pirate_session.h"
#include <nlohmann/json.hpp>
#include <chrono>
#include <fstream>
#include <iostream>
#include <vector>
using nlohmann::json;
struct Policy {int a,b,period,offset;};
static unsigned word(const std::vector<std::uint8_t>& v,unsigned o) {
  return unsigned(v.at(o))|(unsigned(v.at(o+1))<<8);
}
int main(int argc,char** argv) {try {
  if(argc!=4)return 2;
  const std::filesystem::path output=argv[3];std::filesystem::create_directories(output);
  slam::PirateSession session(argv[1],argv[2],slam::PirateTickMode::Full);
  session.enable_lamps(true);
  std::vector<Policy> policies;
  for(int a=0;a<4;++a)policies.push_back({a,a,1,0});
  for(int period:{16,25,40,60,90,120,180,240,360,500,750})
    for(int a=0;a<4;++a)for(int b=0;b<4;++b)if(a!=b)
      policies.push_back({a,b,period,0});
  for(int period:{25,60,120,240,500})
    for(int a=0;a<4;++a)for(int b=0;b<4;++b)if(a!=b)
      for(int offset:{17,53})policies.push_back({a,b,period,offset});
  const auto start=std::chrono::steady_clock::now();
  json rows=json::array(),best;unsigned best_locks=0,best_played=0,total=0;bool found=false;
  const auto elapsed=[&]{return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();};
  for(unsigned index=0;index<policies.size()&&index<256&&elapsed()<60;++index) {
    const auto p=policies[index];session.reset();bool left=false,right=false;
    json events=json::array(),milestones=json::array();unsigned max_locks=0,max_played=0,last_phase=99,last_locks=99,last_played=99;
    std::string error;unsigned steps=0;
    try {for(unsigned tick=0;tick<8000;++tick) {
      if(tick%256==0&&elapsed()>=60)break;
      const int mask=((tick+unsigned(p.offset))/unsigned(p.period))%2?p.b:p.a;
      const bool nl=mask&1,nr=mask&2;
      // The initial plunger key and subsequent actual prelaunch phases only.
      if(session.phase()==1&&(tick==0||tick%200==0)) {
        events.push_back({{"tick",tick},{"action","enter"},{"down",true}});
        session.launch();
        events.push_back({{"tick",tick},{"action","enter"},{"down",false}});
      }
      if(nl!=left)events.push_back({{"tick",tick},{"action","left"},{"down",nl}});
      if(nr!=right)events.push_back({{"tick",tick},{"action","right"},{"down",nr}});
      session.flippers(nl,nr);left=nl;right=nr;session.step();++steps;++total;
      const auto rules=session.rule_state();const auto locks=word(rules,0x9c),played=word(rules,0x9e),phase=session.phase();
      max_locks=std::max(max_locks,locks);max_played=std::max(max_played,played);
      if(locks!=last_locks||played!=last_played||phase!=last_phase) {
        milestones.push_back({{"tick",session.ticks()},{"phase",phase},{"locks",locks},{"played",played},{"ball_number",session.ball_number()},{"ball_count",session.ball_count()}});
        last_locks=locks;last_played=played;last_phase=phase;
      }
      if(phase==4&&played>=1) {found=true;break;}
      if(session.game_over()||session.initials_active())break;
    }}catch(const std::exception& e){error=e.what();}
    json row={{"index",index},{"a",p.a},{"b",p.b},{"period",p.period},{"offset",p.offset},{"steps",steps},{"max_locks",max_locks},{"max_played",max_played},{"error",error},{"milestones",milestones}};
    rows.push_back(row);
    if(index==0||max_played>best_played||(max_played==best_played&&max_locks>best_locks)||found) {
      best_locks=max_locks;best_played=max_played;best=row;
      json candidate={{"scope","Native-only legal Enter/Shift edges from reset; no diagnostic or gameplay-state writes"},{"inputs",events},{"diagnostic_shots",json::array()},{"tick_count",steps},{"policy",row}};
      std::ofstream(output/"best-candidate.json")<<candidate.dump(2)<<'\n';
      std::cout<<"best policy="<<index<<" locks="<<max_locks<<" played="<<max_played<<" steps="<<steps<<'\n'<<std::flush;
    }
    if(found)break;
  }
  json report={{"schema",1},{"status",found?"NATIVE_MULTIBALL_ENTRY":"BOUNDED_NO_MULTIBALL_ENTRY"},{"tested_policies",rows.size()},{"step_count",total},{"wall_seconds",elapsed()},{"best",best},{"policies",rows},{"candidate",(output/"best-candidate.json").string()},{"verification","Native search only; original/reset/SDL proof pending"},{"constraints","At most256 deterministic fixed/periodic policies,8000steps each,60second execution cap. Session reset; public Enter/Shift actions only. No rule, ball, timer, callback or diagnostic writes."}};
  std::ofstream(output/"search.json")<<report.dump(2)<<'\n';report.erase("policies");
  std::ofstream("analysis/pirate-legal-key-search.json")<<report.dump(2)<<'\n';
  return found?0:3;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
