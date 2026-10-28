#pragma once
#include "rules/mean_ball_reset.h"
#include <vector>
#include <functional>
namespace slam {
struct MeanPitStopRequest { std::uint32_t callback; unsigned eax, edx, ecx; std::int32_t stack0=-1, stack1=-1; unsigned ebx=0; };
struct MeanPitStopEvents {
  std::vector<std::uint32_t> scores;
  std::vector<MeanPitStopRequest> requests;
  bool clear_capture_delays=false;
};
// Original41b61c..41b8cd. Event IDs0..3. Shared service34/40f754
// admission explicit; original table mode is unchanged.
MeanPitStopEvents mean_pit_stop(MeanBallResetState &,unsigned event_id,
                               std::uint32_t service34_return);
MeanPitStopEvents mean_pit_stop(MeanBallResetState &,unsigned event_id,
    const std::function<std::uint32_t(const MeanPitStopRequest &)> &admit);
// Original4198ce..419903; called50Hz inside419890, gated by service1c==0.
void mean_pit_stop_tick(MeanBallResetState &,std::uint32_t service1c);
}
