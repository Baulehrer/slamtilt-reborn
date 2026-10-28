#include "physics/mean_upper_capture.h"
#include "physics/mean_upper_release.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json cases;
  std::cin >> cases;
  auto out = nlohmann::json::array();
  for (const auto &c : cases) {
    slam::MeanObject b;
    b.bytes = c.at("ball").get<decltype(b.bytes)>();
    slam::MeanUpperCaptureState s;
    s.table_mode = 4;
    s.field_43f394 = -1;
    s.field_43f1f2 = 6;
    slam::MeanRandomState r;
    r.crt_seed = c.at("seed");
    slam::mean_random_tick(r);
    auto rows = nlohmann::json::array();
    for (unsigned tick = 0; tick < 300; ++tick) {
      slam::mean_random_tick(r);
      slam::MeanUpperCaptureEvent e;
      if (!slam::mean_upper_capture_tick(b, s, e))
        return 2;
      if (e.release_requested)
        slam::mean_upper_release(b, 0x1100000, r.field_43e7ac);
      if (tick % 4 == 3 && s.field_438b5c[0] >= 0)
        --s.field_438b5c[0];
      rows.push_back({{"ball", b.bytes},
                      {"timer", s.field_43f36a},
                      {"slot", s.field_438b5c},
                      {"score", e.score_request},
                      {"seed", r.crt_seed},
                      {"accumulator", r.field_43e7a8},
                      {"rng", r.field_43e7ac}});
      if (e.release_requested)
        break;
    }
    out.push_back(rows);
  }
  std::cout << out.dump() << '\n';
}
