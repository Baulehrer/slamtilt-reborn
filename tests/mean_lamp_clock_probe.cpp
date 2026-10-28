#include "rules/mean_lamps.h"
#include <nlohmann/json.hpp>
#include <iostream>
int main(){
 nlohmann::json input,result=nlohmann::json::array();std::cin>>input;
 for(const auto &c:input.at("cases")){
  auto state=c.at("initial").get<std::array<std::uint8_t,4>>();bool on=c.at("on");
  auto steps=nlohmann::json::array();
  for(std::size_t i=0;i<c.at("steps").size();++i){
   const bool update=slam::mean_lamp_tick(state,on);
   steps.push_back({{"state",state},{"on",on},{"update",update}});
  }
  result.push_back(steps);
 }
 std::cout<<result.dump();
}
