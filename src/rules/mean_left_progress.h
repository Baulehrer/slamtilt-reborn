#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanLeftProgressEvent { bool display_request=false,capture_delay_request=false; std::uint32_t callback=0; };
// Original41b31f..41b491 AFTER pit/shared reward and438b38/3c/40 writes.
// Valid initialized lamp-stage0..2 and progress0..5. Caller preserves ordering.
MeanLeftProgressEvent mean_left_progress(MeanBallResetState&,std::uint32_t display_return=0);
}
