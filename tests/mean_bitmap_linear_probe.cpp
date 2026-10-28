#include "physics/mean_step.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc,char**argv) {
 if(argc!=2)return 2;
 std::ifstream f(argv[1],std::ios::binary);
 slam::MeanCollisionBits bits;bits.dat.assign(std::istreambuf_iterator<char>(f),{});
 nlohmann::json cases;std::cin>>cases;auto out=nlohmann::json::array();
 for(const auto&c:cases){bits.hit_offset=c["hit"];bits.stride=c["stride"];bits.extra_planes=c["planes"];out.push_back({bits.sample_linear(c["x"],c["y"]),bits.extra_plane_mask_linear(c["x"],c["y"])});}
 std::cout<<out.dump();
}
