#include "physics/mean_simulation.h"
#include <iostream>
#include <stdexcept>
int main(int argc,char**argv){if(argc!=4)return 2;try{
 for(unsigned locks=0;locks<4;++locks)for(bool reject:{false,true}){
  slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.debug_speed_jackpot(locks,reject);
  if(s.score()!=10000000u*(locks+1) || s.table_mode()!=6)throw std::runtime_error("SPEED native score/mode mismatch");
  const auto &stats=s.speed_stats();
  if(stats.score!=10000000u*(locks+1) || stats.jackpots[locks]!=1)throw std::runtime_error("SPEED telemetry differs from actual awards");
  for(unsigned i=0;i<4;++i)if(i!=locks && stats.jackpots[i])throw std::runtime_error("SPEED telemetry counted wrong multiplier");
  const auto expected=reject ? std::array<std::int32_t,5>{101,102,103,104,105} : std::array<std::int32_t,5>{};
  if(s.capture_delays()!=expected)throw std::runtime_error("SPEED native admission delay mismatch");
  const auto&f=s.shared_raw_state().fields;unsigned field=0;for(unsigned i=0;i<4;++i)field|=unsigned(f[0x024+i])<<(8*i);
  if(field!=(reject ? 0x1234u : 0u))throw std::runtime_error("SPEED control field mismatch");
  if(s.material5_display_callback()!=(reject ? 0x410b00u : 0x410158u))throw std::runtime_error("SPEED priority owner mismatch");
 }
 slam::MeanSimulation preview(argv[1],argv[2],argv[3]);preview.debug_speed_jackpot(3,false,true);
 bool visible=false;for(auto pixel:preview.material5_pixels())visible|=pixel!=0;
 if(!visible || preview.material5_display_callback()!=0x410158)throw std::runtime_error("SPEED preview captured blank blink phase");
 std::cout<<"PASS eight native SPEED multiplier/admission/control/owner contexts\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
