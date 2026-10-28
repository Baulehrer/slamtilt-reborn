#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
int main(int argc,char**argv){if(argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;
 slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){
 s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
 unsigned tick=0,previous=0,intro_blocked=0;json events=json::array(),awards=json::array();
 auto word=[&](unsigned o){const auto&f=s.shared_raw_state().fields;return unsigned(f[o])|(unsigned(f[o+1])<<8);};
 for(const auto&run:fixture.at("actions_rle"))for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i){
  const unsigned a=run.at("actions");s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();
  if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
  if(tick==fixture.at("entry_steps")){
   if(s.table_mode()!=4||word(0x3a6)!=1||s.ball_number()!=2||s.material5_display_callback()!=0x4130cc||word(0x3aa)!=65535||word(0x3a0)!=499)
    throw std::runtime_error("Natural Kickstart entry/intro missing");
   events.push_back({{"event","entry"},{"tick",tick},{"ball",s.ball_number()},{"callback",s.material5_display_callback()}});
  }
  if(tick>fixture.at("entry_steps").get<unsigned>() && s.material5_display_callback()==0x4130cc){
   if(word(0x3aa)!=65535||word(0x3a0)!=499)throw std::runtime_error("Kickstart countdown started during intro");++intro_blocked;
  }
  if(s.phase1_award_total()!=previous){previous=s.phase1_award_total();awards.push_back(previous);events.push_back({{"event","award"},{"tick",tick},{"award",previous},{"score",s.score()}});}
 }
 if(awards!=fixture.at("expected_awards")||intro_blocked<600||s.table_mode()!=2||s.material5_display_callback()!=0x4102c0||s.point_force_type()!=0)
  throw std::runtime_error("Natural Kickstart full60M/intro/return mismatch");
 const auto score=s.score();s.set_launch(true);s.set_flippers(false,false);unsigned bonuses=s.bonus_completions();
 while(!s.game_over()&&tick<150000){if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
  if(s.bonus_completions()!=bonuses){bonuses=s.bonus_completions();events.push_back({{"event","bonus"},{"tick",tick},{"count",bonuses},{"ball",s.ball_number()},{"score",s.score()}});}}
 if(!s.game_over()||s.ball_count()!=0||bonuses<3||s.score()<score)throw std::runtime_error("Kickstart finite lifecycle incomplete");
 const auto final_score=s.score();const auto raw=s.shared_raw_state().fields;
 for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=final_score||s.shared_raw_state().fields!=raw)throw std::runtime_error("Kickstart GameOver mutated");}
 s.reset();if(s.game_over()||s.score()||s.ball_number()!=1||s.mode4_starts()||s.mode4_completions()||word(0x392))throw std::runtime_error("Kickstart newgame incomplete");
 cases.push_back({{"events",events},{"intro_blocked_ticks",intro_blocked},{"final_tick",tick},{"final_score",final_score}});
 }
 if(cases[0]!=cases[1])throw std::runtime_error("Kickstart replay nondeterministic");
 std::ofstream(argv[5])<<json({{"scope","Two fresh native finite SDL-input Kickstart entry/intro/magnet/25+10+25M/bonus/GameOver/freeze/reset chains; no captured Original whole-table trajectory claim"},{"cases",cases}}).dump(2)<<'\n';
 std::cout<<"PASS two natural finite Kickstart60M chains and intro countdown gate\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
