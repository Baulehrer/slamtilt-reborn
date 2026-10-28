#pragma once
#include "mean_capture_tick.h"
#include "mean_mode_reset.h"
namespace slam {
struct MeanMode5LeftState : MeanModeResetState {
  std::int16_t field_43f3b4 = 0, field_43f39c = 8400;
  std::array<std::int16_t, 6> field_43f044{};
  std::int16_t field_43f372 = 0, field_43f38c = 0, field_43f386 = 0;
  std::int16_t field_43f376 = 0, field_43f36e = 0, field_43f37e = 0,
               field_43f388 = 0;
  std::array<std::uint8_t, 24> field_43f23c{};
  std::int16_t field_43f3ae = 0;
  std::int16_t field_43f382 = 0, field_43f38e = -1, field_43f368 = -1,
               field_43f36c = -1, field_43f35e = 0;
  std::array<std::uint8_t, 4> field_43f260{};
  std::int32_t field_438b90 = 0;
  std::int32_t field_engine_40 = 0;
  std::uint32_t field_43f05c = 0, field_43f058 = 0, field_43f050 = 0;
};
void mean_mode6_begin(MeanMode5LeftState &);
void mean_mode4_transfer(MeanObject &, MeanCaptureTickState &,
                         MeanMode5LeftState &, std::uint32_t);
// Original4157dd..415dc6 bounded selections0/1/2/4 initialization.
bool mean_mode5_begin(MeanMode5LeftState &mode,
                      std::uint32_t field_engine_38 = 0);
// Bounded mode5 callback2 through417068, includes terminal award reset,
// presentation effects external.
bool mean_mode5_left(MeanObject &ball, MeanCaptureTickState &state,
                     MeanMode5LeftState &mode, std::uint32_t dat_base,
                     MeanCaptureTickEvent &event, bool services_1c = false, bool display_accepted = true);
} // namespace slam
