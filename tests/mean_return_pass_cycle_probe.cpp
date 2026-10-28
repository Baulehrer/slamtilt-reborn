#include "rules/mean_return_pass_dispatch.h"
#include <nlohmann/json.hpp>
#include <iostream>
using nlohmann::json;
int main(int argc,char **argv){
 if(argc!=3)return 2;
 auto assets=slam::load_mean_material5_display(argv[1]);auto font=slam::load_mean_score_font(argv[2]);
 json cases;std::cin>>cases;json output=json::array();
 for(auto &c:cases){
  slam::MeanBallResetState raw;raw.fields.fill(0);raw.table_mode=2;
  raw.fields[0x374]=raw.fields[0x375]=255;
  raw.fields[0x024]=77;
  slam::MeanMaterial5Display display;
  for(unsigned i=0;i<display.pixels.size();++i)display.pixels[i]=display.restore_pixels[i]=i%4;
  std::array<std::int32_t,5> timers{11,22,33,44,55};std::uint64_t score=0;
  json rows=json::array();
  for(auto &op:c){
   if(op.contains("block"))display.request({8,7,2,0,-1,-1,0x412d24},0);
   else if(op.contains("hit")){
    const auto event=slam::mean_return_pass_hit(raw);score+=event.score;
    slam::mean_return_pass_dispatch(raw,display,event,timers);
   }else{
    slam::mean_return_pass_tick(raw);
    slam::mean_material5_display_scheduled_step(display,assets,font,{});
   }
   json fields=json::array();
   for(unsigned i: {0x024u,0x038u,0x050u,0x1e6u,0x25cu,0x2bcu,0x2c0u,0x2c4u,0x2c8u,0x2ccu,0x374u,0x37au,0x37cu}){
    const unsigned n=(i==0x1e6 || i>=0x374)?2:4;
    for(unsigned j=0;j<n;++j)fields.push_back(raw.fields[i+j]);
   }
   std::uint64_t hash=14695981039346656037ull;for(auto p:display.pixels)hash=(hash^p)*1099511628211ull;
   auto &s=display.scheduler;
   rows.push_back({{"fields",fields},{"timers",timers},{"score",score},{"display",{s.field_780,s.field_784,s.field_788,s.field_78c,s.field_790}},{"fnv",std::to_string(hash)}});
  }
  output.push_back(rows);
 }
 std::cout<<output.dump()<<'\n';
}
