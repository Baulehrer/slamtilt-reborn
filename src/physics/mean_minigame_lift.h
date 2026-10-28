#pragma once
#include "dmd/windows_dmd.h"
#include "flipper_lift.h"
#include <string>
#include <functional>
namespace slam {
enum class MeanMinigameRevision { Demo, Retail };
struct MeanMinigameLift : FlipperLift {
  MeanMinigameRevision revision=MeanMinigameRevision::Demo;
  unsigned contact_decrement_scale() const { return revision==MeanMinigameRevision::Retail?4:2; }
  unsigned lap_award() const { return revision==MeanMinigameRevision::Retail?40000000:20000000; }
  unsigned completion_value() const { return revision==MeanMinigameRevision::Retail?4:7; }
  std::vector<std::uint8_t> dat;
  std::array<std::uint8_t, 65536> runtime{};
  WindowsDmdPixels pixels{};
  std::uint32_t points = 0;
  std::function<void(MeanMinigameLift &,std::uint32_t)> text_service;
  struct AudioRequest { std::uint32_t descriptor, edx, ebx; unsigned service=0x5c; };
  std::vector<AudioRequest> audio_requests;
  std::uint32_t requested_display_callback = 0;
  std::uint8_t &byte(std::uint32_t a) {
    if (a >= 0x1100000 && a - 0x1100000 < dat.size())
      return dat[a - 0x1100000];
    if (a >= 0x1000000 && a - 0x1000000 < runtime.size())
      return runtime[a - 0x1000000];
    if (a >= 0x400000 && a - 0x400000 < image.size())
      return image[a - 0x400000];
    if (a >= 0x2000000 && a - 0x2000000 < stack.size())
      return stack[a - 0x2000000];
    throw std::out_of_range("Mini-game memory " + std::to_string(a));
  }
  std::uint32_t rd(std::uint32_t a, unsigned n) {
    std::uint32_t v = 0;
    for (unsigned i = 0; i < n; ++i)
      v |= std::uint32_t(byte(a + i)) << (8 * i);
    return v;
  }
  void wr(std::uint32_t a, std::uint32_t v, unsigned n) {
    for (unsigned i = 0; i < n; ++i)
      byte(a + i) = v >> (8 * i);
  }
  void push(std::uint32_t v) {
    r[4] -= 4;
    wr(r[4], v, 4);
  }
  std::uint32_t pop() {
    auto v = rd(r[4], 4);
    r[4] += 4;
    return v;
  }
  void service(std::uint32_t target);
};
void minigame_4180d0(MeanMinigameLift &);
} // namespace slam
