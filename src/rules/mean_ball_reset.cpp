#include "mean_ball_reset.h"
#include <algorithm>
namespace slam {
void mean_ball_reset(MeanBallResetState &s, MeanBallResetEvents &event) {
  auto w = [&](unsigned o, std::uint16_t v) {
    s.fields[o] = v;
    s.fields[o + 1] = v >> 8;
  };
  auto d = [&](unsigned o, std::uint32_t v) {
    for (unsigned j = 0; j < 4; ++j)
      s.fields[o + j] = v >> (j * 8);
  };
  auto word = [&](unsigned o) {
    return static_cast<std::int16_t>(s.fields[o] |
                                     (unsigned(s.fields[o + 1]) << 8));
  };
  for (unsigned o :
       {0x3b8, 0x3ba, 0x3bc, 0x3ac, 0x392, 0x3a2, 0x3a6, 0x39e, 0x3a8,
        0x3aa, 0x3a0, 0x3b2, 0x3a4, 0x39a, 0x394, 0x39c, 0x3b4, 0x046,
        0x04a, 0x386, 0x364, 0x38c, 0x378, 0x366, 0x382, 0x37c, 0x048,
        0x04c, 0x04e, 0x372, 0x38a, 0x36a, 0x380, 0x370, 0x384, 0x36e,
        0x376, 0x37e, 0x388, 0x044, 0x35e, 0x358, 0x35c})
    w(o, 0);
  d(0x064, 0);
  std::copy(s.player_record.begin(), s.player_record.end(),
            s.fields.begin() + 0x1d4);
  s.fields[0x060] = 3;
  for (unsigned o : {0x398, 0x3b6, 0x396, 0x3b0, 0x3ae, 0x390, 0x38e, 0x368,
                     0x36c, 0x37a, 0x374, 0x35a})
    w(o, 0xffff);
  s.field_43ee1c.fill(0xff);
  for (unsigned o : {0x058, 0x05c, 0x050, 0x054})
    d(o, 0);
  w(0x360, 100);
  s.field_438a40 = 0;
  // Actual419da4 rotates to the next unset mode, preserving all-set records.
  if (s.table_mode <= 4) {
    bool all = true;
    for (unsigned i = 0; i < 5; ++i)
      all &= s.fields[0x1e0 + i] != 0;
    if (!all) {
      int previous = word(0x1e6), selected = previous;
      do {
        if (++selected >= 5)
          selected = 0;
      } while (s.fields[0x1e0 + selected] != 0);
      w(0x1e6, selected);
      s.fields[0x2bc + previous * 4] = s.fields[0x1e0 + previous] ? 1 : 2;
      unsigned o = 0x2bc + selected * 4;
      s.fields[o] = 4;
      s.fields[o + 1] = 6;
      s.fields[o + 2] = s.fields[o + 3] = 0;
    }
  }
  s.field_438b44 = 0;
  s.field_438b4c = -1;
  event.lamp_rebuild = true;
  s.field_438af8 = 0;
  if (s.field_438af4 != 0) {
    s.field_438af4 = 0;
    w(0x362, s.engine_3c % (word(0x1f2) >= 5 ? 6 : 7));
  }
  event.service90 = true;
}
} // namespace slam
