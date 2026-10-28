#include "assets/table_flippers.h"
#include <algorithm>
#include <stdexcept>
namespace slam {
TableFlipperParameters
load_table_flipper_parameters(const std::vector<std::uint8_t> &image,
                              std::uint32_t graphics) {
  const auto word = [&](std::uint32_t a) {
    if (a < 0x400000 || std::uint64_t(a) - 0x400000 + 2 > image.size())
      throw std::runtime_error("Invalid original flipper parameter address");
    const auto o = a - 0x400000;
    return std::uint16_t(image[o] | (image[o + 1] << 8));
  };
  const auto dword = [&](std::uint32_t a) {
    return std::uint32_t(word(a)) | (std::uint32_t(word(a + 2)) << 16);
  };
  TableFlipperParameters p;
  p.field_1c = word(graphics + 0x1c);
  for (unsigned i = 0; i < (p.field_1c ? 3u : 2u); ++i) {
    const auto a = dword(graphics + 0xc + i * 4);
    for (unsigned j = 0; j < 12; j += 2) {
      const auto v = word(a + j);
      p.records[i][j] = v;
      p.records[i][j + 1] = v >> 8;
    }
  }
  return p;
}
void configure_table_flippers(FlipperLift &m, const TableFlipperParameters &p) {
  constexpr std::array<unsigned, 6> offsets{0, 2, 24, 4, 6, 8};
  constexpr std::array<std::uint32_t, 3> addresses{0x43e884, 0x43e86a,
                                                   0x43e850};
  for (unsigned i = 0; i < 3; ++i) {
    for (unsigned j = 0; j < 26; ++j)
      m.wr(addresses[i] + j, 0, 1);
    if (i == 2 && !p.field_1c)
      continue;
    for (unsigned j = 0; j < 6; ++j)
      m.wr(addresses[i] + offsets[j],
           unsigned(p.records[i][j * 2]) |
               (unsigned(p.records[i][j * 2 + 1]) << 8),
           2);
  }
  // The lift only reads this descriptor chain's third-flipper enable flag.
  m.wr(0x43e740, 0x43ff00, 4);
  m.wr(0x43ff00, 0x43ff80, 4);
  m.wr(0x43ff80 + 0x1c, p.field_1c, 2);
}
} // namespace slam

namespace slam {
void step_table_flipper_pose(FlipperLift &m, std::int32_t left,
                             std::int32_t right) {
  if (left < -1 || left > 1 || right < -1 || right > 1)
    throw std::runtime_error("Invalid original flipper input edge");
#ifdef SLAM_MEAN_FLIPPER_LIFT
  m.wr(0x4298b8, std::uint32_t(left), 4);
  m.wr(0x4298bc, std::uint32_t(right), 4);
  m.wr(0x4298c0, std::uint32_t(right), 4);
  m.r[4] = 0x200f000;
  m.push(0x2100000);
  flipper_4084bc(m);
#else
  (void)m;
  throw std::runtime_error(
      "Prepare original flipper lift before stepping poses");
#endif
}
} // namespace slam

namespace slam {
#ifdef SLAM_RETAIL_FLIPPER_LIFT
void flipper_409ce8(FlipperLift &);
void flipper_40a380(FlipperLift &);
#endif
std::uint32_t retail_table_flipper_contact(FlipperLift &m, unsigned index) {
  if (index > 2)
    throw std::out_of_range("Retail flipper index");
#ifdef SLAM_RETAIL_FLIPPER_LIFT
  const auto invoke = [&](auto routine) {
    m.r[0] = 0x1000000;
    m.r[2] = 0x46c77c - index * 26;
    m.r[4] = 0x200f000;
    m.push(0x2100000);
    routine(m);
  };
  invoke(flipper_409ce8);
  const auto result = m.r[0];
  if (result == 0)
    invoke(flipper_40a380);
  return result;
#else
  (void)m;
  throw std::runtime_error("Prepare original Retail flipper lift first");
#endif
}
} // namespace slam
