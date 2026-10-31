#include "native_audio.h"
#include "audio_gain.h"
#include <array>
#include <stdexcept>
namespace slam {
NativeAudio::NativeAudio(const std::filesystem::path &path, int order)
    : player_(std::make_unique<StimPlayer>(path, order)) {
  open_device();
}
NativeAudio::NativeAudio(std::vector<std::vector<std::uint8_t>> banks)
    : mean_(std::make_unique<MeanMusicSequencer>(std::move(banks))) {
  open_device();
}
void NativeAudio::open_device() {
  if (!SDL_InitSubSystem(SDL_INIT_AUDIO))
    throw std::runtime_error(SDL_GetError());
  const SDL_AudioSpec spec{SDL_AUDIO_S16, 2, StimPlayer::sample_rate};
  stream_ = SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, &spec,
                                      nullptr, nullptr);
  if (!stream_) {
    SDL_QuitSubSystem(SDL_INIT_AUDIO);
    throw std::runtime_error(SDL_GetError());
  }
}
NativeAudio::~NativeAudio() {
  SDL_DestroyAudioStream(stream_);
  SDL_QuitSubSystem(SDL_INIT_AUDIO);
}
int NativeAudio::queued_bytes() const {
  const auto bytes = SDL_GetAudioStreamQueued(stream_);
  if (bytes < 0)
    throw std::runtime_error(SDL_GetError());
  return bytes;
}
void NativeAudio::pump() {
  if (paused_)
    return;
  // About100ms of sourcePCM. SDL handles device resampling/channel conversion.
  std::array<std::int16_t, 2048> buffer{};
  while (queued_bytes() < StimPlayer::sample_rate * 4 / 10) {
    if (mean_)
      mean_->render(buffer.data(), buffer.size() / 2);
    else
      player_->render(buffer.data(), buffer.size() / 2);
    if (music_gain_ == 1.0f && sfx_gain_ == 1.0f) {
      // Preserve the existing original-PCM regression path exactly.
      if (samples_)
        samples_->mix(buffer.data(), buffer.size() / 2);
    } else {
      std::array<std::int16_t, 2048> effects{};
      if (samples_)
        samples_->mix(effects.data(), effects.size() / 2);
      for (std::size_t i = 0; i < buffer.size(); ++i)
        buffer[i] = mix_audio_levels(buffer[i], effects[i], music_gain_,
                                      sfx_gain_);
    }
    if (!SDL_PutAudioStreamData(stream_, buffer.data(), sizeof(buffer)))
      throw std::runtime_error(SDL_GetError());
  }
}
void NativeAudio::set_levels(float master, float music, float sfx) {
  music_gain_ = audio_gain(music);
  sfx_gain_ = audio_gain(sfx);
  if (!SDL_SetAudioStreamGain(stream_, audio_gain(master)))
    throw std::runtime_error(SDL_GetError());
}
void NativeAudio::set_paused(bool paused) {
  if (paused == paused_)
    return;
  const bool ok = paused ? SDL_PauseAudioStreamDevice(stream_)
                         : SDL_ResumeAudioStreamDevice(stream_);
  if (!ok)
    throw std::runtime_error(SDL_GetError());
  paused_ = paused;
}
void NativeAudio::set_mean_samples(const std::vector<std::uint8_t> &dat) {
  samples_ = std::make_unique<MeanSampleMixer>(dat);
}
void NativeAudio::set_samples(const std::vector<std::uint8_t>& dat,
                              std::vector<SampleProfile> profiles) {
  samples_=std::make_unique<MeanSampleMixer>(dat,std::move(profiles));
}
void NativeAudio::request(int service, int bank, int order,
                          unsigned descriptor, unsigned period, unsigned volume) {
  if (service == 0x5c) {
    if (samples_)
      samples_->request(bank, order, descriptor, period, volume);
    return;
  }
  if (!mean_)
    return;
  const int foreground = mean_->foreground_service();
  bool changes_foreground = true;
  if (service == 0x8c) {
    // Display preemption sends conditional cancellation; an inactive88 must
    // leave both the lower/base context and already queued PCM untouched.
    if (mean_->foreground_service() != 0x88)
      return;
    mean_->stop88();
  } else if (service == 0x80) {
    // Cancelling a paused/absent lower track leaves the audible upper/base
    // track alone; discarding its queued PCM would skip music and effects.
    changes_foreground = foreground == 0x84;
    mean_->stop84();
  } else if (service == 0x90)
    mean_->request90(bank, order);
  else if (service == 0x88)
    mean_->request88(bank, order);
  else if (service == 0x84) {
    // Retail 0x40634c defers this request until the upper track ends.
    changes_foreground = foreground != 0x88;
    mean_->request84(bank, order);
  } else
    throw std::runtime_error("Unsupported Mean sound service");
  if (changes_foreground && !SDL_ClearAudioStream(stream_))
    throw std::runtime_error(SDL_GetError());
}
void NativeAudio::restart() {
  if (samples_)
    samples_->reset();
  if (!SDL_ClearAudioStream(stream_))
    throw std::runtime_error(SDL_GetError());
  if (mean_)
    mean_->reset();
  else
    player_->restart();
}
} // namespace slam
