#include "physics/mean_simulation.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  try {
    if (argc != 4)
      return 2;
    auto chains = nlohmann::json::array();
    for (unsigned selected : {1u, 2u, 4u}) {
      slam::MeanSimulation s(argv[1], argv[2], argv[3]);
      s.debug_start_shared_mode(selected);
      auto events = nlohmann::json::array();
      auto wrong = nlohmann::json();
      if (selected == 2) {
        const auto target = s.shared_target();
        const auto before = s.score();
        const unsigned id = target == 1 ? 2 : 1;
        s.debug_place_shared_switch(id);
        if (!s.step())
          throw std::runtime_error(s.status());
        const auto &f=s.shared_raw_state().fields;
        wrong = {{"pit_punctures", std::array<unsigned,4>{f[0x1d4],f[0x1d5],f[0x1d6],f[0x1d7]}}, {"id", id},
                 {"target", s.shared_target()},
                 {"award", s.score() - before},
                 {"mode", s.table_mode()},
                 {"display", s.material5_display_callback()}};
        if (s.shared_target() != target)
          throw std::runtime_error("Wrong turn changed Rally target");
      }
      const unsigned monster[] = {0, 1, 2, 3, 4, 5};
      const unsigned offroad[] = {1, 1, 2, 2, 3};
      for (unsigned k = 0; k < (selected == 4 ? 5u : 6u); ++k) {
        unsigned id = selected == 1   ? monster[k]
                      : selected == 2 ? s.shared_target()
                                      : offroad[k];
        const auto before = s.score();
        s.debug_place_shared_switch(id);
        if (!s.step())
          throw std::runtime_error(s.status());
        const auto &f=s.shared_raw_state().fields;
        events.push_back({{"pit_punctures", std::array<unsigned,4>{f[0x1d4],f[0x1d5],f[0x1d6],f[0x1d7]}},
                          {"pit_timer", unsigned(f[0x398])|(unsigned(f[0x399])<<8)}, {"id", id},
                          {"award", s.score() - before},
                          {"total", s.phase1_award_total()},
                          {"mode", s.table_mode()},
                          {"target", s.shared_target()},
                          {"layer", s.ball().u16(0x48)},
                          {"display", s.material5_display_callback()}});
      }
      if(selected==1){const auto &m=s.monster_stats();if(m.starts!=1||m.hits!=std::array<unsigned,6>{1,1,1,1,1,1}||m.completions!=1||m.timeouts||m.score!=125000000)throw std::runtime_error("Monster telemetry differs from actual sixswitch dispatcher");}
      if(selected==2){const auto &r=s.rally_stats();if(r.starts!=1||r.correct!=6||r.wrong!=1||r.completions!=1||r.timeouts||r.score!=211500000)throw std::runtime_error("Rally telemetry differs from actual switch dispatcher");}
      if(selected==4){const auto &o=s.offroad_stats();if(o.starts!=1||o.awards!=3||o.repeats!=2||o.ends||o.score!=45000000)throw std::runtime_error("Offroad telemetry differs from actual switch dispatcher");}
      chains.push_back(
          {{"selected", selected}, {"events", events}, {"wrong_turn", wrong}});
    }
    std::cout << chains.dump() << '\n';
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
