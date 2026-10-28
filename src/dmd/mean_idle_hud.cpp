#include "mean_idle_hud.h"
#include "dmd/mean_minigame_text.h"
#include <fstream>
#include <stdexcept>
#include <string>
namespace slam {
MeanIdleHudAssets load_mean_idle_hud(const std::filesystem::path &mean_dat,
                                    const std::filesystem::path &main_dat) {
  MeanIdleHudAssets a;
  a.font=load_mean_bonus_pixels(main_dat);
  std::ifstream in(mean_dat,std::ios::binary);
  auto load=[&](auto &frames,unsigned offset) {
    for(auto &frame:frames) {
      std::array<std::uint8_t,480> packed{};
      in.seekg(offset);in.read(reinterpret_cast<char *>(packed.data()),packed.size());
      if(!in)throw std::runtime_error("Truncated Mean idle HUD");
      frame=decode_windows_dmd(packed);offset+=480;
    }
  };
  load(a.pit_stop,0xfc6ce);load(a.bank_early,0x1456ee);
  load(a.bank_late,0x14640e);load(a.score,0x14d66e);
  return a;
}
void mean_idle_hud_step(MeanIdleHud &s,const MeanIdleHudAssets &a) {
  const auto phase=s.counter&127u;
  const bool pit=s.field_398>=0 && (s.field_37a>=0 ? phase<64 : phase<80);
  ++s.counter;
  if(pit) {
    // Four tyre hits end PitStop; reachable active stages are0..3.
    const auto index=static_cast<int>((s.counter>>2)%3)+s.field_3ac*3;
    if(index<0 || index>=static_cast<int>(a.pit_stop.size()))
      throw std::runtime_error("Unsupported Mean PitStop HUD frame");
    s.pixels=a.pit_stop[index];
    draw_mean_numeric_text(a.font,s.pixels,std::to_string(s.field_398/50),7,13,1,3);
  } else if(s.field_37a>=0) {
    s.pixels=s.field_37a>3000 ? a.bank_early[(s.counter>>1)%7] : a.bank_late[(s.counter>>1)%9];
    draw_mean_numeric_text(a.font,s.pixels,std::to_string(s.field_054),0,0,0,3);
    draw_mean_numeric_text(a.font,s.pixels,std::to_string(s.field_37a/200),24,0,2,3);
  } else {
    s.pixels=a.score[(s.counter>>1)%10];
    // Original406468 strips at most ten leading BCD zeros: minimum two digits.
    if(s.score<10) {
      draw_mean_score(a.font.score,s.pixels,0,20,7);
      draw_mean_score(a.font.score,s.pixels,static_cast<std::uint32_t>(s.score),22,7);
    } else draw_mean_score_u64(a.font.score,s.pixels,s.score,24,7,2);
  }
}
} // namespace slam
