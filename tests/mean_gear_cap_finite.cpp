#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
int main(int argc,char **argv){if(argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,bonus_multiplier=0,base=0,redemptions=0;bool capped=false;json events=json::array();
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){const unsigned a=r.at("actions");const auto oldgear=s.gear_multiplier(),oldcap=s.gear_stats().capped_awards,oldpending=s.pending_upper_extra_balls(),credits=s.extra_ball_credits(),oldball=s.ball_number(),oldstarts=s.bonus_starts(),oldawards=s.bonus_awards(),oldbonuses=s.bonus_completions(),callback=s.material5_display_callback();const auto score=s.score();
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16)s.nudge(1,false);if(a&64)s.nudge(-1,false);if(a&32)s.nudge(0,true);
   if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());++tick;const auto audio=s.take_audio_requests();
   if(s.gear_stats().capped_awards!=oldcap){
    if(capped||s.table_mode()!=5||s.selected_mode()!=4||tick!=38043||oldgear!=5||s.gear_multiplier()!=5||s.gear_stats().capped_awards!=1||s.pending_upper_extra_balls()!=oldpending||s.extra_ball_credits()!=credits||s.score()-score!=10025000||s.material5_display_callback()!=callback)throw std::runtime_error("Natural fifthgear cap differs");
    for(const auto&q:audio)if(q.service==0x88||q.service==0x84||q.service==0x80)throw std::runtime_error("Invented capped-gear display/audio request");
    capped=true;events.push_back({{"event","capped_award"},{"tick",tick},{"gear",s.gear_multiplier()},{"mode",s.table_mode()},{"selected",s.selected_mode()},{"cap_points",10000000},{"contact_points",25000},{"score",s.score()},{"credits",credits},{"pending",oldpending},{"callback_unchanged",callback}});
   }
   if(s.bonus_starts()!=oldstarts){bonus_multiplier=s.gear_multiplier();base=s.pending_bonus();if(s.bonus_starts()==1&&(!capped||bonus_multiplier!=5||base!=14000000))throw std::runtime_error("First bonus lost capped fifthgear");events.push_back({{"event","bonus_start"},{"tick",tick},{"multiplier",bonus_multiplier},{"base",base}});}
   if(s.bonus_awards()!=oldawards){if(s.last_bonus()!=std::uint32_t(base*bonus_multiplier))throw std::runtime_error("Bonus multiplication differs");events.push_back({{"event","bonus_award"},{"tick",tick},{"amount",s.last_bonus()}});}
   if(s.bonus_completions()!=oldbonuses){if(s.gear_multiplier()!=1)throw std::runtime_error("Gear not reset after bonus");if(credits){++redemptions;if(s.ball_number()!=oldball||s.extra_ball_credits()!=credits-1)throw std::runtime_error("Extra-ball consumption differs");}else if(s.ball_number()!=oldball+1)throw std::runtime_error("Normal ball advance differs");events.push_back({{"event","bonus_finish"},{"tick",tick},{"ball",s.ball_number()},{"gear",s.gear_multiplier()},{"credits",s.extra_ball_credits()}});}
  }
  if(tick!=48676||!s.game_over()||s.ball_count()||s.score()!=312380420||s.bonus_completions()!=5||redemptions!=2||s.extra_ball_credits()||!capped||s.gear_stats().capped_awards!=1||s.gear_stats().fifth_enables!=1)throw std::runtime_error("Finite capped-gear outcome differs");
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw)throw std::runtime_error("Capped gear GameOver changed");}
  cases.push_back({{"events",events},{"final_tick",tick},{"final_score",score},{"bonuses",s.bonus_completions()},{"extra_redemptions",redemptions}});
  s.reset();if(s.game_over()||s.score()||s.gear_multiplier()!=1||s.gear_stats().capped_awards||s.gear_stats().fifth_enables||s.extra_ball_credits())throw std::runtime_error("Capped gear reset differs");
 }
 if(cases[0]!=cases[1])throw std::runtime_error("Capped gear replay nondeterministic");std::ofstream(argv[5])<<json({{"scope","Two fresh legalinput capped10M+25kcontact/fifthgear/70Mbonus/gearreset/twoextraredemptions/finiteGameOver/freeze/reset chains; no field injections"},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS two natural capped-gear/bonus/ball-boundary chains\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
