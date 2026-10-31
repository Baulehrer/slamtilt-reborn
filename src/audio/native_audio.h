#pragma once
#include "mean_music_sequencer.h"
#include "mean_sample_mixer.h"
#include "stim_player.h"
#include <SDL3/SDL.h>
namespace slam {
class NativeAudio {
public:
  explicit NativeAudio(const std::filesystem::path &, int order = 0);
  explicit NativeAudio(std::vector<std::vector<std::uint8_t>> banks);
  void set_mean_samples(const std::vector<std::uint8_t> &dat);
  void set_samples(const std::vector<std::uint8_t>& dat,
                   std::vector<SampleProfile> profiles);
  void request(int service, int bank, int order, unsigned descriptor = 0,
               unsigned period = 0, unsigned volume = 64);
  ~NativeAudio();
  NativeAudio(const NativeAudio &) = delete;
  NativeAudio &operator=(const NativeAudio &) = delete;
  void pump();
  void set_paused(bool);
  void set_volume(float gain) { SDL_SetAudioStreamGain(stream_,gain); }
  // Independent bus levels; master is applied by SDL after PCM mixing.
  void set_levels(float master, float music, float sfx);
  void restart();
  int queued_bytes() const;
  bool device_paused() const { return SDL_AudioDevicePaused(SDL_GetAudioStreamDevice(stream_)); }

private:
  void open_device();
  std::unique_ptr<StimPlayer> player_;
  std::unique_ptr<MeanMusicSequencer> mean_;
  SDL_AudioStream *stream_ = nullptr;
  bool paused_ = true;
  std::unique_ptr<MeanSampleMixer> samples_;
  float music_gain_ = 1.0f;
  float sfx_gain_ = 1.0f;
};
} // namespace slam
