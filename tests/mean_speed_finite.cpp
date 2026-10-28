#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json stats(const slam::MeanSimulation&s){const auto&p=s.speed_stats();return {{"jackpots",p.jackpots},{"score",p.score}};}
int main(int argc,char**argv){if(argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,nudges=0,lock_mask=0,max_locks=0;bool returned=false;json events=json::array(),previous;
  auto observe=[&](){auto timers=s.speed_lock_timers();unsigned active=0;for(unsigned i=0;i<3;++i)if(timers[i]>=0){lock_mask|=1u<<i;++active;}max_locks=std::max(max_locks,active);
   if(s.mode6_starts()&&s.table_mode()==2&&s.ball_count()==1)returned=true;
   json now={{"letters",s.speed_letters()},{"mode",s.table_mode()},{"count",s.ball_count()},{"starts",s.mode6_starts()},{"spawns",s.multiball_spawns()},{"speed",stats(s)},{"lock_mask",lock_mask},{"max_locks",max_locks},{"returned",returned}};
   if(now!=previous){events.push_back({{"tick",tick},{"state",now},{"ball",s.ball_number()},{"score",s.score()},{"timers",timers},{"callback",s.material5_display_callback()},{"display_counter",s.material5_display_counter()}});previous=now;}};
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();
   if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}
   if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++tick;observe();}
  if(tick!=fixture.at("ticks")||s.mode6_starts()!=1||s.multiball_spawns()!=7||s.max_balls()!=8||s.minigame_completions()!=1||s.speed_stats().jackpots!=std::array<unsigned,4>{8,4,2,1}||s.speed_stats().score!=260000000||lock_mask!=7||max_locks!=3||s.tilted())throw std::runtime_error("Natural finite SPEED activation/spawns/jackpot differs");
  const auto before=s.score();s.set_launch(true);s.set_flippers(false,false);unsigned bonus=s.bonus_completions();
  while(!s.game_over()&&tick<200000){if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;observe();if(s.bonus_completions()!=bonus){bonus=s.bonus_completions();events.push_back({{"event","bonus"},{"tick",tick},{"completed",bonus},{"score",s.score()}});}}
  if(!returned||!s.game_over()||s.ball_count()||bonus!=4||s.score()<before||s.score()!=482716240||tick!=40380)throw std::runtime_error("SPEED return/finite lifecycle incomplete score="+std::to_string(s.score())+" tick="+std::to_string(tick));
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;const auto final_stats=stats(s);
  for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw||stats(s)!=final_stats)throw std::runtime_error("SPEED GameOver changed");}
  s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.speed_stats().score||s.mode6_starts()||s.multiball_spawns())throw std::runtime_error("SPEED reset incomplete");
  cases.push_back({{"events",events},{"final_tick",tick},{"final_score",score},{"speed",final_stats},{"lock_mask",lock_mask},{"max_locks",max_locks},{"nudges",nudges}});
 }
 if(cases[0]!=cases[1])throw std::runtime_error("SPEED native replay nondeterministic");
 std::ofstream(argv[5])<<json({{"scope","Two fresh native finite legal-input fiveletter/SPEED/eightball/jackpot/return/bonus/GameOver/freeze/reset chains; no injected fields or fullOriginaltrajectory claim"},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS two natural finite SPEED eightball/jackpot/return/GameOver/reset chains\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
