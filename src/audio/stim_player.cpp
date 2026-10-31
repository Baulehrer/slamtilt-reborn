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
  // 44cd4d reads the current sample without interpolation. Libxmp's nearest
  // mode rounds sample positions; Retail floors them, so it is an approximation.
  // Starting libxmp resets these options. The 66% level approximates the tested
  // full-volume six-voice mix; timing and PCM are not yet identical to Retail.
  if (mix_ == TrackerMix::RetailMono &&
      (xmp_set_player(context_, XMP_PLAYER_MIX, 0) != 0 ||
       xmp_set_player(context_, XMP_PLAYER_INTERP, XMP_INTERP_NEAREST) != 0 ||
       xmp_set_player(context_, XMP_PLAYER_VOLUME, 66) != 0))
    throw std::runtime_error("Cannot configure Retail tracker mix");
  if (order_ != 0 && xmp_set_position(context_, order_) < 0)
    throw std::runtime_error("Cannot select music order");
  ended_ = false;
  frame_pcm_.clear();
  frame_offset_ = 0;
}
void StimPlayer::select_order(int order) {
  xmp_module_info info{};
  xmp_get_module_info(context_, &info);
  if (order < 0 || order >= info.mod->len)
    throw std::runtime_error("Invalid music order");
  order_ = order;
  restart();
}
std::size_t StimPlayer::render_once(std::int16_t *output, std::size_t frames) {
  if (frames > std::size_t(std::numeric_limits<int>::max()) / 4)
    throw std::runtime_error("Music buffer exceeds libxmp limit");
  std::fill_n(output, frames * 2, std::int16_t(0));
  std::size_t written = 0;
  while (written < frames && !ended_) {
    if (frame_offset_ == frame_pcm_.size()) {
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
      if (frame.frame == 0) {
        xmp_module_info info{};
        xmp_get_module_info(context_, &info);
        for (int ch = 0; ch < info.mod->chn; ++ch) {
          const auto &event =
              info.mod->xxt[info.mod->xxp[frame.pattern]->index[ch]]
                  ->event[frame.row];
          stop |= event.fxt == 0x0f && event.fxp == 0;
        }
      }
      if (stop) {
        ended_ = true;
        break;
      }
      const auto *pcm = static_cast<const std::int16_t *>(frame.buffer);
      frame_pcm_.assign(pcm, pcm + frame.buffer_size / 2);
      frame_offset_ = 0;
      if (frame_pcm_.empty())
        throw std::runtime_error("libxmp produced empty frame");
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
