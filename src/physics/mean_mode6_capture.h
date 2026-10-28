#pragma once
#include "mean_mode5_left.h"
#include "mean_upper_capture.h"
namespace slam {
struct MeanMode6CaptureEvent {
  bool transfer = false, lamp_reset = false;
};
// Bounded415dc7 and416821 capture-count gates; caller applies original
// transfer.
bool mean_mode6_capture_tick(MeanObject &, MeanMode5LeftState &,
                             MeanUpperCaptureState &, unsigned,
                             MeanMode6CaptureEvent &);
} // namespace slam
