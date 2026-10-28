#include "mean_reward_display.h"
#include <cstdlib>
#include <iostream>
int main(int argc, char **argv) {
  slam::MeanRewardDisplay display;
  if (argc > 1)
    display.last_frame = std::atoi(argv[1]);
  std::int16_t gate = -1;
  for (int tick = 0; tick < display.last_frame + 3; ++tick) {
    slam::mean_reward_display_tick(display, gate);
    std::cout << display.state << ' ' << display.active << ' ' << display.frame
              << ' ' << gate << '\n';
  }
}
