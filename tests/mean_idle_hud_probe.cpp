#include "dmd/mean_idle_hud.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc,char **argv) {
 if(argc!=3)return 2;
 try {
  auto assets=slam::load_mean_idle_hud(argv[1],argv[2]);
  nlohmann::json input;std::cin>>input;auto out=nlohmann::json::array();
  for(const auto &c:input) {
   slam::MeanIdleHud s;s.counter=c.at("counter");s.field_398=c.at("field_398");s.field_37a=c.at("field_37a");s.field_3ac=c.at("field_3ac");s.field_054=c.at("field_054");s.score=c.at("score");
   for(unsigned i=0;i<s.pixels.size();++i)s.pixels[i]=i%4;
   slam::mean_idle_hud_step(s,assets);out.push_back({{"counter",s.counter},{"pixels",s.pixels}});
  }
  std::cout<<out.dump()<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
