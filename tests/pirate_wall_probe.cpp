#include "physics/pirate_contact.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc, char **argv) {
  if (argc != 4)
    return 2;
  std::ifstream f(argv[1]);
  nlohmann::json cases;
  f >> cases;
  std::ifstream d(argv[2], std::ios::binary), l(argv[3], std::ios::binary);
  slam::MeanCollisionBits bits;
  bits.dat.assign(std::istreambuf_iterator<char>(d), {});
  slam::MeanLookup lookup;
  lookup.field_43e764.assign(std::istreambuf_iterator<char>(l), {});
  lookup.field_43e744.assign(lookup.field_43e764.begin() + 0x800,
                             lookup.field_43e764.end());
  auto p = slam::load_table_profile(slam::default_table_profiles(), "pirate");
  auto rows = nlohmann::json::array();
  const auto &g = p.layers.at(0);
  const unsigned base = 0x1100000;
  slam::PirateContactState state{0,
                                 base + g.hit_offset,
                                 base + g.normal_offset,
                                 base + g.render_offset,
                                 g.stride,
                                 g.planes};
  for (const auto &c : cases) {
    slam::MeanObject b;
    b.bytes = c.at("bytes").get<decltype(b.bytes)>();
    auto ok = slam::pirate_wall_contact(b, lookup, state, bits, p, base);
    rows.push_back({{"supported", ok}, {"bytes", b.bytes}});
  }
  std::cout << rows.dump() << '\n';
}
