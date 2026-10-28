#pragma once
#include <array>
#include <cstdint>
#include <filesystem>
#include <vector>
namespace slam {
struct TableImage {
  int width = 320;
  int height = 600;
  std::vector<std::uint8_t> rgba;
  std::array<std::uint8_t, 1024> palette_rgba{};
  std::size_t palette_offset = 0;
};
TableImage load_windows_table(const std::filesystem::path &path);
TableImage load_amiga_table(const std::filesystem::path &path);
} // namespace slam
