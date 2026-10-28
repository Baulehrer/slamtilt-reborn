#include "assets/table_sprites.h"
#include <fstream>
#include <stdexcept>

namespace slam {
std::vector<TableFlipperSprite>
table_flipper_sprite_profiles(const TableDefinition &definition) {
  if (definition.geometry_build.executable_sha256 !=
      "185d5893c76f025caf5fd08f0aedd35d682123f6ac383b67ba21db0adf14e1c6")
    throw std::runtime_error("Unsupported flipper sprite build");
  // WORD fields +0c/+0e/+10/+12/+14 give width/height/X/Y/count;
  // WORD+04 selects the table geometry's foreground bitmap.
  // Initializers write DAT+offset at descriptor+1c:
  // Mean 41c0ea..41c14b, Pirate 42b9b2..42ba08,
  // Space 43a10a..43a16b, Demon 4103e5..410412.
  if (definition.id == "mean")
    return {{0x464b0c, 0x6eabe, 92, 533, 64, 45, 10, 0},
            {0x464b30, 0x75b3e, 170, 533, 64, 45, 10, 0},
            {0x464b54, 0x7cbbe, 256, 145, 64, 49, 8, 2}};
  if (definition.id == "pirate")
    return {{0x4658cc, 0x64484, 80, 540, 64, 45, 10, 0},
            {0x4658f0, 0x6b504, 160, 540, 64, 45, 10, 0},
            {0x465914, 0x72584, 224, 188, 64, 51, 7, 0}};
  if (definition.id == "space")
    return {{0x4665c0, 0x6fd15, 70, 533, 64, 45, 10, 0},
            {0x4665e4, 0x76d95, 148, 533, 64, 45, 10, 0},
            {0x466608, 0x7de15, 48, 210, 64, 51, 8, 0}};
  if (definition.id == "demon")
    return {{0x463aec, 0x84bf6, 80, 535, 64, 45, 10, 0},
            {0x463b10, 0x8bc76, 160, 535, 64, 45, 10, 0}};
  throw std::runtime_error("Unsupported flipper sprite table");
}
std::vector<FlipperFrames>
load_table_flippers(const std::filesystem::path &path,
                    const TableDefinition &definition, const TableImage &table) {
  std::ifstream input(path, std::ios::binary);
  if (!input)
    throw std::runtime_error("Cannot open flipper DAT: " + path.string());
  const std::vector<std::uint8_t> dat{std::istreambuf_iterator<char>(input), {}};
  validate_table_dat(definition, dat);
  if (table.width != 320 || table.height != 600 ||
      table.rgba.size() != 320 * 600 * 4)
    throw std::runtime_error("Invalid active table image for flipper sprites");
  std::vector<FlipperFrames> result;
  for (const auto &sprite : table_flipper_sprite_profiles(definition)) {
    const auto &layer = definition.geometry.layers.at(sprite.geometry_layer);
    const auto pixels = std::size_t(sprite.width) * sprite.height;
    if (sprite.dat_offset + pixels * sprite.frame_count > dat.size() ||
        sprite.x < 0 || sprite.y < 0 || sprite.x + sprite.width > 320 ||
        sprite.y + sprite.height > 600 ||
        (std::size_t(sprite.y + sprite.height - 1) * 40 +
         (sprite.x + sprite.width - 1) / 8) >= layer.stride)
      throw std::runtime_error("Invalid flipper sprite/foreground range");
    FlipperFrames frames{sprite.x, sprite.y, sprite.width, sprite.height, {}};
    for (unsigned frame = 0; frame < sprite.frame_count; ++frame) {
      std::vector<std::uint8_t> rgba(pixels * 4);
      for (std::size_t i = 0; i < pixels; ++i) {
        const auto index = dat.at(sprite.dat_offset + frame * pixels + i);
        const auto x = sprite.x + int(i % sprite.width);
        const auto y = sprite.y + int(i / sprite.width);
        // 40b79c..40b7ea: bit 7-(X&7), row stride40, selected directory+10.
        const auto foreground = dat.at(layer.render_offset + y * 40 + x / 8);
        const bool occluded = (foreground & (1u << (7 - (x & 7)))) != 0;
        for (unsigned channel = 0; channel < 3; ++channel)
          rgba[i * 4 + channel] = table.palette_rgba[index * 4 + channel];
        rgba[i * 4 + 3] = index <= 1 || occluded ? 0 : 255;
      }
      frames.rgba.push_back(std::move(rgba));
    }
    result.push_back(std::move(frames));
  }
  return result;
}
std::vector<std::uint8_t> compose_table_flipper(
    const TableFlipperSprite &profile, const FlipperFrames &sprite,
    unsigned frame, const TableImage &table,
    const std::vector<std::uint8_t> &image,
    const std::vector<std::uint8_t> &dat, std::uint32_t dat_base) {
  const auto read32 = [&](std::uint64_t address) {
    if (address < 0x400000 || address - 0x400000 + 4 > image.size())
      throw std::runtime_error("Invalid flipper descriptor address");
    const auto offset = std::size_t(address - 0x400000);
    std::uint32_t value = 0;
    for (unsigned i = 0; i < 4; ++i)
      value |= std::uint32_t(image[offset + i]) << (8 * i);
    return value;
  };
  if (sprite.width <= 0 || sprite.height <= 0 ||
      sprite.width != profile.width || sprite.height != profile.height ||
      frame >= profile.frame_count || frame >= sprite.rgba.size())
    throw std::runtime_error("Invalid composited flipper frame");
  const auto pixels = std::size_t(sprite.width) * sprite.height;
  auto rgba = sprite.rgba.at(frame);
  const std::uint64_t source = read32(std::uint64_t(profile.descriptor) + 0x1c);
  const std::uint64_t mask = read32(std::uint64_t(profile.descriptor) + 0x20);
  if (rgba.size() != pixels * 4 || source < dat_base ||
      source - dat_base != profile.dat_offset ||
      source - dat_base + (std::uint64_t(frame) + 1) * pixels > dat.size() ||
      mask < 0x400000 || mask - 0x400000 + pixels > image.size())
    throw std::runtime_error("Invalid composited flipper source/mask");
  for (std::size_t i = 0; i < pixels; ++i) {
    const auto index = dat[source - dat_base + frame * pixels + i] &
                       std::uint8_t(~image[mask - 0x400000 + i]);
    for (unsigned c = 0; c < 3; ++c)
      rgba[i * 4 + c] = table.palette_rgba[index * 4 + c];
  }
  return rgba;
}
} // namespace slam
