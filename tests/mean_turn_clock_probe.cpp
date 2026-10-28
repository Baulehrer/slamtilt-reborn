#include "rules/mean_turn_clock.h"
#include <iostream>
#include <nlohmann/json.hpp>
using nlohmann::json;
int main() {
  json batch;
  std::cin >> batch;
  json out = json::array();
  for (auto &c : batch) {
    slam::MeanTurnClockState s;
#define F(x) s.field_##x = c[#x];
    F(3ae)
    F(390) F(35a) F(3b0) F(af4)
#undef F
        s.service_1c = c["service1c"];
    s.fields_ee1c = c["ee1c"].get<decltype(s.fields_ee1c)>();
    s.field_260 = c["260"].get<decltype(s.field_260)>();
    s.field_268 = c["268"].get<decltype(s.field_268)>();
    s.field_258 = c["258"].get<decltype(s.field_258)>();
    slam::mean_turn_clock(s);
    out.push_back(json{{"3ae", s.field_3ae},
                       {"390", s.field_390},
                       {"35a", s.field_35a},
                       {"3b0", s.field_3b0},
                       {"af4", s.field_af4},
                       {"ee1c", s.fields_ee1c},
                       {"260", s.field_260},
                       {"268", s.field_268},
                       {"258", s.field_258}});
  }
  std::cout << out.dump() << '\n';
}
