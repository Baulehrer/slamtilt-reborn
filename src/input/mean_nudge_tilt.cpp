#include "mean_nudge_tilt.h"
#include <cstring>
#include <stdexcept>
namespace slam {
int MeanNudgeTilt::key_event() {
  if (field_43d864 || field_43e7a0 <= 1 || field_43e7a0 == 3)
    return -1;
  auto raw = std::uint32_t(field_43e7d4) + 40u;
  std::memcpy(&field_43e7d4, &raw, 4);
  if (field_43e7d4 > 81) {
    if (count > ball_status.size())
      throw std::out_of_range("Nudge ball status count");
    field_43d864 = 1;
    field_43e7c4 = field_43e7c8 = 0;
    field_4298b8 = field_4298bc = field_4298c0 = -1;
    for (unsigned i = 0; i < count; ++i)
      ball_status[i] = 2;
    return 1;
  }
  return field_43e7d4 > 41 ? 0 : -1;
}
} // namespace slam
