#include "mean_capture_bundle.h"
namespace slam {
void mean_left_capture_slot_tick(MeanLeftCaptureState &state) {
  if (state.field_438b68 >= 0)
    --state.field_438b68;
}
bool mean_left_capture(MeanObject &ball, MeanLeftCaptureState &state,
                       std::int32_t field_services_1c, bool blocked,
                       bool &captured) {
  captured = false;
  if (ball.i32(0) > 60 * 65536 || ball.i32(4) < 170 * 65536)
    return false;
  if (field_services_1c != 0 || state.field_438b68 >= 0 || blocked)
    return true;
  ball.put32(0, 26 * 65536);
  ball.put32(4, 279 * 65536);
  ball.put16(0x5a, 2);
  ball.put16(0x58, 3);
  state.field_438b6c = 100;
  state.field_43f380 = 50;
  captured = true;
  return true;
}
} // namespace slam
