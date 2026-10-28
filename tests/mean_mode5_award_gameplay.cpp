#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 4)
    return 2;
  try {
    auto cases = nlohmann::json::array();
    for (bool tilt : {false, true})
      for (bool reject : {false, true}) {
        slam::MeanSimulation s(argv[1], argv[2], argv[3]);
        s.debug_mode5_award(tilt, reject);
        auto before = s.capture_delays();
        auto score = s.score();
        if (!s.step())
          throw std::runtime_error(s.status());
        auto delays = s.capture_delays();
        if (delays != (reject ? before : std::array<std::int32_t, 5>{}))
          throw std::runtime_error("Award delay admission gate differs: "+nlohmann::json{{"tilt",tilt},{"reject",reject},{"before",before},{"after",delays},{"callback",s.material5_display_callback()}}.dump());
        if (s.score() != score + 65000000)
          throw std::runtime_error("Award score differs");
        if (s.material5_display_callback() != (reject ? 0x410b00u : 0x412908u))
          throw std::runtime_error("Award callback priority differs");
        for (unsigned i = 1; i < 680; ++i)
          if (!s.step())
            throw std::runtime_error(s.status());
        cases.push_back({{"tilt", tilt},
                         {"rejected", reject},
                         {"delay_after_award", delays},
                         {"ticks", 680},
                         {"score", s.score()},
                         {"final_ball", s.ball().bytes},
                         {"callback", s.material5_display_callback()}});
      }
    std::ofstream("analysis/traces/mean-mode5-award-gameplay.json")
        << nlohmann::
               json{{"scope",
                     "Synthetic native award admission/score/capture/display "
                     "integration, not whole-original trajectories"},
                    {"cases", cases}}
                   .dump(2)
        << '\n';
    std::cout << "PASS four award admission/Tilt chains\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
