#include "physics/mean_upper_capture.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input;
  std::cin >> input;
  nlohmann::json out = nlohmann::json::array();
  for (auto &c : input) {
    slam::MeanObject b;
    b.put16(0x58, 3);
    b.put16(0x5a, 1);
    slam::MeanUpperCaptureState s;
    s.field_43f36a = 0;
    s.field_43f200 = c[0];
    s.field_43f202 = c[1];
    s.field_43f1fa = c[2];
    s.field_438b44 = {7, 19, 23};
    slam::MeanUpperCaptureEvent e;
    bool ok = slam::mean_upper_capture_tick(b, s, e);
    out.push_back({{"ok", ok},
                   {"timer", s.field_43f36a},
                   {"gate", s.field_43f364},
                   {"field200", s.field_43f200},
                   {"field202", s.field_43f202},
                   {"field1fa", s.field_43f1fa},
                   {"field378", s.field_43f378},
                   {"field1fc", s.field_43f1fc},
                   {"slot44", s.field_438b44},
                   {"score", e.score_request},
                   {"player08", e.field_player_08_add},
                   {"player10", e.field_player_10_add},
                   {"ball", b.bytes}});
  }
  std::cout << out.dump();
}
