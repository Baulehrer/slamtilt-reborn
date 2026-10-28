#include "mean_sample_mixer.h"
#include <algorithm>
#include <stdexcept>
namespace slam {
namespace {
std::vector<SampleProfile> mean_profiles() {
  // Original Mean direct/bank-relative descriptors, retained golden layout.
  return {{0x437cf0,0x63a1d,0x1941,0xa0},{0x437d14,0x6535e,0xfee,0xe2},
    {0x437da4,0x6aaa4,0xbd2,0xe2},{0x437d38,0x6634c,0x118a,0xe2},
    {0x437d5c,0x674d6,0xfac,0xe2},{0x437dec,0x6d40e,0x16b0,0xe2},
    {0x437dc8,0x6b676,0x1d98,0xe2},{0x437fe4,0x27b66,2747,428},
    {0x438008,0x286ea,2882,428},{0x43802c,0x292f5,3395,428},
    {0x438050,0x2a100,4536,428}};
}
}
MeanSampleMixer::MeanSampleMixer(const std::vector<std::uint8_t>& dat)
    :MeanSampleMixer(dat,mean_profiles()) {}
MeanSampleMixer::MeanSampleMixer(const std::vector<std::uint8_t>& dat,
                                 std::vector<SampleProfile> profiles)
    :profiles_(std::move(profiles)),pcm_(profiles_.size()) {
  if(profiles_.empty())throw std::runtime_error("Empty sample layout");
  for(unsigned sample=0;sample<profiles_.size();++sample){
    const auto& p=profiles_[sample];
    if(!p.period||!p.length||p.offset>dat.size()||p.length>dat.size()-p.offset)
      throw std::runtime_error("Invalid table sample layout");
    for(std::size_t i=0;i<p.length;++i){
      const auto byte=dat[p.offset+i];
      pcm_[sample].push_back(byte<128?int(byte):int(byte)-256);
    }
  }
}
void MeanSampleMixer::request(int a,int b,unsigned descriptor) {
  // Descriptor0 is the historical Mean first-sample API.
  unsigned sample=0;
  if(descriptor){
    const auto it=std::find_if(profiles_.begin(),profiles_.end(),[&](const auto& p){return p.descriptor==descriptor;});
    if(it==profiles_.end())throw std::runtime_error("Unsupported table sample descriptor");
    sample=unsigned(it-profiles_.begin());
  }
  for(const auto& pending:pending_)if(pending.sample==sample)return;
  pending_.push_back({sample,a,b});
}
void MeanSampleMixer::reset() {
  voices_ = {};
  pending_.clear();
}
int MeanSampleMixer::active() const {
  return int(voices_[0].active) + int(voices_[1].active);
}
void MeanSampleMixer::mix(std::int16_t *out, std::size_t frames) {
  for (const auto &request : pending_) {
    const int field_1c_ = request.field_1c, field_20_ = request.field_20;
    int index = -1;
    if (field_1c_ == -1)
      index = 0;
    else if (field_1c_ == -2)
      index = 1;
    else if (voices_[0].field_20 == 0)
      index = 0;
    else if (voices_[1].field_20 == 0)
      index = 1;
    else if (field_1c_ >= voices_[0].field_20)
      index = 0;
    else if (field_1c_ >= voices_[1].field_20)
      index = 1;
    if (index >= 0)
      voices_[index] = {request.sample, 0, field_20_, true};
  }
  pending_.clear();
  // Original420120 Q32 step clears low4fraction bits;41eb60 LUT gain for
  // factory6voices/master65536/fullvolume64. Finalstereo sum remainsnative.
  for (std::size_t f = 0; f < frames; ++f) {
    int value = 0;
    for (auto &v : voices_)
      if (v.active) {
        const auto index = v.phase >> 32;
        if (index >= pcm_[v.sample].size()) {
          v = {};
          continue;
        }
        const auto product =
            std::int64_t(pcm_[v.sample][index]) * (0x20000 / 6) * 127;
        // Arithmetic right shift (floor), explicitly portable for negatives.
        value +=
            int(product >= 0 ? product / 65536 : -((-product + 65535) / 65536));
        v.phase +=
            ((std::uint64_t(0x361f0f / profiles_[v.sample].period) << 32) / 44100) &
            ~std::uint64_t(15);
        if ((v.phase >> 32) >= pcm_[v.sample].size())
          v = {};
      }
    for (unsigned ch = 0; ch < 2; ++ch)
      out[f * 2 + ch] =
          std::int16_t(std::clamp(int(out[f * 2 + ch]) + value, -32768, 32767));
  }
}
} // namespace slam
