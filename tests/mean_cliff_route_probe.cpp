#include "core/mean_diagnostic_input.h"
#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
using json=nlohmann::json;
int main(int argc,char**argv){if(argc!=6)return 2;try{
 slam::MeanSimulation s(argv[1],argv[2],argv[3]);json results=json::array();
 for(unsigned seed=0;seed<std::stoul(argv[4]);++seed){
  if(seed%16==0)std::cerr<<"seed "<<seed<<'\n';
  s.reset();s.set_retail_minigame(true);s.set_continuous_play(true);s.set_endless_play(false);
  slam::MeanDiagnosticInput random(seed);json events=json::array();std::vector<std::pair<unsigned,unsigned>> runs;unsigned old_action=99,ticks=0,entry=0;std::array<unsigned,7> old{};
  auto word=[&](unsigned o){const auto&f=s.shared_raw_state().fields;return unsigned(f[o])|(unsigned(f[o+1])<<8);};
  for(;ticks<30000 && !s.game_over();++ticks){
   bool left=false,right=false,press=false;
   if(seed<64){left=(ticks/(30+seed*3))%2;right=!left;}
   else if(seed<128){const auto k=random.next();left=k[0];right=k[1];}
   else {const auto k=slam::mean_finite_shot_input(ticks,s.ball().i32(4)>>16,seed-128);left=k[0];right=k[1];}
   if(s.table_mode()==4 && word(0x3a6)==0){left=right=false;if(word(0x39e)==3 && (word(0x3a8)&127)==64)press=true;}
   const unsigned action=8|left|(right<<1)|(press<<2);
   if(action==old_action)++runs.back().second;else{runs.emplace_back(action,1);old_action=action;}
   s.set_launch(true);s.set_flippers(left,right);if(press)s.press_plunger();
   if(!s.step()&&!s.game_over())throw std::runtime_error(s.status());s.take_audio_requests();
   const std::array<unsigned,7> current{word(0x3ba),word(0x392),unsigned(s.table_mode()),word(0x39e),s.mode4_starts(),s.mode4_completions(),s.material5_display_callback()};
   if(current!=old){
    if(current[0]!=old[0]||current[1]!=old[1]||current[4]!=old[4]||current[5]!=old[5]||current[6]==0x41249c||current[6]==0x4126ec)
     events.push_back({{"step",ticks+1},{"state",current},{"phase",word(0x3a6)},{"ball",s.ball_number()},{"score",s.score()},{"object",s.ball().bytes}});
    if(current[4]>old[4] && word(0x3a6)==0)++entry;
    old=current;
   }
   if(entry && s.mode4_completions())break;
  }
  if(entry || !events.empty())results.push_back({{"seed",seed},{"steps",ticks},{"entered",entry},{"events",events},{"game_over",s.game_over()}});
  if(entry){json rle=json::array();for(const auto&run:runs)rle.push_back({{"actions",run.first},{"ticks",run.second}});std::ofstream(argv[5])<<json({{"scope","Native finite SDL actions only; no injected ball/rule state, not original autonomous trajectory"},{"seed",seed},{"actions_rle",rle},{"events",events}}).dump(2)<<'\n';std::cout<<json({{"found",true},{"seed",seed},{"steps",ticks},{"events",events}}).dump()<<'\n';return 0;}
 }
 std::ofstream(argv[5])<<json({{"found",false},{"cases",results}}).dump(2)<<'\n';std::cout<<json({{"found",false},{"interesting",results.size()}}).dump()<<'\n';
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
