#include "assets/table_flippers.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
std::vector<std::uint8_t> read(const std::string &p) {
  std::ifstream f(p, std::ios::binary);
  if (!f)
    throw std::runtime_error(p);
  return {std::istreambuf_iterator<char>(f), {}};
}
int main(int argc, char **argv) {
  try {
    if (argc != 5)
      return 2;
    slam::FlipperLift initial;
    initial.image = read(std::string(argv[1]) + "/pe-data.bin");
    initial.image.resize(0x100000);
    auto g = read(std::string(argv[1]) + "/engine-globals.bin");
    std::copy(g.begin(), g.end(), initial.image.begin() + 0x3e700);
    auto p = slam::load_table_flipper_parameters(
        read(argv[2]), std::stoul(argv[3], nullptr, 0));
    slam::configure_table_flippers(initial, p);
    std::ifstream in(argv[4]);
    nlohmann::json cases;
    in >> cases;
    auto out = nlohmann::json::array();
    unsigned case_index = 0;
    for (const auto &c : cases) {
      auto m = initial;
      if (c.value("operation", std::string{}) == "pose") {
        auto states = nlohmann::json::array();
        for (const auto &e : c.at("inputs")) {
          slam::step_table_flipper_pose(
              m, static_cast<std::int32_t>(e[0].get<std::uint32_t>()),
              static_cast<std::int32_t>(e[1].get<std::uint32_t>()));
          states.push_back(std::vector<std::uint8_t>(
              m.image.begin() + 0x3e850, m.image.begin() + 0x3e850 + 78));
        }
        out.push_back(states);
      } else {
        m.ball = c.at("bytes").get<std::array<std::uint8_t, 100>>();
        m.r[0] = 0x1000000;
        m.r[2] = 0x43e884 - c.at("index").get<unsigned>() * 26;
        m.r[4] = 0x200f000;
        m.push(0x2100000);
        try {
          slam::flipper_409050(m);
        } catch (const std::exception &e) {
          throw std::runtime_error(std::to_string(case_index) +
                                   ": contact: " + e.what());
        }
        auto result = m.r[0];
        if (result == 0 && c.value("response", false)) {
          m.r[0] = 0x1000000;
          m.r[2] = 0x43e884 - c.at("index").get<unsigned>() * 26;
          m.push(0x2100000);
          try {
            slam::flipper_4096e8(m);
          } catch (const std::exception &e) {
            throw std::runtime_error(std::to_string(case_index) +
                                     ": response: " + e.what());
          }
        }
        out.push_back({{"result", result},
                       {"bytes", m.ball},
                       {"scratch", m.rd(0x43e75c, 4)}});
      }
      ++case_index;
    }
    std::cout << out.dump() << '\n';
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
