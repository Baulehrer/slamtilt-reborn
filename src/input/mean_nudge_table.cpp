#include "mean_nudge_table.h"
namespace slam {
void MeanNudgeTable::callback(std::int32_t eax, std::int32_t result) {
  requests.clear();
  if (eax == 0) {
    requests.push_back({0x34, 6, 1, 2, 0, {-1, -1, 0x40f93c}});
    field_038 = result;
    requests.push_back({0x40f754, 1, 1, 1, 1, {1, 0}});
  } else {
    // +8c has no explicit register arguments; zeros here are unspecified.
    requests.push_back({0x8c, 0, 0, 0, 0, {}});
    requests.push_back({0x84, 0x34, 1, 0, 0, {}});
    engine_field_14 = 0;
  }
}
} // namespace slam
