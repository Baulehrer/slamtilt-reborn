#pragma once
#include "audio/mean_sound_assets.h"
#include "audio/mean_sample_mixer.h"
namespace slam {
std::array<MeanSoundBank,2> pirate_sound_banks(const std::vector<std::uint8_t>& dat);
std::vector<SampleProfile> pirate_sample_profiles();
}
