#include "physics/mean_simulation.h"
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <map>
using json=nlohmann::json;
int main(int argc,char**argv){if(argc!=6)return 2;try{
 json input;std::ifstream(argv[4])>>input;
 slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
 json cases=json::array();std::map<std::string,unsigned> buckets;unsigned tick=0,observed=0;
 s.set_contact_observer([&](const slam::MeanContactTrace&t){
  if(!t.ok)throw std::runtime_error("Contact boundary stopped");++observed;
  bool nudge=false;for(auto v:t.nudge)nudge|=v!=0;
  const auto kind=t.wall?"wall":t.after.u16(0x1e)==65535?"free":"flipper";
  std::uint32_t geometry=2166136261u;for(auto b:t.lane_saver_normal)geometry=(geometry^b)*16777619u;for(auto b:t.lane_saver_hit)geometry=(geometry^b)*16777619u;
  const std::string key=std::to_string(t.mode)+":"+std::to_string(t.before.u16(0x48))+":"+kind+":"+std::to_string(t.dispatch.u16(0x3c))+":"+std::to_string(nudge)+":"+std::to_string(t.ball_count>1)+":"+std::to_string(geometry);
  if(buckets[key]++>=6)return;
  cases.push_back({{"tick",tick},{"ball_index",t.ball_index},{"ball_count",t.ball_count},{"mode",t.mode},{"selected",t.selected},{"kind",kind},{"before",t.before.bytes},{"dispatch",t.dispatch.bytes},{"after",t.after.bytes},{"flipper_words",t.flipper_words},{"engine_words",t.engine_words},{"nudge",t.nudge},{"dat_base",t.dat_base},{"wall",t.wall},{"cached_fields",t.cached_fields},{"fields_ee1c",t.fields_ee1c},{"geometry_hash",geometry},{"lane_saver_normal",t.lane_saver_normal},{"lane_saver_hit",t.lane_saver_hit},{"material_context",{{"services_1c",t.material.field_services_1c},{"field_1da",t.material.field_43f1da},{"field_390",t.material.field_43f390}}}});
 });
 for(const auto&r:input.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");++tick;s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16)s.nudge(1,false);if(a&64)s.nudge(-1,false);if(a&32)s.nudge(0,true);if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();}
 if(tick!=input.at("ticks") || s.score()!=input.at("expected").at("checkpoint_score"))throw std::runtime_error("Legal route changed with contact observer");
 std::ofstream out(argv[5]);out<<json({{"observed",observed},{"retained",cases.size()},{"selection","First six per mode/layer/contact-kind/material/nudge/multiball/mutable-geometry bucket"},{"cases",cases}}).dump();if(!out)throw std::runtime_error("Cannot write contexts");
 std::cout<<"PASS "<<observed<<" live contact boundaries / "<<cases.size()<<" retained\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
