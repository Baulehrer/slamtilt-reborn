#include "mean_material5.h"
namespace slam {
MeanMaterial5Event mean_material5_rules(std::int32_t x, std::int32_t y,
                                        MeanMaterial5State &s) {
  MeanMaterial5Event e;
  if (y > 350 * 65536) {
    e.sample = true;
    s.command_300 = {6, 2, 0, 48};
    if (s.mode < 4 && s.field_37a >= 0) {
      s.field_37a = -1;
      e.score_add = s.field_054;
      e.stop84 = true;
      e.callback = 0x41062c;
    }
    return e;
  }
  const unsigned index = x <= 80 * 65536    ? 0
                         : x <= 160 * 65536 ? 1
                         : y <= 270 * 65536 ? 2
                                            : 3;
  if (s.fields_ee1c[index] > 0)
    return e;
  s.fields_ee1c[index] = 5;
  e.sample = true;
  s.commands_26c[index] = {5, 2, 0, 35};
  if (s.field_1dc[index])
    return e;
  s.field_1dc[index] = 1;
  bool all = true;
  for (auto flag : s.field_1dc)
    all = all && flag != 0;
  if (!all) {
    e.callback = 0x413a2c;
    return e;
  }
  e.group = true;
  e.callback = 0x413958;
  s.field_1dc.fill(0);
  for (unsigned i = 0; i < 4; ++i)
    s.commands_26c[i] = {6, 2, std::uint8_t(i + 1), 50};
  s.field_1da = 1;
  s.command_268[0] = 1;
  return e;
}
} // namespace slam
