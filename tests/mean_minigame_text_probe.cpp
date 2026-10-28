#include "dmd/mean_minigame_text.h"
#include "physics/mean_minigame_lift.h"
#include <nlohmann/json.hpp>
#include <iostream>
int main(int argc,char **argv){
 if(argc!=2)return 2;
 const auto font=slam::load_mean_bonus_pixels(argv[1]);nlohmann::json cases;std::cin>>cases;auto out=nlohmann::json::array();
 for(auto &c:cases){
  slam::WindowsDmdPixels pixels;for(unsigned i=0;i<pixels.size();++i)pixels[i]=i%4;
  auto regs=c["registers"].get<std::array<std::uint32_t,8>>();
  const auto text=c.value("text",std::string());const auto bcd=c.value("bcd",std::vector<unsigned>{});
  slam::MeanMinigameLift m; m.r=regs; m.pixels=pixels; m.r[4]+=4;
  m.text_service=[&](slam::MeanMinigameLift &state,std::uint32_t target){
   slam::mean_minigame_text_service(font,state.pixels,target,state.r,[&](std::uint32_t a,unsigned n)->std::uint32_t{
    if(a==0x10ff004)return c.value("x",0u);
    if(a==0x10ff008)return 0x1005000;
    if(a>=0x1005000 && a<0x1005000+bcd.size())return bcd[a-0x1005000];
    if(a>=0x1004000 && a<=0x1004000+text.size())return a==0x1004000+text.size()?0:unsigned(text[a-0x1004000]);
    throw std::runtime_error("Unexpected text read");
   });
  };
  m.service(c["target"]);pixels=m.pixels;regs=m.r;
  std::uint64_t h=14695981039346656037ull;for(auto p:pixels)h=(h^p)*1099511628211ull;
  out.push_back({{"fnv",std::to_string(h)},{"result",regs[0]}});
 }
 std::cout<<out.dump()<<'\n';
}
