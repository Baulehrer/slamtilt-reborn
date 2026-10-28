#include "mean_mode4_phase1.h"
#include <cstring>
#include <fstream>
#include <stdexcept>
namespace slam {
MeanMode4Phase1Assets load_mean_mode4_phase1(const std::filesystem::path &p) {
  std::ifstream in(p, std::ios::binary);
  MeanMode4Phase1Assets a;
  auto frame = [&](std::size_t off) {
    std::array<std::uint8_t, 480> bytes{};
    in.seekg(off);
    in.read(reinterpret_cast<char *>(bytes.data()), 480);
    if (!in)
      throw std::runtime_error("Truncated Mean phase1 DMD");
    return decode_windows_dmd(bytes);
  };
  for (unsigned i = 0; i < 5; ++i)
    a.frames_10608e[i] = frame(0x10608e + i * 480);
  for (unsigned i = 0; i < 8; ++i)
    a.frames_1069ee[i] = frame(0x1069ee + i * 480);
  for (unsigned i = 0; i < 10; ++i)
    a.frames_1078ee[i] = frame(0x1078ee + i * 480);
  return a;
}
MeanMode4Phase1Event mean_mode4_phase1(MeanBallResetState &s,
                                       const MeanMode4Phase1Assets &a,
                                       WindowsDmdPixels &pixels) {
  MeanMode4Phase1Event e;
  auto &f = s.fields;
  auto word = [&](unsigned o) { return std::uint16_t(f[o] | (f[o + 1] << 8)); };
  auto set = [&](unsigned o, std::uint16_t v) {
    f[o] = v;
    f[o + 1] = v >> 8;
  };
  auto dword = [&](unsigned o) {
    std::uint32_t v;
    std::memcpy(&v, f.data() + o, 4);
    return v;
  };
  auto put = [&](unsigned o, std::uint32_t v) {
    std::memcpy(f.data() + o, &v, 4);
  };
  auto phase = static_cast<std::int16_t>(word(0x3aa));
  if (phase < 0) {
    e.bank1_order50 = e.service8c = true;
    set(0x3aa, 0);
    phase = 0;
  }
  const auto timer = static_cast<std::int16_t>(word(0x3a0));
  auto sar = [](std::int32_t v, unsigned n) {
    return v >= 0 ? v / (1 << n)
                  : -static_cast<std::int32_t>(
                        (-std::int64_t(v) + (1 << n) - 1) / (1 << n));
  };
  if (phase <= 1) {
    const auto index = sar(timer, 4) % 10;
    if (index < 0)
      return e; // Out-of-domain negative lookup before timeout transition.
    pixels = a.frames_1078ee[index];
    e.number = true;
    e.eax = 2;
    e.edx = 4;
    e.ecx = 23;
    e.value = static_cast<std::uint32_t>(timer / 100 + 1);
  } else if (phase == 2) {
    const auto index = 9 - sar(-std::int32_t(timer), 4) % 10;
    if (index < 0 || index >= 10)
      return e;
    pixels = a.frames_1078ee[index];
    e.number = true;
    e.eax = 2;
    e.edx = 4;
    e.ecx = 23;
    e.value = 0;
  } else {
    set(0x3a0, word(0x3a0) + 1);
    put(0x02c, static_cast<std::uint32_t>(timer));
    if (timer < 20) {
      const auto index = sar(timer, 2);
      if (index < 0 || index >= 5)
        return e;
      pixels = a.frames_10608e[index];
    } else {
      put(0x02c, timer - 20);
      pixels = a.frames_1069ee[sar(timer - 20, 2) & 7];
      const auto count = static_cast<std::int32_t>(dword(0x03c));
      if (count >= 0) {
        put(0x03c, dword(0x03c) - 1);
        if (!(f[0x03c] & 1)) {
          e.number = true;
          e.eax = 1;
          e.edx = 4;
          e.ecx = 12;
          e.value = dword(0x020);
        }
      }
    }
  }
  e.displayed = true;
  return e;
}
} // namespace slam

namespace slam {
MeanMode4Phase1Event render_mean_mode4_phase1(MeanBallResetState &s,
    const MeanMode4Phase1Assets &assets, const MeanScoreFont &font,
    WindowsDmdPixels &pixels) {
  const auto e = mean_mode4_phase1(s, assets, pixels);
  if (e.displayed && e.number)
    draw_mean_score(font, pixels, e.value, e.ecx, e.edx, e.eax);
  return e;
}
} // namespace slam
