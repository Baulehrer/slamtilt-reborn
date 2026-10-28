#include "physics/mean_upper_entry.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input;
  std::cin >> input;
  auto output = nlohmann::json::array();
  for (const auto &c : input) {
    slam::MeanObject ball;
    ball.bytes = c.at("ball").get<decltype(ball.bytes)>();
    slam::MeanUpperCaptureState state;
    state.field_438b5c = c.at("slot").get<decltype(state.field_438b5c)>();
    state.field_43f36a = c.at("timer");
    bool accepted =
        slam::mean_upper_entry(ball, state, c.at("services"), c.at("blocked"));
    output.push_back({{"ball", ball.bytes},
                      {"slot", state.field_438b5c},
                      {"timer", state.field_43f36a},
                      {"accepted", accepted}});
  }
  std::cout << output.dump();
}
