#pragma once
#include "rules/mean_ball_reset.h"
namespace slam {
struct MeanStockCarEvent {
  bool selected_changed = false;
  std::uint32_t score = 0, callback = 0;
};
// Original41e092/41e154 rule side effects AFTER accepted physical bumper response.
// Material3 calls original419da4; material4 does not. No guessed physical response.
MeanStockCarEvent mean_stock_car_bumper(MeanBallResetState &, unsigned material,
                                       bool suppressed, std::uint32_t display_handle);
}
