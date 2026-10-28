#include "rules/mean_material5.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json input;
  std::cin >> input;
  nlohmann::json out = nlohmann::json::array();
  for (const auto &c : input) {
    slam::MeanMaterial5State s;
    s.field_1dc = c.at("flags").get<decltype(s.field_1dc)>();
    s.fields_ee1c = c.at("cooldowns").get<decltype(s.fields_ee1c)>();
    s.commands_26c = c.at("commands").get<decltype(s.commands_26c)>();
    s.command_268 = {9, 8, 7, 6};
    s.command_300 = {9, 8, 7, 6};
    s.field_1da = 7;
    s.field_37a = c.at("field37a");
    s.mode = c.at("mode");
    s.field_054 = 12345;
    auto e = slam::mean_material5_rules(c.at("x"), c.at("y"), s);
    out.push_back({{"flags", s.field_1dc},
                   {"cooldowns", s.fields_ee1c},
                   {"commands", s.commands_26c},
                   {"command268", s.command_268},
                   {"command300", s.command_300},
                   {"field1da", s.field_1da},
                   {"field37a", s.field_37a},
                   {"sample", e.sample},
                   {"group", e.group},
                   {"callback", e.callback},
                   {"score_add", e.score_add},
                   {"stop84", e.stop84}});
  }
  std::cout << out.dump() << '\n';
}
