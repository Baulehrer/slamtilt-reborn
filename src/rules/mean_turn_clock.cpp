#include "mean_turn_clock.h"
namespace slam {
void mean_turn_clock(MeanTurnClockState &s) {
  if (s.service_1c != 0)
    return;
  if (s.field_3ae >= 0) {
    --s.field_3ae;
    if (s.field_3ae == 50) {
      s.field_260[0] = 2;
      s.field_af4 = -1;
    }
    if (s.field_3ae == 150)
      s.field_260 = {{4, 1, 1, 0}};
  }
  if (s.field_390 >= 0) {
    --s.field_390;
    if (s.field_390 == 50)
      s.field_268[0] = 2;
  }
  for (auto &v : s.fields_ee1c)
    if (v >= 0)
      --v;
  if (s.field_35a >= 0) {
    --s.field_35a;
    if (s.field_35a < 0) {
      s.field_258[0] = 2;
      if (s.field_3b0 >= 0)
        s.field_258 = {{4, 4, 1, 0}};
    }
  }
}
} // namespace slam
