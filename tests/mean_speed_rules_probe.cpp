#include "physics/mean_right_gate.h"
#include "rules/mean_shared_reward.h"
#include "rules/mean_capture_delay.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(){nlohmann::json input;std::cin>>input;auto out=nlohmann::json::array();
 for(const auto&c:input){slam::MeanBallResetState s;s.table_mode=6;s.fields=c.at("fields").get<decltype(s.fields)>();
  if(c.at("kind")=="gate"){slam::MeanRightGateState g{17,19};slam::mean_right_gate(s,g,c.at("count"));out.push_back({{"fields",s.fields},{"b2c",g.field_438b2c},{"b34",g.field_438b34}});}
  else{const auto e=slam::mean_shared_reward(s,c.at("id"),c.at("handle"));auto delays=c.at("delays").get<std::array<std::int32_t,5>>();std::uint32_t v=0;for(unsigned i=0;i<4;++i)v|=std::uint32_t(s.fields[0x24+i])<<(8*i);std::int32_t field=v;
   if(e.control)slam::mean_capture_delay(c.at("handle"),field,delays,{1,1,1,1,1},0);
   for(unsigned i=0;i<4;++i)s.fields[0x24+i]=std::uint32_t(field)>>(8*i);
   out.push_back({{"fields",s.fields},{"delays",delays},{"scores",e.scores},{"callback",e.callback}});}}
 std::cout<<out.dump();}
