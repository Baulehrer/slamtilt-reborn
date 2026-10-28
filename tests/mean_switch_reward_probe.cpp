#include "rules/mean_switch_reward.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input, out = nlohmann::json::array();
  std::cin >> input;
  for (auto &c : input) {
    slam::MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    s.field_438af8 = 123;
    auto e = slam::mean_switch_reward(s);
    out.push_back({{"fields", s.fields},
                   {"af8", s.field_438af8},
                   {"score", e.score},
                   {"audio", e.service84}});
  }
  std::cout << out.dump();
}
