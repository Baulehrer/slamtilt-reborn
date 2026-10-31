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
  auto next = start(bank, order);
  reset();
  base_ = std::move(next);
}
void MeanMusicSequencer::request84(int bank, int order) {
  // Validate even deferred requests, without changing the paused context.
  auto player = start(bank, order);
  if (upper_)
    pending_lower_ = {{bank, order}};
  else
    lower_ = std::move(player);
}
void MeanMusicSequencer::request88(int bank, int order) {
  upper_ = start(bank, order);
}
void MeanMusicSequencer::resume() {
  upper_.reset();
  if (pending_lower_) {
    const auto [bank, order] = *pending_lower_;
    lower_ = start(bank, order);
    pending_lower_.reset();
  }
}
void MeanMusicSequencer::stop88() { resume(); }
void MeanMusicSequencer::stop84() {
  lower_.reset();
  pending_lower_.reset();
}
void MeanMusicSequencer::reset() {
  upper_.reset();
  base_.reset();
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
    written += player->render_once(pcm + written * 2, frames - written);
    if (!player->ended())
      break;
    if (upper_)
      resume();
    else
      lower_.reset();
  }
}
} // namespace slam
