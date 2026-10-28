#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <set>
#include <stdexcept>
using json=nlohmann::json;
static std::uint64_t pixel_hash(const slam::WindowsDmdPixels&p){std::uint64_t h=14695981039346656037ull;for(auto v:p){h^=v;h*=1099511628211ull;}return h;}
int main(int argc,char**argv){if(argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){
  slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0;bool earned=false,found=false;
  auto word=[&](unsigned o){const auto&f=s.shared_raw_state().fields;return std::int16_t(unsigned(f[o])|(unsigned(f[o+1])<<8));};
  auto step=[&](unsigned a){s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16)s.nudge(1,false);if(a&64)s.nudge(-1,false);if(a&32)s.nudge(0,true);if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;if(s.extra_ball_credits())earned=true;};
  for(const auto&r:fixture.at("actions_rle")){for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){step(r.at("actions"));if(s.table_mode()==1&&s.player_hud().field_engine_60){found=true;break;}}if(found)break;}
  while(!found && !s.game_over() && tick<150000) {
    step(8);
    found=s.table_mode()==1 && s.player_hud().field_engine_60;
  }
  if(!found||!earned||word(0x360)!=100||s.game_over())throw std::runtime_error("Fresh earned extra-ball prelaunch boundary missing");
  const auto entry_tick=tick,ball=s.ball_number();const auto score=s.score();unsigned decrements=0,extra_samples=0,player_samples=0,score_samples=0;std::set<std::uint64_t> blink_hashes;std::uint64_t rolling=14695981039346656037ull;std::int16_t previous=word(0x360);json changes=json::array();
  for(unsigned idle=0;idle<800;++idle){step(0);if(s.ball_number()!=ball||s.score()!=score||s.table_mode()!=1||s.game_over())throw std::runtime_error("Unlaunched extra-ball idle changed gameplay");const auto now=word(0x360);if(now!=previous){if(now!=previous-1||previous<0)throw std::runtime_error("Extra-ball countdown discontinuity");++decrements;changes.push_back({{"tick",tick},{"from",previous},{"to",now}});previous=now;}
   if(s.player_hud_visible()){const auto&h=s.player_hud();if(h.pixels!=s.material5_pixels()||h.field_360!=now||h.player_0e!=ball||h.field_35c)throw std::runtime_error("Earned extra-ball HUD/raw mismatch");const auto hash=pixel_hash(h.pixels);rolling^=hash;rolling*=1099511628211ull;rolling^=tick;rolling*=1099511628211ull;
    if(decrements<=101&&changes.size()&&changes.back().at("tick")==tick&&changes.back().at("from").get<int>()>=0){++extra_samples;blink_hashes.insert(hash);}else if(now<0){if((h.counter&127u)<=64)++player_samples;else ++score_samples;}
   }
  }
  if(decrements!=101||previous!=-1||extra_samples!=101||blink_hashes.size()!=2||!player_samples||!score_samples)throw std::runtime_error(json({{"error","Extra countdown/blink/ordinary pages incomplete"},{"decrements",decrements},{"extra_samples",extra_samples},{"blink_hashes",blink_hashes.size()},{"player_samples",player_samples},{"score_samples",score_samples}}).dump());
  cases.push_back({{"entry_tick",entry_tick},{"entry_ball",ball},{"score",score},{"idle_ticks",800},{"countdown_changes",changes},{"decrements",decrements},{"blink_pixel_hashes",blink_hashes},{"player_samples",player_samples},{"score_samples",score_samples},{"rolling_fnv",std::to_string(rolling)}});
 }
 if(cases[0]!=cases[1])throw std::runtime_error("Earned extra-ball HUD route nondeterministic");std::ofstream(argv[5])<<json({{"scope","Two fresh legal goal-ladder prefixes earn and redeem extra ball, then release all inputs; raw360100->-1 in101display steps, two original blink outputs, ordinary player/score pages restored; no injected state"},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS earned extra-ball countdown/blink/ordinary HUD twice\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
