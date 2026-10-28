#include "physics/flipper_lift.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
std::vector<std::uint8_t> read(const std::string &p) {
  std::ifstream f(p, std::ios::binary);
  if (!f)
    throw std::runtime_error("Missing lift input");
  return {std::istreambuf_iterator<char>(f), {}};
}
int main(int argc, char **argv) {
  try {
    if (argc != 3)
      return 2;
    std::string base = argv[1];
    std::ifstream f(argv[2]);
    nlohmann::json cases;
    f >> cases;
    slam::FlipperLift initial;
    initial.image = read(base + "/pe-data.bin");
    initial.image.resize(0x100000);
    auto globals = read(base + "/engine-globals.bin"),
         flippers = read(base + "/flipper-state.bin");
    std::copy(globals.begin(), globals.end(), initial.image.begin() + 0x3e700);
    std::copy(flippers.begin(), flippers.end(),
              initial.image.begin() + 0x3e850);
    auto results = nlohmann::json::array();
    for (const auto &c : cases) {
      auto m = initial;
      if (c.value("operation", std::string{}) == "pose") {
        auto out = nlohmann::json::array();
        for (const auto &inputs : c.at("inputs")) {
          m.wr(0x4298b8, inputs.at(0).get<std::uint32_t>(), 4);
          m.wr(0x4298bc, inputs.at(1).get<std::uint32_t>(), 4);
          m.wr(0x4298c0, inputs.at(1).get<std::uint32_t>(), 4);
          m.r[4] = 0x200f000;
          m.push(0x2100000);
          slam::flipper_4084bc(m);
          std::vector<std::uint8_t> poses(m.image.begin() + 0x3e850,
                                          m.image.begin() + 0x3e850 + 78);
          out.push_back(poses);
        }
        results.push_back(out);
        continue;
      }
      m.ball = c.at("bytes").get<std::array<std::uint8_t, 100>>();
      m.r[0] = 0x1000000;
      m.r[2] = c.at("descriptor");
      m.r[4] = 0x200f000;
      m.push(0x2100000);
      slam::flipper_409050(m);
      const auto result = m.r[0];
      if (c.at("response") == true && result == 0) {
        m.r[0] = 0x1000000;
        m.r[2] = c.at("descriptor");
        m.push(0x2100000);
        slam::flipper_4096e8(m);
      }
      results.push_back({{"result", result},
                         {"bytes", m.ball},
                         {"field_43e75c", m.rd(0x43e75c, 4)}});
    }
    std::cout << results.dump() << '\n';
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
