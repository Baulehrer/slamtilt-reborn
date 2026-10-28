#pragma once
#include "assets/windows_table.h"
#include <filesystem>
#include <vector>
namespace slam {
struct FlipperFrames {
  int x, y, width, height;
  std::vector<std::vector<std::uint8_t>> rgba;
  unsigned frame(std::uint16_t pose) const;
};
std::vector<FlipperFrames> load_mean_flippers(const std::filesystem::path &dat,
                                              const TableImage &table);
std::vector<FlipperFrames>
load_mean_contact_frames(const std::filesystem::path &dat,
                         const TableImage &table);
} // namespace slam
