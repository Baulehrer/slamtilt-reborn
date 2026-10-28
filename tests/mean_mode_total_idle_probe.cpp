#include "rules/mean_mode_total_idle.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input, out=nlohmann::json::array();std::cin>>input;
  for(const auto &c:input){
    auto pending=c.at("pending").get<std::int16_t>();
    auto engine=c.at("engine40").get<std::int32_t>();
    bool request=slam::mean_mode_total_idle(pending,engine);
    nlohmann::json events=nlohmann::json::object();
    if(request){events["request"]={8,7,2,0,30,1,0x410c8c};events["control"]={1,1,1,1,1,0};}
    out.push_back({{"pending",pending},{"engine40",engine},{"returned",request?c.at("handle").get<std::int32_t>():123},{"events",events}});
  }
  std::cout<<out.dump()<<'\n';
}
