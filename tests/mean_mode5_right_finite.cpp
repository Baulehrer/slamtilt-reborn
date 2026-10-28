#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
int main(int argc,char**argv){if(argc!=5)return 2;try{json cases=json::array();for(unsigned selected:{1,2,4}){json first;for(unsigned repeat=0;repeat<2;++repeat){slam::MeanSimulation s(argv[1],argv[2],argv[3]);
 // Bounded diagnostic: original marker20 survives a change to main mode5.
 // Existing debug entry places ball/rules; this is not a natural keyboard trace.
 s.debug_start_shared_mode(selected);s.debug_start_mode4_right(true);
 s.set_continuous_play(true);s.set_endless_play(false);s.set_launch(true);
 unsigned tick=0,transfer=0,release=0;json events=json::array();
 while(!s.game_over()&&tick<10000){auto state=s.ball().u16(0x58),cb=s.ball().u16(0x5a);if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++tick;
  if(tick==1&&(s.ball().u16(0x58)!=3||s.ball().u16(0x5a)!=4||s.table_mode()!=5))throw std::runtime_error("Mode5 marker20 entry did not capture");
  if(cb==4&&s.ball().u16(0x5a)==3){transfer=tick;if(tick!=252||s.table_mode()!=5||s.score()!=25500000)throw std::runtime_error("Mode5 callback4 transfer differs");}
  if(state==3&&cb==3&&s.ball().u16(0x58)==2&&!release){release=tick;if(tick!=352)throw std::runtime_error("Mode5 callback3 release differs");}
 }
 if(!s.game_over()||tick!=5712||transfer!=252||release!=352||s.score()!=78625000||s.bonus_completions()!=3||s.ball_count())throw std::runtime_error("Mode5 right diagnostic finite lifecycle differs");
 const auto score=s.score();const auto raw=s.shared_raw_state().fields;for(unsigned i=0;i<64;++i){s.press_plunger();s.set_flippers(true,true);if(s.step()||s.score()!=score||s.shared_raw_state().fields!=raw)throw std::runtime_error("Mode5 right GameOver changed");}
 s.reset();if(s.game_over()||s.score()||s.captures())throw std::runtime_error("Mode5 right reset differs");
 json result={{"selected",selected},{"transfer_tick",transfer},{"release_tick",release},{"final_tick",tick},{"final_score",score},{"bonus_completions",3}};if(repeat&&result!=first)throw std::runtime_error("Mode5 right nondeterministic");first=result;cases.push_back(result);
 }}std::ofstream(argv[4])<<json({{"scope","Six diagnostic mode5 marker20/callback4 timer/score/transfer/release/finite GameOver/freeze/reset; injected initial ball/rules, natural reachability and whole Original trajectory unclaimed"},{"cases",cases}}).dump(2)<<'\n';std::cout<<"PASS six mode5 right capture finite diagnostic chains\n";}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
