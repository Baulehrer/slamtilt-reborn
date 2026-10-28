#include "rules/mean_mode4_events.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json cs, out = nlohmann::json::array();
  std::cin >> cs;
  for (auto &c : cs) {
    slam::MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    s.table_mode = 4;
    s.field_438a40 = 77;
    auto e = slam::mean_mode4_event(s, c["branch"], c["handle"]);
    out.push_back({{"fields", s.fields},
                   {"field438a40", s.field_438a40},
                   {"mode", s.table_mode},
                   {"callback", e.callback},
                   {"score", e.score_add},
                   {"clear_slots", e.clear_slots},
                   {"exit", e.exit_to_mode2}});
  }
  std::cout << out.dump();
}
