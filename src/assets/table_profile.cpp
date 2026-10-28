#include "assets/table_profile.h"
#include <fstream>
#include <cstdlib>
#include <limits>
#include <nlohmann/json.hpp>
#include <stdexcept>
namespace slam {
std::filesystem::path default_table_profiles() {
  if(const auto *path=std::getenv("SLAM_TABLE_PROFILES");path && *path)
    return path;
  return SLAM_TABLE_PROFILES_PATH;
}
TableProfile load_table_profile(const std::filesystem::path &path,
                                const std::string &name) {
  std::ifstream f(path);
  if (!f)
    throw std::runtime_error("Missing table profiles: " + path.string());
  nlohmann::json j;
  f >> j;
  if (j.at("schema") != 1)
    throw std::runtime_error("Unsupported table profile schema");
  const auto &table = j.at("tables").at(name);
  TableProfile p{name, table.at("dat_sha256"), {}};
  p.graphics_descriptor = std::stoul(
      table.at("graphics_descriptor").get<std::string>(), nullptr, 0);
  for (const auto &l : table.at("layers")) {
    if (l.at("layer").get<unsigned>() != p.layers.size())
      throw std::runtime_error("Non-contiguous table layers");
    const auto callback =
        std::stoul(l.at("switch_callback").get<std::string>(), nullptr, 0);
    if (callback > std::numeric_limits<std::uint32_t>::max())
      throw std::runtime_error("Invalid table callback");
    p.layers.push_back({l.at("normal_offset"), l.at("hit_offset"),
                        l.at("render_offset"), l.at("stride"), l.at("planes"),
                        std::uint32_t(callback)});
  }
  if (p.layers.empty())
    throw std::runtime_error("Empty table geometry");
  return p;
}
const TableProfile &mean_table_profile() {
  static const auto p = [] {
    auto result = load_table_profile(default_table_profiles(), "mean");
    // Original41c300..41c341 writes this extra layer during the return ramp.
    // It is not part of the initializer's four base directory entries.
    result.layers.push_back({0xd20d6, 0xd5466, 0xdb406, 0x3390, 1, 0});
    return result;
  }();
  return p;
}
void validate_table_profile(const TableProfile &p, std::size_t size) {
  for (const auto &l : p.layers) {
    if (!l.stride || l.stride % 40 || l.planes > 15 ||
        std::uint64_t(l.normal_offset) + l.stride > size ||
        std::uint64_t(l.hit_offset) + std::uint64_t(l.stride) * (l.planes + 1) >
            size ||
        l.render_offset >= size)
      throw std::runtime_error("Invalid or truncated table geometry: " +
                               p.name);
  }
}
void table_set_layer(MeanObject &ball, const TableProfile &p, unsigned layer,
                     std::uint32_t base) {
  const auto &l = p.layers.at(layer);
  for (auto offset : {l.hit_offset, l.normal_offset, l.render_offset})
    if (std::uint64_t(base) + offset >
        std::numeric_limits<std::uint32_t>::max())
      throw std::runtime_error("Table address overflow");
  ball.put32(0x40, base + l.hit_offset);
  ball.put32(0x44, base + l.normal_offset);
  ball.put32(0x54, base + l.render_offset);
  ball.put32(0x4c, l.stride);
  ball.put32(0x50, l.planes);
  ball.put16(0x48, layer);
  ball.put16(0x38, 65535);
  ball.put16(0x3a, 65535);
}
void table_configure_bits(const MeanObject &ball, const TableProfile &p,
                          std::uint32_t base, MeanCollisionBits &bits) {
  (void)p.layers.at(
      ball.u16(0x48)); // Special shifted pointers are retained below.
  const auto pointer = std::uint32_t(ball.i32(0x40));
  const auto stride = std::uint32_t(ball.i32(0x4c));
  const auto planes = std::uint32_t(ball.i32(0x50));
  if (pointer < base || !stride || stride % 40 || planes > 15 ||
      std::uint64_t(pointer - base) + std::uint64_t(stride) * (planes + 1) >
          bits.dat.size())
    throw std::runtime_error("Invalid original table collision pointer");
  bits.hit_offset = pointer - base;
  bits.stride = stride;
  bits.extra_planes = planes;
}
std::vector<std::uint8_t>
table_collision_overlay(const std::filesystem::path &dat, const TableProfile &p,
                        unsigned layer, unsigned height) {
  std::ifstream f(dat, std::ios::binary);
  if (!f)
    throw std::runtime_error("Missing table DAT");
  MeanCollisionBits bits;
  bits.dat.assign(std::istreambuf_iterator<char>(f), {});
  validate_table_profile(p, bits.dat.size());
  const auto &l = p.layers.at(layer);
  bits.hit_offset = l.hit_offset;
  bits.stride = l.stride;
  bits.extra_planes = l.planes;
  std::vector<std::uint8_t> rgba(320 * height * 4, 0);
  for (unsigned y = 0; y < height && y < l.stride / 40; ++y)
    for (unsigned x = 0; x < 320; ++x)
      if (bits.sample(x, y)) {
        const auto o = (y * 320 + x) * 4;
        rgba[o] = 255;
        rgba[o + 1] = 30;
        rgba[o + 2] = 30;
        rgba[o + 3] = 100;
      }
  return rgba;
}
} // namespace slam
