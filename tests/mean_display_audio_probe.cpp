#include "audio/mean_display_audio.h"
#include <nlohmann/json.hpp>
#include <iostream>
int main() {
  nlohmann::json cases;std::cin>>cases;
  nlohmann::json result=nlohmann::json::array();
  for (const auto &c:cases) {
    const auto e=slam::mean_display_audio(c.at("old780"),c.at("stack0"),
      c.at("stack1"),c.at("admitted"),c.at("flags"));
    result.push_back({{"service",e.service},{"bank",e.bank},{"order",e.order}});
  }
  std::cout<<result.dump()<<'\n';
}
