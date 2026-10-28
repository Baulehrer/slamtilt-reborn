#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json stats(const slam::MeanSimulation&s){const auto&p=s.stock_car_stats();return {{"starts",p.starts},{"hits",p.hits},{"completions",p.completions},{"score",p.score}};}
int main(int argc,char**argv){if(argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){
  s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,nudges=0;json events=json::array();auto previous=stats(s);
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){unsigned a=r.at("actions");
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();
   if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}
   if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(stats(s)!=previous){previous=stats(s);events.push_back({{"tick",tick},{"stock",previous},{"ball",s.ball_number()},{"score",s.score()},{"callback",s.material5_display_callback()}});}
  }
  const auto complete=s.stock_car_stats();
  if(tick!=fixture.at("ticks")||complete.starts!=1||complete.hits!=15||complete.completions!=1||complete.score!=75000000||s.tilted())throw std::runtime_error("Fresh natural75M StockCar replay differs");
  const auto before=s.score();s.set_launch(true);s.set_flippers(false,false);
  unsigned bonus=s.bonus_completions();while(!s.game_over()&&tick<150000){if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
   if(s.bonus_completions()!=bonus){bonus=s.bonus_completions();events.push_back({{"event","bonus"},{"tick",tick},{"ball",s.ball_number()},{"completed",bonus},{"score",s.score()}});}}
  if(!s.game_over()||s.ball_count()||bonus<3||s.score()<before)throw std::runtime_error("StockCar finite lifecycle incomplete");
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;const auto final_stats=stats(s);
  for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw||stats(s)!=final_stats)throw std::runtime_error("StockCar GameOver changed");}
  s.reset();if(s.game_over()||s.ball_number()!=1||s.score()||s.stock_car_stats().score||s.stock_car_stats().starts||s.stock_car_stats().hits||s.stock_car_stats().completions)throw std::runtime_error("StockCar reset incomplete");
  cases.push_back({{"events",events},{"final_tick",tick},{"final_score",score},{"stock",final_stats},{"nudges",nudges}});
 }
 if(cases[0]!=cases[1])throw std::runtime_error("StockCar native replay nondeterministic");
 std::ofstream(argv[5])<<json({{"scope","Two fresh native finite SDL-input StockCar activation/15bumperhits/75M/bonus/GameOver/freeze/reset chains; no ball/rule injections or wholeOriginaltrajectory equivalence claim"},{"cases",cases}}).dump(2)<<'\n';
 std::cout<<"PASS two naturalfinite75M StockCar chains; bonus/GameOver/reset\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
