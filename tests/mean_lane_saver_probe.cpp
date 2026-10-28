#include "physics/mean_lane_saver.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(){
  nlohmann::json input,out=nlohmann::json::array(); std::cin>>input;
  for(const auto &c:input){
    std::array<std::int32_t,3> s=c.at("slot").get<std::array<std::int32_t,3>>();
    const auto e=slam::mean_lane_saver_tick(s,c.at("idle").get<bool>());
    std::vector<std::uint8_t> dat(0x100000);
    for(std::size_t i=0;i<dat.size();++i)dat[i]=std::uint8_t((i*17+(i>>8))&255);
    if(e.patch_requested)slam::mean_lane_saver_patch(dat,0x10000,0x30000,e.enabled);
    std::vector<std::uint8_t> patch;
    for(unsigned y=0;y<30;++y)for(unsigned x=0;x<4;++x)patch.push_back(dat[0x149e1+y*40+x]);
    std::vector<std::uint8_t> hit;
    for(unsigned plane=0;plane<4;++plane)for(unsigned y=0;y<32;++y)
      for(unsigned x=0;x<4;++x)hit.push_back(dat[0x349e1+plane*0x6040+y*40+x]);
    out.push_back({{"slot",s},{"draw",e.draw_requested?nlohmann::json(e.drawn_frame):nlohmann::json(nullptr)},
                   {"patch",patch},{"hit",hit}});
  }
  std::cout<<out.dump();
}
