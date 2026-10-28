#include "core/mean_diagnostic_input.h"
#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 4)
    return 2;
  try {
    auto records = nlohmann::json::array();
    for (auto spec : {std::pair<unsigned, unsigned>{4, 1},
                      {5, 1},
                      {6, 1},
                      {4, 2},
                      {5, 2},
                      {6, 2},
                      {6, 4},
                      {5, 4}}) {
      nlohmann::json first;
      for (unsigned repeat = 0; repeat < 2; ++repeat) {
        slam::MeanSimulation s(argv[1], argv[2], argv[3]);
        s.debug_tilt_capture(spec.second, spec.first);
        if(s.table_mode()!=int(spec.first)) throw std::runtime_error("Special capture fixture mode differs");
        auto initial = s.ball().bytes;
        s.set_launch(true);
        unsigned samples = 0;
        for (unsigned tick = 0; tick < 100; ++tick) {
          if (!s.step())
            throw std::runtime_error(s.status());
          for (const auto &q : s.take_audio_requests())
            samples += q.service == 0x5c && q.descriptor == 0x437dec;
        }
        if (initial == s.ball().bytes)
          throw std::runtime_error("Tilt capture remained frozen");
        const auto state100 = s.ball().bytes;
        slam::MeanDiagnosticInput keys(0);
        unsigned continuation = 0;
        bool suppressed = false, cleared = false;
        for (; continuation < 200000 && !s.game_over(); ++continuation) {
          auto k = keys.next();
          s.set_flippers(k[0], k[1]);
          const bool bonus = s.bonus_active();
          if (!s.step() && !s.game_over())
            throw std::runtime_error(s.status());
          if (s.bonus_active() && s.tilted() && s.bonus_phase() > 1 &&
              s.last_bonus())
            throw std::runtime_error("Special Tilt awarded bonus");
          suppressed |= s.bonus_active() && s.tilted();
          cleared |= bonus && !s.bonus_active() && !s.tilted();
          s.take_audio_requests();
        }
        if (!s.game_over() || !suppressed || !cleared)
          throw std::runtime_error("Special Tilt finite lifecycle incomplete");
        nlohmann::json out = {{"mode", spec.first},
                              {"callback", spec.second},
                              {"ticks", 100},
                              {"initial", initial},
                              {"state100", state100},
                              {"final", s.ball().bytes},
                              {"continuation", continuation},
                              {"bonus_suppressed", suppressed},
                              {"next_ball_clear", cleared},
                              {"samples", samples},
                              {"score", s.score()}};
        if (!repeat)
          first = out;
        else if (out != first)
          throw std::runtime_error("Tilt repeat differs");
      }
      records.push_back(first);
    }
    std::ofstream("analysis/traces/mean-special-tilt-gameplay.json")
        << nlohmann::json{{"scope",
                           "Synthetic native special-mode capture integration; "
                           "not whole-original trajectories"},
                          {"cases", records}}
               .dump(2)
        << '\n';
    std::cout << "PASS seven special-mode capture pairs /100steps\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
