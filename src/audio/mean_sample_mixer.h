#pragma once
#include <array>
#include <cstdint>
#include <vector>
namespace slam {
struct SampleProfile {
  unsigned descriptor;
  std::size_t offset,length;
  unsigned period;
};
// Original Mean direct and bank-relative samples; two SFX slots4/5, allocator4016dc.
class MeanSampleMixer {
public:
  explicit MeanSampleMixer(const std::vector<std::uint8_t> &dat);
  MeanSampleMixer(const std::vector<std::uint8_t> &dat,
                  std::vector<SampleProfile> profiles);
  void request(int field_1c, int field_20, unsigned descriptor = 0);
  void mix(std::int16_t *stereo, std::size_t frames);
  void reset();
  int active() const;

private:
  struct Voice {
    unsigned sample = 0;
    std::uint64_t phase = 0;
    int field_20 = 0;
    bool active = false;
  };
  std::vector<SampleProfile> profiles_;
  std::vector<std::vector<std::int8_t>> pcm_;
  std::array<Voice, 2> voices_{};
  struct Request {
    unsigned sample;
    int field_1c, field_20;
  };
  std::vector<Request> pending_;
};
} // namespace slam
