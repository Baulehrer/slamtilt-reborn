#include "rules/mean_left_progress.h"
#include <nlohmann/json.hpp>
#include <iostream>
int main(){nlohmann::json input;std::cin>>input;auto out=nlohmann::json::array();for(auto& c:input){slam::MeanBallResetState s;s.table_mode=c.at("mode");auto fields=c.at("fields").get<std::vector<unsigned>>();for(unsigned i=0;i<fields.size();++i)s.fields[i]=fields[i];auto e=slam::mean_left_progress(s,c.at("admitted"));out.push_back({{"fields",s.fields},{"callback",e.callback},{"display",e.display_request},{"delay",e.capture_delay_request}});}std::cout<<out;}
