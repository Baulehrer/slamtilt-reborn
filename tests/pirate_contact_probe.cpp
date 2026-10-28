#include "physics/pirate_contact.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 3)
    return 2;
  std::ifstream f(argv[1]);
  nlohmann::json j;
  f >> j;
  std::ifstream lut(argv[2], std::ios::binary);
  std::vector<std::uint8_t> data{std::istreambuf_iterator<char>(lut), {}};
  slam::MeanLookup l;
  l.field_43e764.assign(data.begin(), data.begin() + 8192);
  l.field_43e744.assign(data.begin() + 0x800, data.end());
  auto out = nlohmann::json::array();
  for (auto &c : j) {
    slam::MeanObject b;
    b.bytes = c.at("bytes").get<decltype(b.bytes)>();
    slam::PirateContactState s;
    s.field_services_1c = c.at("services_1c");
    s.layer0_hit = c.at("layer0")[0];
    s.layer0_normal = c.at("layer0")[1];
    s.layer0_render = c.at("layer0")[2];
    s.layer0_stride = c.at("layer0")[3];
    s.layer0_planes = c.at("layer0")[4];
    bool ok = slam::pirate_contact(b, l, s, c.at("offset_x"), c.at("offset_y"));
    out.push_back({{"supported", ok}, {"bytes", b.bytes}});
  }
  std::cout << out.dump() << '\n';
}
