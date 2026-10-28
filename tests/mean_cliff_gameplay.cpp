#include "physics/mean_simulation.h"
#include <iostream>
#include <stdexcept>
int main(int argc,char**argv){if(argc!=4)return 2;try{
 for(unsigned previous=0;previous<6;++previous)for(bool failure:{false,true})for(bool reject:{false,true}){
  slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.debug_cliff_jump(previous,failure,reject);
  if(s.score()!=(failure?0:30000000u+previous*15000000u) || s.table_mode()!=2 || s.mode4_completions()!=1)
    throw std::runtime_error("Cliff result/return mismatch");
  const auto expected=reject?std::array<std::int32_t,5>{101,102,103,104,105}:std::array<std::int32_t,5>{};
  if(s.capture_delays()!=expected)throw std::runtime_error("Cliff five-slot admission mismatch");
  const auto&f=s.shared_raw_state().fields;unsigned control=0;for(unsigned i=0;i<4;++i)control|=unsigned(f[0x024+i])<<(8*i);
  if(control!=(reject?0x1234u:0u))throw std::runtime_error("Cliff control mismatch");
  if((unsigned(f[0x1f4])|(unsigned(f[0x1f5])<<8))!=previous+!failure)throw std::runtime_error("Cliff next award mismatch");
  if(s.material5_display_callback()!=(reject?0x410b00u:failure?0x4126ecu:0x41249cu))throw std::runtime_error("Cliff result owner discarded");
 }
 slam::MeanSimulation p(argv[1],argv[2],argv[3]);p.debug_cliff_jump(0,false,false,true);
 bool visible=false;for(auto pixel:p.material5_pixels())visible|=pixel!=0;
 if(!visible)throw std::runtime_error("Cliff preview blank");
 std::cout<<"PASS24nativeCliff instruction/input/award-or-timeout/priority/five-slots/return contexts\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
