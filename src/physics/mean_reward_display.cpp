#include "mean_reward_display.h"
namespace slam {
void mean_reward_display_tick(MeanRewardDisplay &display, std::int16_t &gate,
                              MeanRewardDisplayEvent *event) {
  if (event)
    *event = {};
  if (display.state == 4) {
    if (display.active == 0) {
      display.state = 3;
    } else {
      if (event && display.reward == 3 && display.frame == 75) {
        event->service_70_request = true;
        event->service_68_request = true;
        event->field_438afc_request = true;
      }
      // Increment shared+1c; clear shared+14 at the original last frame.
      if (display.frame++ >= display.last_frame)
        display.active = 0;
    }
  }
  // 40726f/407283 ->413b04 human idle callback.
  if (display.state == 0 && gate != 0)
    gate = 0;
  if (display.state == 3)
    display.state = 0;
}
} // namespace slam
