#include "physics/mean_ramp_bundle.h"
#include <iostream>
#include <nlohmann/json.hpp>

int main() {
  nlohmann::json input;
  std::cin >> input;
  auto output = nlohmann::json::array();
  for (const auto &item : input) {
    slam::MeanObject ball;
    ball.bytes = item.get<std::array<std::uint8_t, 100>>();
    if (!slam::mean_ramp_bundle(ball, ball.u16(0x38), 0x1100000))
      return 1;
    output.push_back(ball.bytes);
  }
  std::cout << output.dump() << '\n';
}
