#ifdef NDEBUG
#undef NDEBUG
#endif
#include "audio/audio_gain.h"
#include <cassert>
#include <limits>

int main() {
  using slam::mix_audio_levels;
  assert(mix_audio_levels(30000, 10000, 1, 1) == 32767);
  assert(mix_audio_levels(-30000, -10000, 1, 1) == -32768);
  // Attenuate each source before clipping: clipping first would give 16383.
  assert(mix_audio_levels(30000, 10000, .5f, .5f) == 20000);
  assert(mix_audio_levels(30000, -10000, 0, 1) == -10000);
  assert(mix_audio_levels(-30000, 10000, 1, 0) == -30000);
  assert(mix_audio_levels(30000, -10000, 0, 0) == 0);
  assert(slam::audio_gain(-1) == 0);
  assert(slam::audio_gain(2) == 1);
  assert(slam::audio_gain(std::numeric_limits<float>::quiet_NaN()) == 1);
}
