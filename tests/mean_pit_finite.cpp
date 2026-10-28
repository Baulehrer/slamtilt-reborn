#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json stats(const slam::MeanSimulation&s){const auto&p=s.pit_stop_stats();return {{"punctures",p.punctures},{"repairs",p.repairs},{"starts",p.starts},{"completions",p.completions},{"timeouts",p.timeouts},{"score",p.score}};}
int main(int argc,char**argv){if(argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){
  s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,nudges=0;json events=json::array();std::uint64_t previous=0;
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();
   if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}
   if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   const auto&p=s.pit_stop_stats();
   if(p.score!=previous){previous=p.score;events.push_back({{"tick",tick},{"pit",stats(s)},{"ball",s.ball_number()},{"score",s.score()},{"callback",s.material5_display_callback()}});}
   if(tick==fixture.at("pit_start_tick")){
    if(p.punctures!=std::array<unsigned,4>{1,1,1,1}||p.starts!=1||p.score!=10000000||s.ball_number()!=2)
     throw std::runtime_error("Four natural ramp punctures did not start PitStop");
   }
  }
  const auto complete=s.pit_stop_stats();
  if(tick!=fixture.at("pit_complete_tick")||complete.punctures!=std::array<unsigned,4>{1,1,1,1}||complete.repairs!=std::array<unsigned,4>{1,1,1,1}||complete.starts!=1||complete.completions!=1||complete.timeouts||complete.score!=65000000||s.tilted()||nudges!=2)
   throw std::runtime_error("Fresh natural65M PitStop replay differs");
  const auto before=s.score();s.set_launch(true);s.set_flippers(false,false);
  unsigned bonus=s.bonus_completions();while(!s.game_over()&&tick<150000){if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(s.bonus_completions()!=bonus){bonus=s.bonus_completions();events.push_back({{"event","bonus"},{"tick",tick},{"ball",s.ball_number()},{"completed",bonus},{"score",s.score()}});}}
  if(!s.game_over()||s.ball_count()||bonus<3||s.score()<before)throw std::runtime_error("PitStop finite lifecycle incomplete");
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;const auto final_stats=stats(s);
  for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw||stats(s)!=final_stats)throw std::runtime_error("PitStop GameOver changed");}
  s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.pit_stop_stats().score||s.pit_stop_stats().completions)throw std::runtime_error("PitStop reset incomplete");
  cases.push_back({{"events",events},{"final_tick",tick},{"final_score",score},{"pit",final_stats},{"nudges",nudges}});
 }
 if(cases[0]!=cases[1])throw std::runtime_error("PitStop native replay nondeterministic");
 std::ofstream(argv[5])<<json({{"scope","Two fresh native finite SDL-input fourpuncture/fourrepair65M/PitStopdeadline/bonus/GameOver/freeze/reset chains; two legalrightnudges, no ball/rule injections or capturedOriginalwholetrajectory claim"},{"cases",cases}}).dump(2)<<'\n';
 std::cout<<"PASS two naturalfinite65M PitStop chains beforetimeout; bonus/GameOver/reset\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
