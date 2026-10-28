#include "rules/mean_game_end.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input, output = nlohmann::json::array();
  std::cin >> input;
  for (const auto &c : input.at("cases"))
    output.push_back(slam::mean_game_end_required(c.at("field_player_0e"),
                                                  c.at("field_454aa4")));
  std::cout << output.dump();
}
