#include "mean_mode5_clock.h"
namespace slam {
bool mean_mode5_clock(MeanMode5LeftState &mode, MeanCaptureTickState &state,
                      unsigned ball_count) {
  if (state.table_mode != 6 &&
      (state.table_mode != 5 || mode.field_43f1e6 < 0 ||
       (mode.field_43f1e6 > 2 && mode.field_43f1e6 != 4)))
    return false;
  if (state.table_mode == 6 || mode.field_43f1e6 == 4) {
    mode.field_engine_40 = 5;
    // 414fe9..415041: bounded original single-ball stage1/3 clock.
    if (mode.field_43f37e == 2)
      return false; // Caller must stop before unsupported ball-spawn work.
    if (mode.field_43f37e <= 0 || ball_count > 1)
      return false;
    mode.field_43f376 = static_cast<std::int16_t>(
        static_cast<std::uint16_t>(mode.field_43f376) - 1);
    if (mode.field_43f376 >= 0)
      return false;
    const bool reset = mean_mode_reset(mode, state.table_mode);
    if (reset) {
      for (unsigned i : {0u, 4u, 12u, 16u, 20u})
        mode.field_43f23c[i] = 2;
      mode.field_engine_40 = 5;
    }
    return reset;
  }
  const std::int32_t timer = mode.field_43f39c;
  mode.field_engine_40 = 4;
  if (mode.field_43f1e6 == 0)
    mode.field_43f05c =
        timer < 1000
            ? 75000000u
            : static_cast<std::uint32_t>(65000000 - (timer - 1000) * 6000);
  mode.field_43f39c =
      static_cast<std::int16_t>(static_cast<std::uint16_t>(timer) - 1);
  return mode.field_43f39c < 0 && mean_mode_reset(mode, state.table_mode);
}
} // namespace slam
