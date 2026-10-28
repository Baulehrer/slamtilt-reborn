#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
using json=nlohmann::json;
static json requests(slam::MeanSimulation &s) {
  json result=json::array();
  for(const auto &r:s.take_audio_requests())
    result.push_back({{"service",r.service},{"bank",r.bank},{"order",r.order},{"descriptor",r.descriptor}});
  return result;
}
int main(int argc,char **argv) {
  if(argc!=5)return 2;
  try {
    slam::MeanSimulation s(argv[1],argv[2],argv[3]);
    s.set_retail_minigame(true);s.reset();
    s.set_flippers(true,true);
    const auto expected=requests(s);
    if(expected.size()!=3||expected[0].at("service")!=0x90||expected[1].at("service")!=0x5c||expected[2].at("service")!=0x5c)
      throw std::runtime_error("Fresh startup and two flipper edges missing");
    json cycles=json::array();
    for(unsigned cycle=0;cycle<8;++cycle) {
      // Legal R/newgame while physical keys remain held: new SDL key-down
      // must produce the same edges as an independent new game.
      s.set_flippers(true,true);s.set_launch(true);s.reset();
      if(cycle&1)s.reset();
      s.set_flippers(true,true);
      const auto actual=requests(s);
      if(actual!=expected)throw std::runtime_error("Reset retained input latches, cycle "+std::to_string(cycle));
      s.set_flippers(true,true);
      if(!requests(s).empty())throw std::runtime_error("Held flippers synthesized repeated edges");
      cycles.push_back({{"cycle",cycle},{"double_reset",bool(cycle&1)},{"audio",actual}});
    }
    std::ofstream(argv[4])<<json({{"status","PASS"},{"scope","Eight legal held-input newgame cycles; reset and double-reset restore fresh flipper audio edges, held repeats remain silent"},{"cycles",cycles}}).dump(2)<<'\n';
    std::cout<<"PASS held-input reset: eight cycles / fresh flipper edges / silent held repeats\n";
  } catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
