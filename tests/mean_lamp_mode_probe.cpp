#include "rules/mean_lamp_mode.h"
#include <iostream>
#include <nlohmann/json.hpp>
using nlohmann::json;
int main() {
  json batch;
  std::cin >> batch;
  json out = json::array();
  for (auto &c : batch) {
    slam::MeanLampModeInput s;
#define FIELD(x)                                                               \
  if (c.contains(#x))                                                          \
    s.field_##x = c[#x].get<std::int16_t>();
    FIELD(398)
    FIELD(3ba) FIELD(3bc) FIELD(392) FIELD(3a2) FIELD(3b0) FIELD(374) FIELD(3ae)
        FIELD(1da) FIELD(394) FIELD(38a) FIELD(1f2) FIELD(1e6) FIELD(384)
            FIELD(204) FIELD(1fa) FIELD(202) FIELD(200) FIELD(1fc) FIELD(37a)
#undef FIELD
                s.table_mode = c.at("mode");
    s.service10_field10 = c.at("service10");
    s.field_1d4 = c.at("1d4").get<decltype(s.field_1d4)>();
    s.field_060 = c.at("060").get<decltype(s.field_060)>();
    s.field_1dc = c.at("1dc").get<decltype(s.field_1dc)>();
    s.field_1e0 = c.at("1e0").get<decltype(s.field_1e0)>();
    s.field_1ec = c.at("1ec").get<decltype(s.field_1ec)>();
    s.field_1e8 = c.at("1e8").get<decltype(s.field_1e8)>();
    auto d = c.at("commands").get<slam::MeanLampCommands>();
    slam::mean_lamp_mode_reset(s, d);
    out.push_back(d);
  }
  std::cout << out.dump() << '\n';
}
