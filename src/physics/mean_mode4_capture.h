#pragma once
#include "physics/mean_ball_pool.h"
#include "physics/mean_capture_tick.h"
#include "physics/mean_multiball_release.h"
#include "rules/mean_ball_reset.h"
namespace slam {
// Original415fd7 callback2, activation416246, release416440/416ca4.
// Raw fields are authoritative for392/3a6 and activation lamps; capture
// owns380/364. Caller keeps capture.table_mode/raw.table_mode synchronized
// after return.
bool mean_mode4_capture(MeanObject &, MeanCaptureTickState &,
                        MeanBallResetState &, MeanMultiballReleaseState &,
                        const MeanBallPool &, std::uint32_t,
                        MeanCaptureTickEvent &, bool &sample_437dec,
                        bool services_1c = false);
} // namespace slam
