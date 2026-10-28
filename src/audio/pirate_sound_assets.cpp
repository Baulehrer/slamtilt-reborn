#include "audio/pirate_sound_assets.h"
namespace slam {
std::array<MeanSoundBank,2> pirate_sound_banks(const std::vector<std::uint8_t>& dat) {
  // Original42b4d3..42b4f1; shared31-sample directory atDAT0.
  return table_sound_banks(dat,{0x51876,0x568e8});
}
std::vector<SampleProfile> pirate_sample_profiles() {
  // Original464f18..465134. Allvolume64, one-shot PCM; direct or bank slices.
  return {
    {0x464f18,0x58ffb,4078,226},
    {0x464f3c,0x18c92,4388,452},
    {0x464f60,0x59fe9,4490,226},
    {0x464f84,0x5b173,4012,226},
    {0x464fa8,0x5c11f,9762,226},
    {0x464fcc,0x5e741,4026,226},
    {0x464ff0,0x5f6fb,7576,226},
    {0x465014,0x61493,5808,226},
    {0x465038,0x2afb2,13178,226},
    {0x46505c,0x3f188,3044,300},
    {0x465080,0x23306,12852,226},
    {0x4650a4,0x373d0,12636,226},
    {0x4650c8,0x1dc70,7636,226},
    {0x4650ec,0x2afb2,13178,226},
    {0x465110,0x62b43,6465,160},
  };
}
}
