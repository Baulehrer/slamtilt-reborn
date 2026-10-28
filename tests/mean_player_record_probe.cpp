#include "rules/mean_player_record.h"
#include <nlohmann/json.hpp>
#include <iostream>
int main(){
 nlohmann::json input;std::cin>>input;auto output=nlohmann::json::array();
 for(auto &v:input){auto record=v.get<std::array<std::uint8_t,52>>();slam::mean_initialize_player_record(record);output.push_back(record);}
 std::cout<<output.dump()<<'\n';
}
