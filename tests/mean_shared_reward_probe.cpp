#include "rules/mean_shared_reward.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(){nlohmann::json in;std::cin>>in;auto out=nlohmann::json::array();for(auto &c:in){slam::MeanBallResetState s;s.fields=c["fields"].get<decltype(s.fields)>();s.table_mode=c["mode"];if(c.contains("target_only")){
      bool valid=slam::mean_rally_target(s,c["engine38"],c["directory"].get<std::vector<std::uint32_t>>(),c["targets"].get<std::vector<std::uint32_t>>());
      out.push_back({{"fields",s.fields},{"valid",valid}});continue;
    }
    auto e=slam::mean_shared_reward(s,c["id"],c["returned"]);out.push_back({{"fields",s.fields},{"mode",s.table_mode},{"scores",e.scores},{"callback",e.callback},{"callback_regs",{e.callback_eax,e.callback_edx,e.callback_ecx}},{"args",{e.callback_arg0,e.callback_arg1}},{"control",e.control},{"control_arg1",e.control_arg1},{"services",{e.service_419da4,e.service_419f6c,e.service_4194e4,e.service_4169e4}}});}std::cout<<out.dump();}
