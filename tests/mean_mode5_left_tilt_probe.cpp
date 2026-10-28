#include "physics/mean_mode5_left.h"
#include <iostream>
#include <nlohmann/json.hpp>
using namespace slam;
int main(){nlohmann::json cases;std::cin>>cases;auto out=nlohmann::json::array();for(auto&c:cases){MeanObject b;b.bytes=c["ball"].get<decltype(b.bytes)>();MeanCaptureTickState s;s.table_mode=5;s.field_43f380=c["timer"];s.field_438b68=c["slot2"].get<decltype(s.field_438b68)>();s.field_438b74=c["slot3"].get<decltype(s.field_438b74)>();MeanMode5LeftState m;m.field_43f05c=10000000;MeanCaptureTickEvent e;bool ok=mean_mode5_left(b,s,m,0x1100000,e,c["tilt"],c.value("accepted",true));out.push_back({{"ball",b.bytes},{"timer",s.field_43f380},{"slot2",s.field_438b68},{"slot3",s.field_438b74},{"slot50",s.field_438b50},{"field050",m.field_43f050},{"field058",m.field_43f058},{"field3b4",m.field_43f3b4},{"score",e.score_request},{"samples",e.services_1c_samples},{"ok",ok}});}std::cout<<out.dump();}
