#include "physics/mean_simulation.h"
#include <iostream>
#include <stdexcept>
int main(int argc,char**argv){if(argc!=4)return 2;try{
 slam::MeanSimulation s(argv[1],argv[2],argv[3]);
 auto word=[&](unsigned o){const auto&f=s.shared_raw_state().fields;return unsigned(f[o])|(unsigned(f[o+1])<<8);};
 for(unsigned choice=0;choice<3;++choice){s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  if(word(0x35c)||word(0x358))throw std::runtime_error("New game Skillshot not unlocked/score selected");
  for(unsigned i=0;i<choice;++i){s.set_flippers(false,true);s.set_flippers(false,false);}
  unsigned selected=choice%2?0x7fff:0;
  if(word(0x358)!=selected)throw std::runtime_error("Prelaunch right edge did not select Skillshot");
  s.set_launch(true);unsigned tick=0;
  while(!s.launches()&&tick++<1000){if(!s.step())throw std::runtime_error(s.status());s.take_audio_requests();}
  if(!s.launches()||word(0x35c)!=0xffff)throw std::runtime_error("Launch did not lock Skillshot");
  // Test immediately, before playfield entry changes mode1 to mode2.
  s.set_flippers(false,true);s.set_flippers(false,false);
  if(word(0x358)!=selected)throw std::runtime_error("Right edge changed Skillshot after launch");
 }
 s.reset();if(word(0x35c)||word(0x358))throw std::runtime_error("Reset did not restore Skillshot selection");
 std::cout<<"PASS three fresh Skillshot choices/launch locks/newgame reset\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
