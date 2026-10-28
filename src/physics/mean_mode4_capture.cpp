#include "mean_left_tilt_release.h"
#include "physics/mean_mode4_capture.h"
namespace slam {
namespace {
std::int16_t word(const MeanBallResetState &s, unsigned o) {
  return static_cast<std::int16_t>(unsigned(s.fields[o]) |
                                   unsigned(s.fields[o + 1]) << 8);
}
void put(MeanBallResetState &s, unsigned o, std::int16_t n) {
  s.fields[o] = n;
  s.fields[o + 1] = static_cast<std::uint16_t>(n) >> 8;
}
bool slot_tick(std::array<std::int32_t, 3> &s) {
  if (s[1] != 0) {
    --s[1];
    if (s[1] > 0) {
      if (s[2] != 0)
        --s[2];
      return false;
    }
  }
  return s[2] == 0 || --s[2] <= 0;
}
bool allocate(const MeanBallPool &p, const std::array<std::int32_t, 3> &slot,
              unsigned callback) {
  if (slot[0] >= 0)
    return false;
  for (unsigned i = 0; i < p.count; ++i)
    if (p.objects[i].u16(0x5a) == callback &&
        (p.objects[i].u16(0x58) == 3 || p.objects[i].u16(0x58) == 6))
      return false;
  return true;
}
} // namespace
bool mean_mode4_capture(MeanObject &b, MeanCaptureTickState &s,
                        MeanBallResetState &raw, MeanMultiballReleaseState &r,
                        const MeanBallPool &p, std::uint32_t base,
                        MeanCaptureTickEvent &e, bool &sample, bool services_1c) {
  e = {};
  sample = false;
  if (b.u16(0x58) != 3 || b.u16(0x5a) != 2 || s.table_mode < 1 ||
      s.table_mode > 4)
    return false;
  if (services_1c) {
    mean_left_tilt_release(b, base);
    ++e.services_1c_samples;
  }
  const auto armed = word(raw, 0x392);
  // Original human activation branch reached on the decrement to-2.
  if (s.field_43f380 == -1 && s.table_mode <= 3 && armed != 0) {
    s.field_43f380 = -2;
    s.field_43f392 = 0;
    for (auto o : {0x392, 0x3ba, 0x3a6, 0x39e, 0x3a8, 0x396})
      put(raw, o, 0);
    raw.fields[0x218] = 4;
    raw.fields[0x219] = 6;
    raw.fields[0x21a] = 1;
    raw.fields[0x21b] = 0;
    for (auto o : {0x21c, 0x220, 0x230, 0x234})
      raw.fields[o] = 2;
    s.table_mode = raw.table_mode = 4;
    return true;
  }
  if (s.field_43f380 <= -3) {
    if (!slot_tick(s.field_438b68))
      return true;
    s.field_438b68[0] = 10;
    if (s.table_mode == 4 && word(raw, 0x3a6) == 0) {
      if (!allocate(p, r.slot, 5))
        return true;
      b.put16(0x34, 0);
      b.put32(0x2c, 0x30b1d6);
      b.put32(0x30, 0x30000);
      b.put16(0x58, 7);
      b.put16(0x5c, 21);
      b.put32(0x60, 0x200000);
      b.put32(0x54, base + 0xcbb96);
      sample = true;
      return true;
    }
    if (!allocate(p, s.field_438b74, 3))
      return true;
    // Same417068 transfer already preserved in base capture helper.
    auto proxy = s;
    proxy.table_mode = 2;
    proxy.field_43f392 = 0;
    proxy.field_438b68 = {-1, 0, 0};
    b.put16(0x58, 3);
    if (!mean_capture_tick(b, proxy, base, e))
      return false;
    if (services_1c) e.services_1c_samples = 1;
    s.field_438b74 = proxy.field_438b74;
    s.field_438b50 = proxy.field_438b50;
    return true;
  }
  const auto mode = s.table_mode;
  const auto save392 = s.field_43f392;
  s.table_mode = 2;
  s.field_43f392 = 0;
  const auto released_state = b.u16(0x58);
  b.put16(0x58, 3);
  const auto ok = mean_capture_tick(b, s, base, e);
  if (services_1c) { b.put16(0x58, released_state); e.services_1c_samples = 1; }
  s.table_mode = mode;
  s.field_43f392 = save392;
  raw.table_mode = mode;
  return ok;
}
} // namespace slam
