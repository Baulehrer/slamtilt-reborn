#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace slam {
inline float audio_gain(float value) {
  return std::isfinite(value) ? std::clamp(value, 0.0f, 1.0f) : 1.0f;
}
inline std::int16_t mix_audio_levels(std::int16_t music, std::int16_t sfx,
                                     float music_gain, float sfx_gain) {
  const int value = int(float(music) * music_gain) +
                    int(float(sfx) * sfx_gain);
  return std::int16_t(std::clamp(value, -32768, 32767));
}
} // namespace slam
