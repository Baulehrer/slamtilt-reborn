#include "renderer/pirate_camera.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc,char**argv){try{
  if(argc!=2)return 2;
  std::ifstream in(argv[1]);nlohmann::json f;in>>f;slam::PirateCamera camera;
  unsigned count=0;
  for(const auto& row:f.at("cases")){
    std::vector<slam::PirateCamera::Ball> balls;
    for(const auto& b:row.at("balls"))balls.push_back({b.at("y"),b.at("state")});
    camera.step(row.at("phase"),balls);
    if(nlohmann::json(camera.state())!=row.at("state"))throw std::runtime_error("Camera state mismatch at "+std::to_string(count));
    for(unsigned residual=0;residual<5;++residual)
      if(camera.scroll(residual)!=row.at("scroll").at(residual))throw std::runtime_error("Camera interpolation mismatch at "+std::to_string(count));
    ++count;
  }
  std::cout<<count<<" original camera states / "<<count*5<<" interpolation observations exact\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
