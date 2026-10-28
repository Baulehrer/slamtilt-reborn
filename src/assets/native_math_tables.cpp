#include "assets/native_math_tables.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>
#include <utility>

namespace slam {
void initialize_native_math(std::vector<std::uint8_t>& image) {
  constexpr std::size_t begin = 0x556cc, end = 0x63274;
  if (image.size() < end)
    throw std::invalid_argument("Native math image is too small");
  std::fill(image.begin() + begin, image.begin() + end, 0);
  constexpr double pi = 3.141592653589793238462643383279502884;
  constexpr double angle_scale = 2048.0 / pi;
  const auto word = [&](std::size_t offset, std::uint32_t value) {
    image[offset] = static_cast<std::uint8_t>(value);
    image[offset + 1] = static_cast<std::uint8_t>(value >> 8);
  };
  const auto native_offset = [](std::size_t demo_offset) {
    return demo_offset + 0x2b588;
  };

  // The normal evaluator interpolates these eleven vector directions over
  // eight quarter turns. Two leading words retain its established indexing.
  constexpr std::array<std::pair<int, int>, 11> directions{{
      {0, 1}, {1, 8}, {1, 4}, {3, 7}, {4, 7}, {5, 6},
      {6, 5}, {7, 4}, {7, 3}, {4, 1}, {8, 1}}};
  for (unsigned i = 0; i < 88; ++i) {
    const auto [y, x] = directions[i % directions.size()];
    const auto angle = static_cast<unsigned>(0.5 + std::atan(double(y) / x) * angle_scale);
    word(native_offset(0x2a144) + (i + 2) * 2, (i / 11) * 1024 + angle);
  }

  // Conversion intentionally adds 0.5 before truncation, including negatives.
  // A symmetric round() changes 2,047 negative entries and alters collisions.
  for (unsigned i = 0; i < 5120; ++i) {
    const auto value = static_cast<std::int32_t>(0.5 + 16384.0 * std::sin(i * pi / 2048.0));
    word(native_offset(0x2a1f8) + i * 2, static_cast<std::uint32_t>(value));
  }
  word(native_offset(0x2c9f8), 64); // Adjacent native engine scalar.

  for (unsigned i = 0; i < 1025; ++i)
    word(native_offset(0x2c9fc) + i * 2,
         static_cast<unsigned>(0.5 + std::atan(i / 1024.0) * angle_scale));
  // Sparse historical quantization quirks, verified against both build families.
  constexpr std::array<std::pair<unsigned, unsigned>, 6> atan_quantization{{
      {70, 45}, {244, 153}, {259, 162}, {291, 181}, {706, 394}, {882, 463}}};
  for (const auto& [i, value] : atan_quantization)
    word(native_offset(0x2c9fc) + i * 2, value);
  word(native_offset(0x2d1fe), 2); // Adjacent native engine scalar.

  // Flipper envelope: pivot radius 15, tip radius 12, center separation 40.
  // The discrete original body/cap splice advances two distance samples.
  const double tangent_angle = std::asin(3.0 / 40.0);
  for (unsigned i = 0; i < 9471; ++i) {
    const double d = (3840.0 + i + (i >= 7070 ? 2.0 : 0.0)) / 256.0;
    const double angle = i < 7070
        ? std::asin(15.0 / d) - tangent_angle
        : std::acos(std::clamp((d * d + 1456.0) / (80.0 * d), -1.0, 1.0));
    word(native_offset(0x2d200) + i * 2, static_cast<unsigned>(0.5 + angle * angle_scale));
  }
  for (unsigned i = 0; i < 2404; ++i) {
    const double d = (10909.0 + i) / 256.0;
    const double angle = std::acos(std::clamp((d * d - 1744.0) / 960.0, -1.0, 1.0));
    word(native_offset(0x31c00) + i * 2, static_cast<unsigned>(0.5 + angle * angle_scale));
  }

  for (unsigned i = 0; i < 9999; ++i) {
    const auto value = static_cast<std::uint32_t>(16777216.0 / std::pow(i + 1.0, 1.5));
    word(native_offset(0x32ecc) + i * 2, value);
  }
  constexpr std::array<std::pair<unsigned, unsigned>, 11> force_quantization{{
      {1, 33405}, {3, 65535}, {4, 58808}, {5, 27433}, {15, 65535},
      {19, 56503}, {63, 32767}, {255, 4095}, {1023, 511}, {1071, 478}, {4095, 63}}};
  for (const auto& [i, value] : force_quantization)
    word(native_offset(0x32ecc) + i * 2, value);
}
}
