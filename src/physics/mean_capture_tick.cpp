#include "mean_capture_tick.h"

namespace slam {
namespace {
bool slot_tick(std::array<std::int32_t, 3> &slot) {
  if (slot[1] != 0) {
    --slot[1];
    if (slot[1] > 0) {
      if (slot[2] != 0)
        --slot[2];
      return false;
    }
  }
  if (slot[2] == 0)
    return true;
  return --slot[2] <= 0;
}
void release(MeanObject &ball, std::uint32_t base) {
  mean_set_layer(ball, 1, base);
  ball.put32(0x40, ball.i32(0x40) + 7);
  ball.put32(0x44, ball.i32(0x44) + 7);
  ball.put32(0x54, base + 0xb3b36);
  ball.put16(0x22, 0);
  ball.put16(0x2a, 0);
  ball.put16(0x5c, 0);
  ball.put16(0x1c, 0);
  ball.put32(0x60, 0xaa1);
  ball.put16(0x28, 40);
  ball.put32(0, 34 * 65536);
  ball.put32(4, 391 * 65536);
  ball.put32(0x14, 0);
  ball.put32(0x18, 0x4000);
  ball.put16(0x58, 2);
}
void release_callback2(MeanObject &ball, std::uint32_t base) {
  // Actual416d08: release occurs before the original dispatch continuation.
  mean_set_layer(ball, 0, base);
  ball.put16(0x22, 0);
  ball.put16(0x2a, 0);
  ball.put16(0x5c, 0);
  ball.put16(0x1c, 40);
  ball.put32(0x60, 0xaa1);
  ball.put32(0, 26 * 65536);
  ball.put32(4, 279 * 65536);
  ball.put32(0x14, 0x2000);
  ball.put32(0x18, 0x4000);
  ball.put16(0x58, 2);
  ball.put16(0x28, 40);
}
} // namespace
bool mean_capture_tick(MeanObject &ball, MeanCaptureTickState &state,
                       std::uint32_t base, MeanCaptureTickEvent &event,
                       bool services_1c) {
  event = {};
  if (ball.u16(0x58) != 3)
    return false;
  if (services_1c && ball.u16(0x5a) == 2) {
    release_callback2(ball, base);
    ++event.services_1c_samples;
  }
  if (ball.u16(0x5a) == 3) {
    if (services_1c) {
      release(ball, base);
      ++event.services_1c_samples;
    }
    if (slot_tick(state.field_438b74)) {
      state.field_438b74[0] = 10;
      release(ball, base);
      if (services_1c)
        ++event.services_1c_samples;
      event.rule_service_request = true;
    }
    return true;
  }
  if (ball.u16(0x5a) != 2 || state.table_mode < 1 || state.table_mode > 3 ||
      state.field_43f392 != 0)
    return false;
  auto &timer = state.field_43f380;
  if (timer >= -1 || (timer == -2 && state.field_43f364 == 0)) {
    timer = static_cast<std::int16_t>(static_cast<std::uint16_t>(timer) - 1);
    if (timer >= 0)
      return true;
    if (timer == -1) {
      event.score_request = 500000;
      event.field_player_08_add = 1000000;
      state.field_43f364 = -1;
      if (state.field_43f204 == 5) {
        state.field_43f204 = 0;
        event.score_request += 25000000;
        state.field_438b68[2] = 740;
        const auto previous = state.field_43f1fe;
        state.field_43f1fe =
            static_cast<std::int16_t>(static_cast<std::uint16_t>(previous) + 1);
        if (state.field_43f1fe >= 3)
          state.field_43f1fe = 0;
        if (previous == 0)
          state.field_43f200 = -1;
        else if (previous == 1)
          state.field_43f202 = -1;
        else if (previous == 2)
          state.field_43f1fa = static_cast<std::int16_t>(
              static_cast<std::uint16_t>(state.field_43f1fa) + 1);
      } else
        ++state.field_43f204;
      event.rule_service_request = true;
    } else if (timer == -2) {
      state.field_43f364 = 0;
      event.rule_service_request = true;
    }
    return true;
  }
  if (timer <= -3 && slot_tick(state.field_438b68)) {
    state.field_438b68[0] = 10;
    if (state.field_438b74[0] >= 0)
      return true;
    mean_set_layer(ball, 1, base);
    ball.put32(0x40, ball.i32(0x40) + 7);
    ball.put32(0x44, ball.i32(0x44) + 7);
    ball.put32(0x54, base + 0xb3b36);
    ball.put16(0x22, 0);
    ball.put16(0x2a, 0);
    ball.put16(0x5c, 19);
    ball.put16(0x1c, 5);
    ball.put32(0x60, 0xaa1);
    ball.put16(0x28, 40);
    ball.put32(0, 34 * 65536);
    ball.put32(4, 391 * 65536);
    ball.put16(0x5a, 3);
    if (services_1c) {
      ball.put16(0x58, 3);
    }
    state.field_438b50 = {0, 0, 5};
    state.field_438b74[1] = 100;
  }
  return true;
}
} // namespace slam
