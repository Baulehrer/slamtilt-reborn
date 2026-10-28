#include "core/mean_diagnostic_input.h"
#include "physics/mean_simulation.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 4)
    return 2;
  try {
    auto cases = nlohmann::json::array();
    for (unsigned cb = 1; cb <= 5; ++cb)
      for (unsigned repeat = 0; repeat < 2; ++repeat) {
        slam::MeanSimulation s(argv[1], argv[2], argv[3]);
        s.debug_tilt_capture(cb);
        s.set_launch(true);
        if (!s.tilted())
          throw std::runtime_error("Tilt not applied");
        unsigned stop88 = 0, tilt_music = 0;
        for (const auto &q : s.take_audio_requests()) {
          stop88 += q.service == 0x8c;
          tilt_music += q.service == 0x84 && q.bank == 1 && q.order == 52;
        }
        if (stop88 != 1 || tilt_music != 1)
          throw std::runtime_error("Tilt table audio missing/repeated");
        if (!s.step())
          throw std::runtime_error(s.status());
        unsigned samples = 0;
        for (const auto &q : s.take_audio_requests())
          if (q.service == 0x5c && q.descriptor == 0x437dec) {
            if (q.bank != 6 || q.order != 5)
              throw std::runtime_error("Tilt sample arguments differ");
            ++samples;
          }
        if (samples != (cb == 4 ? 0u : 1u))
          throw std::runtime_error("Tilt sample ordering/count differs");
        if (s.ball().u16(0x58) == 3 && cb != 4)
          throw std::runtime_error("Tilt left ball held");
        if (cb == 2 && s.field_43f380() != 49)
          throw std::runtime_error("Tilt timer did not continue");
        unsigned steps = 1;
        slam::MeanDiagnosticInput keys(0);
        bool bonus = false, reset = false, suppressed = false;
        unsigned frozen = 0;
        for (; steps < 200000 && !s.game_over(); ++steps) {
          auto k = keys.next();
          s.set_flippers(k[0], k[1]);
          const bool old = s.bonus_active();
          auto ball = s.ball().bytes;
          if (!s.step() && !s.game_over())
            throw std::runtime_error(s.status());
          s.take_audio_requests();
          if (s.bonus_active() && s.tilted()) {
            bonus = true;
            if (s.pending_bonus() && s.bonus_phase() > 1 && s.last_bonus())
              throw std::runtime_error("Tilt bonus awarded");
          }
          if (old && s.bonus_active()) {
            if (ball != s.ball().bytes)
              throw std::runtime_error("Bonus moved ball");
            ++frozen;
          }
          if (bonus && !s.tilted()) {
            reset = true;
            if (!suppressed) {
              if (s.last_bonus() != 0 || s.bonus_awards() != 0)
                throw std::runtime_error("Nonzero Tilt bonus was awarded");
              suppressed = true;
            }
          }
        }
        if (!s.game_over() || !bonus || !reset || !suppressed || !frozen ||
            s.bonus_starts() != s.bonus_completions())
          throw std::runtime_error("Tilt lifecycle incomplete");
        nlohmann::json c = {{"callback", cb},
                            {"steps", steps},
                            {"score", s.score()},
                            {"bonus", s.bonus_completions()},
                            {"releases", s.releases()},
                            {"frozen_bonus_steps", frozen},
                            {"tilt_bonus_suppressed", suppressed}};
        if (repeat && c != cases.back())
          throw std::runtime_error("Tilt repeat differs");
        cases.push_back(c);
        s.reset();
        if (s.tilted() || s.score() != 0)
          throw std::runtime_error("Newgame retained Tilt");
      }
    std::ofstream("analysis/traces/mean-tilt-gameplay.json")
        << nlohmann::
               json{{"scope",
                     "Native five diagnostic captured entries then persistent "
                     "Tilt/release/bonus/nextball/finiteGameOver; not original "
                     "whole-table trajectory"},
                    {"cases", cases}}
                   .dump(2)
        << '\n';
    std::cout << "PASS five Tilt lifecycle chains, exact repeats\n";
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
