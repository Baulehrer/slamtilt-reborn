#include "dmd/mean_main_mode_hud.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc,char **argv) {
 if(argc!=3)return 2;
 try {
  auto assets=slam::load_mean_main_mode_hud(argv[1],argv[2]);
  nlohmann::json input;std::cin>>input;auto out=nlohmann::json::array();
  for(const auto &c:input) {
   slam::MeanMainModeHud s;s.counter=c.at("counter");s.mode=c.at("mode");s.selected=c.at("selected");s.field_39c=c.at("field_39c");s.field_38c=c.at("field_38c");s.field_38e=c.at("field_38e");s.field_368=c.at("field_368");s.field_36c=c.at("field_36c");s.field_05c=c.at("field_05c");s.score=c.at("score");
   for(unsigned i=0;i<s.pixels.size();++i)s.pixels[i]=i%4;
   auto active=slam::mean_main_mode_hud_step(s,assets);out.push_back({{"active",active},{"counter",s.counter},{"pixels",s.pixels}});
  }
  std::cout<<out.dump()<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
