#include "physics/pirate_step_lift.h"
#include <fstream>
#include <iostream>
#include <iterator>
#include <nlohmann/json.hpp>
#include <stdexcept>

using json = nlohmann::json;

int main(int argc, char **argv) {
  try {
    if (argc != 3) return 1;
    const std::string base = argv[1];
    const auto read = [&](const std::string &name) {
      std::ifstream in(base + "/" + name, std::ios::binary);
      if (!in) throw std::runtime_error("missing context");
      return std::vector<std::uint8_t>{std::istreambuf_iterator<char>(in), {}};
    };
    const auto image = read("human-image.bin"), runtime = read("human-runtime.bin"), dat = read("human-dat.bin");
    std::ifstream source(argv[2]);
    if (!source) return 1;
    json cases; source >> cases;
    json result = json::array();
    for (const auto &entry : cases) {
      slam::PirateStepLift machine;
      machine.image = image; machine.runtime = runtime; machine.dat = dat;
      machine.wr(0x46d60c,0x1000100,4);
      machine.wr(0x100011c,entry.at("counter").get<unsigned>(),4);
      machine.wr(0x46d5e0,entry.at("phase").get<unsigned>(),4);
      machine.wr(0x46d600,entry.at("position").get<unsigned>(),4);
      machine.wr(0x463b64,entry.at("previous").get<unsigned>(),4);
      machine.wr(0x46d64c,0x1005000,4);
      machine.wr(0x100505c,0x2100100,4);
      machine.wr(0x100503c,0x2100104,4);
      json events=json::array();
      machine.external_service = [&](slam::PirateStepLift &m, std::uint32_t address) {
        if (address == 0x2100100)
          events.push_back({m.r[0],m.r[2],m.r[3]});
        else if (address != 0x2100104)
          throw std::runtime_error("unexpected adapted service");
        (void)m.pop();
      };
      machine.invoke(0x413048);
      result.push_back({{"events",events},{"counter",machine.rd(0x100011c,4)},
                        {"previous",machine.rd(0x463b64,4)}});
    }
    std::cout << result.dump() << '\n';
  } catch (const std::exception &e) {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
