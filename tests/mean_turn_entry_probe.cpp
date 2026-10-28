#include "rules/mean_turn_entry.h"
#include <iostream>
#include <nlohmann/json.hpp>
int main() {
  nlohmann::json in, out = nlohmann::json::array();
  std::cin >> in;
  for (auto &c : in.at("cases")) {
    slam::MeanTurnEntry s;
    s.mode = c.at("mode");
    s.field_43f3ae = c.at("field_43f3ae");
    s.field_43f35a = c.at("field_43f35a");
    s.command_43f258 = c.at("command258").get<std::array<std::uint8_t, 4>>();
    s.command_43f260 = c.at("command260").get<std::array<std::uint8_t, 4>>();
    slam::MeanObject b;
    b.bytes = c.at("ball").get<std::array<std::uint8_t, 100>>();
    bool event = false;
    std::string op = c.at("operation");
    if (op == "entry")
      event = slam::mean_turn_playfield_entry(s);
    else if (op == "drain")
      event = slam::mean_turn_drain_intercept(b, s, c.at("count"),
                                              c.at("services"));
    else
      event = slam::mean_turn_save_clock(s);
    out.push_back({{"mode", s.mode},
                   {"field_43f3ae", s.field_43f3ae},
                   {"field_43f35a", s.field_43f35a},
                   {"command258", s.command_43f258},
                   {"command260", s.command_43f260},
                   {"ball", b.bytes},
                   {"event", event}});
  }
  std::cout << out.dump();
}
