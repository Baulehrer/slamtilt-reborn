#include "physics/pirate_step_lift.h"
#include <fstream>
#include <cstdlib>
#include <iostream>
#include <nlohmann/json.hpp>
using json=nlohmann::json;
int main(int argc,char**argv) {
  if(argc<4||argc>5)return 2;
  unsigned current=0;
  try {
    slam::PirateStepLift m;
    std::ifstream image(std::string(argv[1])+"/image.bin",std::ios::binary),runtime(std::string(argv[1])+"/runtime.bin",std::ios::binary),dat(argv[2],std::ios::binary);
    m.image.assign(std::istreambuf_iterator<char>(image),{});m.runtime.assign(std::istreambuf_iterator<char>(runtime),{});m.dat.assign(std::istreambuf_iterator<char>(dat),{});
    if(m.image.size()!=0x100000||m.runtime.size()!=0x10000||m.dat.empty())throw std::runtime_error("Missing original Pirate inputs");
    unsigned ticks=argc==5?std::stoul(argv[4]):100;
    json states=json::array();
    states.push_back(std::vector<std::uint8_t>(m.runtime.begin(),m.runtime.begin()+100));
    json instructions=json::array();
    const char* trace_step=std::getenv("SLAM_PIRATE_TRACE_STEP");
    const unsigned traced=trace_step?std::stoul(trace_step):~0u;
    for(unsigned tick=0;tick<ticks;++tick){
      current=tick;
      if(tick==traced)m.instruction_observer=[&](slam::PirateStepLift&state,std::uint32_t pc){instructions.push_back(json::array({pc,state.r,state.z,state.s,state.o,state.c}));};
      if(trace_step&&tick==traced+1)m.instruction_observer={};
      m.wr(0x46c5fc,1,4);m.invoke(0x409154);m.invoke(0x40950c);
      states.push_back(std::vector<std::uint8_t>(m.runtime.begin(),m.runtime.begin()+100));
    }
    std::ofstream output(argv[3]);output<<json({{"tick_count",ticks},{"states",states},{"instructions",instructions}}).dump()<<'\n';
    if(!output)throw std::runtime_error("Cannot write Pirate native trace");
    std::cout<<"Native Pirate steps: "<<ticks<<'\n';return 0;
  }catch(const std::exception&e){std::cerr<<"tick "<<current<<": "<<e.what()<<'\n';return 1;}
}
