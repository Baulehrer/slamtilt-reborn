#include "rules/mean_bonus_turn.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input, result = nlohmann::json::array();
  std::cin >> input;
  for (const auto &c : input.at("cases")) {
    slam::MeanBonusTurn s;
    s.field_player_08 = c.at("field_player_08");
    s.field_player_0e = c.at("field_player_0e");
    s.field_player_10 = c.at("field_player_10");
    s.field_player_12 = c.at("field_player_12");
    s.field_player_14 = c.at("field_player_14");
    s.current_player = c.at("current_player");
    s.player_count = c.at("player_count");
    const auto points = slam::mean_drain_bonus(s, c.at("field_43d864"));
    const bool extra = slam::mean_finish_bonus_turn(s);
    result.push_back({{"score_argument", points},
                      {"field_player_08", s.field_player_08},
                      {"field_player_0e", s.field_player_0e},
                      {"field_player_10", s.field_player_10},
                      {"field_player_12", s.field_player_12},
                      {"field_player_14", s.field_player_14},
                      {"current_player", s.current_player},
                      {"extra_ball", extra}});
  }
  std::cout << result.dump();
}
