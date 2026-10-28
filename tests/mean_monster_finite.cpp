#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json stats(const slam::MeanSimulation&s){const auto&p=s.monster_stats();return {{"starts",p.starts},{"hits",p.hits},{"completions",p.completions},{"timeouts",p.timeouts},{"score",p.score}};}
int main(int argc,char**argv){if(argc!=7)return 2;const bool timeout=std::string(argv[6])=="timeout";try{
 json fixture;std::ifstream(argv[4])>>fixture;slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){
  s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,nudges=0;bool locked=false;json events=json::array();auto previous=stats(s);
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();
   if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}
   if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(s.mode_locked()&&s.selected_mode()==1)locked=true;
   if(stats(s)!=previous){previous=stats(s);events.push_back({{"tick",tick},{"monster",previous},{"ball",s.ball_number()},{"score",s.score()},{"callback",s.material5_display_callback()}});}
  }
  const auto complete=s.monster_stats();
  if(tick!=fixture.at("ticks")||complete.starts!=1||s.tilted()||!locked)throw std::runtime_error("Natural MonsterCar start/Returnlock differs");
  if(timeout){if(complete.completions||complete.timeouts!=1||complete.score!=15000000||complete.hits!=std::array<unsigned,6>{0,1,0,0,0,1}||tick!=18796)throw std::runtime_error("Natural9401step MonsterCar timeout differs");}
  else if(complete.hits!=std::array<unsigned,6>{1,1,1,1,1,1}||complete.completions!=1||complete.timeouts||complete.score!=125000000||tick!=18076||s.table_mode()!=2)throw std::runtime_error("Natural sixdistinct125M MonsterCar completion differs");
  const auto before=s.score();s.set_launch(true);s.set_flippers(false,false);
  unsigned bonus=s.bonus_completions();while(!s.game_over()&&tick<150000){if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(s.bonus_completions()!=bonus){bonus=s.bonus_completions();events.push_back({{"event","bonus"},{"tick",tick},{"ball",s.ball_number()},{"completed",bonus},{"score",s.score()}});}}
  if(!s.game_over()||s.ball_count()||bonus!=3||s.score()<before||s.score()!=(timeout?32029640u:147922810u)||tick!=(timeout?24632u:23640u))throw std::runtime_error("MonsterCar finite lifecycle incomplete");
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;const auto final_stats=stats(s);
  for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw||stats(s)!=final_stats)throw std::runtime_error("MonsterCar GameOver changed");}
  s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.monster_stats().score||s.monster_stats().starts||s.monster_stats().hits!=std::array<unsigned,6>{}||s.monster_stats().completions||s.monster_stats().timeouts)throw std::runtime_error("MonsterCar reset incomplete");
  cases.push_back({{"events",events},{"final_tick",tick},{"final_score",score},{"monster",final_stats},{"nudges",nudges}});
 }
 if(cases[0]!=cases[1])throw std::runtime_error("MonsterCar native replay nondeterministic");
 std::ofstream(argv[5])<<json({{"scope","Two fresh native finite legal-input MonsterCar Returnlock/start/sixdistinct125M or actual9401step timeout/bonus/GameOver/freeze/reset chains; no ball/rule injections or wholeOriginaltrajectory equivalence claim"},{"cases",cases}}).dump(2)<<'\n';
 std::cout<<"PASS two natural finite MonsterCar completion/timeout chains; bonus/GameOver/reset\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
