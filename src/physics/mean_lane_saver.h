#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>
namespace slam {
struct MeanLaneSaverEvent {
  bool draw_requested = false;
  std::int32_t drawn_frame = 0;
  bool patch_requested = false;
  bool enabled = false;
};
// Original417dd4, slot438b44. Called by table animation service417d68.
// descriptor_idle means signed WORD[438230[5]+2]<0. Service60 is reported;
// caller retains original animation descriptor ownership.
MeanLaneSaverEvent mean_lane_saver_tick(std::array<std::int32_t,3> &slot,
                                      bool descriptor_idle);
// Original terminal copies:30 normal DWORD rows and32 DWORD rows in each
// of four hit/material planes (stride6040); destination byte49e1.
void mean_lane_saver_patch(std::vector<std::uint8_t> &dat,
                          std::size_t normal_offset, std::size_t hit_offset,
                          bool enabled);
} // namespace slam
