#include "physics/mean_mode5_left.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input;
  std::cin >> input;
  auto out = nlohmann::json::array();
  for (auto c : input) {
    slam::MeanObject b;
    for (unsigned i = 0; i < 100; ++i)
      b.bytes[i] = c["ball"][i];
    slam::MeanMode5LeftState m;
    slam::MeanCaptureTickState s;
    m.field_43f37e = c["stage"];
    m.field_43f3ae = 123;
    m.field_43f260 = {9, 8, 7, 6};
    slam::mean_mode4_transfer(b, s, m, 0x1100000);
    out.push_back({{"ball", b.bytes},
                   {"stage", m.field_43f37e},
                   {"field3ae", m.field_43f3ae},
                   {"data", m.field_43f260},
                   {"slot", s.field_438b50},
                   {"delay", m.field_438b90}});
  }
  std::cout << out.dump();
}
