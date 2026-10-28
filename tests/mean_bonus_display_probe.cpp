#include "rules/mean_bonus_display.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json j, out = nlohmann::json::array();
  std::cin >> j;
  for (auto &c : j["cases"]) {
    slam::MeanBonusDisplay s;
    s.phase = c["phase"];
    s.timer = c["timer"];
    s.step = c["step"];
    s.field_43e734 = c["field_43e734"];
    s.bonus_total = c["bonus_total"];
    s.field_43e718 = c["field_43e718"];
    slam::MeanBonusDisplayInput i;
    i.bonus = c["bonus"];
    i.suppressed = c["suppressed"];
    i.multiplier = c["multiplier"];
    i.callback_result = c["callback_result"];
    auto e = slam::mean_bonus_display_step(s, i);
    out.push_back({{"phase", s.phase},
                   {"timer", s.timer},
                   {"step", s.step},
                   {"bonus_total", s.bonus_total},
                   {"field_43e718", s.field_43e718},
                   {"award", e.award},
                   {"score_argument", e.score_argument},
                   {"finish", e.finish},
                   {"rotate_only", e.rotate_only},
                   {"initialize", e.initialize},
                   {"callback_stage", e.callback_stage}});
  }
  std::cout << out.dump();
}
