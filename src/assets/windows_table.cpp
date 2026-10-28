#include "assets/windows_table.h"
#include <array>
#include <fstream>
#include <stdexcept>
#include <string>
namespace slam {
TableImage load_windows_table(const std::filesystem::path &path) {
  std::ifstream stream(path, std::ios::binary | std::ios::ate);
  if (!stream)
    throw std::runtime_error("Cannot open DAT: " + path.string());
  const auto size = stream.tellg();
  if (size < 0 || size > 32 * 1024 * 1024)
    throw std::runtime_error("Invalid DAT size");
  std::vector<std::uint8_t> bytes(static_cast<std::size_t>(size));
  stream.seekg(0);
  if (!stream.read(reinterpret_cast<char *>(bytes.data()), size))
    throw std::runtime_error("Cannot read DAT");
  // Profiles recovered from per-table Windows initializers; see
  // docs/file-formats.md.
  struct Profile {
    std::size_t size, palette;
  };
  constexpr std::array<Profile, 4> profiles{{{1622024, 0x1590c8},
                                             {1543772, 0x14605c},
                                             {1568309, 0x14c035},
                                             {1546096, 0x146830}}};
  const Profile *profile = nullptr;
  for (const auto &item : profiles)
    if (item.size == bytes.size())
      profile = &item;
  if (!profile)
    throw std::runtime_error("Unsupported Windows table DAT revision/size");
  const auto palette = profile->palette;
  constexpr std::size_t pixel_count = 320 * 600;
  const auto pixels = palette + 1024;
  if (pixels + pixel_count > bytes.size())
    throw std::runtime_error("Truncated table image");
  for (std::size_t i = 0; i < 256; ++i)
    if (bytes[palette + i * 4] != 0)
      throw std::runtime_error("Invalid 00RRGGBB palette for this profile");
  TableImage result;
  result.palette_offset = palette;
  for (std::size_t i = 0; i < 256; ++i) {
    for (int c = 0; c < 3; ++c)
      result.palette_rgba[i * 4 + c] = bytes[palette + i * 4 + 1 + c];
    result.palette_rgba[i * 4 + 3] = 255;
  }
  result.rgba.resize(pixel_count * 4);
  for (std::size_t i = 0; i < pixel_count; ++i) {
    const auto color = palette + bytes[pixels + i] * 4;
    for (int channel = 0; channel < 3; ++channel)
      result.rgba[i * 4 + channel] = bytes[color + 1 + channel];
    result.rgba[i * 4 + 3] = 255;
  }
  return result;
}
} // namespace slam
