#include "physics/mean_mode5_clock.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json cases;
  std::cin >> cases;
  auto output = nlohmann::json::array();
  for (const auto &c : cases) {
    slam::MeanMode5LeftState m;
    slam::MeanCaptureTickState s;
    slam::MeanObject b;
    b.put32(0, 26 * 65536);
    b.put32(4, 279 * 65536);
    b.put16(0x58, 3);
    b.put16(0x5a, 2);
    m.field_43f39c = c.value("timer", 8400);
    m.field_43f05c = c.value("award", 0u);
    m.field_43f058 = 20000000;
    m.field_43f3b4 = c.value("counter", 2);
    m.field_43f366 = 123;
    m.field_43f1e6 = c.value("selected", 0);
    m.field_43f384 = c.value("guard", 0);
    const int mask = c.value("mask", 1);
    for (unsigned i = 0; i < 5; ++i)
      m.field_43f1e0[i] = (mask >> i) & 1;
    s.table_mode = 5;
    s.field_43f380 = -1;
    slam::MeanCaptureTickEvent event;
    const std::string op = c.at("operation");
    unsigned steps = 1;
    if (op == "cycle") {
      s.field_43f380 = 50;
      std::uint32_t points = 0;
      for (steps = 0; steps < 400 && b.u16(0x58) == 3;) {
        if (!(s.table_mode == 5 && b.u16(0x5a) == 2
                  ? slam::mean_mode5_left(b, s, m, 0x1100000, event)
                  : slam::mean_capture_tick(b, s, 0x1100000, event)))
          return 3;
        points += event.score_request;
        if (++steps % 4 == 0)
          for (auto *slot : {&s.field_438b68, &s.field_438b74})
            if ((*slot)[0] >= 0)
              --(*slot)[0];
      }
      event.score_request = points;
    } else if (op == "clock")
      slam::mean_mode5_clock(m, s);
    else if (op == "reset")
      slam::mean_mode_reset(m, s.table_mode);
    else if (!slam::mean_mode5_left(b, s, m, 0x1100000, event))
      return 2;
    output.push_back({{"steps", steps},
                      {"award", m.field_43f05c},
                      {"timer", m.field_43f39c},
                      {"mode", s.table_mode},
                      {"selected", m.field_43f1e6},
                      {"counter", m.field_43f3b4},
                      {"field366", m.field_43f366},
                      {"sum", m.field_43f058},
                      {"score", event.score_request},
                      {"capture_timer", s.field_43f380},
                      {"ball", b.bytes}});
  }
  std::cout << output.dump() << '\n';
}
