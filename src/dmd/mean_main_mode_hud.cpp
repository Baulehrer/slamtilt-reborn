#include "mean_main_mode_hud.h"
#include "dmd/mean_minigame_text.h"
#include <algorithm>
#include <fstream>
#include <stdexcept>
#include <string>
namespace slam {
MeanMainModeHudAssets load_mean_main_mode_hud(const std::filesystem::path &mean,
                                             const std::filesystem::path &main) {
  MeanMainModeHudAssets a;
  a.font=load_mean_bonus_pixels(main);
  std::ifstream in(mean,std::ios::binary);
  auto bytes=[&](auto &data,unsigned offset) {
    in.seekg(offset);in.read(reinterpret_cast<char *>(data.data()),data.size());
    if(!in)throw std::runtime_error("Truncated Mean main-mode HUD");
  };
  auto frames=[&](auto &out,unsigned offset) {
    for(auto &frame:out) {
      std::array<std::uint8_t,480> packed{};
      bytes(packed,offset);frame=decode_windows_dmd(packed);offset+=480;
    }
  };
  frames(a.chicken_a,0x10eb4e);frames(a.chicken_b,0x10f68e);
  frames(a.monster_a,0x11850e);frames(a.monster_b,0x118aae);
  frames(a.offroad,0x13128e);frames(a.speed,0x13b1ee);frames(a.speed_locks,0x14eece);
  for(unsigned i=0;i<a.rally.size();++i)bytes(a.rally[i],0x120a2e + i*480);
  for(unsigned i=0;i<a.rally_arrows.size();++i)bytes(a.rally_arrows[i],0x15100c+i*56);
  return a;
}
bool mean_main_mode_hud_step(MeanMainModeHud &s,const MeanMainModeHudAssets &a) {
  if(s.mode!=6 && (s.mode!=5 || s.selected>4 || s.selected==3))return false;
  const auto old=s.counter++;
  auto number=[&](std::uint64_t v,int x,int y,int align,unsigned mask,bool bcd=false) {
    auto digits=std::to_string(v);
    if(bcd && digits.size()<2)digits.insert(digits.begin(),'0');
    draw_mean_numeric_text(a.font,s.pixels,digits,x,y,align,mask);
  };
  if(s.mode==6) {
    const int active=(s.field_38e>=0)+(s.field_368>=0)+(s.field_36c>=0);
    if(!active)s.pixels=a.speed[s.counter%7];
    else if(s.counter&4)s.pixels.fill(0);
    else s.pixels=a.speed_locks[active-1];
    number(s.score,24,0,2,3,true);
  } else if(s.selected==0) {
    const auto count=static_cast<std::int32_t>(old);
    const int frame=count%6;
    if(frame<0)throw std::runtime_error("Unsupported negative Chicken HUD counter");
    s.pixels=((count/6)&31)<16 ? a.chicken_a[frame] : a.chicken_b[frame];
    number(s.field_05c,24,1,2,0);number(s.field_05c,24,0,2,3);
    const auto seconds=s.field_39c/200;
    const auto value=seconds<5 ? seconds : seconds-5;
    number(static_cast<std::uint32_t>(value),0,1,0,0);
    number(static_cast<std::uint32_t>(value),0,0,0,3);
  } else if(s.selected==1) {
    const auto half=s.counter>>1;
    s.pixels=((half/3)&31)<16 ? a.monster_a[half%3] : a.monster_b[half%3];
    number(static_cast<std::uint32_t>(s.field_39c/200),24,1,2,3);
    number(s.score,24,14,2,3,true);
  } else if(s.selected==2) {
    const auto count=static_cast<std::int32_t>(old);
    // Arithmetic shift before signed remainder in413e3c.
    const int frame=(count>=0 ? count/2 : (static_cast<std::int64_t>(count)-1)/2)%22;
    if(frame<0)throw std::runtime_error("Unsupported negative Rally HUD counter");
    auto packed=a.rally[frame];
    if(old&8) {
      constexpr unsigned selection[]={4,0,1,1,2,3};
      constexpr unsigned columns[]={1,3,7,9,1};
      if(s.field_38c<0 || s.field_38c>=6)throw std::runtime_error("Unsupported Rally HUD target");
      const unsigned arrow=selection[s.field_38c],column=columns[arrow];
      const auto &data=a.rally_arrows[arrow];
      for(unsigned plane=0;plane<2;++plane) {
        auto base=plane*240+column;
        packed[base+24]=packed[base+25]=0;
        packed[base+204]=packed[base+205]=0;
        for(unsigned row=0;row<14;++row)
          std::copy_n(data.begin()+plane*28+row*2,2,packed.begin()+base+36+row*12);
      }
    }
    s.pixels=decode_windows_dmd(packed);
    number(static_cast<std::uint32_t>(s.field_39c/200),24,14,2,3);
  } else {
    const int frame=(static_cast<std::int32_t>(old)/3)%20;
    if(frame<0)throw std::runtime_error("Unsupported negative Offroad HUD counter");
    s.pixels=a.offroad[frame];
    number(s.score,24,13,2,0,true);number(s.score,24,14,2,3,true);
  }
  return true;
}
} // namespace slam
