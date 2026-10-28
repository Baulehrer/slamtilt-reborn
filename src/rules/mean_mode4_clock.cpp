#include "mean_mode4_clock.h"
#include <cstring>
namespace slam {
MeanMode4ClockEvents mean_mode4_clock(MeanBallResetState &s,
                                      std::int32_t &engine40,
                                      std::uint32_t handle) {
  MeanMode4ClockEvents e;
  auto word = [&](unsigned o) {
    return std::uint16_t(s.fields[o] | (s.fields[o + 1] << 8));
  };
  auto set = [&](unsigned o, std::uint16_t v) {
    s.fields[o] = v;
    s.fields[o + 1] = v >> 8;
  };
  auto put = [&](unsigned o, std::uint32_t v) {
    std::memcpy(s.fields.data() + o, &v, 4);
  };
  if (s.table_mode != 4)
    return e;
  if (word(0x3a6) == 0) {
    if (word(0x39e) == 15) {
      const auto next = std::uint16_t(word(0x396) + 1);
      set(0x396, next);
      if (static_cast<std::int16_t>(next) < 350)
        return e;
      s.table_mode = 2;
      e.exit_to_mode2 = true;
      e.callback = 0x4126ec;
      if (static_cast<std::int16_t>(word(0x37a)) < 0)
        e.stop80 = true;
      else
        e.bank_order62 = true;
      put(0x038, handle);
      if (handle) {
        put(0x024, 0);
        e.clear_slots = true;
      }
    } else if (word(0x39e) == 3)
      set(0x3a8, std::uint16_t(word(0x3a8) + 1));
  } else if (word(0x3a6) == 1) {
    engine40 = 6;
    const auto aa = static_cast<std::int16_t>(word(0x3aa));
    if (aa < 0 || aa >= 2)
      return e;
    const auto timer = static_cast<std::int16_t>(word(0x3a0));
    if (timer < 0)
      return e;
    const auto next = std::uint16_t(timer - 1);
    set(0x3a0, next);
    if (static_cast<std::int16_t>(next) < 0)
      set(0x3aa, 2);
    else if (next == 18) {
      s.field_438a40 = 0;
      set(0x3aa, 1);
    }
  }
  return e;
}
} // namespace slam
