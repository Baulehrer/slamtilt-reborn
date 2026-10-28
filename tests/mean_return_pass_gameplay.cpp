#include "physics/mean_simulation.h"
#include <nlohmann/json.hpp>
#include <iostream>
#include <stdexcept>
int main(int argc,char **argv){
 if(argc!=4)return 2;
 try{
  slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.reset();
  nlohmann::json rows=nlohmann::json::array();
  for(unsigned hit=0;hit<3;++hit){
   s.debug_place_return_pass();
   if(!s.step())throw std::runtime_error(s.status());
   const auto &f=s.shared_raw_state().fields;
   const unsigned count=f[0x37c]|(unsigned(f[0x37d])<<8);
   if(s.return_passes()!=hit+1 || count!=hit || s.score()!=hit*(hit+1)*2500000ull)
    throw std::runtime_error("Return-pass native chain mismatch");
   rows.push_back({{"hit",hit+1},{"selected",s.selected_mode()},{"score",s.score()},
       {"counter",count},{"timer",f[0x374]|(unsigned(f[0x375])<<8)},
       {"callback",s.material5_display_callback()},{"ball",s.ball().bytes}});
  }
  if(s.return_pass_awards()!=2 || s.material5_display_callback()!=0x41163c)
   throw std::runtime_error("Return-pass display request missing");
  std::cout<<rows.dump()<<'\n';
 }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
