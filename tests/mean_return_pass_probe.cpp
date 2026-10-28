#include "rules/mean_return_pass.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json in;
  std::cin >> in;
  auto out = nlohmann::json::array();
  for (const auto &c : in) {
    slam::MeanBallResetState s;
    s.fields = c.at("fields").get<decltype(s.fields)>();
    s.table_mode = c.at("mode");
    slam::MeanReturnPassEvent e;
    if (c.at("op") == "hit")
      e = slam::mean_return_pass_hit(s);
    else
      slam::mean_return_pass_tick(s);
    out.push_back({{"fields", s.fields},
                   {"score", e.score},
                   {"announcement", e.announcement}});
  }
  std::cout << out.dump() << '\n';
}
