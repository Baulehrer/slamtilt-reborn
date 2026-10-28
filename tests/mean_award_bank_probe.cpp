#include "rules/mean_award_bank.h"
#include "rules/mean_material5.h"
#include <iostream>
#include <nlohmann/json.hpp>
#include <stdexcept>
int main() {
  nlohmann::json cases, out = nlohmann::json::array();
  std::cin >> cases;
  for (auto &c : cases) {
    auto flags = c["flags"].get<std::array<std::uint8_t, 5>>();
    auto timer = c["timer"].get<std::int16_t>();
    auto value = c["value"].get<std::uint32_t>();
    slam::MeanLampCommands commands{};
    for (auto &cmd : commands)
      cmd = {9, 8, 7, 6};
    std::uint32_t callback = 0;
    if (c["kind"] == "tick")
      callback = slam::mean_award_bank_tick(timer, value, commands);
    else if (slam::mean_award_bank_target(c["x"], c["mode"], flags, timer,
                                          value, commands))
      callback = 0x4107c8;
    nlohmann::json lamps = nlohmann::json::array();
    for (unsigned i = 33; i < 38; ++i)
      lamps.push_back(commands[i]);
    out.push_back({{"flags", flags},
                   {"timer", timer},
                   {"value", value},
                   {"lamps", lamps},
                   {"lamp62", commands[62]},
                   {"callback", callback}});
  }
  // Full bounded native chain: five switches ->100ticks ->Material5 award.
  std::array<std::uint8_t, 5> flags{};
  std::int16_t timer = -1;
  std::uint32_t value = 0;
  slam::MeanLampCommands commands{};
  for (int x : {22, 23, 45, 160, 275})
    slam::mean_award_bank_target(x * 65536, 2, flags, timer, value, commands);
  if (timer != 6000 || value != 60000000)
    throw std::runtime_error("bank activation");
  for (unsigned i = 0; i < 100; ++i)
    slam::mean_award_bank_tick(timer, value, commands);
  slam::MeanMaterial5State state;
  state.field_37a = timer;
  state.field_054 = value;
  const auto award =
      slam::mean_material5_rules(100 * 65536, 351 * 65536, state);
  if (award.score_add != 59000000 || award.callback != 0x41062c ||
      state.field_37a != -1 || !award.stop84)
    throw std::runtime_error("bank collection");
  if (slam::mean_material5_rules(100 * 65536, 351 * 65536, state).score_add)
    throw std::runtime_error("duplicate bank collection");
  timer = 6000;
  for (unsigned i = 0; i < 6000; ++i)
    slam::mean_award_bank_tick(timer, value, commands);
  if (timer != 0 || value != 10000000 ||
      slam::mean_award_bank_tick(timer, value, commands) != 0x410504 ||
      timer != -1 || commands[62][0] != 2)
    throw std::runtime_error("bank expiration");
  std::cout << out.dump();
}
