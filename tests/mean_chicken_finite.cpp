#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json stats(const slam::MeanSimulation&s){const auto&p=s.chicken_stats();return {{"starts",p.starts},{"races",p.races},{"awards",p.awards},{"completions",p.completions},{"max_finishes",p.max_finishes},{"timeouts",p.timeouts},{"score",p.score}};}
int main(int argc,char**argv){if(argc!=7)return 2;const bool timeout=std::string(argv[6])=="timeout",maximum=std::string(argv[6])=="max";try{
 json fixture;std::ifstream(argv[4])>>fixture;slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){
  s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,nudges=0;bool locked=false;json events=json::array();auto previous=stats(s);
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");
   const auto old=s.chicken_stats();const int timer=s.shared_mode_ticks();
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();
   if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}
   if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(s.mode_locked()&&s.selected_mode()==0)locked=true;
   const auto&now=s.chicken_stats();
   if(now.races>old.races){const std::uint32_t expected=timer<1000?75000000u:65000000u-(timer-1000)*6000u;
    if(now.races!=old.races+1||now.score!=old.score+expected||s.shared_mode_ticks()!=timer-1)throw std::runtime_error("ChickenRace original timedaward formula differs");
   }
   if(stats(s)!=previous){previous=stats(s);events.push_back({{"tick",tick},{"chicken",previous},{"ball",s.ball_number()},{"score",s.score()},{"callback",s.material5_display_callback()},{"timer",s.shared_mode_ticks()}});}
  }
  const auto complete=s.chicken_stats();
  if(tick!=fixture.at("ticks")||complete.starts!=1||s.tilted()||!locked)throw std::runtime_error("Natural ChickenRace start/Returnlock differs");
  const std::array<std::uint32_t,3> values=timeout?std::array<std::uint32_t,3>{35684000,48446000,0}:maximum?std::array<std::uint32_t,3>{35684000,48446000,75000000}:std::array<std::uint32_t,3>{35684000,48446000,56078000};
  if(complete.awards!=values||complete.races!=(timeout?2u:3u)||complete.score!=(timeout?84130000u:maximum?159130000u:140208000u)||complete.completions!=(timeout?0u:1u)||complete.max_finishes!=unsigned(maximum)||complete.timeouts!=unsigned(timeout)||tick!=(timeout?17796u:maximum?16988u:15309u)||s.table_mode()!=2)throw std::runtime_error("Natural ChickenRace tripleaward/max/expiry differs");
  const auto before=s.score();s.set_launch(true);s.set_flippers(false,false);
  unsigned bonus=s.bonus_completions();while(!s.game_over()&&tick<150000){if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(s.bonus_completions()!=bonus){bonus=s.bonus_completions();events.push_back({{"event","bonus"},{"tick",tick},{"ball",s.ball_number()},{"completed",bonus},{"score",s.score()}});}}
  if(!s.game_over()||s.ball_count()||bonus!=3||s.score()<before||s.score()!=(timeout?101995980u:maximum?175420980u:156498980u)||tick!=(timeout?23004u:maximum?22552u:20872u))throw std::runtime_error("ChickenRace finite lifecycle incomplete");
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;const auto final_stats=stats(s);
  for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw||stats(s)!=final_stats)throw std::runtime_error("ChickenRace GameOver changed");}
  s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.chicken_stats().score||s.chicken_stats().starts||s.chicken_stats().races||s.chicken_stats().max_finishes||s.chicken_stats().completions||s.chicken_stats().timeouts)throw std::runtime_error("ChickenRace reset incomplete");
  cases.push_back({{"events",events},{"final_tick",tick},{"final_score",score},{"chicken",final_stats},{"nudges",nudges}});
 }
 if(cases[0]!=cases[1])throw std::runtime_error("ChickenRace native replay nondeterministic");
 std::ofstream(argv[5])<<json({{"scope","Two fresh native finite legal-input ChickenRace Returnlock/start/three timedawards or75Mfinish or8401step expiry/bonus/GameOver/freeze/reset chains; no ball/rule injections or wholeOriginaltrajectory equivalence claim"},{"cases",cases}}).dump(2)<<'\n';
 std::cout<<"PASS two natural finite ChickenRace completion/timeout chains; bonus/GameOver/reset\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
