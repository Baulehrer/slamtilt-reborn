#include "physics/mean_simulation.h"
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <map>
using json=nlohmann::json;
int main(int argc,char**argv){if(argc!=6)return 2;try{
 json input;std::ifstream(argv[4])>>input;
 slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
 json cases=json::array();std::map<std::string,unsigned> buckets;unsigned tick=0,observed=0,changed=0,batch_tick=0;
 json visits=json::array();std::map<std::string,json> schedules;
 auto flush=[&]{if(visits.empty())return;auto key=visits.dump();auto&v=schedules[key];if(v.is_null())v={{"visits",visits},{"batches",0},{"first_tick",batch_tick}};v["batches"]=v["batches"].get<unsigned>()+1;visits=json::array();};
 s.set_pair_observer([&](const slam::MeanPairTrace&t){
  if(batch_tick!=tick){flush();batch_tick=tick;}visits.push_back({t.first,t.second,t.count});
  ++observed;const bool change=t.before[0].bytes!=t.after[0].bytes||t.before[1].bytes!=t.after[1].bytes;
  if(change)++changed;
  const auto key=std::to_string(t.count)+":"+std::to_string(t.first)+":"+std::to_string(t.second)+":"+std::to_string(t.before[0].u16(0x58))+":"+std::to_string(t.before[1].u16(0x58))+":"+std::to_string(t.before[0].u16(0x48))+":"+std::to_string(t.before[1].u16(0x48));
  if(!change&&buckets[key]++>=2)return;
  cases.push_back({{"tick",tick},{"first",t.first},{"second",t.second},{"count",t.count},{"mode",t.mode},{"changed",change},{"before",{t.before[0].bytes,t.before[1].bytes}},{"after",{t.after[0].bytes,t.after[1].bytes}},{"globals",t.globals}});
 });
 for(const auto&r:input.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");++tick;s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16)s.nudge(1,false);if(a&64)s.nudge(-1,false);if(a&32)s.nudge(0,true);if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();}
 if(tick!=input.at("ticks")||s.score()!=input.at("expected").at("checkpoint_score"))throw std::runtime_error("Legal pair route changed");
 flush();json schedule_list=json::array();for(const auto&v:schedules)schedule_list.push_back(v.second);
 std::ofstream out(argv[5]);out<<json({{"observed",observed},{"changed",changed},{"retained",cases.size()},{"schedules",schedule_list},{"selection","Every pair mutation plus first two no-ops per count/indices/states/layers bucket"},{"cases",cases}}).dump();if(!out)throw std::runtime_error("Cannot write pair contexts");
 std::cout<<"PASS "<<observed<<" pair calls / "<<changed<<" mutations / "<<cases.size()<<" retained\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
