#pragma once
#include "audio/mean_sound_assets.h"
#include "audio/mean_sample_mixer.h"
namespace slam {
std::vector<MeanSoundBank> demon_sound_banks(const std::vector<std::uint8_t>&);
std::vector<SampleProfile> demon_sample_profiles();
}
