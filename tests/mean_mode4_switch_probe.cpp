#include "rules/mean_mode4_switch.h"
#include <iostream>
#include <nlohmann/json.hpp>
using namespace slam;
int main() {
  nlohmann::json j;
  std::cin >> j;
  auto out = nlohmann::json::array();
  for (auto &c : j) {
    MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    s.table_mode = c["mode"];
    auto e = mean_mode4_switch(s, c["layer"], c["mask"], c["x"], c["y"]);
    out.push_back({{"fields", s.fields},
                   {"mode", s.table_mode},
                   {"score", e.score},
                   {"callback", e.callback},
                   {"audio84", e.service84},
                   {"audio80", e.service80},
                   {"rebuild", e.lamp_rebuild},
                   {"reset", e.service416fe0}});
  }
  std::cout << out.dump();
}
