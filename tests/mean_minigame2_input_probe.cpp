#include "rules/mean_minigame2_input.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json cs, out = nlohmann::json::array();
  std::cin >> cs;
  for (auto &c : cs) {
    slam::MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    auto e =
        slam::mean_minigame2_input(s, c["edge"], c["service1c"], c["engine44"]);
    out.push_back({{"fields", s.fields},
                   {"descriptor", e.descriptor},
                   {"edx", e.edx},
                   {"ebx", e.ebx}});
  }
  std::cout << out.dump();
}
