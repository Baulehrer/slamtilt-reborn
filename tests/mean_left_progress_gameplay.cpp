#include "physics/mean_simulation.h"
#include <iostream>
#include <stdexcept>
int main(int argc,char**argv){if(argc!=4)return 2;try{
 slam::MeanSimulation s(argv[1],argv[2],argv[3]);unsigned cases=0;
 for(unsigned mode=2;mode<=6;++mode)for(unsigned stage=0;stage<3;++stage)for(unsigned letters:{0u,4u,5u})for(bool reject:{false,true}){
  s.debug_left_progress(stage,letters,mode,reject);
  const auto&f=s.shared_raw_state().fields;auto word=[&](unsigned o){return unsigned(f[o])|(unsigned(f[o+1])<<8);};
  const bool active=mode<=4,wrap=active&&stage==2,request=wrap&&letters<5,admitted=request&&!reject&&mode!=3;
  if(word(0x3ba)!=(active?(stage+1)%3:stage)||word(0x1f2)!=(letters+(request?1:0)))throw std::runtime_error("Left progression stage/letter mismatch");
  if(word(0x392)!=(active?(stage==1?65535u:stage==2?0u:0u):(stage==2?65535u:0u)))throw std::runtime_error("Left progression arm mismatch");
  const auto delays=admitted?std::array<std::int32_t,5>{}:std::array<std::int32_t,5>{101,102,103,104,105};
  if(s.capture_delays()!=delays)throw std::runtime_error("Left progression actual admission delays mismatch");
  if(s.material5_display_callback()!=(reject?0x410b00u:admitted?0x412df0u:0u))throw std::runtime_error("Left progression DMD owner mismatch");
  if(admitted && (s.display_scheduler().field_788!=5||s.display_scheduler().field_297ac!=11))throw std::runtime_error("Left progression original priority/sound mismatch");
  if(active){const auto next=(stage+1)%3;if(f[0x218+next*4]!=4||f[0x219+next*4]!=6)throw std::runtime_error("Left progression lamp mismatch");}
  ++cases;
 }
 std::cout<<"PASS "<<cases<<" native left progression/arming/letter/admission/lamps contexts\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
