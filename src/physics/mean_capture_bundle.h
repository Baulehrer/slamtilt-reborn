#pragma once
#include "mean_step.h"
namespace slam {
struct MeanLeftCaptureState {
  // PE initial value0;4198b3..4198cc reduces to-1 on first table tick.
  std::int32_t field_438b68 = 0;
  std::int32_t field_438b6c = 0;
  std::uint16_t field_43f380 = 0;
};
void mean_left_capture_slot_tick(MeanLeftCaptureState &state);
// Exact left switch3 branch41d9e3..41da47, x<=60,y>=170.
// blocked means another ball has58=3/6 AND5a=2 (original41db1c).
// Return false outside bounded region/mode; accepted no-op returns true.
// captured=true requires caller to implement captured-ball state3 tick.
bool mean_left_capture(MeanObject &ball, MeanLeftCaptureState &state,
                       std::int32_t field_services_1c, bool blocked,
                       bool &captured);
} // namespace slam
