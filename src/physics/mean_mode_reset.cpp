#include "mean_mode_reset.h"
namespace slam {
bool mean_mode_reset(MeanModeResetState &state, std::int32_t &table_mode) {
  if (state.field_43f1e6 < 0 || state.field_43f1e6 >= 5)
    return false;
  table_mode = 2;
  if (state.field_43f384 == 0)
    for (int step = 1; step <= 5; ++step) {
      const int candidate = (state.field_43f1e6 + step) % 5;
      if (!state.field_43f1e0[candidate]) {
        state.field_43f1e6 = static_cast<std::int16_t>(candidate);
        break;
      }
    }
  state.field_43f366 = -1;
  return true;
}
} // namespace slam
