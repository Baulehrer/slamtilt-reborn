#include "physics/mean_simulation.h"
#include <iostream>
int main(int argc,char**argv) {
 if(argc!=4)return 2;
 try {
  slam::MeanSimulation s(argv[1],argv[2],argv[3]);
  s.reset();if(s.table_mode()!=1)throw std::runtime_error("Reset is not Mode1");
  s.press_plunger();if(s.mode_locked())throw std::runtime_error("Mode1 locked");
  s.debug_nudge_warning();s.press_plunger();
  if(!s.mode_locked() || s.material5_display_callback()!=0x411908)throw std::runtime_error("Mode Lock admission missing");
  if(s.capture_delays()!=std::array<std::int32_t,5>{})throw std::runtime_error("Mode Lock delay helper missing");
  s.set_launch(true);
  for(unsigned i=0;i<440;++i)if(!s.step())throw std::runtime_error(s.status());
  s.reset();if(s.mode_locked())throw std::runtime_error("Mode Lock survives reset");
  s.debug_nudge_warning();s.apply_tilt();s.press_plunger();
  if(s.mode_locked())throw std::runtime_error("Tilt permits Mode Lock");
  std::cout<<"PASS normal/input/reset/Tilt Mode Lock integration\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
