#include "mean_lamp_mode.h"
namespace slam {
void mean_lamp_mode_reset(const MeanLampModeInput &s, MeanLampCommands &d) {
  auto cmd = [&](int i, int v) {
    if (i >= 0 && i < 63)
      d[i][0] = v;
  };
  auto blink = [&](int i, int p, int t) {
    if (i >= 0 && i < 63)
      d[i] = {4, static_cast<std::uint8_t>(p), static_cast<std::uint8_t>(t), 0};
  };
  for (int i = 0; i < 4; ++i) {
    if (s.field_398 <= 0)
      cmd(i, s.field_1d4[i] ? 1 : 2);
    else {
      blink(i, 4, 1 + 2 * i);
      if (s.field_060[i])
        cmd(i, 2);
    }
  }
  for (int i = 4; i <= 6; ++i)
    cmd(i, 2);
  blink(4 + s.field_3ba, 6, 1);
  for (int i = 7; i <= 9; ++i)
    cmd(i, 2);
  blink(7 + s.field_3bc, 6, 6);
  cmd(10, 2);
  cmd(11, 2);
  if (s.field_392) {
    blink(10, 6, 5);
    blink(11, 6, 3);
  }
  cmd(12, 2);
  cmd(19, 2);
  if (s.field_3a2) {
    blink(12, 6, 5);
    blink(19, 6, 3);
  }
  for (int i = 13; i <= 18; ++i)
    cmd(i, 2);
  cmd(20, 2);
  if (s.field_3b0 >= 0)
    blink(20, 4, 1);
  cmd(21, 2);
  if (s.field_374 >= 0)
    blink(21, 3, 1);
  cmd(22, 2);
  if (s.field_3ae >= 50)
    blink(22, s.field_3ae >= 150 ? 1 : 3, 1);
  cmd(23, s.service10_field10 > 0 ? 1 : 2);
  cmd(24, s.field_1da ? 1 : 2);
  cmd(29, 2);
  if (s.field_394)
    blink(29, 6, 1);
  for (int i = 0; i < 3; ++i)
    cmd(30 + i, s.field_1e8[i] ? 1 : 2);
  for (int i = 0; i < 5; ++i)
    cmd(33 + i, s.field_1ec[i] ? 1 : 2);
  cmd(38, 2);
  if (s.field_38a > 0)
    blink(38, 6, 1);
  for (int i = 39; i <= 43; ++i)
    cmd(i, 2);
  for (int i = 1; i <= s.field_1f2 && i < 63 - 38; ++i)
    cmd(38 + i, 1);
  cmd(44, 2);
  if (s.field_1f2 >= 5)
    blink(44, 6, 4);
  for (int i = 0; i < 5; ++i)
    cmd(45 + i, s.field_1e0[i] ? 1 : 2);
  blink(45 + s.field_1e6, s.field_384 ? 2 : 6, 1);
  cmd(50, 2);
  if (s.table_mode <= 4)
    blink(50, 6, 4);
  for (int i = 51; i <= 56; ++i)
    cmd(i, 2);
  for (int i = 1; i <= s.field_204 && i < 63 - 50; ++i)
    cmd(50 + i, 1);
  blink(51 + s.field_204, 6, 1);
  cmd(57, 2);
  cmd(58, 2);
  cmd(59, 2);
  if (s.field_1fa)
    blink(59, 6, 1);
  if (s.field_202)
    blink(58, 6, 5);
  if (s.field_200)
    blink(57, 6, 3);
  cmd(60, 2);
  cmd(61, 2);
  if (s.field_1fc > 0 && s.field_1fc + 59 >= 0 && s.field_1fc + 59 < 63)
    d[59 + s.field_1fc] = {4, 5, 0, 0};
  for (int i = 0; i < 4; ++i)
    cmd(25 + i, s.field_1dc[i] ? 1 : 2);
  cmd(62, 2);
  if (s.field_37a >= 0)
    blink(62, 6, 1);
}
} // namespace slam
