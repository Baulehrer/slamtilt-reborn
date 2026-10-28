#include "mean_bonus_display.h"
namespace slam {
void mean_bonus_input_edge(MeanBonusDisplay &s, bool right, bool pressed) {
  const auto bit = right ? 2u : 1u;
  s.field_43e734 = pressed ? s.field_43e734 | bit : s.field_43e734 & ~bit;
}

MeanBonusDisplayEvents mean_bonus_display_step(MeanBonusDisplay &s,
                                               const MeanBonusDisplayInput &i) {
  MeanBonusDisplayEvents e;
  if (s.field_43e734 == 3) {
    s.step = 4;
    if (s.phase == 1) {
      s.phase = 2;
      s.timer = 0;
    }
  }
  if (s.phase > 7) {
    e.finish = true;
    return e;
  }
  switch (s.phase) {
  case 0:
    s.field_43e718 = 0xffffffffu;
    s.bonus_total = 0;
    if (!i.suppressed) {
      e.award = true;
      e.score_argument =
          i.bonus * std::uint32_t(std::int32_t(std::int16_t(i.multiplier)));
      s.bonus_total = e.score_argument;
    }
    e.initialize = true;
    s.phase = 1;
    // Phase0 falls through stage1 in the same original invocation.
    [[fallthrough]];
  case 1:
    e.callback_stage = 1;
    s.phase += i.callback_result;
    break;
  case 2: {
    if (i.suppressed) {
      s.phase = 5;
      s.timer = 0;
      break;
    }
    if (!s.timer)
      s.field_43e718 = 0;
    s.timer += s.step;
    const auto t = std::int32_t(s.timer);
    if (t <= 62)
      break;
    if (i.bonus && i.multiplier != 1) {
      const auto shifted = std::int32_t(s.timer - 62);
      if (shifted <= 62) {
        if (shifted == 1 && s.step == 1)
          s.field_43e718 = 0;
        break;
      }
    }
    s.phase = 4;
    s.timer = 0;
    break;
  }
  case 3: {
    const auto old = s.timer;
    s.timer += s.step;
    if (std::int32_t(old) >= 62) {
      s.phase = 4;
      s.timer = 0;
    } else if (!old && s.step == 1)
      s.field_43e718 = 0;
    break;
  }
  case 4:
    e.callback_stage = 2;
    if (i.callback_result) {
      s.phase = 5;
      s.timer = 0;
    } else
      s.timer += s.step;
    break;
  case 5: {
    const auto old = s.timer;
    s.timer += s.step + 1;
    if (std::int32_t(old) >= 112)
      e.finish = true;
    else if (!old && s.step == 1)
      s.field_43e718 = 0;
    break;
  }
  case 6:
    break;
  case 7: {
    const auto old = s.timer;
    ++s.timer;
    if (std::int32_t(old) >= 112)
      e.rotate_only = true;
    break;
  }
  }
  return e;
}
} // namespace slam
