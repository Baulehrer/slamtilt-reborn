#include "physics/mean_mode5_left.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input;
  std::cin >> input;
  auto out = nlohmann::json::array();
  slam::MeanObject ball;
  ball.bytes = input.at("ball").get<decltype(ball.bytes)>();
  slam::MeanCaptureTickState s;
  s.table_mode = 5;
  slam::MeanMode5LeftState m;
  m.field_43f05c = input.at("field05c");
  for (int i = 0; i < 400; i++) {
    slam::MeanCaptureTickEvent e;
    bool ok = slam::mean_mode5_left(ball, s, m, 0x1100000, e);
    if (i % 4 == 3)
      for (auto *p : {&s.field_438b68, &s.field_438b74, &s.field_438b50})
        if ((*p)[0] >= 0)
          --(*p)[0];
    out.push_back({{"ball", ball.bytes},
                   {"slot2", s.field_438b68},
                   {"slot3", s.field_438b74},
                   {"slot50", s.field_438b50},
                   {"timer", s.field_43f380},
                   {"score", e.score_request},
                   {"field050", m.field_43f050},
                   {"field058", m.field_43f058},
                   {"field3b4", m.field_43f3b4},
                   {"ok", ok}});
    if (!ok || ball.u16(0x5a) == 3)
      break;
  }
  std::cout << out.dump();
}
