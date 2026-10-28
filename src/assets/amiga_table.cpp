#include "assets/windows_table.h"
#include <fstream>
#include <stdexcept>
namespace slam {
TableImage load_amiga_table(const std::filesystem::path &path) {
  std::ifstream file(path, std::ios::binary | std::ios::ate);
  if (!file)
    throw std::runtime_error("Cannot open decoded Amiga RAW");
  const auto size = file.tellg();
  if (size < 24 || size > 64 * 1024 * 1024)
    throw std::runtime_error("Invalid decoded RAW size");
  std::vector<std::uint8_t> data(static_cast<std::size_t>(size));
  file.seekg(0);
  if (!file.read(reinterpret_cast<char *>(data.data()), size))
    throw std::runtime_error("Cannot read RAW");
  if (data[0] == 'S' && data[1] == 'L' && data[2] == 'A' && data[3] == 'M')
    throw std::runtime_error(
        "Compressed RAW: first run python tools/slamdecode.py INPUT OUTPUT");
  auto be32 = [&](std::size_t offset) -> std::size_t {
    if (offset > data.size() - 4)
      throw std::runtime_error("Section outside RAW");
    return (std::uint32_t(data[offset]) << 24) |
           (std::uint32_t(data[offset + 1]) << 16) |
           (std::uint32_t(data[offset + 2]) << 8) | data[offset + 3];
  };
  const auto section = be32(0);
  if (section > data.size() - 24)
    throw std::runtime_error("Missing playfield section");
  const auto pixels_offset = be32(section);
  const auto palette_offset = be32(section + 4);
  if (pixels_offset != 24 || palette_offset != 0x32938)
    throw std::runtime_error("Unsupported Amiga playfield layout");
  if (data.size() - section < palette_offset + 1024 ||
      data.size() - section < pixels_offset + 192000)
    throw std::runtime_error("Truncated Amiga playfield");
  const auto start = section + pixels_offset;
  const auto palette = section + palette_offset;
  for (std::size_t i = 0; i < 256; ++i)
    if (data[palette + 4 * i] != 0)
      throw std::runtime_error("Invalid Amiga palette");
  TableImage result;
  result.palette_offset = palette;
  for (std::size_t i = 0; i < 256; ++i) {
    for (int c = 0; c < 3; ++c)
      result.palette_rgba[i * 4 + c] = data[palette + i * 4 + 1 + c];
    result.palette_rgba[i * 4 + 3] = 255;
  }
  result.rgba.resize(320 * 600 * 4);
  for (std::size_t y = 0; y < 600; ++y)
    for (std::size_t x = 0; x < 320; ++x) {
      unsigned index = 0;
      for (unsigned plane = 0; plane < 8; ++plane)
        index |=
            ((data[start + y * 320 + plane * 40 + x / 8] >> (7 - x % 8)) & 1u)
            << plane;
      const auto color = palette + 4 * index;
      const auto destination = (y * 320 + x) * 4;
      for (int channel = 0; channel < 3; ++channel)
        result.rgba[destination + channel] = data[color + 1 + channel];
      result.rgba[destination + 3] = 255;
    }
  return result;
}
} // namespace slam
