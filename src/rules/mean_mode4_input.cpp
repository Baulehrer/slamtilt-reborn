#include "mean_mode4_input.h"
#include <cstring>
namespace slam {
MeanMode4InputEvents mean_mode4_input(MeanBallResetState &s, bool right,
                                      std::int32_t lookup_value,
                                      std::uint32_t service34_return) {
  MeanMode4InputEvents e;
  auto word = [&](unsigned o) {
    return std::uint16_t(s.fields[o] | (s.fields[o + 1] << 8));
  };
  auto set = [&](unsigned o, std::uint16_t v) {
    s.fields[o] = v;
    s.fields[o + 1] = v >> 8;
  };
  auto dword = [&](unsigned o) {
    std::uint32_t v;
    std::memcpy(&v, s.fields.data() + o, 4);
    return v;
  };
  auto put = [&](unsigned o, std::uint32_t v) {
    std::memcpy(s.fields.data() + o, &v, 4);
  };
  if (s.table_mode != 4)
    return e;
  if (word(0x3a6) == 0) {
    if (word(0x39e) != 3)
      return e;
    const auto divisor = static_cast<std::int32_t>(dword(0x030) + 2u);
    if (!divisor) {
      e.invalid_divisor = true;
      return e;
    }
    s.fields[0x39e] |= 4;
    put(0x064, static_cast<std::uint32_t>(lookup_value) +
                   static_cast<std::uint32_t>(0x30000 / divisor) - 0x18000u);
    put(0x038, service34_return);
    if (service34_return) {
      put(0x024, 0);
      e.clear_slots = true;
    }
    e.callback = 0x41265c;
  } else if (right && word(0x3a6) == 1) {
    const auto v = static_cast<std::int16_t>(word(0x3aa));
    if (v < 0 || v >= 3)
      return e;
    s.field_438a40 = 0;
    if (v == 0) {
      put(0x038, service34_return);
      if (service34_return) {
        put(0x024, 0);
        e.clear_slots = true;
      }
      s.table_mode = 2;
      e.callback = 0x4114cc;
      e.exit_to_mode2 = true;
      // 4194e4/419f6c/416fe0 are caller-owned exit/reset adapters.
    } else {
      set(0x3a0, 0);
      set(0x3aa, 3);
      s.fields[0x248] = 4;
      s.fields[0x249] = 5;
      s.fields[0x24a] = 1;
      s.fields[0x24b] = 0;
    }
  }
  return e;
}
} // namespace slam
