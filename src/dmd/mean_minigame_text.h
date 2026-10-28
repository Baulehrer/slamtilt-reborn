#pragma once
#include "dmd/mean_bonus_pixels.h"
#include <functional>
namespace slam {
unsigned draw_mean_numeric_text(const MeanBonusPixels &, WindowsDmdPixels &,
    std::string_view digits, int x, int y, int align, unsigned mask);
void mean_minigame_text_service(const MeanBonusPixels &, WindowsDmdPixels &,
    std::uint32_t target, std::array<std::uint32_t,8> &registers,
    const std::function<std::uint32_t(std::uint32_t,unsigned)> &read);
} // namespace slam
