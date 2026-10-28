#include "physics/mean_mode6_side.h"
#include <iostream>
#include <nlohmann/json.hpp>
using nlohmann::json;
int main() {
  json cases;
  std::cin >> cases;
  json out = json::array();
  for (auto &c : cases) {
    slam::MeanObject b{};
    if (c.contains("ball")) b.bytes = c["ball"].get<std::array<std::uint8_t,100>>();
    b.put16(0x58, 3);
    b.put16(0x5a, c["callback"]);
    slam::MeanMode6SideState s;
    s.field_43f380 = s.field_43f370 = c["timer"];
    s.field_43f364 = c["gate"];
    s.active_count = c["count"];
    s.field_43f38e = c["captures"][0];
    s.field_43f368 = c["captures"][1];
    s.field_43f36c = c["captures"][2];
    s.field_438b40 = c["blocked"];
    s.field_438b38 = c["field38"];
    s.field_438b68 = s.field_438b80 = c["slot"].get<std::array<int, 3>>();
    s.field_438b74 = c.value("slot3", std::array<int,3>{-1,100,0});
    s.callback3_occupied = c.value("callback3_occupied", false);
    slam::MeanMode6SideEvent e;
    slam::mean_mode6_side_tick(b, s, e, c.value("tilt", false));
    out.push_back(
        {{"state", b.u16(0x58)},
         {"timer", c["callback"] == 2 ? s.field_43f380 : s.field_43f370},
         {"gate", s.field_43f364},
         {"captures", {s.field_43f38e, s.field_43f368, s.field_43f36c}},
         {"slot", c["callback"] == 2 ? s.field_438b68 : s.field_438b80},
         {"field38", s.field_438b38},
         {"score", e.score_request},
         {"player08", e.field_player_08_add},
         {"transfer", e.transfer_requested},
         {"lamp", e.lamp_reset_requested}});
    if (c.contains("tilt")) {
      out.back()["ball"] = b.bytes;
      out.back()["slot3"] = s.field_438b74;
      out.back()["slot50"] = s.field_438b50;
      out.back()["samples"] = e.services_1c_samples;
      out.back()["early_transfer_count"] = e.early_transfer_count;
    }
  }
  std::cout << out.dump();
}
