#include "mean_turn_entry.h"
namespace slam {
bool mean_turn_playfield_entry(MeanTurnEntry &s) {
  if (s.mode != 1)
    return false;
  s.mode = 2;
  s.field_43f3ae = 400;
  s.field_43f35a = 200;
  s.command_43f258 = {4, 3, 1, 0};
  s.command_43f260 = {4, 5, 1, 0};
  return true;
}
bool mean_turn_drain_intercept(MeanObject &b, MeanTurnEntry &s, unsigned count,
                               std::int32_t services) {
  b.put16(0x58, 4);
  b.put32(0, 0xfff00000);
  b.put32(4, 0x2680000);
  if (services != 0 || s.field_43f3ae < 0)
    return false;
  b.put16(0x58, 0xffff);
  if (count <= 1) {
    s.field_43f3ae = -1;
    s.command_43f260[0] = 2;
  }
  return true;
}
bool mean_turn_save_clock(MeanTurnEntry &s) {
  if (s.field_43f3ae < 0)
    return false;
  --s.field_43f3ae;
  if (s.field_43f3ae == 150)
    s.command_43f260 = {4, 1, 1, 0};
  if (s.field_43f3ae == 50) {
    s.command_43f260[0] = 2;
    return true;
  }
  return false;
}
} // namespace slam
