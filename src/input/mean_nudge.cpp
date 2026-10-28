#include "mean_nudge.h"
#include <cstring>
namespace slam {
namespace {
std::int32_t bits(std::uint32_t x) {
  std::int32_t r;
  std::memcpy(&r, &x, 4);
  return r;
}
std::int32_t sub(std::int32_t a, std::int32_t b) {
  return bits(std::uint32_t(a) - std::uint32_t(b));
}
std::int32_t sar16(std::int32_t x) {
  return bits((std::uint32_t(x) >> 16) | (x < 0 ? 0xffff0000u : 0u));
}
} // namespace
void MeanNudge::accept_pending() {
  if (field_429858 != 0) {
    field_429858 = 0;
    field_42985c = 0;
  }
  if (field_42980c != 0) {
    field_429808 = field_42980c;
    field_42980c = 0;
    field_429810 = 0;
  }
}
void MeanNudge::step() {
  auto edx = field_429810, ebx = field_42985c, ecx = field_43e71c;
  if (ebx >= 0) {
    if (ebx < 16) {
      const auto next = vertical[unsigned(ebx) + 1];
      field_43e564 = sub(next, vertical[unsigned(ebx)]);
      field_43e410 = next;
      ++ebx;
    } else {
      field_43e564 = 0;
      field_43e410 = 0;
      ebx = -1;
    }
  }
  if (edx >= 0) {
    std::int32_t value = 0;
    if (edx < 16) {
      ++edx;
      const auto next = horizontal[unsigned(edx)];
      const auto prev = horizontal[unsigned(edx) - 1];
      if (field_429808 < 0) {
        ecx = sub(0, next);
        field_43e70c = sar16(bits(std::uint32_t(ecx) + 0xffffu));
        value = sub(prev, next);
      } else {
        ecx = next;
        field_43e70c = sar16(ecx);
        value = sub(next, prev);
      }
    } else {
      edx = -1;
      ecx = 0;
      field_429808 = 0;
      field_43e70c = 0;
    }
    field_43e724 = value;
  }
  field_43e71c = ecx;
  field_42985c = ebx;
  field_429810 = edx;
}
} // namespace slam
