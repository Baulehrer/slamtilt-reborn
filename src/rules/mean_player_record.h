#pragma once
#include <array>
#include <cstdint>
namespace slam {
// Actual419e68 initializes eight52-byte records; bytes17/23/29 are untouched.
inline void mean_initialize_player_record(std::array<std::uint8_t,52> &record) {
  for(unsigned i=0;i<record.size();++i)
    if(i!=17 && i!=23 && i!=29) record[i]=0;
  record[4]=4; record[18]=4;
  record[34]=0x40;record[35]=0x1f; // WORD43f1f6 after419b00:8000.
}
} // namespace slam
