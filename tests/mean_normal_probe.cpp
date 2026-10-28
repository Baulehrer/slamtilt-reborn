#include "physics/mean_normal_lift.h"
#include <fstream>
#include <iostream>
#include <iterator>
static std::vector<std::uint8_t> read(const char* path) {
  std::ifstream in(path, std::ios::binary);
  return {std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>()};
}
int main(int argc, char** argv) {
  if (argc != 3) return 2;
  slam::MeanNormalLift m;
  m.image = read(argv[1]); m.image.resize(0x100000);
  const auto dat = read(argv[2]); m.dat = &dat;
  std::uint32_t input[5];
  while (std::cin.read(reinterpret_cast<char*>(input), sizeof(input))) {
    m.wr(0x1000000, input[0], 4); m.wr(0x1000004, input[1], 4);
    m.wr(0x1000044, 0x1100000 + input[2], 4);
    m.wr(0x43e71c, input[3], 4); m.wr(0x43e410, input[4], 4);
    m.r[0] = 0x1000000; m.r[4] = 0x200f000; m.push(0);
    slam::flipper_40e1d0(m);
    std::cout.write(reinterpret_cast<char*>(&m.r[0]), 4);
  }
}
