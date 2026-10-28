#include "mean_mode4_events.h"
#include <cstring>
namespace slam {
MeanMode4Events mean_mode4_event(MeanBallResetState &s, std::uint32_t branch,
                                 std::uint32_t handle) {
  MeanMode4Events e;
  auto &f = s.fields;
  auto word = [&](unsigned o) { return std::uint16_t(f[o] | (f[o + 1] << 8)); };
  auto set = [&](unsigned o, std::uint16_t v) {
    f[o] = v;
    f[o + 1] = v >> 8;
  };
  auto dword = [&](unsigned o) {
    std::uint32_t v;
    std::memcpy(&v, f.data() + o, 4);
    return v;
  };
  auto put = [&](unsigned o, std::uint32_t v) {
    std::memcpy(f.data() + o, &v, 4);
  };
  if (s.table_mode != 4 || word(0x3a6) != 1)
    return e;
  if (branch == 0x41bf0c) {
    if (word(0x3aa) != 3)
      return e;
    const auto next = std::uint16_t(word(0x3b2) + 1);
    set(0x3b2, next);
    e.score_add = next == 1 ? 25000000 : 10000000;
    put(0x020, e.score_add);
    put(0x03c, 50);
    put(0x058, dword(0x058) + e.score_add);
  } else if (branch == 0x41c0df || branch == 0x41c39e) {
    s.field_438a40 = 0;
    set(0x366, 0xffff);
    s.table_mode = 2;
    e.exit_to_mode2 = true;
    if (branch == 0x41c0df) {
      e.score_add = 25000000;
      put(0x058, dword(0x058) + e.score_add);
      e.callback = 0x4102c0;
      put(0x038, handle);
      if (handle) {
        put(0x024, 0);
        e.clear_slots = true;
      }
    }
  }
  return e;
}
} // namespace slam
