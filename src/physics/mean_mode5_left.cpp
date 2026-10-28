#include "mean_left_tilt_release.h"
#include "mean_mode5_left.h"
#include "mean_upper_release.h"
namespace slam {
void mean_mode4_transfer(MeanObject &ball, MeanCaptureTickState &capture,
                         MeanMode5LeftState &mode, std::uint32_t base) {
  // Actual416b28, distinct from ordinary417068 transfer.
  mean_set_layer(ball, 1, base);
  ball.put16(0x38, 0xffff);
  ball.put16(0x3a, 0xffff);
  ball.put16(0x22, 0);
  ball.put16(0x2a, 0);
  ball.put16(0x5c, 18);
  ball.put16(0x1c, 10);
  ball.put32(0x60, 0x40000);
  ball.put32(0, 13 * 65536);
  ball.put32(4, 306 * 65536);
  ball.put32(8, 13 * 65536);
  ball.put32(12, 306 * 65536);
  ball.put16(0x5a, 5);
  ball.put16(0x58, 3);
  ball.put16(0x28, 0);
  ball.put32(0x14, 0);
  ball.put32(0x18, 0);
  capture.field_438b50 = {0, 0, 5};
  mode.field_438b90 = 100;
  if (mode.field_43f37e == 1) {
    mode.field_43f37e = 2;
    mode.field_438b90 = 200;
    mode.field_43f3ae = 750;
    mode.field_43f260 = {4, 3, 1, 0};
  }
}
void mean_mode6_begin(MeanMode5LeftState &mode) {
  mode.field_43f382 = -1;
  mode.field_43f37e = 1;
  mode.field_43f376 = 800;
  mode.field_43f38e = mode.field_43f368 = mode.field_43f36c = -1;
  mode.field_43f058 = 0;
  mode.field_43f35e = 3;
  mode.field_43f36e = 7;
  auto &d = mode.field_43f23c;
  d[0] = 2;
  d[4] = 4;
  d[5] = 6;
  d[6] = 3;
  d[7] = 0;
  d[8] = 4;
  d[9] = 6;
  d[10] = 3;
  d[11] = 0;
  d[12] = 4;
  d[13] = 6;
  d[14] = 7;
  d[15] = 0;
  d[16] = 4;
  d[17] = 6;
  d[18] = 9;
  d[19] = 0;
  d[20] = 2;
}
bool mean_mode5_begin(MeanMode5LeftState &mode, std::uint32_t field_engine_38) {
  const auto selected = mode.field_43f1e6;
  if (selected < 0 || (selected > 2 && selected != 4))
    return false;
  mode.field_43f384 = 0;
  mode.field_43f1e0[selected] = 1;
  bool all = true;
  for (auto value : mode.field_43f1e0)
    all = all && value != 0;
  if (all)
    mode.field_43f1e0.fill(0);
  mode.field_43f058 = 0;
  if (selected == 0) {
    mode.field_43f3b4 = 0;
    mode.field_43f39c = 8400;
    mode.field_43f05c = 10000000;
  } else if (selected == 1) {
    mode.field_43f044.fill(1);
    mode.field_43f372 = 0;
    mode.field_43f39c = 9400;
  } else if (selected == 4) {
    mode.field_43f376 = 800;
    mode.field_43f36e = 3;
    mode.field_43f37e = 1;
    mode.field_43f388 = 2;
    mode.field_43f23c = {4, 6, 1, 0, 4, 6, 3, 0, 2, 0, 0,  0,
                         4, 6, 7, 0, 4, 6, 9, 0, 4, 6, 11, 0};
  } else {
    // 4169e4 first lookup row selected from original initial38c=0.
    static constexpr std::int16_t row[] = {4, 5, 4};
    mode.field_43f38c = row[(field_engine_38 >> 4) % 3];
    mode.field_43f386 = 0;
    mode.field_43f39c = 6400;
  }
  return true;
}

bool mean_mode5_left(MeanObject &ball, MeanCaptureTickState &state,
                     MeanMode5LeftState &mode, std::uint32_t base,
                     MeanCaptureTickEvent &event, bool services_1c, bool display_accepted) {
  event = {};
  if (ball.u16(0x58) != 3 || ball.u16(0x5a) != 2 || state.table_mode != 5)
    return false;
  if (services_1c) {
    mean_left_tilt_release(ball, base);
    ++event.services_1c_samples;
  }
  auto &timer = state.field_43f380;
  if (timer >= -2) {
    timer = static_cast<std::int16_t>(static_cast<std::uint16_t>(timer) - 1);
    if (timer == -1) {
      event.score_request = 500000;
      event.field_player_08_add = 1000000;
    } else if (timer == -2) {
      event.rule_service_request = true;
      if (mode.field_43f1e6 == 0) {
        if(display_accepted) state.field_438b68[2]=0;
        event.score_request = mode.field_43f05c;
        mode.field_43f050 = mode.field_43f05c;
        mode.field_43f058 += mode.field_43f05c;
        if (mode.field_43f05c == 75000000) {
          if (!mean_mode_reset(mode, state.table_mode))
            return false;
        } else {
          mode.field_43f3b4 = static_cast<std::int16_t>(
              static_cast<std::uint16_t>(mode.field_43f3b4) + 1);
          if (mode.field_43f3b4 >= 3 &&
              !mean_mode_reset(mode, state.table_mode))
            return false;
        }
      }
    }
    return true;
  }
  auto &slot = state.field_438b68;
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
  if (state.field_438b74[0] < 0) {
    mean_upper_transfer(ball, base);
    if (services_1c) ball.put16(0x58, 3);
    state.field_438b50 = {0, 0, 5};
    state.field_438b74[1] = 100;
  }
  return true;
}
} // namespace slam
