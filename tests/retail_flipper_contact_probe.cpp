#include "assets/table_flippers.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 3)
    return 2;
  std::ifstream image(argv[1], std::ios::binary), file(argv[2]);
  slam::FlipperLift initial;
  initial.image.assign(std::istreambuf_iterator<char>(image), {});
  nlohmann::json cases;
  file >> cases;
  auto out = nlohmann::json::array();
  for (const auto &c : cases) {
    auto m = initial;
    m.ball = c.at("bytes").get<decltype(m.ball)>();
    auto result =
        slam::retail_table_flipper_contact(m, c.at("index").get<unsigned>());
    out.push_back({{"result", result},
                   {"bytes", m.ball},
                   {"scratch", m.rd(0x46c660, 4)}});
  }
  std::cout << out.dump() << '\n';
}
