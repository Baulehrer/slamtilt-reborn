#include "rules/mean_right_cancel.h"
namespace slam {
MeanRightCancelEvent mean_right_cancel(MeanBallResetState &s,
                                      MeanRightGateState &gate,
                                      std::uint32_t service34_result) {
  auto &f = s.fields;
  if (s.table_mode < 1 || s.table_mode > 4 || !(f[0x3a2] | f[0x3a3]))
    return {};
  auto put = [&](unsigned o, std::uint32_t v, unsigned n = 2) {
    for (unsigned i = 0; i < n; ++i)
      f[o + i] = std::uint8_t(v >> (8 * i));
  };
  const auto old38a = std::uint16_t(f[0x38a] | (f[0x38b] << 8));
  put(0x3a2, 0);
  put(0x038, service34_result, 4);
  put(0x3bc, 0);
  put(0x364, 0xffff);
  f[0x2a0] = 4; f[0x2a1] = 4; f[0x2a2] = 1; f[0x2a3] = 0;
  f[0x224] = 4; f[0x225] = 6; f[0x226] = 1; f[0x227] = 0;
  put(0x38a, std::uint16_t(old38a + 15));
  f[0x228] = f[0x22c] = f[0x254] = f[0x238] = 2;
  mean_right_gate(s, gate);
  return {true, 0x413490};
}
} // namespace slam
