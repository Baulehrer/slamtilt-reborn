#pragma once
#include <cstdint>
namespace slam {
// Raw shared-engine fields, original405f98 /4071e8. No suspended queue.
struct MeanDisplayScheduler {
  std::int32_t field_780 = 0, field_784 = 0, field_788 = -1, field_78c = 0;
  std::uint32_t field_790 = 0;
  std::int32_t field_7a0 = 2, field_7b0 = 0, field_7b4 = 0, field_81c = 0;
  std::int32_t field_297a8 = 0, field_297ac = 0, field_297b8 = 0,
               field_297bc = 0;
  std::uint8_t field_297cc = 0;
};
struct MeanDisplayRequest {
  std::int32_t eax = 0, edx = 0, ecx = 0, ebx = 0, stack_0 = 0, stack_1 = 0;
  std::uint32_t callback = 0;
};
inline std::int32_t mean_display_request(MeanDisplayScheduler &s,
                                         const MeanDisplayRequest &r) {
  if (s.field_7a0 < 2 || s.field_7a0 == 3 ||
      (s.field_780 != 0 && r.eax <= s.field_788) || r.eax <= s.field_7b0)
    return 0;
  const auto old = s.field_780;
  s.field_788 = r.edx;
  s.field_78c = r.ebx;
  s.field_784 = r.ecx;
  s.field_790 = r.callback;
  s.field_780 = 4;
  if (r.stack_0 >= 0) {
    s.field_297ac = r.stack_0;
    s.field_297a8 = r.stack_1;
    s.field_297bc = 0;
    s.field_297b8 = -1;
  } else if (old == 4 && (s.field_297cc & 2)) {
    s.field_297b8 = 0;
    s.field_297bc = -1;
  }
  return -1;
}
enum class MeanDisplayDispatch { None, Alternate, Engine28, Callback, Idle };
inline MeanDisplayDispatch
mean_display_scheduler_begin(MeanDisplayScheduler &s) {
  if (s.field_81c == 2)
    return MeanDisplayDispatch::Alternate;
  if (s.field_81c != 0)
    return MeanDisplayDispatch::None;
  if (s.field_7b4 != 0)
    return MeanDisplayDispatch::Engine28;
  if (s.field_7a0 == 0)
    return MeanDisplayDispatch::None;
  if (s.field_780 == 4) {
    if (s.field_784 == 0) {
      s.field_790 = 0;
      s.field_788 = -1;
      s.field_780 = 3;
    } else if (s.field_790)
      return MeanDisplayDispatch::Callback;
  }
  return s.field_780 == 0 ? MeanDisplayDispatch::Idle
                          : MeanDisplayDispatch::None;
}
// Called after Callback/Idle (or None on the ordinary scheduler path).
inline bool mean_display_scheduler_finish(MeanDisplayScheduler &s) {
  if (s.field_81c != 0 || s.field_7b4 != 0 || s.field_7a0 == 0)
    return false;
  if (s.field_780 == 3)
    s.field_780 = 0;
  return s.field_7a0 == 3; // Original4072cc restart requested.
}
} // namespace slam

namespace slam {
// Original415bf7: minigames take ownership; shared counter is retained.
inline void mean_display_minigame_enter(MeanDisplayScheduler &s) {
  s.field_780=0; s.field_784=0; s.field_788=-1; s.field_790=0; s.field_7b4=1;
}
// Original4080bc/4080d4: bonus suppresses ordinary callbacks without clearing them.
inline void mean_display_bonus_enter(MeanDisplayScheduler &s) {
  s.field_7a0=3; s.field_780=6;
}
// Original407870/40789b/4078a0, after external table reset adapters.
inline void mean_display_bonus_return(MeanDisplayScheduler &s) {
  s.field_780=3; s.field_7b4=0; s.field_7a0=1;
}
} // namespace slam
