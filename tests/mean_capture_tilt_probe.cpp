#include "physics/mean_capture_tick.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input;
  std::cin >> input;
  auto out = nlohmann::json::array();
  for (const auto &c : input) {
    slam::MeanObject b;
    b.bytes = c.at("ball").get<std::array<std::uint8_t, 100>>();
    slam::MeanCaptureTickState s;
    s.field_438b68 = c.at("slot2").get<std::array<int, 3>>();
    s.field_438b74 = c.at("slot3").get<std::array<int, 3>>();
    s.field_43f380 = c.at("timer");
    s.field_43f364 = c.at("gate");
    slam::MeanCaptureTickEvent e;
    if (!slam::mean_capture_tick(b, s, 0x1100000, e, true))
      return 2;
    out.push_back({{"ball", b.bytes},
                   {"slot2", s.field_438b68},
                   {"slot3", s.field_438b74},
                   {"slot50", s.field_438b50},
                   {"timer", s.field_43f380},
                   {"gate", s.field_43f364},
                   {"samples", e.services_1c_samples}});
  }
  std::cout << out.dump() << '\n';
}
