#include "mean_mode4_idle.h"
#include <algorithm>
#include <cstring>
#include <fstream>
#include <stdexcept>
namespace slam {
MeanMode4IdleAssets load_mean_mode4_idle(const std::filesystem::path &p) {
  std::ifstream in(p, std::ios::binary);
  MeanMode4IdleAssets a;
  auto read = [&](std::size_t off, auto &bytes) {
    in.seekg(off);
    in.read(reinterpret_cast<char *>(bytes.data()), bytes.size());
    if (!in)
      throw std::runtime_error("Truncated Mean mode4 idle DMD");
  };
  for (unsigned i = 0; i < 5; ++i)
    read(0x10482e + i * 480, a.frames_10482e[i]);
  for (unsigned i = 0; i < 20; ++i)
    read(0xf9776 + i * 120, a.needles_f9776[i]);
  return a;
}
MeanMode4IdleEvents mean_mode4_idle(MeanBallResetState &s,
                                    const MeanMode4IdleAssets &a,
                                    WindowsDmdPixels &pixels,
                                    std::int32_t lookup, std::uint32_t handle) {
  MeanMode4IdleEvents e;
  auto &f = s.fields;
  s.field_438af8 =
      static_cast<std::int32_t>(static_cast<std::uint32_t>(s.field_438af8) + 1);
  const auto state = std::uint16_t(f[0x39e] | (f[0x39f] << 8));
  if (state == 0) {
    std::memcpy(f.data() + 0x038, &handle, 4);
    if (handle) {
      std::fill(f.begin() + 0x024, f.begin() + 0x028, 0);
      e.clear_slots = true;
    }
    f[0x39e] |= 2;
    e.callback = 0x412574;
    return e;
  }
  if (state != 3 && state != 7)
    return e;
  auto data =
      a.frames_10482e[(static_cast<std::uint32_t>(s.field_438af8) >> 2) % 5];
  if (state == 3) {
    const auto index = (static_cast<std::int32_t>(
                           static_cast<std::uint32_t>(lookup) - 0x18000u)) /
                       0x47af;
    if (index < 0 || index >= 20) {
      e.invalid_lookup = true;
      return e;
    }
    const auto &needle = a.needles_f9776[index];
    for (unsigned row = 0; row < 40; ++row) {
      const auto bits = (std::uint32_t(needle[row * 3]) << 13) |
                        (std::uint32_t(needle[row * 3 + 1]) << 5) |
                        (needle[row * 3 + 2] >> 3);
      data[row * 12 + 9] =
          (data[row * 12 + 9] & 0xe0) | std::uint8_t(bits >> 16);
      data[row * 12 + 10] = std::uint8_t(bits >> 8);
      data[row * 12 + 11] = std::uint8_t(bits);
    }
  }
  pixels = decode_windows_dmd(data);
  e.displayed = true;
  return e;
}
} // namespace slam
