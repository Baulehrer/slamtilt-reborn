#include "mean_game_end.h"
namespace slam {
bool mean_game_end_required(std::uint16_t ball, std::uint32_t field_454aa4) {
  const int signed_ball = ball < 0x8000 ? ball : int(ball) - 65536;
  return signed_ball >= (field_454aa4 == 0 ? 4 : 6);
}
} // namespace slam
