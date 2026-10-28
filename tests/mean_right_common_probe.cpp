#include "rules/mean_right_progress.h"
#include "rules/mean_shared_reward.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(){nlohmann::json in;std::cin>>in;auto out=nlohmann::json::array();for(auto &c:in){slam::MeanBallResetState s;s.fields=c["fields"].get<decltype(s.fields)>();s.table_mode=c["mode"];slam::MeanSharedRewardEvents common;auto e=slam::mean_right_progress(s,[&](slam::MeanBallResetState &state){common=slam::mean_shared_reward(state,4,c["returned"]);});auto scores=common.scores;if(static_cast<std::int16_t>(c["fields"][0x3b0].get<unsigned>()|(c["fields"][0x3b1].get<unsigned>()<<8))>=0)scores.insert(scores.begin(),e.score);out.push_back({{"fields",s.fields},{"mode",s.table_mode},{"scores",scores},{"reset",e.reset_right_gate},{"services",{common.service_419da4,common.service_419f6c,common.service_4194e4,common.service_4169e4}}});}std::cout<<out.dump();}
