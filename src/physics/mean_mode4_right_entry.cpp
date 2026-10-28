#include "physics/mean_mode4_right_entry.h"
namespace slam {
namespace {
std::int16_t word(const MeanBallResetState &s, unsigned o) {
  return static_cast<std::int16_t>(unsigned(s.fields[o]) |
                                   unsigned(s.fields[o + 1]) << 8);
}
void put(MeanBallResetState &s, unsigned o, std::uint32_t n,
         unsigned size = 2) {
  for (unsigned i = 0; i < size; ++i)
    s.fields[o + i] = n >> (8 * i);
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
void reset(MeanBallResetState &s, MeanMode4RightEvent &e) {
  put(s, 0x3b8, 0);
  e.mode4_reset = true;
}
} // namespace
bool mean_mode4_right_capture_entry(MeanObject &b, MeanBallResetState &raw,
                                    MeanMode4RightState &s,
                                    const MeanBallPool &p,
                                    MeanMode4RightEvent &e) {
  e = {};
  if (b.i32(0) < 260 * 65536 || b.u16(0x5c) != 20 || s.field_438b80[0] >= 0)
    return false;
  for (unsigned i = 0; i < p.count; ++i)
    if (p.objects[i].u16(0x5a) == 4 &&
        (p.objects[i].u16(0x58) == 3 || p.objects[i].u16(0x58) == 6))
      return false;
  b.put32(0, 280 * 65536);
  b.put32(4, 285 * 65536);
  b.put16(0x5a, 4);
  b.put16(0x58, 3);
  put(raw, 0x370, 50);
  s.field_438b80[1] = 200;
  reset(raw, e);
  e.sample_437dc8 = true;
  return true;
}
MeanMode4RightEvent mean_mode4_right_ramp(MeanBallResetState &s, unsigned layer,
                                          unsigned mask, std::int32_t y) {
  MeanMode4RightEvent e;
  if (layer != 3 || mask != 1 || y >= 64 * 65536 || s.table_mode < 1 ||
      s.table_mode >= 4 || word(s, 0x392) == 0)
    return e;
  put(s, 0x392, 0);
  put(s, 0x3ba, 0);
  put(s, 0x3a6, 1);
  put(s, 0x058, 0, 4);
  put(s, 0x03c, 0xffffffff, 4);
  put(s, 0x3a0, 499);
  put(s, 0x3b2, 0);
  put(s, 0x3aa, 0xffff);
  s.field_438a40 = -1;
  s.fields[0x218] = 4;
  s.fields[0x219] = 6;
  s.fields[0x21a] = 1;
  s.fields[0x21b] = 0;
  for (auto o : {0x21c, 0x220, 0x230, 0x234})
    s.fields[o] = 2;
  s.fields[0x25c] = 4;
  s.fields[0x25d] = 3;
  s.fields[0x25e] = 1;
  s.fields[0x25f] = 0;
  s.table_mode = 4;
  reset(s, e);
  e.callback = 0x4130cc;
  return e;
}
bool mean_mode4_right_capture(MeanObject &b, MeanBallResetState &raw,
                              MeanMode4RightState &s, MeanCaptureTickState &cap,
                              const MeanBallPool &p, std::uint32_t base,
                              MeanMode4RightEvent &e, bool services_1c) {
  e = {};
  // Actual4164e1 also runs in mode5; only mode6 has a separate lock branch.
  if (b.u16(0x58) != 3 || b.u16(0x5a) != 4 || raw.table_mode < 1 ||
      raw.table_mode > 5)
    return false;
  const auto transfer = [&]() {
    // Original417068 transfer through verified callback2 wrapper.
    auto proxy = cap;
    proxy.table_mode = 2;
    proxy.field_43f380 = -3;
    proxy.field_438b68 = {-1, 0, 0};
    MeanBallResetState scratch = raw;
    scratch.fields[0x392] = scratch.fields[0x393] = 0;
    MeanMultiballReleaseState release;
    MeanCaptureTickEvent effect;
    bool sample = false;
    const auto previous_callback = b.u16(0x5a);
    b.put16(0x5a, 2);
    bool ok =
        mean_mode4_capture(b, proxy, scratch, release, p, base, effect, sample);
    if (b.u16(0x5a) == 2)
      b.put16(0x5a, previous_callback);
    cap.field_438b74 = proxy.field_438b74;
    cap.field_438b50 = proxy.field_438b50;
    return ok;
  };
  // Original4164ee keeps executing callback4 after417068 changed callback5a.
  if (services_1c && !transfer())
    return false;
  const auto timer = word(raw, 0x370);
  if (timer < 0) {
    if (!slot_tick(s.field_438b80))
      return true;
    s.field_438b80[0] = 10;
    return transfer();
  }
  put(raw, 0x370, static_cast<std::uint16_t>(timer) - 1);
  if (s.field_438b40 != 0)
    return true;
  s.field_438b38 =
      static_cast<std::int32_t>(static_cast<std::uint32_t>(s.field_438b38) - 1);
  e.score = 500000;
  e.field_player_08_add = 1000000;
  if (raw.table_mode >= 4 || word(raw, 0x3a2) == 0)
    return true;
  for (auto o : {0x034, 0x01c, 0x040})
    put(raw, o, 0, 4);
  put(raw, 0x3a6, 2);
  put(raw, 0x3a4, 2);
  put(raw, 0x3a2, 0);
  put(raw, 0x3bc, 0);
  raw.fields[0x224] = 4;
  raw.fields[0x225] = 6;
  raw.fields[0x226] = 1;
  raw.fields[0x227] = 0;
  for (auto o : {0x228, 0x22c, 0x238, 0x254})
    raw.fields[o] = 2;
  raw.table_mode = 4;
  reset(raw, e);
  e.start_shared44 = true;
  e.service88_1_56 = e.service84_0_73 = true;
  return true;
}
} // namespace slam
