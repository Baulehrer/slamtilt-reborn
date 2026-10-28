#pragma once
#include <cstdint>
namespace slam {
// Bounded original410a34 reward animation and4071e8 idle transition.
// No queue, interruption, rendering or unrelated DMD semantics are implied.
struct MeanRewardDisplay {
  std::int32_t state = 4, active = 2, frame = 0;
  std::int32_t last_frame = 168; // 410a34;410910 uses159;410d34 uses197.
  std::uint8_t reward = 1;
};
struct MeanRewardDisplayEvent {
  bool service_70_request = false, service_68_request = false;
  bool field_438afc_request = false; // original slot{1,0,0}
};
void mean_reward_display_tick(MeanRewardDisplay &display, std::int16_t &gate,
                              MeanRewardDisplayEvent *event = nullptr);
} // namespace slam
