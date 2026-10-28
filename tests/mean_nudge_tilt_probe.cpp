#include "input/mean_nudge_tilt.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json rows;
  std::cin >> rows;
  auto out = nlohmann::json::array();
  for (const auto &c : rows) {
    slam::MeanNudgeTilt s;
    auto v = c.at("fields").get<std::array<int, 8>>();
    s.field_43d864 = v[0];
    s.field_43e7a0 = v[1];
    s.field_43e7d4 = v[2];
    s.field_43e7c4 = v[3];
    s.field_43e7c8 = v[4];
    s.field_4298b8 = v[5];
    s.field_4298bc = v[6];
    s.field_4298c0 = v[7];
    s.count = c.at("count");
    s.ball_status = c.at("status").get<std::array<std::uint8_t, 8>>();
    const int callback = s.key_event();
    out.push_back(
        {{"fields",
          {s.field_43d864, s.field_43e7a0, s.field_43e7d4, s.field_43e7c4,
           s.field_43e7c8, s.field_4298b8, s.field_4298bc, s.field_4298c0}},
         {"status", s.ball_status},
         {"callback", callback}});
  }
  std::cout << out.dump() << '\n';
}
