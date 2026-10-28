#include "mean_upper_entry.h"
namespace slam {
bool mean_upper_entry(MeanObject &ball, MeanUpperCaptureState &state,
                      std::int32_t field_services_1c, bool blocked) {
  if (field_services_1c != 0 || ball.i32(0) > 60 * 65536 ||
      ball.i32(4) >= 170 * 65536 || state.field_438b5c[0] >= 0 || blocked)
    return false;
  ball.put32(0, 14 * 65536);
  ball.put32(4, 14 * 65536);
  ball.put16(0x5a, 1);
  ball.put16(0x58, 3);
  state.field_438b5c[1] = 100;
  state.field_43f36a = 50;
  return true;
}
} // namespace slam
