#pragma once
#include "dmd/windows_dmd.h"
#include "assets/mean_score_font.h"
#include "rules/mean_ball_reset.h"
#include <filesystem>
namespace slam {
struct MeanMode4Phase1Assets {
  std::array<WindowsDmdPixels, 5> frames_10608e{};
  std::array<WindowsDmdPixels, 8> frames_1069ee{};
  std::array<WindowsDmdPixels, 10> frames_1078ee{};
};
MeanMode4Phase1Assets load_mean_mode4_phase1(const std::filesystem::path &);
struct MeanMode4Phase1Event {
  bool bank1_order50 = false, service8c = false, displayed = false;
  // Original service40 numeric overlay, renderer adapter owns font composition.
  bool number = false;
  std::uint32_t value = 0;
  std::int32_t eax = 0, edx = 0, ecx = 0;
};
// Original4141b8 idle Phase1; call only while mode4/phase1 idle is selected.
MeanMode4Phase1Event mean_mode4_phase1(MeanBallResetState &,
                                       const MeanMode4Phase1Assets &,
                                       WindowsDmdPixels &);
// Compose existing original numeric service406280 over the original frames.
MeanMode4Phase1Event render_mean_mode4_phase1(MeanBallResetState &,
    const MeanMode4Phase1Assets &, const MeanScoreFont &, WindowsDmdPixels &);
} // namespace slam
