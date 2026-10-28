#include "rules/mean_flipper_actions.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input, out = nlohmann::json::array();
  std::cin >> input;
  for (auto &c : input) {
    slam::MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    auto descriptor = slam::mean_flipper_actions(s, c["mode"], c["edge"],
                                                 c["right"], c["service"]);
    out.push_back({{"fields", s.fields}, {"descriptor", descriptor}});
  }
  std::cout << out.dump();
}
