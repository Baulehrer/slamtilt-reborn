#pragma once
#include "assets/windows_table.h"
namespace slam {
struct MeanLampFrames {
  int x, y, width, height;
  std::vector<std::uint8_t> mask;
  std::array<std::vector<std::uint8_t>, 2> rgba; // off,on
};
std::vector<MeanLampFrames> load_mean_lamps(const std::filesystem::path &,
                                            const TableImage &);
} // namespace slam
