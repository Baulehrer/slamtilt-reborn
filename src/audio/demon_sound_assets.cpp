#include "audio/demon_sound_assets.h"
namespace slam {
// Original410005/410017/410029, verified canonical DAT bindings.
std::vector<MeanSoundBank> demon_sound_banks(const std::vector<std::uint8_t>& dat) {
 return {table_sound_bank(dat,0x6ffb4),table_sound_bank(dat,0x6b2bc),table_sound_bank(dat,0x6e2ce)};
}
// Original40ff3f..40fffa writes descriptor+20; remaining fields retained in PE data.
// Shared IDs are 1-based: 4017a8 resolves the sample header +8 +descriptor offset.
// The original463428 length includes one byte after sample30 PCM.
std::vector<SampleProfile> demon_sample_profiles(){return {
 {0x463278,0x74cf5,4078,226},
 {0x46329c,0x79c0d,4490,226},
 {0x4632c0,0x7ad97,4012,226},
 {0x4632e4,0x81c8c,5808,226},
 {0x463308,0x7bd43,590,226},
 {0x46332c,0x7dd29,6465,160},
 {0x463350,0x76df3,11802,226},
 {0x463374,0x7f66a,9762,226},
 {0x4633bc,0x8333c,6330,226},
 {0x4633e0,0x75ce3,4368,226},
 {0x463404,0x7bf91,7576,226},
 {0x463398,0x5bbd8,6232,226},
 {0x463428,0x5d4d8,2083,226},
 {0x46344c,0x4b040,3072,226},
 };}
}
