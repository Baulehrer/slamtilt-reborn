#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
int main(int argc,char**argv){if(argc!=5&&argc!=6)return 2;try{
 json fixture;std::ifstream(argv[4])>>fixture;
 slam::MeanSimulation s(argv[1],argv[2],argv[3]);json cases=json::array();
 for(bool failure:{false,true})for(unsigned repeat=0;repeat<2;++repeat){
  s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned ticks=0,checkpoint=0;json events=json::array();
  auto word=[&](unsigned o){const auto&f=s.shared_raw_state().fields;return unsigned(f[o])|(unsigned(f[o+1])<<8);};
  for(const auto&run:fixture.at("actions_rle"))for(unsigned i=0;i<run.at("ticks").get<unsigned>();++i){
   unsigned action=run.at("actions");if(failure){action&=~4u;if(ticks+1==fixture.at("failure_press_step").get<unsigned>()){if(word(0x3a6)!=0||word(0x39e)>=3)throw std::runtime_error("Cliff failure input missed early-rev window");action|=4;}}
   s.set_launch(action&8);s.set_flippers(action&1,action&2);if(action&4)s.press_plunger();
   if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++ticks;
   if(checkpoint<fixture.at("events").size() && ticks==fixture["events"][checkpoint]["step"]){
    const auto&e=fixture["events"][checkpoint];
    if(!failure||checkpoint<3){
     const std::array<unsigned,7> state{word(0x3ba),word(0x392),unsigned(s.table_mode()),word(0x39e),s.mode4_starts(),s.mode4_completions(),s.material5_display_callback()};
     if(json(state)!=e.at("state") || json(s.ball().bytes)!=e.at("object") || s.score()!=e.at("score") || s.ball_number()!=1)
      throw std::runtime_error("Natural Cliff recorded checkpoint changed at"+std::to_string(ticks));
    }
    ++checkpoint;
   }
  }
  s.set_flippers(false,false);s.set_launch(true);
  for(unsigned i=0;s.table_mode()==4&&i<4000;++i){if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();++ticks;}
  const auto callback=s.material5_display_callback();
  if(s.state7_steps()!=18||s.mode4_starts()!=1||s.mode4_completions()!=1||s.table_mode()!=2||callback!=(failure?0x4126ecu:0x41249cu))
   throw std::runtime_error("Natural Cliff outcome mismatch: failure="+std::to_string(failure)+" callback="+std::to_string(callback));
  const auto result=s.score();events.push_back({{"event",failure?"timeout":"success"},{"step",ticks},{"score",result},{"callback",callback},{"state7_steps",s.state7_steps()}});
  auto old_bonus=s.bonus_completions();
  while(!s.game_over()&&ticks<100000){
   if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();++ticks;
   if(s.bonus_completions()!=old_bonus){old_bonus=s.bonus_completions();events.push_back({{"event","bonus"},{"step",ticks},{"ball",s.ball_number()},{"score",s.score()},{"completed",old_bonus}});}
  }
  if(!s.game_over()||s.ball_count()!=0||s.bonus_completions()<3||s.score()<result)throw std::runtime_error("Natural Cliff finite lifecycle incomplete");
  const auto final_score=s.score();const auto raw=s.shared_raw_state().fields;
  for(unsigned i=0;i<100;++i){s.set_flippers(true,true);s.press_plunger();if(s.step()||s.score()!=final_score||s.shared_raw_state().fields!=raw)throw std::runtime_error("Cliff GameOver not frozen");}
  s.reset();if(s.game_over()||s.ball_number()!=1||s.score()!=0||s.mode4_starts()||s.mode4_completions()||word(0x392))throw std::runtime_error("Cliff reset incomplete");
  cases.push_back({{"failure",failure},{"repeat",repeat},{"ticks",ticks},{"final_score",final_score},{"events",events}});
 }
 if(cases[0]["events"]!=cases[1]["events"]||cases[2]["events"]!=cases[3]["events"])throw std::runtime_error("Natural Cliff replay nondeterministic");
 const json report={{"scope","Four native finite SDL-input Cliff success/early-rev-timeout -> bonus -> GameOver/freeze/reset chains; no whole original trajectory claim"},{"cases",cases}};
 if(argc==6){std::ofstream(argv[5])<<report.dump(2)<<'\n';std::cout<<"PASS four natural finite Cliff success/timeout/bonus/GameOver/reset chains\n";}
 else std::cout<<report.dump()<<'\n';
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
