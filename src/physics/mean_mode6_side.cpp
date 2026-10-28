#include "mean_mode6_side.h"
namespace slam {
namespace {
std::int16_t dec(std::int16_t v) {
  return static_cast<std::int16_t>(static_cast<std::uint16_t>(v) - 1);
}
bool slot(std::array<std::int32_t, 3> &s) {
  if (s[1] != 0) {
    --s[1];
    if (s[1] > 0) {
      if (s[2] != 0)
        --s[2];
      return false;
    }
  }
  if (s[2] == 0)
    return true;
  return --s[2] <= 0;
}
int count(const MeanMode6SideState &s) {
  return (s.field_43f38e >= 0) + (s.field_43f368 >= 0) + (s.field_43f36c >= 0);
}
} // namespace
bool mean_mode6_side_tick(MeanObject &b, MeanMode6SideState &s,
                          MeanMode6SideEvent &e, bool services_1c, std::uint32_t base) {
  e = {};
  if (b.u16(0x58) != 3)
    return false;
  const auto callback = b.u16(0x5a);
  if (services_1c && callback == 2) {
    mean_set_layer(b, 0, base);
    for (auto o : {0x22, 0x2a, 0x5c}) b.put16(o, 0);
    b.put16(0x1c, 40); b.put32(0x60, 0xaa1);
    b.put32(0, 26 * 65536); b.put32(4, 279 * 65536);
    b.put32(0x14, 0x2000); b.put32(0x18, 0x4000);
    b.put16(0x58, 2); b.put16(0x28, 40);
    ++e.services_1c_samples;
  }
  const auto transfer = [&]() {
    if (s.field_438b74[0] < 0 && !s.callback3_occupied &&
        !((b.u16(0x58) == 3 || b.u16(0x58) == 6) && b.u16(0x5a) == 3)) {
      mean_set_layer(b, 1, base);
      b.put32(0x40, b.i32(0x40) + 7);
      b.put32(0x44, b.i32(0x44) + 7);
      b.put32(0x54, base + 0xb3b36);
      for (auto o : {0x22, 0x2a}) b.put16(o, 0);
      b.put16(0x5c, 19); b.put16(0x1c, 5); b.put32(0x60, 0xaa1);
      b.put16(0x28, 40); b.put32(0, 34 * 65536); b.put32(4, 391 * 65536);
      b.put16(0x5a, 3); b.put16(0x58, 3);
      s.field_438b50 = {0, 0, 5}; s.field_438b74[1] = 100;
    }
  };
  if (services_1c && callback == 4) {
    ++e.early_transfer_count;
    transfer();
  }
  if (callback == 2) {
    auto &t = s.field_43f380;
    if (t <= -3) {
      if (slot(s.field_438b68)) {
        s.field_438b68[0] = 10;
        if (services_1c) transfer();
        else e.transfer_requested = true;
      }
      return true;
    }
    if (t == -2 && s.field_43f364 != 0)
      return true;
    t = dec(t);
    if (t >= 0)
      return true;
    if (t == -1) {
      e.score_request = 500000;
      e.field_player_08_add = 1000000;
      return true;
    }
    if (t == -2) {
      if (count(s) - s.active_count < -1) {
        b.put16(0x58, 6);
        s.field_43f368 = 2000;
      }
      s.field_43f364 = 0;
    }
    return true;
  }
  if (callback == 4) {
    auto &t = s.field_43f370;
    if (t < 0) {
      if (slot(s.field_438b80)) {
        s.field_438b80[0] = 10;
        if (services_1c) transfer();
        else e.transfer_requested = true;
      }
      return true;
    }
    t = dec(t);
    if (s.field_438b40 != 0)
      return true;
    --s.field_438b38;
    e.score_request = 500000;
    e.field_player_08_add = 1000000;
    if (count(s) - s.active_count < -1) {
      b.put16(0x58, 6);
      s.field_43f36c = 2000;
    }
    e.lamp_reset_requested = true;
    return true;
  }
  return false;
}
} // namespace slam
