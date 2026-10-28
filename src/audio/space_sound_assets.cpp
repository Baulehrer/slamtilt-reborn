#include "audio/space_sound_assets.h"
namespace slam {
// Original439c35/439c47/439c59; shared stripped-STIM parser, no new decoder.
std::vector<MeanSoundBank> space_sound_banks(const std::vector<std::uint8_t>& dat) {
 return {table_sound_bank(dat,0x53642),table_sound_bank(dat,0x5b8e0),table_sound_bank(dat,0x5fef8)};
}
// Original initialized descriptors; bank-relative offsets resolved by DAT0 directory.
std::vector<SampleProfile> space_sample_profiles(){return {
    {0x465ce4,0x66f7d,4078,226},
    {0x465d08,0x67f6b,4490,226},
    {0x465d2c,0x690f5,4012,226},
    {0x465d50,0x6a0a1,9762,226},
    {0x465d74,0x6c6c3,6330,226},
    {0x465d98,0x6df7d,7576,226},
    {0x465dbc,0x658cd,5808,226},
    {0x465de0,0x68d2,2800,120},
    {0x465e04,0x62b10,6465,160},
    {0x465e28,0x64451,5244,226},
 };}
}
