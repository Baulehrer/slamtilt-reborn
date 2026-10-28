#include "physics/mean_mode4_right_entry.h"
#include "rules/mean_mode4_input.h"
#include "rules/mean_mode4_clock.h"
#include "rules/mean_mode4_events.h"
#include "dmd/mean_mode4_phase1.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc,char **argv) {
 using nlohmann::json; json cases,out=json::array(); std::cin>>cases;
 auto assets=slam::load_mean_mode4_phase1(argv[1]);
 for(auto &c:cases) {
  slam::MeanBallResetState s; s.fields=c["fields"].get<decltype(s.fields)>();
  s.table_mode=2;s.field_438a40=77;std::int32_t engine40=13;
  slam::WindowsDmdPixels pixels{};json rows=json::array();
  for(auto &op:c["operations"]) {
   std::uint32_t cb=0,score=0;bool exit=false,clear=false;
   std::string k=op["kind"];
   if(k=="entry") {auto e=slam::mean_mode4_right_ramp(s,3,1,50<<16);cb=e.callback;}
   else if(k=="idle") slam::mean_mode4_phase1(s,assets,pixels);
   else if(k=="clock") {auto e=slam::mean_mode4_clock(s,engine40,0);cb=e.callback;exit=e.exit_to_mode2;clear=e.clear_slots;}
   else if(k=="right") {auto e=slam::mean_mode4_input(s,true,0x210000,0);cb=e.callback;exit=e.exit_to_mode2;clear=e.clear_slots;}
   else {auto e=slam::mean_mode4_event(s,op["branch"],0);cb=e.callback;score=e.score_add;exit=e.exit_to_mode2;clear=e.clear_slots;}
   rows.push_back({{"fields",s.fields},{"a40",s.field_438a40},{"mode",s.table_mode},{"engine40",engine40},{"callback",cb},{"score",score},{"exit",exit},{"clear_slots",clear}});
  }
  out.push_back(rows);
 }
 std::cout<<out.dump();
}
