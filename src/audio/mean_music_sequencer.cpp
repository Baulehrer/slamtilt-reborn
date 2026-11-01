#include "mean_music_sequencer.h"
#include <algorithm>
#include <stdexcept>
namespace slam {
MeanMusicSequencer::MeanMusicSequencer(
    std::vector<std::vector<std::uint8_t>> banks)
    : banks_(std::move(banks)) {}
std::unique_ptr<StimPlayer> MeanMusicSequencer::start(int bank,
                                                      int order) const {
  if (bank < 0 || std::size_t(bank) >= banks_.size())
    throw std::runtime_error("Invalid Mean music bank");
  return std::make_unique<StimPlayer>(banks_[bank], order, TrackerMix::RetailMono);
}
void MeanMusicSequencer::request90(int bank, int order) {
  if (base_ && !upper_ && !lower_ && base_bank_ == bank) {
    base_->select_order(order);
    pending_lower_.reset();
    return;
  }
  auto next = start(bank, order);
  if (base_ && !upper_ && !lower_)
    next->inherit_history(*base_);
  reset();
  base_ = std::move(next);
  base_bank_ = bank;
}
void MeanMusicSequencer::request84(int bank, int order) {
  if (!upper_ && lower_ && lower_bank_ == bank) {
    lower_->select_order(order);
    return;
  }
  // Validate even deferred requests, without changing the paused context.
  auto player = start(bank, order);
  if (upper_)
    pending_lower_ = {{bank, order}};
  else {
    if (lower_)
      player->inherit_history(*lower_);
    else if (base_)
      player->inherit_history(*base_);
    lower_ = std::move(player);
    lower_bank_ = bank;
  }
}
void MeanMusicSequencer::request88(int bank, int order) {
  if (upper_ && upper_bank_ == bank) {
    upper_->select_order(order);
    return;
  }
  auto next = start(bank, order);
  if (upper_)
    next->inherit_history(*upper_);
  else if (lower_)
    next->inherit_history(*lower_);
  else if (base_)
    next->inherit_history(*base_);
  upper_ = std::move(next);
  upper_bank_ = bank;
}
void MeanMusicSequencer::resume() {
  if (pending_lower_) {
    const auto [bank, order] = *pending_lower_;
    auto next = start(bank, order);
#ifdef SLAM_STIM_CHANNEL_HISTORY
    // Retail starts the deferred tracker while the upper voices are still
    // live. Preserve their phase and channel history before releasing it.
    if (upper_)
      next->inherit_history(*upper_);
#endif
    lower_ = std::move(next);
    lower_bank_ = bank;
    pending_lower_.reset();
  }
  upper_.reset();
  upper_bank_ = -1;
}
void MeanMusicSequencer::stop88() { resume(); }
void MeanMusicSequencer::stop84() {
  lower_.reset();
  lower_bank_ = -1;
  pending_lower_.reset();
}
void MeanMusicSequencer::reset() {
  upper_.reset();
  upper_bank_ = -1;
  base_.reset();
  base_bank_ = -1;
  stop84();
}
void MeanMusicSequencer::render(std::int16_t *pcm, std::size_t frames) {
  std::fill_n(pcm, frames * 2, std::int16_t(0));
  std::size_t written = 0;
  while (written < frames) {
    auto *player = upper_ ? upper_.get() : lower_.get();
    if (!player) {
      if (base_)
        base_->render(pcm + written * 2, frames - written);
      break;
    }
#ifdef SLAM_STIM_CHANNEL_HISTORY
    // Retail's 84 service remains active at F00 until another service stops it.
    if (!upper_) {
      lower_->render(pcm + written * 2, frames - written);
      break;
    }
    // 4062f0 observes F00 on the following step, then restores on the next.
    written += player->render_once(pcm + written * 2, frames - written, 2);
#else
    written += player->render_once(pcm + written * 2, frames - written);
#endif
    if (!player->ended())
      break;
    if (upper_) {
#ifdef SLAM_STIM_CHANNEL_HISTORY
      if (upper_->ended_by_f00() && !pending_lower_) {
        auto *previous = lower_ ? lower_.get() : base_.get();
        if (previous)
          previous->resume_history(*upper_);
      }
#endif
      resume();
    } else {
      lower_.reset();
      lower_bank_ = -1;
    }
  }
}
} // namespace slam
