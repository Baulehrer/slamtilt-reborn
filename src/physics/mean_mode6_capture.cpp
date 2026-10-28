#include "mean_mode6_capture.h"
namespace slam {
bool mean_mode6_capture_tick(MeanObject &b, MeanMode5LeftState &m,
                             MeanUpperCaptureState &u, unsigned count,
                             MeanMode6CaptureEvent &e) {
  e = {};
  auto active = [&]() {
    return unsigned(m.field_43f38e >= 0) + unsigned(m.field_43f368 >= 0) +
           unsigned(m.field_43f36c >= 0);
  };
  const auto cb = b.u16(0x5a);
  if (b.u16(0x58) == 3) {
    if (cb != 1 || u.field_43f36a != -1 || u.field_43f364 != 0)
      return false;
    u.field_43f36a = -2;
    if (active() < count) {
      b.put16(0x58, 6);
      m.field_43f38e = 2000;
    }
    return true;
  }
  if (b.u16(0x58) != 6 || (cb != 1 && cb != 2 && cb != 4))
    return false;
  auto &timer = cb == 1   ? m.field_43f38e
                : cb == 2 ? m.field_43f368
                          : m.field_43f36c;
  if (timer < 0) {
    timer = -1;
    e.transfer = e.lamp_reset = true;
    return true;
  }
  timer = static_cast<std::int16_t>(static_cast<std::uint16_t>(timer) - 1);
  if (active() >= count) {
    timer = -1;
    e.transfer = e.lamp_reset = true;
  }
  return true;
}
} // namespace slam
