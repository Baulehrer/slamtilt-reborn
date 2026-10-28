#include "renderer/mean_camera.h"
#include <iostream>
#include <nlohmann/json.hpp>
#include <vector>
int main() {
  nlohmann::json in;
  std::cin >> in;
  auto out = nlohmann::json::array();
  for (auto &c : in) {
    slam::MeanCameraState s;
    s.field_429aec = c.at("center");
    s.field_429af0 = c.at("velocity");
    s.scroll = c.at("scroll");
    std::vector<slam::MeanCameraBall> balls;
    for (auto &b : c.at("balls"))
      balls.push_back(
          {b.at(0).get<std::int16_t>(), b.at(1).get<std::uint16_t>()});
    slam::mean_camera_step(s, balls.data(), balls.size(), c.at("max_scroll"),
                           c.at("viewport"));
    out.push_back(
        {s.field_429aec, s.field_429af0, s.scroll, s.previous_scroll});
  }
  std::cout << out.dump() << '\n';
}
