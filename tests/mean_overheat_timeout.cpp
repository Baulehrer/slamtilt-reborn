#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
int main(int argc,char **argv){if(argc!=6)return 2;try{
 json input;std::ifstream(argv[4])>>input;json cases=json::array();
 for(unsigned run=0;run<2;++run){slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,half=0,expired=0,early_pages=0,late_pages=0,floor_ticks=0;json events=json::array();
  for(const auto&r:input.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){const unsigned a=r.at("actions");const auto previous=s.award_bank_timer();
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16)s.nudge(1,false);if(a&64)s.nudge(-1,false);if(a&32)s.nudge(0,true);
   if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());++tick;const auto audio=s.take_audio_requests();const auto timer=s.award_bank_timer();
   if(timer>=0&&timer<1000){++floor_ticks;if(s.award_bank_value()!=10000000)throw std::runtime_error("Overheat minimum differs");}
   if(previous>3000&&timer==3000){++half;if(s.award_bank_value()!=30000000||s.material5_display_callback()!=0x41086c)throw std::runtime_error("Overheat half-time differs");events.push_back({{"tick",tick},{"event","half"},{"timer",timer}});}
   if(previous==0&&timer==-1){++expired;bool stopped=false;for(const auto&q:audio)stopped|=q.service==0x80;if(!stopped||s.material5_display_callback()!=0x410504)throw std::runtime_error("Overheat expiry differs");events.push_back({{"tick",tick},{"event","expired"}});}
   if(s.idle_hud_visible()&&s.idle_hud().field_37a>=0){if(s.idle_hud().field_37a>3000)++early_pages;else ++late_pages;}
  }
  if(tick!=19780||!s.game_over()||s.ball_count()||s.score()!=7822810||s.bonus_completions()!=3||s.award_bank_starts()!=1||s.award_bank_awards()||half!=1||expired!=1||!early_pages||!late_pages||floor_ticks!=1000)throw std::runtime_error(json({{"error","Overheat finite timeout differs"},{"tick",tick},{"score",s.score()},{"half",half},{"expired",expired},{"early",early_pages},{"late",late_pages},{"floor",floor_ticks}}).dump());
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;for(unsigned i=0;i<64;++i){s.press_plunger();s.set_flippers(true,true);if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw)throw std::runtime_error("Overheat timeout GameOver changed");}
  cases.push_back({{"events",events},{"early_bank_hud_ticks",early_pages},{"late_bank_hud_ticks",late_pages},{"minimum_value_ticks",floor_ticks},{"final_tick",tick},{"final_score",score},{"bonuses",s.bonus_completions()}});
  s.reset();if(s.game_over()||s.award_bank_timer()!=-1||s.award_bank_value()||s.award_bank_starts()||s.award_bank_awards()||s.score())throw std::runtime_error("Overheat timeout reset differs");
 }
 if(cases[0]!=cases[1])throw std::runtime_error("Overheat timeout nondeterministic");std::ofstream(argv[5])<<json({{"scope","Two fresh legal-input Overheat activation/half/true expiry/musicstop/early+lateHUD/finiteGameOver/freeze/reset runs; distinguishes drain reset from timeout"},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS two finite natural Overheat half/expiry chains\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
