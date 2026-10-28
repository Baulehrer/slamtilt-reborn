#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
int main(int argc,char **argv){if(argc!=6)return 2;try{
 json input;std::ifstream(argv[4])>>input;json cases=json::array();
 for(unsigned run=0;run<2;++run){
  slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned tick=0,bank_pages=0,bank_values=0,previous_value=0;bool theme=false,voice=false,stop=false,sample=false;json events=json::array();
  for(const auto&r:input.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i){
   const unsigned a=r.at("actions");const auto starts=s.award_bank_starts(),awards=s.award_bank_awards();const auto score=s.score();
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();if(a&16)s.nudge(1,false);if(a&64)s.nudge(-1,false);if(a&32)s.nudge(0,true);
   if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());++tick;
   const auto audio=s.take_audio_requests();
   if(s.award_bank_starts()!=starts){
    for(const auto&q:audio)theme|=q.service==0x84&&q.bank==0&&q.order==62;
    if(tick!=10154||s.award_bank_timer()!=6000||s.award_bank_value()!=60000000||s.switch_rewards()||s.material5_display_callback()!=0x4107c8||!theme)throw std::runtime_error("Natural Overheat activation differs");
    events.push_back({{"tick",tick},{"event","five_lit_lanes"},{"timer",s.award_bank_timer()},{"value",s.award_bank_value()}});
   }
   if(s.idle_hud_visible()&&s.idle_hud().field_37a>=0){++bank_pages;if(s.idle_hud().field_054!=previous_value){++bank_values;previous_value=s.idle_hud().field_054;}}
   if(s.award_bank_awards()!=awards){
    for(const auto&q:audio){voice|=q.service==0x88&&q.bank==1&&q.order==36;stop|=q.service==0x80;sample|=q.service==0x5c&&q.descriptor==0x437da4;}
    if(tick!=10678||s.award_bank_timer()!=-1||s.award_bank_value()!=54760000||s.score()-score!=54810000||s.material5_display_callback()!=0x41062c||!voice||!stop||!sample)throw std::runtime_error("Natural Overheat collection differs");
    events.push_back({{"tick",tick},{"event","blue_target_collection"},{"bank_award",s.award_bank_value()},{"score_delta_including_contact",s.score()-score},{"score",s.score()}});
   }
  }
  if(tick!=14036||!s.game_over()||s.ball_count()||s.score()!=61398660||s.bonus_completions()!=3||s.award_bank_starts()!=1||s.award_bank_awards()!=1||s.switch_rewards()||!theme||!voice||!stop||!sample)throw std::runtime_error("Finite Overheat outcome differs");
  const auto score=s.score();const auto raw=s.shared_raw_state().fields;
  for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw)throw std::runtime_error("Overheat GameOver changed");}
  cases.push_back({{"events",events},{"bank_hud_ticks",bank_pages},{"bank_hud_values",bank_values},{"final_tick",tick},{"final_score",score},{"bonuses",s.bonus_completions()}});
  s.reset();if(s.game_over()||s.score()||s.award_bank_starts()||s.award_bank_awards()||s.award_bank_timer()!=-1||s.award_bank_value())throw std::runtime_error("Overheat reset differs");
 }
 if(cases[0]!=cases[1])throw std::runtime_error("Overheat replay nondeterministic");
 std::ofstream(argv[5])<<json({{"scope","Two fresh finite legal-input five-lit-lane activation/60M decay/blue collection/audio/GameOver/freeze/reset chains;54.76M bank plus50k contact, not54.81M bank. No state injections."},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS two natural finite Overheat collection chains\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
