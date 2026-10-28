#include "mean_minigame2_input.h"
#include <cstring>
namespace slam {
MeanMinigame2InputEvent mean_minigame2_input(MeanBallResetState &s,
                                             std::int32_t edge,
                                             std::int32_t service1c,
                                             std::int32_t engine44) {
  MeanMinigame2InputEvent e;
  const auto variant = std::uint16_t(s.fields[0x3a4] | (s.fields[0x3a5] << 8));
  if (service1c || edge < 0 || !engine44 || variant != 2)
    return e;
  auto get = [&](unsigned off) {
    std::uint32_t v;
    std::memcpy(&v, s.fields.data() + off, 4);
    return v;
  };
  auto put = [&](unsigned off, std::uint32_t v) {
    std::memcpy(s.fields.data() + off, &v, 4);
  };
  if (get(0x01c) == 1) {
    put(0x01c, 2);
    put(0x040, 0);
    e.descriptor = 0x438050;
    e.edx = 255;
    e.ebx = 245;
  } else if (get(0x01c) == 2) {
    const auto current = get(0x034);
    const auto difference = static_cast<std::int32_t>(0x140000u - current);
    const auto shift = difference >= 0
                           ? std::int64_t(difference) / 128
                           : -((-std::int64_t(difference) + 127) / 128);
    put(0x034, current + static_cast<std::uint32_t>(shift));
  }
  return e;
}
} // namespace slam
