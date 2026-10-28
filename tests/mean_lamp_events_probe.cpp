#include "rules/mean_lamp_events.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input, result = nlohmann::json::array();
  std::cin >> input;
  for (const auto &c : input.at("cases")) {
    if (c.contains("field_player_12")) {
      slam::MeanTopTargetReward s;
      s.field_player_12 = c.at("field_player_12");
      s.field_43f1fa = c.at("field_43f1fa");
      s.command_43f2f4 =
          c.at("command_43f2f4").get<std::array<std::uint8_t, 4>>();
      const auto e = slam::mean_top_target_reward(s);
      result.push_back({{"field_player_12", s.field_player_12},
                        {"field_43f1fa", s.field_43f1fa},
                        {"command_43f2f4", s.command_43f2f4},
                        {"score_points", e.score_points},
                        {"services_pending", e.services_pending}});
      continue;
    }
    slam::MeanLampEvents s;
    s.field_43f1e8 = c.at("flags").get<std::array<std::uint8_t, 3>>();
    auto commands =
        c.at("commands").get<std::array<std::array<std::uint8_t, 4>, 3>>();
    const auto event = slam::mean_top_target_lamps(
        s, commands, c.at("x"), c.at("y"), 0, 4, c.at("field_services_1c"));
    result.push_back({{"flags", s.field_43f1e8},
                      {"commands", commands},
                      {"request_41d153", event.request_41d153}});
  }
  std::cout << result.dump();
}
