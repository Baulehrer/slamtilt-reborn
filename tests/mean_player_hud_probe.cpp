#include "dmd/mean_player_hud.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc,char **argv) {
 if(argc!=3)return 2;
 try {
  const auto assets=slam::load_mean_player_hud(argv[1],argv[2]);
  nlohmann::json input;std::cin>>input;auto out=nlohmann::json::array();
  for(const auto &c:input) {
   slam::MeanPlayerHud s;
#define FIELD(n) s.n=c.at(#n).get<decltype(s.n)>();
   FIELD(counter) FIELD(field_engine_5c) FIELD(field_engine_60) FIELD(field_engine_04) FIELD(field_engine_08)
   FIELD(field_360) FIELD(field_35c) FIELD(field_358) FIELD(field_206) FIELD(field_362) FIELD(player_0e) FIELD(score)
#undef FIELD
   for(unsigned i=0;i<s.pixels.size();++i)s.pixels[i]=i%4;
   for(unsigned i=0;i<s.scratch.size();++i)s.scratch[i]=(i*13+i/12)%256;
   auto frames=nlohmann::json::array();
   for(unsigned tick=0;tick<c.at("steps").get<unsigned>();++tick) {
    const bool valid=slam::mean_player_hud_step(s,assets);
    frames.push_back({{"counter",s.counter},{"field_360",s.field_360},{"pixels",s.pixels},{"scratch",s.scratch},{"valid",valid}});
   }
   out.push_back(frames);
  }
  std::cout<<out.dump()<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
