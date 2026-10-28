#include "input/mean_nudge_table.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json rows;
  std::cin >> rows;
  auto out = nlohmann::json::array();
  for (auto &c : rows) {
    slam::MeanNudgeTable s;
    s.field_038 = c[1];
    s.engine_field_14 = c[2];
    s.callback(c[0], c[3]);
    auto events = nlohmann::json::array();
    for (auto &e : s.requests) {
      if (e.target == 0x8c)
        events.push_back({e.target});
      else if (e.target == 0x84)
        events.push_back({e.target, e.eax, e.edx});
      else
        events.push_back({e.target, e.eax, e.edx, e.ecx, e.ebx, e.stack});
    }
    out.push_back({s.field_038, s.engine_field_14, events});
  }
  std::cout << out.dump() << '\n';
}
