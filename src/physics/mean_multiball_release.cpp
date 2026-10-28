#include "mean_multiball_release.h"
namespace slam {
namespace {
// Original416f24/416e78 unconditional release; mode4 inline release has no sample.
void release(MeanObject &b, std::uint32_t base, std::int32_t vy,
             bool sample, unsigned *sample_count) {
  mean_set_layer(b, 1, base);
  b.put16(0x22, 0);
  b.put16(0x2a, 0);
  b.put16(0x5c, 18);
  b.put16(0x1c, 10);
  b.put32(0x60, 0x40000);
  b.put32(0, 13 * 65536);
  b.put32(4, 306 * 65536);
  b.put32(8, 13 * 65536);
  b.put32(12, 306 * 65536);
  b.put32(0x18, vy);
  b.put16(0x58, 2);
  b.put16(0x28, 0);
  b.put32(0x14, 0);
  if (sample && sample_count)
    ++*sample_count;
}
} // namespace
void mean_multiball_release(MeanObject &b, MeanMultiballReleaseState &s,
                            std::uint32_t base, bool tilt, unsigned *sample_count) {
  // Original4166d8 release does not terminate callback5: timer follows.
  if (tilt)
    release(b, base, 0x30000, true, sample_count);
  auto &slot = s.slot;
  if (slot[1] != 0) {
    --slot[1];
    if (slot[1] > 0) {
      if (slot[2] != 0)
        --slot[2];
      return;
    }
  }
  if (slot[2] != 0 && --slot[2] > 0)
    return;
  slot[0] = 10;
  std::int32_t vy = 0x30000;
  if (s.mode == 4 && s.field_43f3a6 == 0) {
    s.bits |= 1;
    s.slot50[2] = 3;
    if (s.bits != 7)
      return;
    vy = s.field_43f064;
  } else if (s.mode == 5 && s.selected == 4)
    vy = 0x5a000;
  else if (s.mode == 6) {
    if (s.field_43f382 != 0)
      return;
    vy = 0x5a000;
  }
  release(b, base, vy, s.mode != 4 || s.field_43f3a6 != 0, sample_count);
}
} // namespace slam
namespace slam {
void mean_multiball_guide(MeanObject &b) {
  // Actual417238, before415330 and integration. Field18 follows three rails.
  if (b.u16(0x5c) != 18)
    return;
  b.put16(0x22, 0);
  if (b.i32(4) >= 533 * 65536) {
    b.put16(0x2a, 0xc00);
    b.put16(0x28, 20);
  } else if (b.i32(0) > 160 * 65536) {
    b.put16(0x2a, 0x800);
    b.put16(0x28, 20);
  } else {
    b.put16(0x2a, 0);
    b.put16(0x28, b.i32(4) >= 379 * 65536 ? 20 : 0);
  }
}
} // namespace slam
