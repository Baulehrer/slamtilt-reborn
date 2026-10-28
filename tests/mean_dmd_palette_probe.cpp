#include "dmd/mean_dmd_palette.h"
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>
int main(int argc, char **argv) {
  if (argc != 2) return 2;
  std::ifstream file(argv[1], std::ios::binary);
  const std::vector<unsigned char> dat((std::istreambuf_iterator<char>(file)), {});
  if (dat.size() < 0x1590c8 + 1024) return 3;
  std::array<unsigned char, 1024> rgba{};
  for (unsigned i = 0; i < 256; ++i) {
    for (unsigned c = 0; c < 3; ++c) rgba[i * 4 + c] = dat[0x1590c8 + i * 4 + c + 1];
    rgba[i * 4 + 3] = 255;
  }
  const auto palette = slam::mean_dmd_original_palette(rgba.data(), rgba.size());
  for (const auto &color : palette) {
    for (auto value : color) std::cout << unsigned(value) << ' ';
    std::cout << '\n';
  }
  try { slam::mean_dmd_original_palette(rgba.data(), 1023); return 4; }
  catch (const std::runtime_error &) {}
}
