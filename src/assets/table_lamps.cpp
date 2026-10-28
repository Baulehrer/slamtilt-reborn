#include "assets/table_lamps.h"
#include <fstream>
#include <stdexcept>

namespace slam {
namespace {
std::uint16_t word(const std::vector<std::uint8_t> &image,
                   std::uint64_t address) {
  if (address < 0x400000 || address - 0x400000 + 2 > image.size())
    throw std::runtime_error("Invalid original lamp descriptor address");
  const auto offset = std::size_t(address - 0x400000);
  return std::uint16_t(image[offset] | (image[offset + 1] << 8));
}
std::uint32_t dword(const std::vector<std::uint8_t> &image,
                    std::uint64_t address) {
  return std::uint32_t(word(image, address)) |
         (std::uint32_t(word(image, address + 2)) << 16);
}
int signed_word(const std::vector<std::uint8_t> &image, std::uint64_t address) {
  const auto value = word(image, address);
  return value < 0x8000 ? int(value) : int(value) - 0x10000;
}
} // namespace

unsigned
TableLampFrames::frame(const std::vector<std::uint8_t> &mapped_image) const {
  const auto state = word(mapped_image, std::uint64_t(descriptor) + 8);
  if (state != 0 && state != 0xffff)
    throw std::runtime_error("Invalid original lamp visible state");
  return state == 0xffff ? 1u : 0u;
}

std::vector<TableLampSprite>
table_lamp_sprite_profiles(const TableDefinition &definition,
                           const std::vector<std::uint8_t> &image,
                           std::uint32_t dat_base) {
  if (definition.geometry_build.executable_sha256 !=
          "185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6" ||
      dword(image, 0x46c644) != definition.geometry_build.returned_descriptor)
    throw std::runtime_error("Unsupported or unprepared table lamp image");
  const auto metadata = dword(
      image, std::uint64_t(definition.geometry_build.returned_descriptor) + 8);
  const auto descriptors = dword(image, std::uint64_t(metadata) + 0x10);
  const auto count = dword(image, 0x46c6a4);
  if (!count || count > 256)
    throw std::runtime_error("Invalid original table lamp count");
  std::vector<TableLampSprite> result;
  result.reserve(count);
  for (unsigned i = 0; i < count; ++i) {
    const auto descriptor = dword(image, std::uint64_t(descriptors) + i * 4);
    const auto source = dword(image, std::uint64_t(descriptor) + 0x10);
    const auto x = signed_word(image, descriptor);
    const auto y = signed_word(image, std::uint64_t(descriptor) + 2);
    const auto width = signed_word(image, std::uint64_t(descriptor) + 4) * 16;
    const auto height = signed_word(image, std::uint64_t(descriptor) + 6);
    if (x < 0 || y < 0 || width <= 0 || height <= 0 || x + width > 320 ||
        y + height > 600 || source < dat_base)
      throw std::runtime_error("Invalid original table lamp bounds/source");
    result.push_back(
        {descriptor, std::size_t(source - dat_base), x, y, width, height});
  }
  return result;
}

std::vector<TableLampFrames>
load_table_lamps(const std::filesystem::path &path,
                 const TableDefinition &definition, const TableImage &table,
                 const std::vector<std::uint8_t> &image,
                 std::uint32_t dat_base) {
  std::ifstream input(path, std::ios::binary);
  if (!input)
    throw std::runtime_error("Cannot open lamp DAT: " + path.string());
  const std::vector<std::uint8_t> dat{std::istreambuf_iterator<char>(input),
                                      {}};
  validate_table_dat(definition, dat);
  if (table.width != 320 || table.height != 600 ||
      table.rgba.size() != 320 * 600 * 4 || table.palette_offset > dat.size() ||
      1024 + 320 * 600 > dat.size() - table.palette_offset)
    throw std::runtime_error("Invalid active table image for lamp sprites");
  std::vector<TableLampFrames> result;
  for (const auto &sprite :
       table_lamp_sprite_profiles(definition, image, dat_base)) {
    const auto pixels = std::size_t(sprite.width) * sprite.height;
    if (sprite.dat_offset > dat.size() ||
        pixels / 8 > dat.size() - sprite.dat_offset)
      throw std::runtime_error("Truncated original table lamp mask");
    TableLampFrames frames{sprite.descriptor, sprite.x, sprite.y, sprite.width,
                           sprite.height,     {},       {}};
    frames.mask.resize(pixels);
    for (auto &rgba : frames.rgba)
      rgba.resize(pixels * 4);
    for (std::size_t i = 0; i < pixels; ++i) {
      const auto x = int(i % sprite.width);
      const auto y = int(i / sprite.width);
      const bool opaque =
          (dat[sprite.dat_offset + y * (sprite.width / 8) + x / 8] &
           (128u >> (x & 7))) != 0;
      frames.mask[i] = opaque;
      const auto source_index = dat[table.palette_offset + 1024 +
                                    (sprite.y + y) * 320 + sprite.x + x];
      for (unsigned on = 0; on < 2; ++on) {
        const unsigned color = on ? source_index & 127u : source_index | 128u;
        for (unsigned channel = 0; channel < 3; ++channel)
          frames.rgba[on][i * 4 + channel] =
              table.palette_rgba[color * 4 + channel];
        frames.rgba[on][i * 4 + 3] = opaque ? 255 : 0;
      }
    }
    result.push_back(std::move(frames));
  }
  return result;
}
} // namespace slam
