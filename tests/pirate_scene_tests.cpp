#include "renderer/pirate_scene.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>

int main(int argc,char**argv) {
  try {
    if(argc!=2)return 2;
    std::ifstream input(argv[1]);nlohmann::json fixture;input>>fixture;
    unsigned count=0,clipped=0;
    for(const auto& row:fixture.at("cases")) {
      const auto got=slam::pirate_scene_origin(row.at("camera_scroll"),row.at("horizontal_pixels"),
        row.at("vertical_fixed"),fixture.at("maximum_scroll"));
      if(got!=row.at("origin").get<std::array<int,2>>())
        throw std::runtime_error("Native scene differs from original source viewport");
      const auto src=row.at("original_source_rect").get<std::array<int,4>>();
      if(got[0]!=8-src[0]||got[1]!=-src[1])throw std::runtime_error("Original backing border mismatch");
      if(src[1]==0||src[1]==208)++clipped;
      ++count;
    }
    if(count!=63||!clipped)throw std::runtime_error("Incomplete original viewport coverage");
    std::cout<<count<<" original viewport transforms including edge clipping match native\n";
    return 0;
  }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
