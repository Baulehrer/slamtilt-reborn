#include "physics/mean_upper_capture.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json in;
  std::cin >> in;
  auto out = nlohmann::json::array();
  for (const auto &c : in) {
    slam::MeanObject b;
    b.put16(0x58, 3);
    b.put16(0x5a, 1);
    slam::MeanUpperCaptureState s;
    s.table_mode = 4;
    s.field_43f36a = c.at("timer");
    s.field_43f364 = c.at("gate");
    s.field_43f394 = c.at("field394");
    s.field_43f1f2 = c.at("field1f2");
    s.field_438b5c = c.at("slot").get<decltype(s.field_438b5c)>();
    slam::MeanUpperCaptureEvent e;
    if (!slam::mean_upper_capture_tick(b, s, e))
      return 2;
    out.push_back({{"timer", s.field_43f36a},
                   {"gate", s.field_43f364},
                   {"field394", s.field_43f394},
                   {"field1f2", s.field_43f1f2},
                   {"slot", s.field_438b5c},
                   {"mode", s.table_mode},
                   {"score", e.score_request},
                   {"bonus", e.field_player_08_add},
                   {"release", e.release_requested},
                   {"rule", e.rule_service_request},
                   {"transfer", e.transfer_requested},
                   {"mode6", e.mode6_start_requested}});
  }
  std::cout << out.dump() << '\n';
}
