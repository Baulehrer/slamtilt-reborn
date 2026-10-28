#include "physics/mean_simulation.h"
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <stdexcept>
int main(int argc,char **argv){
 if(argc!=5)return 2;
 try{
  std::ifstream input(argv[4]);nlohmann::json fixture;input>>fixture;
  const auto &expected=fixture.at("expected").at(0);
  for(unsigned profile=0;profile<4;++profile){
   slam::MeanSimulation s(argv[1],argv[2],argv[3]);
   if(!s.debug_start_minigame())throw std::runtime_error(s.status());
   for(unsigned i=0;i<6000 && !s.minigame_completions();++i){
    s.set_flippers(profile==1 || (profile==3 && i%400<200),profile==2 || (profile==3 && i%400>=200));
    if(!s.step())throw std::runtime_error(s.status());
   }
   if(s.minigame_completions()!=1 || s.material5_display_callback()!=0x40f994 || s.score()!=0)
    throw std::runtime_error("First minigame result/admission mismatch");
   s.set_flippers(false,false);
   unsigned checked=0;
   for(unsigned i=0;i<750 && s.material5_display_callback()==0x40f994;++i){
    if(!s.step())throw std::runtime_error(s.status());
    const auto count=s.material5_display_counter();if(!count)continue;
    std::uint64_t h=14695981039346656037ull;for(auto p:s.material5_pixels())h=(h^p)*1099511628211ull;
    const auto &e=expected.at(count-1);
    if(std::to_string(h)!=e.at("fnv") || (s.material5_display_callback()!=0)!=e.at("active"))
     throw std::runtime_error("Shared-owner minigame result pixel/retirement mismatch");
    ++checked;
   }
   if(s.material5_display_callback()==0x40f994 || checked<168)
    throw std::runtime_error("First minigame result did not retire");
   for(unsigned i=0;i<8;++i)if(!s.step())throw std::runtime_error(s.status());
   if(s.display_scheduler().field_784!=0)throw std::runtime_error("Result retained display ownership");
  }
  std::cout<<"Four native first-minigame result chains match original pixels and release DMD ownership\n";
 }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
