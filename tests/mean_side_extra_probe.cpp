#include "rules/mean_award_bank.h"
#include "rules/mean_bonus_turn.h"
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
int main() {
  nlohmann::json cases, result = nlohmann::json::array();
  std::cin >> cases;
  for (auto &c : cases) {
    auto field = c["field"].get<std::int16_t>();
    auto player = c["player"].get<std::uint16_t>();
    slam::MeanLampCommands lamps;
    for (auto &l : lamps)
      l = {9, 8, 7, 6};
    const auto hit = slam::mean_side_extra_ball(c["x"], field, player, lamps);
    result.push_back({{"field", field},
                      {"player", player},
                      {"hit", hit},
                      {"lamps", {lamps[23], lamps[60], lamps[61]}}});
  }
  // Collection once, then existing bonus lifecycle consumes the extra ball.
  std::int16_t field = 1;
  std::uint16_t player = 0;
  slam::MeanLampCommands lamps{};
  if (!slam::mean_side_extra_ball(22 * 65536, field, player, lamps) ||
      player != 1 ||
      slam::mean_side_extra_ball(22 * 65536, field, player, lamps))
    throw std::runtime_error("extra ball collection once");
  slam::MeanBonusTurn turn;
  turn.field_player_10 = player;
  if (!slam::mean_finish_bonus_turn(turn) || turn.field_player_0e != 1 ||
      turn.field_player_10 != 0 || slam::mean_finish_bonus_turn(turn) ||
      turn.field_player_0e != 2)
    throw std::runtime_error("extra ball bonus lifecycle");
  std::cout << result.dump();
}
