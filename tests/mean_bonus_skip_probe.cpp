#include "physics/mean_simulation.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 4)
    return 2;
  auto out = nlohmann::json::array();
  for (int profile = 0; profile < 3; ++profile) {
    slam::MeanSimulation s(argv[1], argv[2], argv[3]);
    s.reset();
    s.set_continuous_play(true);
    s.set_launch(true);
    s.set_flippers(false, false);
    unsigned n = 0;
    while (!s.bonus_active() && n++ < 100000)
      if (!s.step())
        return 3;
    if (!s.bonus_active())
      return 4;
    auto ball = s.ball().bytes;
    auto score = s.score();
    auto before = s.bonus_display_ticks();
    s.set_flippers(profile > 0, profile == 2);
    n = 0;
    while (s.bonus_active() && n++ < 2000) {
      if (!s.step())
        return 5;
      if (s.bonus_active() && s.ball().bytes != ball)
        return 6;
    }
    if (s.bonus_active())
      return 7;
    out.push_back({{"profile", profile},
                   {"steps", n},
                   {"display_ticks", s.bonus_display_ticks() - before},
                   {"score_before", score},
                   {"score_after", s.score()},
                   {"ball_number", s.ball_number()}});
  }
  std::cout << out.dump() << '\n';
}
