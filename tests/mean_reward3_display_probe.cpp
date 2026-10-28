#include "physics/mean_reward_display.h"
#include <iostream>
int main() {
  slam::MeanRewardDisplay d;
  d.reward = 3;
  d.last_frame = 197;
  std::int16_t g = -1;
  for (int i = 0; i < 200; ++i) {
    slam::MeanRewardDisplayEvent e;
    slam::mean_reward_display_tick(d, g, &e);
    std::cout << d.state << ' ' << d.active << ' ' << d.frame << ' ' << g << ' '
              << e.service_70_request << ' ' << e.service_68_request << ' '
              << e.field_438afc_request << '\n';
  }
}
