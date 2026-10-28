#include "assets/mean_lamps.h"
#include <fstream>
#include <stdexcept>
namespace slam {
std::vector<MeanLampFrames> load_mean_lamps(const std::filesystem::path &path,
                                            const TableImage &table) {
  std::ifstream f(path, std::ios::binary);
  std::vector<std::uint8_t> bytes(std::istreambuf_iterator<char>(f), {});
  if (bytes.size() != 1622024)
    throw std::runtime_error("Unsupported Mean lamp DAT revision");
  struct Profile {
    int x, y, w, h;
    std::size_t offset;
  };
  // Original4387ac descriptor table; DAT masks remain user-provided.
  constexpr Profile profiles[] = {
      {80, 141, 16, 9, 0xf6f26},   {128, 104, 16, 9, 0xf6fb6},
      {240, 96, 16, 9, 0xf7046},   {224, 243, 32, 9, 0xf70d6},
      {80, 321, 32, 15, 0xf64d6},  {96, 340, 16, 15, 0xf66b6},
      {96, 359, 32, 15, 0xf67a6},  {192, 314, 32, 15, 0xf6986},
      {192, 335, 32, 15, 0xf6b66}, {192, 356, 32, 15, 0xf6d46},
      {48, 326, 32, 28, 0xf5c46},  {112, 264, 32, 21, 0xf5fc6},
      {224, 355, 48, 13, 0xf6266}, {32, 296, 32, 27, 0xf43f6},
      {64, 281, 48, 30, 0xf4756},  {112, 232, 32, 29, 0xf4cf6},
      {224, 139, 48, 21, 0xf5096}, {208, 274, 32, 34, 0xf5486},
      {240, 322, 32, 28, 0xf58c6}, {160, 316, 32, 21, 0xf4156},
      {208, 246, 32, 26, 0xf3e16}, {208, 170, 48, 17, 0xf3ae6},
      {112, 490, 80, 10, 0xf37c6}, {144, 575, 32, 21, 0xf3526},
      {0, 430, 32, 23, 0xf3246},   {48, 307, 32, 11, 0xf2d76},
      {96, 268, 16, 11, 0xf2ed6},  {192, 234, 32, 11, 0xf2f86},
      {224, 311, 32, 11, 0xf30e6}, {176, 210, 32, 23, 0xf24f6},
      {32, 38, 32, 15, 0xf27d6},   {64, 38, 32, 15, 0xf29b6},
      {80, 38, 32, 15, 0xf2b96},   {0, 456, 32, 15, 0xf1d96},
      {16, 451, 32, 15, 0xf1f76},  {48, 447, 16, 14, 0xf2156},
      {256, 447, 16, 14, 0xf2236}, {272, 451, 32, 15, 0xf2316},
      {64, 97, 32, 24, 0xf1a96},   {96, 427, 32, 25, 0xf0bd6},
      {112, 420, 32, 27, 0xf0ef6}, {144, 418, 32, 29, 0xf1256},
      {176, 422, 16, 26, 0xf15f6}, {192, 428, 32, 24, 0xf1796},
      {160, 228, 48, 25, 0xf0726}, {144, 111, 16, 6, 0xf04e6},
      {144, 111, 16, 6, 0xf0546},  {160, 111, 16, 6, 0xf05a6},
      {160, 111, 16, 6, 0xf0606},  {160, 111, 32, 6, 0xf0666},
      {64, 361, 32, 15, 0xf0306},  {16, 225, 16, 5, 0xf02b6},
      {0, 230, 16, 5, 0xf0266},    {16, 214, 32, 6, 0xf01a6},
      {0, 220, 32, 6, 0xf00e6},    {32, 203, 16, 7, 0xf0076},
      {16, 208, 16, 7, 0xf0006},   {160, 289, 32, 23, 0xefd26},
      {160, 267, 32, 23, 0xefa46}, {160, 245, 48, 23, 0xef5f6},
      {0, 482, 32, 24, 0xeeff6},   {272, 495, 32, 24, 0xef2f6},
      {48, 385, 32, 15, 0xeee16},
  };
  std::vector<MeanLampFrames> result;
  for (auto p : profiles) {
    MeanLampFrames frame{p.x, p.y, p.w, p.h, {}, {}};
    frame.mask.resize(p.w * p.h);
    for (auto &rgba : frame.rgba)
      rgba.resize(p.w * p.h * 4);
    for (int y = 0; y < p.h; ++y)
      for (int x = 0; x < p.w; ++x) {
        unsigned i = y * p.w + x;
        bool mask =
            bytes.at(p.offset + y * (p.w / 8) + x / 8) & (128 >> (x % 8));
        frame.mask[i] = mask;
        auto index =
            bytes.at(table.palette_offset + 1024 + (p.y + y) * 320 + p.x + x);
        for (unsigned on = 0; on < 2; ++on) {
          unsigned color = on ? (index & 127) : (index | 128);
          for (unsigned c = 0; c < 3; ++c)
            frame.rgba[on][i * 4 + c] = table.palette_rgba[color * 4 + c];
          frame.rgba[on][i * 4 + 3] = mask ? 255 : 0;
        }
      }
    result.push_back(std::move(frame));
  }
  return result;
}
} // namespace slam
