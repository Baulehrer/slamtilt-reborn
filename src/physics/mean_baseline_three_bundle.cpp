#include "mean_baseline_three_bundle.h"
namespace slam {
bool mean_baseline_three_noop(const MeanObject &ball) {
  return ball.i32(0) > 60 * 65536 &&
         (ball.i32(0) < 260 * 65536 || ball.u16(0x5c) != 20);
}
} // namespace slam
