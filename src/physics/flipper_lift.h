#pragma once
#include <array>
#include <cstdint>
#include <stdexcept>
#include <vector>
namespace slam {
// Bounded temporary static intermediate for the original flipper island.
// Instructions are compiled C++, never decoded/interpreted at runtime.
struct FlipperLift {
  std::array<std::uint32_t, 8> r{}; // eax,ecx,edx,ebx,esp,ebp,esi,edi
  std::vector<std::uint8_t> image;
  std::array<std::uint8_t, 0x64> ball{};
  std::array<std::uint8_t, 65536> stack{};
  bool z = false, s = false, o = false, c = false;
  std::uint8_t &byte(std::uint32_t a) {
    if (a >= 0x400000 && a - 0x400000 < image.size())
      return image[a - 0x400000];
    if (a >= 0x1000000 && a - 0x1000000 < ball.size())
      return ball[a - 0x1000000];
    if (a >= 0x2000000 && a - 0x2000000 < stack.size())
      return stack[a - 0x2000000];
    throw std::out_of_range("Static flipper lift memory");
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
  static std::uint32_t mask(unsigned n) {
    return n == 4 ? 0xffffffffu : (1u << (n * 8)) - 1;
  }
  std::uint32_t flags(std::uint32_t v, unsigned n) {
    v &= mask(n);
    z = v == 0;
    s = (v >> (n * 8 - 1)) != 0;
    return v;
  }
  std::uint32_t add(std::uint32_t a, std::uint32_t b, unsigned n) {
    auto v = (a + b) & mask(n);
    o = (~(a ^ b) & (a ^ v) & (1u << (n * 8 - 1))) != 0;
    c = std::uint64_t(a & mask(n)) + (b & mask(n)) > mask(n);
    return flags(v, n);
  }
  std::uint32_t sub(std::uint32_t a, std::uint32_t b, unsigned n) {
    auto v = (a - b) & mask(n);
    o = ((a ^ b) & (a ^ v) & (1u << (n * 8 - 1))) != 0;
    c = (a & mask(n)) < (b & mask(n));
    return flags(v, n);
  }
  std::uint32_t sbb(std::uint32_t a, std::uint32_t b, unsigned n) {
    auto borrow = c ? 1u : 0u;
    auto v = (a - b - borrow) & mask(n);
    o = ((a ^ b) & (a ^ v) & (1u << (n * 8 - 1))) != 0;
    c = std::uint64_t(a & mask(n)) < std::uint64_t(b & mask(n)) + borrow;
    return flags(v, n);
  }
  std::uint32_t logic(std::uint32_t v, unsigned n) {
    o = c = false;
    return flags(v, n);
  }
  static std::int64_t sign(std::uint32_t v, unsigned n) {
    v &= mask(n);
    return (v & (1u << (n * 8 - 1)))
               ? std::int64_t(v) - (std::int64_t(1) << (n * 8))
               : v;
  }
  std::uint32_t shift(std::uint32_t v, unsigned count, unsigned n, int kind) {
    count &= 31;
    if (!count)
      return v;
    v &= mask(n);
    const auto bits = n * 8;
    auto out = kind == 0   ? std::uint32_t(std::uint64_t(v) << count)
               : kind == 1 ? v >> count
                           : std::uint32_t(sign(v, n) >> count);
    c = kind == 0 ? (count <= bits && ((v >> (bits - count)) & 1))
                  : ((v >> (count - 1)) & 1);
    if (count == 1)
      o = kind == 0   ? (((out >> (bits - 1)) & 1) != c)
          : kind == 1 ? ((v >> (bits - 1)) & 1)
                      : false;
    else
      o = false;
    return flags(out, n);
  }
};
void flipper_409050(FlipperLift &);
void flipper_4096e8(FlipperLift &);
void flipper_4084bc(FlipperLift &);
} // namespace slam
