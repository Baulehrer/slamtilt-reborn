#pragma once
#include <cstdint>

namespace slam {
// Modern numeric representation of the original six-byte packed-BCD score.
class MeanScore {
public:
  explicit MeanScore(std::uint64_t value = 0) : value_(value % modulus) {}
  void add(std::uint32_t points) { value_ = (value_ + points) % modulus; }
  std::uint64_t value() const { return value_; }

private:
  static constexpr std::uint64_t modulus = 1000000000000ULL;
  std::uint64_t value_;
};
} // namespace slam
