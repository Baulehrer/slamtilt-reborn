#include "assets/menu_assets.h"
#include "core/sha256.h"
#include <fstream>
#include <stdexcept>
namespace slam {
TableImage load_windows_menu(const std::filesystem::path &path) {
  constexpr std::size_t file_size = 3338232;
  constexpr std::size_t pixels = 0xb2bc8, palette = 0x32ecf8;
  std::ifstream input(path, std::ios::binary | std::ios::ate);
  if (!input || input.tellg() != std::streampos(file_size))
    throw std::runtime_error("Unsupported or missing original MENU.DAT");
  std::vector<std::uint8_t> bytes(file_size);
  input.seekg(0);
  if (!input.read(reinterpret_cast<char *>(bytes.data()), file_size))
    throw std::runtime_error("Cannot read original MENU.DAT");
  if (sha256(bytes) !=
      "eb46503d8a7b7b70366403ffc5a4d9075271bafa10a7efac3abc761dcb5990ee")
    throw std::runtime_error("Unsupported original MENU.DAT revision");
  TableImage image;
  image.width = 640;
  image.height = 480;
  image.palette_offset = palette;
  for (std::size_t i = 0; i < 256; ++i) {
    for (int c = 0; c < 3; ++c)
      image.palette_rgba[4 * i + c] = bytes[palette + 3 * i + c];
    image.palette_rgba[4 * i + 3] = 255;
  }
  image.rgba.resize(640 * 480 * 4);
  for (int y = 0; y < image.height; ++y)
    for (int x = 0; x < image.width; ++x) {
      const auto color = bytes[pixels + (479 - y) * 640 + x];
      for (int c = 0; c < 4; ++c)
        image.rgba[(y * 640 + x) * 4 + c] = image.palette_rgba[color * 4 + c];
    }
  return image;
}
} // namespace slam
