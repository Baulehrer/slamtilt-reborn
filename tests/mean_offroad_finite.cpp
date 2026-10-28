#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json stats(const slam::MeanSimulation&s){const auto&p=s.offroad_stats();return {{"starts",p.starts},{"awards",p.awards},{"repeats",p.repeats},{"ends",p.ends},{"hits",p.hits},{"score",p.score}};}
static unsigned target(const slam::MeanSimulation&s){const auto&f=s.shared_raw_state().fields;return unsigned(f[0x388])|(unsigned(f[0x389])<<8);}
int main(int argc,char**argv){if(argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,nudges=0,paid_repeats=0,clock_checks=0;bool locked=false;json events=json::array(),previous;
  auto observe=[&](){json now={{"mode",s.table_mode()},{"selected",s.selected_mode()},{"count",s.ball_count()},{"stage",s.offroad_stage()},{"spawns",s.multiball_spawns()},{"offroad",stats(s)}};if(now!=previous){events.push_back({{"tick",tick},{"state",now},{"ball",s.ball_number()},{"score",s.score()},{"callback",s.material5_display_callback()},{"counter",s.material5_display_counter()},{"timer",s.offroad_ticks()}});previous=now;}};
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");const auto old=s.offroad_stats();const auto old_target=target(s);const int old_timer=s.offroad_ticks();const bool clock=s.table_mode()==5&&s.selected_mode()==4&&s.offroad_stage()==3&&s.ball_count()==1;
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}
   if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(s.mode_locked()&&s.selected_mode()==4)locked=true;const auto&now=s.offroad_stats();
   if(now.awards>old.awards && now.score-old.score!=std::uint64_t(now.awards-old.awards)*15000000)throw std::runtime_error("Offroad distincttarget award differs");
   if(now.repeats>old.repeats && old.awards){++paid_repeats;if(now.awards==old.awards&&(now.score!=old.score||target(s)!=old_target))throw std::runtime_error("Offroad repeatedtarget changed score/target");}
   if(clock){++clock_checks;if(s.offroad_ticks()!=old_timer-1)throw std::runtime_error("Offroad oneball200Hz countdown differs");}
   observe();
  }
  const auto complete=s.offroad_stats();if(tick!=fixture.at("ticks")||complete.starts!=1||complete.awards!=6||complete.repeats!=5||complete.ends!=1||complete.score!=90000000||s.max_balls()!=4||s.multiball_spawns()!=3||s.table_mode()!=2||s.ball_count()!=1||s.minigame_completions()!=1||!locked||!paid_repeats||!clock_checks||s.tilted())throw std::runtime_error("Natural Offroad fourball90M/repeat/oneballend differs");
  const auto before=s.score();s.set_launch(true);s.set_flippers(false,false);unsigned bonus=s.bonus_completions();while(!s.game_over()&&tick<150000){if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;if(s.bonus_completions()!=bonus){bonus=s.bonus_completions();events.push_back({{"event","bonus"},{"tick",tick},{"completed",bonus},{"score",s.score()}});}}
  if(!s.game_over()||s.ball_count()||bonus!=4||s.score()<before||s.score()!=249209410||tick!=35028)throw std::runtime_error("Offroad finite lifecycle incomplete");
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;const auto final_stats=stats(s);for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw||stats(s)!=final_stats)throw std::runtime_error("Offroad GameOver changed");}
  s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.offroad_stats().score||s.offroad_stats().starts||s.offroad_stats().ends)throw std::runtime_error("Offroad reset incomplete");cases.push_back({{"events",events},{"final_tick",tick},{"final_score",score},{"offroad",final_stats},{"paid_repeats",paid_repeats},{"clock_checks",clock_checks},{"nudges",nudges}});
 }
 if(cases[0]!=cases[1])throw std::runtime_error("Offroad native replay nondeterministic");std::ofstream(argv[5])<<json({{"scope","Two fresh native legal-input Formula1win/Returnlock/Offroad/fourball90M/paidtargetrepeat/oneball200Hzend/bonus/GameOver/freeze/reset chains; handbook3 vs Windows3additionalballs preserved, no injected fields or fullOriginaltrajectory claim"},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS two natural finite Offroad fourball90M/repeat/oneballend/GameOver/reset chains\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
