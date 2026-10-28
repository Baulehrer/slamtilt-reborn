#include "rules/mean_right_cancel.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json in; std::cin >> in;
  auto out = nlohmann::json::array();
  for (auto &c : in) {
    slam::MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    s.table_mode = c["mode"];
    slam::MeanRightGateState gate;
    gate.field_438b2c = c["b2c"]; gate.field_438b34 = c["b34"];
    auto e = slam::mean_right_cancel(s, gate, c["service_result"]);
    out.push_back({{"fields", s.fields}, {"b2c", gate.field_438b2c},
                   {"b34", gate.field_438b34}, {"cancelled", e.cancelled},
                   {"callback", e.callback}});
  }
  std::cout << out.dump();
}
