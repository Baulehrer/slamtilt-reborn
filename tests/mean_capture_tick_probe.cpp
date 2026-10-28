#include "physics/mean_capture_tick.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input;
  std::cin >> input;
  slam::MeanObject b;
  b.bytes = input["ball"].get<std::array<std::uint8_t, 100>>();
  slam::MeanCaptureTickState s;
  s.field_438b68 = {-1, 100, 0};
  s.field_43f204 = input.value("field204", 0);
  s.field_43f1fe = input.value("field1fe", 0);
  s.field_43f200 = input.value("field200", 0);
  s.field_43f202 = input.value("field202", 0);
  s.field_43f1fa = input.value("field1fa", 0);
  auto out = nlohmann::json::array();
  for (int tick = 0; tick < input.value("steps", 400) && b.u16(0x58) == 3;
       ++tick) {
    slam::MeanCaptureTickEvent event;
    if (!slam::mean_capture_tick(b, s, 0x1100000, event))
      return 1;
    if (tick % 4 == 3) {
      if (s.field_438b68[0] >= 0)
        --s.field_438b68[0];
      if (s.field_438b74[0] >= 0)
        --s.field_438b74[0];
    }
    out.push_back({{"ball", b.bytes},
                   {"slot2", s.field_438b68},
                   {"slot3", s.field_438b74},
                   {"slot50", s.field_438b50},
                   {"timer", s.field_43f380},
                   {"gate", s.field_43f364},
                   {"field204", s.field_43f204},
                   {"score", event.score_request}});
    if (input.value("sixth", false)) {
      out.back()["field1fe"] = s.field_43f1fe;
      out.back()["field200"] = s.field_43f200;
      out.back()["field202"] = s.field_43f202;
      out.back()["field1fa"] = s.field_43f1fa;
    }
  }
  std::cout << out.dump() << '\n';
}
