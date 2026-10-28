#pragma once
#include <array>
#include <cstdint>
namespace slam {
// Original419919..419944, once per ungated50Hz table tick.
inline void mean_skull_clock(std::int16_t &timer,std::uint16_t &count,std::array<std::uint8_t,4>&lamp){
 if(timer<0)return;
 if(--timer<0){count=0;lamp[0]=2;}
}
}
