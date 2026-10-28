#include "mean_mode_lock.h"
#include <stdexcept>
namespace slam {
void MeanModeLock::press(std::int32_t admission,std::int32_t indexed) {
  requests.clear();
  if(service_1c)return;
  if(engine_30==4 && !field_3a6) {
    if(field_39e!=3)return;
    field_39e|=4;
    const auto divisor=std::int32_t(std::uint32_t(field_030)+2u);
    if(!divisor)throw std::runtime_error("Original Mode Lock IDIV zero divisor");
    field_064=std::int32_t(std::uint32_t(0x30000/divisor-0x18000)+std::uint32_t(indexed));
    requests.push_back({0x34,8,7,2,0,{0x13,1,0x41265c}});
  } else {
    if(engine_30>=4 && engine_30!=4)return;
    if(engine_30<4 && engine_44)return;
    if(engine_30<=1 || field_384)return;
    selected_lamp={4,2,1,0};field_384=0xffff;
    requests.push_back({0x34,7,6,2,0,{0xf,1,0x411908}});
  }
  field_038=admission;
  requests.push_back({0x40f754,1,1,1,1,{1,0}});
}
}
