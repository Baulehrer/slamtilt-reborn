#include "assets/mean_flippers.h"
#include <algorithm>
#include <fstream>
#include <stdexcept>
namespace slam {
unsigned FlipperFrames::frame(std::uint16_t pose) const {
  return std::min(unsigned((pose >> 10) + ((pose >> 9) & 1)),
                  unsigned(rgba.size() - 1));
}
static std::vector<FlipperFrames>
load_mean_frames(const std::filesystem::path &path, const TableImage &table,
                 bool contacts) {
  std::ifstream f(path, std::ios::binary);
  std::vector<std::uint8_t> dat(std::istreambuf_iterator<char>(f), {});
  if (dat.size() != 1622024)
    throw std::runtime_error("Unsupported Mean flipper DAT");
  struct Profile {
    std::size_t offset;
    int x, y, w, h, count;
  };
  std::vector<FlipperFrames> result;
  const std::vector<Profile> profiles =
      contacts ? std::vector<Profile>{{0x85cfe, 0, 549, 64, 51, 3},
                                      {0x91dee, 240, 550, 64, 50, 3},
                                      {0x82dbe, 0, 140, 48, 66, 3},
                                      {0x852de, 272, 473, 32, 27, 3}}
               : std::vector<Profile>{{0x6eabe, 92, 533, 64, 45, 10},
                                      {0x75b3e, 170, 533, 64, 45, 10},
                                      {0x7cbbe, 256, 145, 64, 49, 8}};
  for (const auto &p : profiles) {
    FlipperFrames frames{p.x, p.y, p.w, p.h, {}};
    for (int frame = 0; frame < p.count; ++frame) {
      std::vector<std::uint8_t> pixels(p.w * p.h * 4);
      for (int i = 0; i < p.w * p.h; ++i) {
        const auto index = dat.at(p.offset + frame * p.w * p.h + i);
        for (int c = 0; c < 3; ++c)
          pixels[i * 4 + c] = table.palette_rgba[index * 4 + c];
        pixels[i * 4 + 3] = !contacts && index <= 1 ? 0 : 255;
      }
      frames.rgba.push_back(std::move(pixels));
    }
    result.push_back(std::move(frames));
  }
  return result;
}
std::vector<FlipperFrames> load_mean_flippers(const std::filesystem::path &path,
                                              const TableImage &table) {
  return load_mean_frames(path, table, false);
}
std::vector<FlipperFrames>
load_mean_contact_frames(const std::filesystem::path &path,
                         const TableImage &table) {
  return load_mean_frames(path, table, true);
}
} // namespace slam
