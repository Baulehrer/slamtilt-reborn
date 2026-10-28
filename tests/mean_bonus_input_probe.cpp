#include "rules/mean_bonus_display.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json in;
  std::cin >> in;
  auto out = nlohmann::json::array();
  for (auto &c : in) {
    slam::MeanBonusDisplay s;
    s.field_43e734 = c.at("flags");
    slam::mean_bonus_input_edge(s, c.at("right"), c.at("pressed"));
    out.push_back(s.field_43e734);
  }
  std::cout << out.dump() << '\n';
}
