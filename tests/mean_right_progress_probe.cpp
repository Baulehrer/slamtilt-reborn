#include "rules/mean_right_progress.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json in;
  std::cin >> in;
  auto out = nlohmann::json::array();
  for (auto &c : in) {
    slam::MeanBallResetState s;
    s.fields = c["fields"].get<decltype(s.fields)>();
    s.table_mode = c["mode"];
    auto e = slam::mean_right_progress(s);
    out.push_back({{"fields", s.fields},
                   {"score", e.score},
                   {"callback", e.callback},
                   {"reset", e.reset_right_gate}});
  }
  std::cout << out.dump();
}
