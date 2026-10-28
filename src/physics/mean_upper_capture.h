#pragma once
#include "mean_step.h"
namespace slam {
struct MeanUpperCaptureState {
  std::array<std::int32_t, 3> field_438b5c{{-1, 100, 0}};
  std::int16_t field_43f36a = 50;
  std::int16_t field_43f364 = 0, field_43f394 = 0;
  std::int16_t field_43f1f2 = 0, field_43f1e6 = 0;
  std::int16_t field_43f37e = 0;
  std::int16_t field_43f200 = 0, field_43f202 = 0, field_43f1fa = 0;
  std::int16_t field_43f378 = 0, field_43f1fc = 0;
  std::array<std::int32_t, 3> field_438b44{{0, 0, 0}};
  std::int32_t table_mode = 2;
};
struct MeanUpperCaptureEvent {
  std::uint32_t score_request = 0, field_player_08_add = 0;
  unsigned early_release_count = 0; // 416be4 before callback1 continuation.
  bool release_requested = false, transfer_requested = false;
  bool rule_service_request = false;
  bool capture_delay_request = false; // Actual40f754 after service34 admission.
  std::array<std::int32_t, 5> capture_delay_selectors{{0,1,1,1,1}};
  std::int32_t capture_delay = 0;
  bool field_024_minus_one_after_delay = false; // 415795 first-unlock continuation.
  bool mode4_transfer_requested = false;
  bool mode6_start_requested = false;
  bool selected3_start_requested =
      false; // 415b9a: caller must initialize/dispatch shared+44.
  std::uint16_t field_player_10_add = 0;
  std::uint8_t reward_request = 0; // 1=field200, 2=field202, 3=field1fa
};
// Human callback1, including mode4 hold/award/release, and mode5 transfer for
// selections0/1/2; reward branches200/202/1fa set the original shared gate.
// Caller handles reward display requests and gate progression. Full mode5
// rule/lamp writes omitted. Caller supplies observed/shared randomness to the
// separate416be4 release.
bool mean_upper_capture_tick(const MeanObject &ball,
                             MeanUpperCaptureState &state,
                             MeanUpperCaptureEvent &event);
// Tilt human1..3 wrapper: early416be4 runs before saved-entry continuation.
// Caller still applies ordinary release/transfer requests and their audio.
bool mean_upper_capture_tilt_tick(MeanObject &ball, MeanUpperCaptureState &state,
                                  MeanUpperCaptureEvent &event,
                                  std::uint32_t dat_base, std::uint32_t random);
} // namespace slam
