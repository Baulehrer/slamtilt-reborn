#pragma once
#include "physics/mean_mode4_capture.h"
namespace slam {
struct MeanMode4RightState {
  std::array<std::int32_t, 3> field_438b80{{-1, 100, 0}};
  std::int32_t field_438b38 = 0, field_438b3c = 0, field_438b40 = 0;
};
struct MeanMode4RightEvent {
  std::uint32_t score = 0, field_player_08_add = 0, callback = 0;
  bool mode4_reset = false, service88_1_56 = false, service84_0_73 = false;
  // 4165a3..5cb: shared10/14/20=0,18=-1,44=1;43efd4/43efcc=0.
  bool start_shared44 = false, sample_437dc8 = false;
};
// Caller owns service1c==0 guard.
// 41da51..daec pre-ball right capture: x>=260,field5c20,slot80/callback4 free.
bool mean_mode4_right_capture_entry(MeanObject &, MeanBallResetState &,
                                    MeanMode4RightState &, const MeanBallPool &,
                                    MeanMode4RightEvent &);
// 41b010 phase1 from layer3/mask1/y<64, human mode<4,WORD392!=0.
MeanMode4RightEvent mean_mode4_right_ramp(MeanBallResetState &, unsigned layer,
                                          unsigned mask, std::int32_t y);
// 4164e1 callback4 human modes1..4; optional service1c transfer then continuation.
//  Mode4 special reset416fe0 is reported externally (slots438b2c/34).
bool mean_mode4_right_capture(MeanObject &, MeanBallResetState &,
                              MeanMode4RightState &, MeanCaptureTickState &,
                              const MeanBallPool &, std::uint32_t dat_base,
                              MeanMode4RightEvent &, bool services_1c = false);
} // namespace slam
