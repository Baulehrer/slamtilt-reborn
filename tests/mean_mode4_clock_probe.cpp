#include "rules/mean_mode4_clock.h"
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
    std::int32_t engine40 = 13;
    auto e = slam::mean_mode4_clock(s, engine40, c["handle"]);
    out.push_back({{"fields", s.fields},
                   {"field438a40", s.field_438a40},
                   {"mode", s.table_mode},
                   {"engine40", engine40},
                   {"callback", e.callback},
                   {"clear_slots", e.clear_slots},
                   {"exit", e.exit_to_mode2},
                   {"audio", e.bank_order62 ? 62
                             : e.stop80     ? -1
                                            : 0}});
  }
  std::cout << out.dump();
}
