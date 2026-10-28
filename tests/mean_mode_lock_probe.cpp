#include "input/mean_mode_lock.h"
#include <nlohmann/json.hpp>
#include <iostream>
int main(){nlohmann::json rows;std::cin>>rows;auto out=nlohmann::json::array();for(auto& c:rows){slam::MeanModeLock s;s.service_1c=c[0];s.engine_30=c[1];s.engine_44=c[2];s.field_384=c[3];s.field_3a6=c[4];s.field_39e=c[5];s.field_3a8=c[6];s.field_030=c[7];s.field_064=c[8];s.field_038=c[9];s.selected_lamp={9,8,7,6};s.press(c[10],c[11]);auto ev=nlohmann::json::array();for(auto&e:s.requests)ev.push_back({e.target,e.eax,e.edx,e.ecx,e.ebx,e.stack});out.push_back({s.field_384,s.field_39e,s.field_064,s.field_038,s.selected_lamp,ev});}std::cout<<out.dump()<<'\n';}
