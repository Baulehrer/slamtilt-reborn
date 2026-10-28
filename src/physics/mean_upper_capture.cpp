#include "mean_upper_capture.h"
#include "mean_upper_release.h"
namespace slam {
bool mean_upper_capture_tick(const MeanObject &ball,
                             MeanUpperCaptureState &state,
                             MeanUpperCaptureEvent &event) {
  event = {};
  if (ball.u16(0x58) != 3 || ball.u16(0x5a) != 1 || state.table_mode < 1 ||
      (state.table_mode > 4 && state.table_mode != 6 &&
       !(state.table_mode == 5 && state.field_43f1e6 >= 0 &&
         (state.field_43f1e6 <= 2 || state.field_43f1e6 == 4))))
    return false;
  auto &timer = state.field_43f36a;
  if (timer < -1) {
    auto &slot = state.field_438b5c;
    if (slot[1] != 0) {
      --slot[1];
      if (slot[1] > 0) {
        if (slot[2] != 0)
          --slot[2];
        return true;
      }
    }
    if (slot[2] != 0 && --slot[2] > 0)
      return true;
    slot[0] = 10;
    if (state.table_mode == 5 || state.table_mode == 6) {
      event.transfer_requested = true;
      event.mode4_transfer_requested =
          (state.table_mode == 6 || state.field_43f1e6 == 4) &&
          state.field_43f37e != 3;
    } else
      event.release_requested = true;
    return true;
  }
  if (timer <= 0 && state.field_43f364 != 0)
    return true;
  --timer;
  if (timer == -1) {
    event.score_request = 500000;
    event.field_player_08_add = 1000000;
    if (state.field_43f200 != 0) {
      state.field_43f200 = 0;
      state.field_43f378 = -1;
      state.field_438b44[0] = 0;
      state.field_438b44[2] = 1;
      event.reward_request = 1;
    } else if (state.field_43f202 != 0) {
      state.field_43f202 = 0;
      state.field_43f1fc = 1;
      event.reward_request = 2;
    } else if (state.field_43f1fa != 0) {
      state.field_43f1fa = static_cast<std::int16_t>(state.field_43f1fa - 1);
      event.field_player_10_add = 1;
      event.reward_request = 3;
    }
    if (event.reward_request != 0)
      state.field_43f364 =
          -1; // Cleared by original human gate helper when its caller permits.

  } else if (timer == -2) {
    if (state.table_mode >= 4)
      return true; // 415dc7 mode!=6 returns; no extra slot delay.
    if (state.field_43f1f2 >= 5) {
      state.field_43f1f2 = 0;
      state.table_mode = 6;
      state.field_438b5c[2] = 600;
      event.capture_delay_request = true;
      event.capture_delay = 600;
      event.mode6_start_requested = true;
      return true;
    }
    if (state.field_43f394 != 0) {
      if (state.field_43f1e6 < 0 || state.field_43f1e6 > 4)
        return false;
      state.field_43f394 = 0;
      ++state.field_43f1f2;
      if (state.field_43f1e6 == 3) {
        // 415b90..415c85 leaves table mode and upper slot untouched.
        // Shared+44 starts a separate mini-game dispatcher, not mode5.
        event.selected3_start_requested = true;
      } else {
        state.table_mode = 5;
        state.field_438b5c[2] = 400;
        event.capture_delay_request = true;
        event.capture_delay = 400;
      }
    } else {
      state.field_43f394 = -1;
      state.field_438b5c[2] = 300;
      event.capture_delay_request = true;
      event.capture_delay = 300;
      event.field_024_minus_one_after_delay = true;
    } // Actual40f754 stackargument, not DMD timing.
    event.rule_service_request = !event.selected3_start_requested;
  }
  return true;
}
bool mean_upper_capture_tilt_tick(MeanObject &ball, MeanUpperCaptureState &state,
                                  MeanUpperCaptureEvent &event,
                                  std::uint32_t dat_base, std::uint32_t random) {
  event = {};
  if (ball.u16(0x58) != 3 || ball.u16(0x5a) != 1 ||
      state.table_mode < 1 || state.table_mode > 6)
    return false;
  const auto entry = ball;
  mean_upper_release(ball, dat_base, random);
  const auto ok = mean_upper_capture_tick(entry, state, event);
  event.early_release_count = 1;
  return ok;
}
} // namespace slam
