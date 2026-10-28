#pragma once
#include "rules/mean_return_pass.h"
#include "dmd/mean_material5_display.h"
namespace slam {
// Actual41be8d..41beca +405f98/40f754. Raw038 is the request result, not a pointer.
inline bool mean_return_pass_dispatch(MeanBallResetState &s,
    MeanMaterial5Display &display, const MeanReturnPassEvent &event,
    std::array<std::int32_t,5> &secondary_timers) {
  if (!event.announcement) return false;
  display.field_050=event.score; // Written before admission, including rejection.
  display.scheduler.field_7a0=s.table_mode;
  const bool accepted=display.request({5,4,2,0,45,1,0x41163c},event.score);
  for(unsigned i=0;i<4;++i) s.fields[0x038+i]=accepted?255:0;
  if(accepted){
    for(unsigned i=0;i<4;++i) s.fields[0x024+i]=0;
    secondary_timers.fill(0);
  }
  return accepted;
}
} // namespace slam
