#include "physics/mean_simulation.h"
#include <iostream>
#include <stdexcept>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  try {
    if (argc != 4) return 2;
    slam::MeanSimulation s(argv[1], argv[2], argv[3]);
    s.reset(); s.debug_start_point_force(true);
    unsigned phase1_audio_pairs = 0;
    auto steps = [&](unsigned n) {
      for (unsigned i = 0; i < n; ++i) {
        if (!s.step()) throw std::runtime_error(s.status());
        const auto requests = s.take_audio_requests();
        for (std::size_t j = 0; j < requests.size(); ++j)
          if (requests[j].service == 0x84 && requests[j].bank == 1 &&
              requests[j].order == 50) {
            if (j + 1 >= requests.size() || requests[j + 1].service != 0x8c)
              throw std::runtime_error("Phase1 music cancellation missing or out of order");
            ++phase1_audio_pairs;
          }
      }
    };
    unsigned release_tick = 0;
    while (s.phase1_state() != 1 && release_tick < 600) { steps(1); ++release_tick; }
    if (s.phase1_state() != 1 || s.point_force_type() != 0)
      throw std::runtime_error("Original clock did not open phase1 release window");
    if (phase1_audio_pairs != 1)
      throw std::runtime_error("Phase1 music transition missing or repeated");
    s.set_flippers(false, true);
    if (s.phase1_state() != 3) throw std::runtime_error("Right input did not release phase1");
    auto rows = nlohmann::json::array();
    for (unsigned event = 0; event < 3; ++event) {
      s.debug_place_phase1_switch(event == 2); steps(1);
      rows.push_back({{"event", event}, {"layer", s.ball().u16(0x48)},
                     {"mode", s.table_mode()}, {"award", s.phase1_award_total()},
                     {"score", s.score()}, {"type", s.point_force_type()}});
    }
    if (s.material5_display_callback()!=0x4102c0 || s.phase1_award_total() != 60000000 || s.table_mode() != 2 ||
        !s.right_route_armed() || !s.right_route_open())
      throw std::runtime_error("Original phase1 reward/gate continuity failed");
    std::cout << nlohmann::json({{"states",rows}, {"release_tick",release_tick}, {"point_force_updates",s.point_force_updates()},
          {"mode4_completions",s.mode4_completions()}, {"armed",s.right_route_armed()},
          {"gate_open",s.right_route_open()}}).dump() << '\n';
  } catch (const std::exception &e) { std::cerr << e.what() << '\n'; return 1; }
}
