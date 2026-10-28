#include "physics/mean_simulation.h"
#include "rules/mean_player_record.h"
#include <nlohmann/json.hpp>
#include <iostream>
#include <stdexcept>
int main(int argc,char **argv){
 if(argc!=4)return 2;
 try{
  nlohmann::json out=nlohmann::json::array();unsigned wins=0;
  for(unsigned period: {5u,10u,20u,40u}){
   slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.reset();
   if(s.selected_mode()!=0)throw std::runtime_error("Original new-game selection mismatch");
   s.debug_start_mode4_right(true);
   unsigned sounds=0;std::vector<slam::MeanAudioRequest> terminal_music;
   for(unsigned i=0;i<12000 && !s.minigame_completions();++i){
    s.set_flippers((i/period)%2,((i/period)+1)%2);
    if(!s.step())throw std::runtime_error(s.status());
    for (const auto &a:s.take_audio_requests()) {
     if(s.minigame_completions() && (a.service==0x84 || a.service==0x80))terminal_music.push_back(a);
     if(a.service==0x5c && a.descriptor>=0x437fe4 && a.descriptor<=0x438050){
     if(a.bank!=255 || a.order!=245)throw std::runtime_error("Minigame sample arguments mismatch");
     ++sounds;
     }
    }
   }
   if(s.minigame_completions()!=1)throw std::runtime_error("Second minigame did not return");
   if(sounds!=1)throw std::runtime_error("Countdown/start samples missing or repeated");
   const auto callback=s.material5_display_callback();
   if(callback!=0x41210c && callback!=0x4122cc)
    throw std::runtime_error("Second minigame terminal display missing");
   auto state=s.shared_raw_state();
   const auto w=[&](unsigned o){return unsigned(state.fields[o])|(unsigned(state.fields[o+1])<<8);};
   const auto expected_music=static_cast<std::int16_t>(w(0x37a))>=0?0x84:0x80;
   if(terminal_music.size()!=1 || terminal_music[0].service!=expected_music || terminal_music[0].bank!=0 || terminal_music[0].order!=(expected_music==0x84?62:0))
    throw std::runtime_error("Original terminal music branch mismatch");
   const auto threshold=w(0x1f6),completed=w(0x1f8);
   if(threshold!=8000 && threshold!=7600)throw std::runtime_error("Original threshold update mismatch");
   if((threshold==7600)!=(callback==0x4122cc))throw std::runtime_error("Wrong terminal display");
   if(threshold==7600){if(completed!=1)throw std::runtime_error("Completion count mismatch");++wins;}
   slam::mean_ball_save(state);slam::MeanBallResetEvents event;slam::mean_ball_reset(state,event);
   if((unsigned(state.fields[0x1f6])|(unsigned(state.fields[0x1f7])<<8))!=threshold)
    throw std::runtime_error("Updated target lost across next-ball reset");
   slam::mean_initialize_player_record(state.player_record);
   if((unsigned(state.player_record[34])|(unsigned(state.player_record[35])<<8))!=8000)
    throw std::runtime_error("New-game target not restored");
   out.push_back({{"period",period},{"threshold",threshold},{"completed",completed},{"score",s.score()},{"mode",s.table_mode()},{"display_callback",callback}});
  }
  std::cout<<out.dump()<<'\n';
  if(!wins) return 3;
 }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
