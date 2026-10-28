#include "physics/mean_upper_release.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input;
  std::cin >> input;
  auto output = nlohmann::json::array();
  for (const auto &c : input) {
    slam::MeanObject ball;
    ball.bytes = c.at("ball").get<decltype(ball.bytes)>();
    slam::MeanRandomState state;
    state.crt_seed = c.at("seed");
    state.field_43e7a8 = c.at("accumulator");
    state.field_43e834 = c.at("field_43e834");
    slam::mean_random_tick(state);
    if (c.value("transfer", false))
      slam::mean_upper_transfer(ball, 0x1100000);
    else
      slam::mean_upper_release(ball, 0x1100000, state.field_43e7ac);
    output.push_back({{"ball", ball.bytes},
                      {"seed", state.crt_seed},
                      {"accumulator", state.field_43e7a8},
                      {"field_43e7ac", state.field_43e7ac}});
  }
  std::cout << output.dump();
}
