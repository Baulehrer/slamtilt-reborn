#include "physics/mean_right_gate.h"
#include <iostream>
#include <nlohmann/json.hpp>
using namespace slam;
int main() {
  nlohmann::json j;
  std::cin >> j;
  auto out = nlohmann::json::array();
  for (auto &c : j) {
    MeanBallResetState s;
    s.fields = c["raw"].get<decltype(s.fields)>();
    s.table_mode = c["mode"];
    MeanObject b;
    b.bytes = c["ball"].get<decltype(b.bytes)>();
    MeanRightGateState g{17, 19};
    auto k = c["kind"].get<std::string>();
    if (k == "gate")
      mean_right_gate(s, g, c.value("active_count",1u));
    else if (k == "a")
      mean_right_marker20_a(b, s, 0x110be000);
    else
      mean_right_marker20_b(b, s, 0x110be000);
    out.push_back({{"raw", s.fields},
                   {"ball", b.bytes},
                   {"b2c", g.field_438b2c},
                   {"b34", g.field_438b34}});
  }
  std::cout << out.dump();
}
