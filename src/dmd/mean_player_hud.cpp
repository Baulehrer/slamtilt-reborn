#include "mean_player_hud.h"
#include "dmd/mean_minigame_text.h"
#include <algorithm>
#include <fstream>
#include <stdexcept>
#include <string>
namespace slam {
MeanPlayerHudAssets load_mean_player_hud(const std::filesystem::path &mean,
                                        const std::filesystem::path &main) {
  MeanPlayerHudAssets a;
  a.skillshot=load_mean_skillshot_display(mean);
  a.skillshot.font=load_mean_bonus_pixels(main);
  std::ifstream in(mean,std::ios::binary);
  auto read=[&](unsigned offset) {
    std::array<std::uint8_t,480> packed{};
    in.seekg(offset);in.read(reinterpret_cast<char *>(packed.data()),packed.size());
    if(!in)throw std::runtime_error("Truncated Mean player HUD");
    return packed;
  };
  a.frame_14e92e=read(0x14e92e);
  a.frame_14eb0e=decode_windows_dmd(read(0x14eb0e));
  a.frame_151a84=decode_windows_dmd(read(0x151a84));
  return a;
}
bool mean_player_hud_step(MeanPlayerHud &s,const MeanPlayerHudAssets &a) {
  if(s.field_35c) {
    auto counter=static_cast<std::int32_t>(s.counter);
    if(!mean_skillshot_display(counter,a.skillshot,s.pixels,s.field_358,s.field_206,s.field_362))return false;
    s.counter=static_cast<std::uint32_t>(counter);
    s.scratch.fill(0); // Original414573 clears120DWORDs, before text service.
    if(s.counter&2) {
      const auto &tile=s.field_358 ? a.skillshot.rewards_1587a4[s.field_362] : a.skillshot.scores_158be8[s.field_206];
      for(unsigned plane=0;plane<2;++plane)for(unsigned y=0;y<13;++y)
        std::copy_n(tile.begin()+plane*78+y*6,6,s.scratch.begin()+plane*240+87+y*12);
    }
    return true;
  }
  if(s.field_360>=0 && s.field_engine_60) {
    ++s.counter;
    s.field_360=static_cast<std::int16_t>(static_cast<std::uint16_t>(s.field_360)-1);
    s.pixels=s.counter&2 ? a.frame_151a84 : WindowsDmdPixels{};
    return true;
  }
  auto number=[&](std::uint64_t n,int x,int y,bool bcd=false) {
    auto digits=std::to_string(n);
    if(bcd && digits.size()<2)digits.insert(digits.begin(),'0');
    draw_mean_numeric_text(a.skillshot.font,s.pixels,digits,x,y,2,3);
  };
  if(s.field_engine_5c) {
    s.pixels=a.frame_14eb0e;
    number(s.player_0e,24,1);number(s.field_engine_04,12,1);
    number(s.field_engine_08,19,11);
    return true;
  }
  ++s.counter;
  const bool player_page=(s.counter&127)<=64;
  if(player_page)s.scratch=a.frame_14e92e;
  else s.scratch.fill(0); //414aac increments inside the loop: all120DWORDs.
  s.pixels=decode_windows_dmd(s.scratch);
  if(!mean_skillshot_choice_pair(static_cast<std::int32_t>(s.counter),a.skillshot,s.pixels,s.field_358,s.field_206,s.field_362))return false;
  // Persist only the packed choice overlay, before numeric screen services.
  for(unsigned i=0;i<480;++i) {
    const unsigned plane=i/240,byte=i%240;
    std::uint8_t value=0;
    for(unsigned bit=0;bit<8;++bit)value|=((s.pixels[byte*8+bit]>>plane)&1)<<(7-bit);
    s.scratch[i]=value;
  }
  if(player_page) {number(s.player_0e,24,1);number(s.field_engine_04,12,1);}
  else number(s.score,24,1,true);
  return true;
}
} // namespace slam
