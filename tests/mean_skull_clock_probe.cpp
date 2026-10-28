#include "rules/mean_skull_clock.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(){nlohmann::json input,out=nlohmann::json::array();std::cin>>input;for(auto&c:input){auto t=c.at("timer").get<std::int16_t>();auto n=c.at("count").get<std::uint16_t>();auto lamp=c.at("lamp").get<std::array<std::uint8_t,4>>();slam::mean_skull_clock(t,n,lamp);out.push_back({{"timer",t},{"count",n},{"lamp",lamp}});}std::cout<<out;}
