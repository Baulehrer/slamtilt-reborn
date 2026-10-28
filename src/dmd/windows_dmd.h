#pragma once
#include <array>
#include <cstdint>
namespace slam {
using WindowsDmdPixels = std::array<std::uint8_t, 96 * 20>;
// Original4060a4: signed level clamped0..6, alternating pairs429a9c.
inline void mean_clear_windows_dmd(WindowsDmdPixels &pixels, int level) {
  level=level<0?0:level>6?6:level;
  for(unsigned y=0;y<20;++y) for(unsigned x=0;x<96;++x)
    pixels[y*96+x]=std::uint8_t((level+((x+y)&1))/2);
}
// Original406680:20rows,12bytes each, two consecutive240-byte planes.
inline WindowsDmdPixels
decode_windows_dmd(const std::array<std::uint8_t, 480> &data) {
  WindowsDmdPixels pixels{};
  for (unsigned i = 0; i < pixels.size(); ++i) {
    const unsigned byte = i / 8, bit = 7 - i % 8;
    pixels[i] =
        ((data[byte] >> bit) & 1) | (((data[byte + 240] >> bit) & 1) << 1);
  }
  return pixels;
}
} // namespace slam
