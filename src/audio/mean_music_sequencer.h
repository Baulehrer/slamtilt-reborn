#pragma once
#include "stim_player.h"
#include <memory>
#include <optional>
#include <utility>
namespace slam {
// Original4059ac: one foreground, 88 preempts84;84 remains paused.
class MeanMusicSequencer {
public:
  explicit MeanMusicSequencer(std::vector<std::vector<std::uint8_t>> banks);
  void request90(int bank, int order);
  void request84(int bank, int order);
  void request88(int bank, int order);
  void stop88(); // service8c
  void stop84(); // service80: cancel queued/paused84
  void reset();
  void render(std::int16_t *, std::size_t frames);
  int foreground_service() const {
    return upper_ ? 0x88 : lower_ ? 0x84 : base_ ? 0x90 : 0;
  }

private:
  std::unique_ptr<StimPlayer> start(int bank, int order) const;
  void resume();
  std::vector<std::vector<std::uint8_t>> banks_;
  std::unique_ptr<StimPlayer> lower_, upper_, base_;
  int lower_bank_ = -1, upper_bank_ = -1, base_bank_ = -1;
  std::optional<std::pair<int, int>> pending_lower_;
};
} // namespace slam
