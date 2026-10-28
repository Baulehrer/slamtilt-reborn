#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json stats(const slam::MeanSimulation&s){const auto&p=s.rally_stats();return {{"starts",p.starts},{"hits",p.hits},{"completions",p.completions},{"timeouts",p.timeouts},{"correct",p.correct},{"wrong",p.wrong},{"score",p.score}};}
int main(int argc,char**argv){if(argc!=7)return 2;const bool timeout=std::string(argv[6])=="timeout";try{
 json fixture;std::ifstream(argv[4])>>fixture;slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){
  s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,nudges=0;bool locked=false;json events=json::array();auto previous=stats(s);
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");
   const auto before_stats=s.rally_stats();const auto before_target=s.shared_target();const int before_timer=s.shared_mode_ticks();
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();
   if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}
   if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(s.mode_locked()&&s.selected_mode()==2)locked=true;
   const auto &after=s.rally_stats();
   if(after.correct==before_stats.correct+1){
    if(!after.completions && (s.shared_mode_ticks()!=before_timer+1999 || after.score!=before_stats.score+15000000))throw std::runtime_error("Rally correctturn timer extension/award differs");
    if(after.completions && after.score!=before_stats.score+15000000+std::uint64_t((before_timer-1)/200)*1500000)throw std::runtime_error("Rally final timed bonus differs");
   }
   if(after.wrong>before_stats.wrong && after.correct==before_stats.correct && (s.shared_target()!=before_target || s.shared_mode_ticks()!=before_timer-1 || after.score!=before_stats.score))throw std::runtime_error("Wrong Rally turn changed target/timer/score");
   if(stats(s)!=previous){previous=stats(s);events.push_back({{"tick",tick},{"rally",previous},{"ball",s.ball_number()},{"score",s.score()},{"callback",s.material5_display_callback()},{"target",s.shared_target()},{"timer",s.shared_mode_ticks()}});}
  }
  const auto complete=s.rally_stats();
  if(tick!=fixture.at("ticks")||complete.starts!=1||s.tilted()||!locked)throw std::runtime_error("Natural LiquidRally start/Returnlock differs");
  if(!complete.wrong)throw std::runtime_error("Natural Rally wrongturn coverage absent");
  if(timeout){if(complete.completions||complete.timeouts!=1||complete.correct!=5||complete.score!=75000000||tick!=25796)throw std::runtime_error("Natural extended Rally timeout differs");}
  else if(complete.correct!=6||complete.completions!=1||complete.timeouts||complete.score!=112500000||tick!=22794||s.table_mode()!=2)throw std::runtime_error("Natural sixturn112.5M Rally completion differs");
  const auto before=s.score();s.set_launch(true);s.set_flippers(false,false);
  unsigned bonus=s.bonus_completions();while(!s.game_over()&&tick<150000){if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(s.bonus_completions()!=bonus){bonus=s.bonus_completions();events.push_back({{"event","bonus"},{"tick",tick},{"ball",s.ball_number()},{"completed",bonus},{"score",s.score()}});}}
  if(!s.game_over()||s.ball_count()||bonus!=3||s.score()<before||s.score()!=(timeout?127079640u:159529640u)||tick!=(timeout?30944u:29268u))throw std::runtime_error("LiquidRally finite lifecycle incomplete");
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;const auto final_stats=stats(s);
  for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw||stats(s)!=final_stats)throw std::runtime_error("LiquidRally GameOver changed");}
  s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.rally_stats().score||s.rally_stats().starts||s.rally_stats().hits!=std::array<unsigned,6>{}||s.rally_stats().completions||s.rally_stats().timeouts)throw std::runtime_error("LiquidRally reset incomplete");
  cases.push_back({{"events",events},{"final_tick",tick},{"final_score",score},{"rally",final_stats},{"nudges",nudges}});
 }
 if(cases[0]!=cases[1])throw std::runtime_error("LiquidRally native replay nondeterministic");
 std::ofstream(argv[5])<<json({{"scope","Two fresh native finite legal-input LiquidRally Returnlock/start/sixcorrect112.5M+wrongturns or extended6401+5x2000step timeout/bonus/GameOver/freeze/reset chains; no ball/rule injections or wholeOriginaltrajectory equivalence claim"},{"cases",cases}}).dump(2)<<'\n';
 std::cout<<"PASS two natural finite LiquidRally completion/timeout chains; bonus/GameOver/reset\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
