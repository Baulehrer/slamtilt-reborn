#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <vector>

namespace slam {
// Retail409350..40950a, presentation-only. Coordinates are projected sprite Y
// (WORD ball+12), not physical center Y. Never writes the gameplay ball pool.
class PirateCamera {
public:
  struct Ball {int y;unsigned state;};
  void step(unsigned phase,const std::vector<Ball>& balls) {
    previous_=current_;
    if(!phase) {
      pan_+=direction_*32768;
      if(pan_<=0){pan_=0;direction_=-direction_;}
      if(pan_>=maximum_*65536){pan_=maximum_*65536;direction_=-direction_;}
      current_=pan_>>16;velocity_=0;
      // Preserve original game-over branch's mixed-scale +quarter-height.
      position_=pan_+height_/4;
      return;
    }
    int y=-1;
    for(const auto& b:balls)if(b.state!=6)y=std::max(y,b.y);
    if(y==-1)for(const auto& b:balls)y=std::max(y,b.y);
    const int desired=floor_shift(position_-y*65536,3);
    velocity_+=std::clamp(desired-velocity_,-131072,131072);
    position_-=velocity_;
    current_=floor_shift(position_,16)-height_/4;
    if(current_<0){current_=0;position_=(height_/4)*65536;}
    if(current_>maximum_){current_=maximum_;position_=(maximum_+height_/4)*65536;}
  }
  int scroll(unsigned residual_ms) const {
    // Retail40549a..4054da uses truncation toward zero after interpolation.
    return int(double(previous_)+(double(current_)-previous_)*residual_ms/5.0);
  }
  std::array<int,6> state()const{return {current_,previous_,position_,velocity_,pan_,direction_};}
private:
  static int floor_shift(int value,unsigned bits) {
    const int scale=1<<bits;
    return value/scale-(value<0&&value%scale!=0);
  }
  int current_=0,previous_=0,position_=0,velocity_=0,pan_=0,direction_=1;
  static constexpr int height_=400,maximum_=200;
};
}
