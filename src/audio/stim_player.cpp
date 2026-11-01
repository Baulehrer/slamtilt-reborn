#include "stim_player.h"
#include <algorithm>
#include <limits>
#include <stdexcept>
namespace slam {
StimPlayer::StimPlayer(const std::filesystem::path &path, int order, TrackerMix mix)
    : order_(order), mix_(mix) {
  context_ = xmp_create_context();
  if (!context_)
    throw std::runtime_error("libxmp context allocation failed");
  initialize(xmp_load_module(context_, path.string().c_str()));
}
StimPlayer::StimPlayer(const std::vector<std::uint8_t> &data, int order, TrackerMix mix)
    : order_(order), mix_(mix) {
  if (data.size() > std::size_t(std::numeric_limits<long>::max()))
    throw std::runtime_error("Music module exceeds libxmp limit");
  context_ = xmp_create_context();
  if (!context_)
    throw std::runtime_error("libxmp context allocation failed");
  initialize(
      xmp_load_module_from_memory(context_, data.data(), long(data.size())));
}
void StimPlayer::initialize(int load_result) {
  if (load_result != 0) {
    xmp_free_context(context_);
    context_ = nullptr;
    throw std::runtime_error("Cannot load music module");
  }
  xmp_module_info info{};
  xmp_get_module_info(context_, &info);
  if (order_ < 0 || order_ >= info.mod->len ||
      xmp_start_player(context_, sample_rate, 0) != 0) {
    xmp_release_module(context_);
    xmp_free_context(context_);
    context_ = nullptr;
    throw std::runtime_error(
        "Invalid music order or libxmp player initialization failed");
  }
  restart();
}
StimPlayer::~StimPlayer() {
  if (context_) {
    xmp_end_player(context_);
    xmp_release_module(context_);
    xmp_free_context(context_);
  }
}
void StimPlayer::render(std::int16_t *output, std::size_t frames) {
  if (frames > std::size_t(std::numeric_limits<int>::max()) / 4)
    throw std::runtime_error("Music buffer exceeds libxmp limit");
  if (xmp_play_buffer(context_, output, int(frames * 4), 0) != 0)
    throw std::runtime_error("libxmp PCM rendering failed");
}
void StimPlayer::restart() {
  // Restart the mixer too: xmp_restart_module retains partially buffered PCM.
  xmp_end_player(context_);
  if (xmp_start_player(context_, sample_rate, 0) != 0)
    throw std::runtime_error("Cannot restart libxmp player");
  // Retail 44b560 mixes all six game voices into one mono buffer, and
  // 44cd4d reads the current sample without interpolation. Starting libxmp
  // resets these settings. The pinned STIM patch reproduces the tested Retail
  // mixer behavior in this mode; an unpatched system libxmp approximates it.
  if (mix_ == TrackerMix::RetailMono &&
      (xmp_set_player(context_, XMP_PLAYER_MIX, 0) != 0 ||
       xmp_set_player(context_, XMP_PLAYER_INTERP, XMP_INTERP_NEAREST) != 0 ||
       xmp_set_player(context_, XMP_PLAYER_VOLUME, 66) != 0))
    throw std::runtime_error("Cannot configure Retail tracker mix");
  if (order_ != 0 && xmp_set_position(context_, order_) < 0)
    throw std::runtime_error("Cannot select music order");
  ended_ = false;
  ended_by_f00_ = false;
  f00_ticks_remaining_ = -1;
  frame_pcm_.clear();
  frame_offset_ = 0;
}
void StimPlayer::select_order(int order) {
  xmp_module_info info{};
  xmp_get_module_info(context_, &info);
  if (order < 0 || order >= info.mod->len)
    throw std::runtime_error("Invalid music order");
  order_ = order;
#ifndef SLAM_STIM_CHANNEL_HISTORY
  restart();
#else
  if (mix_ != TrackerMix::RetailMono) {
    restart();
    return;
  }
  // A Retail order change keeps the tracker channels and live mixer voices.
  // Discard buffered audio before switching; the pinned STIM patch preserves
  // channel history when libxmp applies the new position.
  if (xmp_play_buffer(context_, nullptr, 0, 0) != 0)
    throw std::runtime_error("Cannot clear buffered tracker audio");
  const int position = xmp_set_position(context_, order);
  if (position < -1 || (position < 0 && order != 0))
    throw std::runtime_error("Cannot select music order");
  ended_ = false;
  ended_by_f00_ = false;
  f00_ticks_remaining_ = -1;
  frame_pcm_.clear();
  frame_offset_ = 0;
#endif
}
bool StimPlayer::inherit_history(const StimPlayer &source) {
#ifdef SLAM_STIM_CHANNEL_HISTORY
  if (mix_ == TrackerMix::RetailMono && source.mix_ == TrackerMix::RetailMono)
    return xmp_slam_transfer(source.context_, context_) == 0;
#else
  (void)source;
#endif
  return false;
}
bool StimPlayer::resume_history(const StimPlayer &source) {
#ifdef SLAM_STIM_CHANNEL_HISTORY
  if (mix_ == TrackerMix::RetailMono && source.mix_ == TrackerMix::RetailMono &&
      xmp_slam_resume(source.context_, context_) == 0) {
    ended_ = false;
    ended_by_f00_ = false;
    f00_ticks_remaining_ = -1;
    frame_pcm_.clear();
    frame_offset_ = 0;
    return true;
  }
#else
  (void)source;
#endif
  return false;
}
std::size_t StimPlayer::render_once(std::int16_t *output, std::size_t frames,
                                    unsigned f00_tail_ticks) {
  if (frames > std::size_t(std::numeric_limits<int>::max()) / 4)
    throw std::runtime_error("Music buffer exceeds libxmp limit");
  std::fill_n(output, frames * 2, std::int16_t(0));
  std::size_t written = 0;
  while (written < frames && !ended_) {
    if (frame_offset_ == frame_pcm_.size()) {
      if (f00_ticks_remaining_ == 0) {
        ended_ = true;
        ended_by_f00_ = true;
        break;
      }
      const int result = xmp_play_frame(context_);
      if (result == -XMP_END) {
        ended_ = true;
        break;
      }
      if (result != 0)
        throw std::runtime_error("libxmp frame rendering failed");
      xmp_frame_info frame{};
      xmp_get_frame_info(context_, &frame);
      bool stop = frame.loop_count > 0;
      bool f00 = false;
      if (frame.frame == 0) {
        xmp_module_info info{};
        xmp_get_module_info(context_, &info);
        for (int ch = 0; ch < info.mod->chn; ++ch) {
          const auto &event =
              info.mod->xxt[info.mod->xxp[frame.pattern]->index[ch]]
                  ->event[frame.row];
          f00 |= event.fxt == 0x0f && event.fxp == 0;
        }
      }
      if (f00 && f00_tail_ticks && f00_ticks_remaining_ < 0)
        f00_ticks_remaining_ = int(f00_tail_ticks);
      else if (f00 && !f00_tail_ticks)
        stop = true;
      if (stop) {
        ended_ = true;
        ended_by_f00_ = f00;
        break;
      }
      const auto *pcm = static_cast<const std::int16_t *>(frame.buffer);
      frame_pcm_.assign(pcm, pcm + frame.buffer_size / 2);
      frame_offset_ = 0;
      if (frame_pcm_.empty())
        throw std::runtime_error("libxmp produced empty frame");
      if (f00_ticks_remaining_ > 0)
        --f00_ticks_remaining_;
    }
    const auto count =
        std::min((frame_pcm_.size() - frame_offset_) / 2, frames - written);
    std::copy_n(frame_pcm_.data() + frame_offset_, count * 2,
                output + written * 2);
    frame_offset_ += count * 2;
    written += count;
  }
  return written;
}
} // namespace slam
