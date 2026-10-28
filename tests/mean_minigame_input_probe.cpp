#include "physics/mean_minigame_input.h"
#include <iostream>
int main() {
  std::uint32_t angle, rate, a, b;
  while (std::cin >> angle >> rate >> a >> b) {
    slam::MeanMinigameInputState s{angle, rate};
    slam::mean_minigame_input_step(s,a,b);
    std::cout << s.field_efe8 << ' ' << s.field_eff8 << '\n';
  }
}
