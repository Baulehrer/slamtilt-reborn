#include "mean_material5_display.h"
#include "dmd/mean_bonus_pixels.h"
#include "dmd/mean_minigame_text.h"
#include <fstream>
#include <stdexcept>
#include <string>
namespace slam {
MeanMaterial5DisplayAssets
load_mean_material5_display(const std::filesystem::path &p) {
  std::ifstream in(p, std::ios::binary);
  auto frame = [&](std::size_t offset) {
    std::array<std::uint8_t, 480> data{};
    in.seekg(offset);
    in.read(reinterpret_cast<char *>(data.data()), data.size());
    if (!in)
      throw std::runtime_error("Truncated Mean material5 DMD");
    return decode_windows_dmd(data);
  };
  MeanMaterial5DisplayAssets a;
  a.frame_151304=frame(0x151304);
  for(unsigned i=0;i<8;++i)a.frames_13038e[i]=frame(0x13038e + i*480);
  for(unsigned i=0;i<12;++i)a.frames_12a7ae[i]=frame(0x12a7ae + i*480);
  for(unsigned i=0;i<7;++i){a.frames_12be2e[i]=frame(0x12be2e + i*480);a.frames_12cb4e[i]=frame(0x12cb4e + i*480);}
  for (unsigned i=0;i<17;++i) a.frames_12e3ae[i]=frame(0x12e3ae + i*480);
  for (unsigned i=0;i<16;++i) a.frames_11670e[i]=frame(0x11670e + i*480);
  for(unsigned i=0;i<16;++i) a.frames_1359ce[i]=frame(0x1359ce + i*480);
  for(unsigned i=0;i<5;++i) a.frames_1377ce[i]=frame(0x1377ce + i*480);
  a.frame_14fbee=frame(0x14fbee);
  for(unsigned i=0;i<10;++i){a.frames_11544e[i]=frame(0x11544e + i*480);a.frames_11418e[i]=frame(0x11418e + i*480);}
  a.frame_11652e=frame(0x11652e);
  a.frame_14fa0e=frame(0x14fa0e);a.frame_105eae=frame(0x105eae);
  for(unsigned i=0;i<8;++i)a.frames_10518e[i]=frame(0x10518e + i*480);
  for(unsigned i=0;i<6;++i)a.frames_10176e[i]=frame(0x10176e + i*480);
  for(unsigned i=0;i<7;++i)a.frames_fb9ae[i]=frame(0xfb9ae + i*480);
  for(unsigned i=0;i<12;++i)a.frames_fa32e[i]=frame(0xfa32e + i*480);
  for(unsigned i=0;i<5;++i)a.frames_151e44[i]=frame(0x152024-480+i*480);
  for(unsigned i=0;i<15;++i)a.frames_ffb4e[i]=frame(0xffb4e + i*480);
  a.frame_14ecee=frame(0x14ecee);
  a.frame_14f82e=frame(0x14f82e);
  a.frame_15018e=frame(0x15018e);
  for(unsigned i=0;i<23;++i) a.frames_13f92e[i]=frame(0x13f92e + i*480);
  a.text_font=load_mean_bonus_pixels(p.parent_path()/"MAIN.DAT");
  for (unsigned i = 0; i < 6; ++i) {
    a.frames_11904e[i] = frame(0x11904e + i * 480);
    a.frames_119b8e[i] = frame(0x119b8e + i * 480);
  }
  for (unsigned i = 0; i < 20; ++i)
    a.frames_1022ae[i] = frame(0x1022ae + i * 480);
  for (unsigned i = 0; i < 14; ++i)
    a.frames_14a5ae[i] = frame(0x14a5ae + i * 480);
  for (unsigned i = 0; i < 12; ++i)
    a.frames_14bfee[i] = frame(0x14bfee + i * 480);
  a.frame_10464e = frame(0x10464e);
  a.frame_1506ac = frame(0x1506ac);
  for (unsigned i = 0; i < 25; ++i)
    a.frames_12336e[i] = frame(0x12336e + i * 480);
  for (unsigned i = 0; i < 14; ++i)
    a.frames_12624e[i] = frame(0x12624e + i * 480);
  for (unsigned i = 0; i < 6; ++i)
    a.frames_144bae[i] = frame(0x144d8e - 480 + i * 480);
  for (unsigned i = 0; i < 10; ++i)
    a.frames_1483ee[i] = frame(0x1483ee + i * 480);
  a.frame_13b00e = frame(0x13b00e);
  a.frame_151c64 = frame(0x151c64);
  a.frame_14f46e = frame(0x14f46e);
  a.frame_14f64e = frame(0x14f64e);
  for (unsigned i = 0; i < 19; ++i)
    a.frames_111dee[i] = frame(0x111dee + i * 480);
  const std::size_t offsets[] = {0x150a6c, 0x1585c4, 0x151124, 0x15088c,
                                 0x1514e4, 0x1518a4, 0x1516c4};
  for (unsigned i = 0; i < 7; ++i)
    a.reward_pages[i] = frame(offsets[i]);
  for(unsigned i=0;i<9;++i)a.frames_108bae[i]=frame(0x108bae + i*480);
  for (unsigned i = 0; i < 6; ++i)
    a.frames_109c8e[i] = frame(0x109c8e + i * 480);
  for (unsigned i = 0; i < 17; ++i) {
    in.seekg(0xfdd4e + i * 480);
    in.read(reinterpret_cast<char *>(a.masks_fdd4e[i].data()), 240);
    if (!in)
      throw std::runtime_error("Truncated Mean extra-ball mask");
  }
  a.frame_150e2c = frame(0x150e2c);
  a.frame_150a6c = frame(0x150a6c);
  a.frame_150c4c = frame(0x150c4c);
  for (unsigned i = 0; i < 8; ++i) {
    a.frames_1474ee[i] = frame(0x1474ee + i * 480);
    a.frames_1496ae[i] = frame(0x1496ae + i * 480);
  }
  for (unsigned i = 0; i < 20; ++i) a.frames_11a6ce[i] = frame(0x11a6ce + i * 480);
  for (unsigned i = 0; i < 6; ++i) a.frames_12d86e[i] = frame(0x12d86e + i * 480);
  for (unsigned i = 0; i < 20; ++i) a.frames_10c5ce[i] = frame(0x10c5ce + i * 480);
  for (unsigned i = 0; i < 16; ++i) a.frames_10a7ce[i] = frame(0x10a7ce + i * 480);
  for (unsigned i = 0; i < 18; ++i) a.frames_13380e[i] = frame(0x13380e + i * 480);
  for (unsigned i = 0; i < 9; ++i) a.frames_11f94e[i] = frame(0x11f94e + i * 480);
  for (unsigned i=0;i<9;++i) a.frames_14244e[i]=frame(0x14244e + i*480);
  for (unsigned i=0;i<13;++i) a.frames_14352e[i]=frame(0x14352e + i*480);
  for (unsigned i=0;i<27;++i) a.frames_137f4e[i]=frame(0x137f4e + i*480);
  for (unsigned i=0;i<19;++i) a.frames_13bf0e[i]=frame(0x13bf0e + i*480);
  draw_mean_bonus_text(a.text_font, a.mode6_ready, "READY", 7, 7);
  return a;
}
void mean_material5_display_step(MeanMaterial5Display &s,
                                 const MeanMaterial5DisplayAssets &a,
                                 const MeanScoreFont &font,
                                 const std::array<std::uint8_t, 4> &flags) {
  s.stop_audio_8c=false;
  if (!s.callback)
    return;
  const auto count = s.counter++;
  if(s.callback==0x410c8c){
    if(!s.field_058){s.stop_audio_8c=true;s.callback=0;}
    else if(static_cast<std::int32_t>(count)>=100)s.callback=0;
    else {s.pixels=a.frame_151304;draw_mean_score(font,s.pixels,s.field_058,12,7,1);}
    return;
  }
  if(s.callback==0x411544){
    if(count>=96)s.callback=0;
    else {s.pixels=a.frames_13038e[(count/4)&7];
      if(count>=32 && !((count-32)&8))draw_mean_score(font,s.pixels,s.field_050,12,4,1);
    }
    return;
  }
  if(s.callback==0x4119e0) {
    if(count>=125) s.callback=0;
    else if(count<10) s.pixels=a.frames_12a7ae[0];
    else if(count<34) s.pixels=a.frames_12a7ae[(count-10)/2];
    else if(count<109) {
      const auto frame=((count-34)/4)%7;
      s.pixels=s.field_204==5?a.frames_12cb4e[frame]:a.frames_12be2e[frame];
      if(s.field_204!=5) draw_mean_score(font,s.pixels,6-s.field_204,11,3,1);
    } else {
      for(unsigned i=0;i<s.pixels.size();++i)
        if((a.masks_fdd4e[count-109][i/8]>>(7-i%8))&1)
          s.pixels[i]=s.restore_pixels[i];
    }
    return;
  }
  if(s.callback==0x413608) {
    if(count>=231) s.callback=0;
    else if(count<25) s.pixels=a.frames_13f92e[0];
    else if(count<71) s.pixels=a.frames_13f92e[(count-25)/2];
    else if(count>=131 && count<147 && s.field_1fe<3) {
      const unsigned reward[]={1,5,6};
      for(unsigned i=0;i<s.pixels.size();++i)
        if((a.masks_fdd4e[count-131][i/8]>>(7-i%8))&1)
          s.pixels[i]=a.reward_pages[reward[s.field_1fe]][i];
    }
    return;
  }
  if(s.callback==0x410fcc || s.callback==0x41121c) {
    const bool extra=s.callback==0x41121c;
    const unsigned restore_start=extra?217:142;
    if(count>=restore_start+16) s.callback=0;
    else if(count<15) s.pixels=a.frames_1359ce[0];
    else if(count<27) s.pixels=a.frames_1359ce[(count-15)/2];
    else if(count>=32 && count<46) s.pixels=a.frames_1359ce[6+(count-32)/2];
    else if(count>=61 && count<67) s.pixels=a.frames_1359ce[13+(count-61)/2];
    else if(count>=67 && count<(extra?117u:142u)) {
      if(s.gear>=2 && s.gear<=6) s.pixels=a.frames_1377ce[s.gear-2];
    } else if(extra && count>=117 && count<217) {
      if((count-117)&1) s.pixels=a.reward_pages[1];
      else s.pixels.fill(0);
    } else if(count>=restore_start) {
      for(unsigned i=0;i<s.pixels.size();++i)
        if((a.masks_fdd4e[count-restore_start][i/8]>>(7-i%8))&1)
          s.pixels[i]=s.restore_pixels[i];
    }
    return;
  }
  if(s.callback==0x40f93c) {
    if(count>=50)s.callback=0;
    else if(count&2)s.pixels=a.frame_14ecee;
    else s.pixels.fill(0);
    return;
  }
  if(s.callback==0x40f994 || s.callback==0x40fb78) {
    const bool animation=s.callback==0x40fb78;
    const unsigned text_start=animation?121:67;
    const unsigned text_end=animation?196:167;
    const auto result_text=[&](unsigned local) {
      s.pixels.fill(0);
      const auto value=s.field_43efdc;
      if(value==1) {
        draw_mean_bonus_text(a.text_font,s.pixels,"NO SCORE",4,7);
        return;
      }
      const bool single=value==2;
      draw_mean_numeric_text(a.text_font,s.pixels,std::to_string(value-1),
                             single?7:6,1,0,3);
      draw_mean_bonus_text(a.text_font,s.pixels,single?"LAP":"LAPS",
                           single?11:10,1);
      // The animated callback's singular LAP branch returns before score.
      if((!animation || !single) && !(local&4))
        draw_mean_score(font,s.pixels,(value-1)*s.minigame_lap_points,12,7,1);
    };
    if(!animation) {
      if(count>=167) s.callback=0;
      else if(count<5) mean_clear_windows_dmd(s.pixels,6);
      else if(count<17) mean_clear_windows_dmd(s.pixels,6-int(count-5)/2);
      else if(count<67) s.pixels=a.frame_15018e;
      else result_text(count-text_start);
    } else {
      if(count>=300) s.callback=0;
      else if(count<46) s.pixels=a.frames_13f92e[count/2];
      else if(count>=text_start && count<text_end) result_text(count-text_start);
      else if(count==196) for(auto &v:s.pixels) v^=3;
      else if(count>=200) {
        if((count-200)&1) s.pixels=a.reward_pages[1];
        else s.pixels.fill(0);
      }
    }
    return;
  }
  if (s.callback == 0x41210c || s.callback == 0x4122cc) {
    const bool success=s.callback==0x4122cc;
    const unsigned text_end=success?97:122;
    const unsigned restore_start=text_end+100;
    if(count>=restore_start+16) s.callback=0;
    else if(count<32) s.pixels=a.frames_11670e[count/2];
    else if(count>=47 && count<text_end) {
      s.pixels.fill(0);
      const auto digits=std::to_string(s.field_43efcc);
      // Actual40617c: small numeric font, align1, x10, y7, ink3.
      const auto size=draw_mean_numeric_text(a.text_font,s.pixels,digits,10,7,1,3);
      draw_mean_bonus_text(a.text_font,s.pixels,"S",int(size)+12,7);
    } else if(count>=text_end && count<restore_start) {
      const unsigned local=count-text_end;
      if(success) {
        if(local==0) {
          s.pixels.fill(0);
          draw_mean_score(font,s.pixels,s.field_050,12,4,1);
        } else if(!((local-1)&3)) for(auto &v:s.pixels) v^=3;
      } else if(local<16) {
        for(unsigned i=0;i<s.pixels.size();++i)
          if((a.masks_fdd4e[local][i/8]>>(7-i%8))&1)
            s.pixels[i]=a.frame_14fbee[i];
      }
    } else if(count>=restore_start) {
      for(unsigned i=0;i<s.pixels.size();++i)
        if((a.masks_fdd4e[count-restore_start][i/8]>>(7-i%8))&1)
          s.pixels[i]=s.restore_pixels[i];
    }
    return;
  }
  if(s.callback==0x41163c){
    if(count>=80) s.callback=0;
    else if(count==0) for(auto &v:s.pixels) v^=3;
    else if(count>=5){
      s.pixels.fill(0);
      if(!((count-5)&1)) draw_mean_score(font,s.pixels,s.field_050,12,4,1);
    }
    return;
  }
  if (s.callback == 0x410a34 || s.callback == 0x410910 ||
      s.callback == 0x410d34 || s.callback == 0x410b00) {
    const auto cb=s.callback;
    const unsigned animation=cb==0x410a34?52:cb==0x410910?43:cb==0x410d34?81:101;
    const unsigned mask_start=animation+100;
    const unsigned final_tick=mask_start+16+(cb==0x410b00?50:0);
    if(count>=final_tick) s.callback=0;
    else if(count<animation){
      if(cb==0x410a34) s.pixels=a.frames_14352e[count/4];
      else if(cb==0x410910) s.pixels=a.frames_14244e[count<25?0:(count-25)/2];
      else if(cb==0x410d34) s.pixels=a.frames_137f4e[count/3];
      else if(count<25) s.pixels.fill(0);
      else s.pixels=a.frames_13bf0e[(count-25)/4];
    }else if(count>=mask_start && count<mask_start+16){
      for(unsigned i=0;i<s.pixels.size();++i)
        if((a.masks_fdd4e[count-mask_start][i/8]>>(7-i%8))&1)
          s.pixels[i]=s.restore_pixels[i];
    }else if(cb==0x410b00 && count>=mask_start+16){
      s.pixels=a.mode6_ready;
      if(!((count-mask_start-16)&2))
        for(auto &v:s.pixels) v^=3;
    }
    return;
  }
  if (s.callback == 0x413490) {
    if(count>=80)s.callback=0;
    else if(count<30)s.pixels=a.frames_ffb4e[count/2];
    return;
  }
  if (s.callback == 0x413770) {
    if(count>=127)s.callback=0;
    else if(count<12)s.pixels=a.frames_10176e[count/2];
    else if(count<17)mean_clear_windows_dmd(s.pixels,6);
    else if(count<52){
      mean_clear_windows_dmd(s.pixels,std::max(0,6-int((count-17)/2)));
      draw_mean_score(font,s.pixels,5000000,12,4,1);
    } else {
      s.pixels.fill(0);
      if((count-52)&4){
        if(!s.field_38a)draw_mean_bonus_text(a.text_font,s.pixels,"NO CARS LEFT",0,7);
        else if(s.field_38a==1)draw_mean_bonus_text(a.text_font,s.pixels,"1 CAR LEFT",2,7);
        else {
          const auto n=draw_mean_numeric_text(a.text_font,s.pixels,std::to_string(s.field_38a),2,7,1,3);
          draw_mean_bonus_text(a.text_font,s.pixels,"CARS LEFT",int(n)+4,7);
        }
      }
    }
    return;
  }
  if(s.callback==0x4131cc || s.callback==0x4132d4){
    const bool jackpot=s.callback==0x4131cc;
    if(count>=(jackpot?128u:103u))s.callback=0;
    else if(count<28)s.pixels=a.frames_fb9ae[count/4];
    else if(count>=53){
      s.pixels.fill(0);
      if(!((count-53)&(jackpot?2:4)))
        draw_mean_score(font,s.pixels,jackpot?25000000:10000000,12,4,1);
    }
    return;
  }
  if(s.callback==0x4133d4 || s.callback==0x413518){
    const bool start=s.callback==0x413518;
    if(count>=(start?138u:98u))s.callback=0;
    else if(count<48)s.pixels=a.frames_fa32e[count/4];
    else if(!start){
      // Original signedremaining-1 indexes DAT152024; zero selects priorframe.
      s.pixels=a.frames_151e44.at(s.field_1d8);
    } else if(count>=63 && count<79){
      for(unsigned i=0;i<s.pixels.size();++i)
        if((a.masks_fdd4e[count-63][i/8]>>(7-i%8))&1)s.pixels[i]=a.reward_pages[4][i];
    }
    return;
  }
  if (s.callback == 0x4114cc) {
    // Original input exit:75 ticks alternating clear and the14f82e page.
    if (count >= 75) s.callback = 0;
    else if (count & 1) s.pixels = a.frame_14f82e;
    else s.pixels.fill(0);
    return;
  }
  if (s.callback == 0x411908) {
    if (count >= 109) s.callback = 0;
    else if (count < 18) s.pixels = a.frames_12d86e[count / 3];
    else if (count >= 93) {
      for (unsigned i = 0; i < s.pixels.size(); ++i)
        if ((a.masks_fdd4e[count - 93][i / 8] >> (7 - i % 8)) & 1)
          s.pixels[i] = s.restore_pixels[i];
    }
    return;
  }
  if (s.callback == 0x4130cc) {
    if(count>=157)s.callback=0;
    else if(count<75){
      s.pixels=a.frame_14fa0e;
      if(!(count&4))for(auto &v:s.pixels)v^=3;
    } else if(count<107)s.pixels=a.frames_10518e[(count-75)/4];
    else s.pixels=a.frame_105eae;
    return;
  }
  if (s.callback == 0x412df0) {
    // Original:15 still,36 animation,15 hold,75 currentletter,16 restore.
    if(count>=157)s.callback=0;
    else if(count<15)s.pixels=a.frames_108bae[0];
    else if(count<51)s.pixels=a.frames_108bae[(count-15)/4];
    else if(count>=66 && count<141)s.pixels=a.frames_109c8e.at(s.field_1f2);
    else if(count>=141){
      for(unsigned i=0;i<s.pixels.size();++i)
        if((a.masks_fdd4e[count-141][i/8]>>(7-i%8))&1)s.pixels[i]=s.restore_pixels[i];
    }
    return;
  }
  if (s.callback == 0x41249c) {
    if(count>=115)s.callback=0;
    else if(count<40)s.pixels=a.frames_11544e[count/4];
    else {
      s.pixels=a.frame_11652e;
      if((count-40)&4)draw_mean_score(font,s.pixels,s.field_050,12,4,1);
    }
    return;
  }
  if (s.callback == 0x4126ec) {
    if(count>=91)s.callback=0;
    else if(count<40)s.pixels=a.frames_11418e[count/4];
    else if(count>=75){
      for(unsigned i=0;i<s.pixels.size();++i)
        if((a.masks_fdd4e[count-75][i/8]>>(7-i%8))&1)s.pixels[i]=s.restore_pixels[i];
    }
    return;
  }
  if (s.callback == 0x412908) {
    // Original: 40 animation,15 hold,16 restore,75 score,16 restore.
    if (count >= 162) s.callback = 0;
    else if (count < 40) s.pixels = a.frames_10c5ce[count / 2];
    else if ((count >= 55 && count < 71) || count >= 146) {
      const auto local = count < 71 ? count - 55 : count - 146;
      for (unsigned i = 0; i < s.pixels.size(); ++i)
        if ((a.masks_fdd4e[local][i / 8] >> (7 - i % 8)) & 1)
          s.pixels[i] = s.restore_pixels[i];
    } else if (count >= 71) {
      const auto local = count - 71;
      if (!local) {
        s.pixels.fill(0);
        draw_mean_score(font, s.pixels, s.field_050, 12, 4, 1);
      }
      if (!(local & 3)) for (auto &v : s.pixels) v ^= 3;
    }
    return;
  }
  if (s.callback == 0x412d24 || s.callback == 0x411f10 ||
      s.callback == 0x412af8 || s.callback == 0x412c58) {
    const unsigned animation = s.callback == 0x412d24 ? 32 :
                               s.callback == 0x411f10 ? 80 :
                               s.callback == 0x412af8 ? 58 : 36;
    const unsigned mask_start = animation + (s.callback == 0x411f10 ? 75 : 100);
    if (count >= mask_start + 16) s.callback = 0;
    else if (count < animation) {
      if (s.callback == 0x412d24) s.pixels = a.frames_10a7ce[count / 2];
      else if (s.callback == 0x411f10) s.pixels = a.frames_11a6ce[count / 4];
      else if (s.callback == 0x412c58) s.pixels = a.frames_13380e[count / 2];
      else {
        const auto local = count < 40 ? count % 20 : count - 40;
        const auto index = local / 2;
        s.pixels = a.frames_11f94e[count < 40 && index > 4 ? 10 - index : index];
      }
    } else if (count >= mask_start) {
      for (unsigned i = 0; i < s.pixels.size(); ++i)
        if ((a.masks_fdd4e[count - mask_start][i / 8] >> (7 - i % 8)) & 1)
          s.pixels[i] = s.restore_pixels[i];
    }
    return;
  }
  if (s.callback == 0x411fdc) {
    if (count >= 155)
      s.callback = 0;
    else if (count < 24)
      s.pixels = a.frames_11904e[count / 4];
    else if (count < 48)
      s.pixels = a.frames_119b8e[(count - 24) / 4];
    else if (count < 64)
      s.pixels = a.frames_119b8e[(count - 48) / 4];
    else if (count >= 139) {
      for (unsigned i = 0; i < s.pixels.size(); ++i)
        if ((a.masks_fdd4e[count - 139][i / 8] >> (7 - i % 8)) & 1)
          s.pixels[i] = s.restore_pixels[i];
    }
    return;
  }
  if (s.callback == 0x411c60) {
    // Actual Rally turn: 30 animation ticks, 20 overlay ticks, 50 score ticks.
    if (count >= 100)
      s.callback = 0;
    else if (count < 30)
      s.pixels = a.frames_12336e[count / 2];
    else if (count < 50) {
      const auto local = count - 30;
      s.pixels = a.frames_12336e[15 + local / 2];
      if (local & 4)
        draw_mean_score(font, s.pixels, 15000000, 12, 4, 1);
    } else {
      s.pixels.fill(0);
      if (!((count - 50) & 4))
        draw_mean_score(font, s.pixels, 15000000, 12, 4, 1);
    }
    return;
  }
  if (s.callback == 0x411db4) {
    // Actual final turn: 50 animation, 75 masked-page, 100 award ticks.
    if (count >= 225)
      s.callback = 0;
    else if (count < 50)
      s.pixels = a.frames_12336e[count / 2];
    else if (count < 125) {
      const auto local = count - 50;
      if (local < 16)
        for (unsigned i = 0; i < s.pixels.size(); ++i)
          if ((a.masks_fdd4e[local][i / 8] >> (7 - i % 8)) & 1)
            s.pixels[i] = a.frame_1506ac[i];
    } else {
      const auto local = count - 125;
      if (!local) {
        s.pixels.fill(0);
        draw_mean_score(font, s.pixels, s.field_050, 12, 4, 1);
      } else if (!((local - 1) & 3))
        for (auto &pixel : s.pixels)
          pixel = (~pixel) & 3;
    }
    return;
  }
  if (s.callback == 0x411824) {
    // Actual wrong turn: 28 animation, 35 hold, 16 masked restore ticks.
    if (count >= 79)
      s.callback = 0;
    else if (count < 28)
      s.pixels = a.frames_12624e[count / 2];
    else if (count >= 63) {
      const auto local = count - 63;
      for (unsigned i = 0; i < s.pixels.size(); ++i)
        if ((a.masks_fdd4e[local][i / 8] >> (7 - i % 8)) & 1)
          s.pixels[i] = s.restore_pixels[i];
    }
    return;
  }
  if (s.callback == 0x411710) {
    // Original kickback: 34 animation ticks, 75 hold, 16 masked restore.
    if (count >= 125)
      s.callback = 0;
    else if (count < 34)
      s.pixels = a.frames_12e3ae[count / 2];
    else if (count >= 109) {
      const auto local = count - 109;
      for (unsigned i = 0; i < s.pixels.size(); ++i)
        if ((a.masks_fdd4e[local][i / 8] >> (7 - i % 8)) & 1)
          s.pixels[i] = s.restore_pixels[i];
    }
    return;
  }
  if (s.callback == 0x412fa8) {
    // Original Monster Car reward: 80 animation ticks, 75 score-page ticks.
    if (count >= 155)
      s.callback = 0;
    else if (count < 80)
      s.pixels = a.frames_1022ae[count / 4];
    else {
      s.pixels = a.frame_10464e;
      if (!((count - 80) & 4))
        draw_mean_score(font, s.pixels, s.field_050, 12, 4, 1);
    }
    return;
  }
  if (s.callback == 0x41041c) {
    // Original Offroad reward: 42 animation ticks, 75 blinking score ticks.
    if (count >= 117)
      s.callback = 0;
    else if (count < 42)
      s.pixels = a.frames_14a5ae[count / 3];
    else if (!((count - 42) & 1))
      s.pixels.fill(0);
    else
      draw_mean_score(font, s.pixels, 15000000, 12, 4, 1);
    return;
  }
  if (s.callback == 0x410158 || s.callback == 0x4102c0) {
    const bool kickstart=s.callback==0x4102c0;
    // Original mode6 reward: animation, hold, invert, hold, blinking award.
    if (count >= (kickstart?112u:87u))
      s.callback = 0;
    else if (count < 12)
      s.pixels = a.frames_14bfee[count];
    else if (count == 32) {
      for (auto &p : s.pixels)
        p = (~p) & 3;
    } else if (count >= 37) {
      if ((count - 37) & 1)
        s.pixels.fill(0);
      else
        draw_mean_score(font, s.pixels, kickstart?25000000:s.field_050, 12, 4, 1);
    }
    return;
  }
  if (s.callback == 0x412574) {
    // Actual412574: two75-tick masked pages,16-tick restore,thenend.
    if (count >= 166)
      s.callback = 0;
    else {
      const auto local = count < 75    ? count
                         : count < 150 ? count - 75
                                       : count - 150;
      if (local < 16) {
        const auto &page = count < 75    ? a.frame_14f46e
                           : count < 150 ? a.frame_14f64e
                                         : s.restore_pixels;
        for (unsigned i = 0; i < s.pixels.size(); ++i)
          if ((a.masks_fdd4e[local][i / 8] >> (7 - i % 8)) & 1)
            s.pixels[i] = page[i];
      }
    }
    return;
  }
  if (s.callback == 0x41265c) {
    // Actual41265c: first16 frames at2ticks,then3framesloop forever.
    s.pixels =
        a.frames_111dee[count < 32 ? count / 2 : 16 + ((count - 32) / 2) % 3];
    return;
  }
  if (s.callback == 0x40fdec) {
    if (count >= 154)
      s.callback = 0;
    else if (count == 0) {
      for (auto &p : s.pixels)
        p = (~p) & 3;
    } else if (count >= 4 && count < 54) {
      if ((count - 4) & 1)
        s.pixels = a.frame_151c64;
      else
        s.pixels.fill(0);
    } else if (count >= 54) {
      const auto n = count - 54;
      if (!s.field_358) {
        s.pixels.fill(0);
        if (n & 1)
          draw_mean_score(font, s.pixels, s.field_050, 12, 4, 1);
      } else if (s.field_362 == 6) {
        s.pixels = a.frames_109c8e.at(s.field_1f2);
      } else if (s.field_362 <= 5 && n <= 16) {
        unsigned page = s.field_362;
        if (page == 5) {
          const unsigned indices[] = {1, 5, 6};
          if (s.field_1fe >= 3)
            throw std::runtime_error("Invalid reward page");
          page = indices[s.field_1fe];
        }
        const auto &mask = a.masks_fdd4e[n];
        for (unsigned i = 0; i < s.pixels.size(); ++i)
          if ((mask[i / 8] >> (7 - i % 8)) & 1)
            s.pixels[i] = a.reward_pages[page][i];
      }
    }
    return;
  }
  if (s.callback == 0x410e4c) {
    if (count >= 122)
      s.callback = 0;
    else if (count == 1) {
      for (auto &pixel : s.pixels)
        pixel = (~pixel) & 3;
    } else if (count >= 6 && count < 106) {
      if ((count - 6) & 1)
        s.pixels = a.frame_13b00e;
      else
        s.pixels.fill(0);
    } else if (count >= 106) {
      const auto &mask = a.masks_fdd4e[count - 106];
      for (unsigned i = 0; i < s.pixels.size(); ++i)
        if ((mask[i / 8] >> (7 - i % 8)) & 1)
          s.pixels[i] = s.restore_pixels[i];
    }
    return;
  }
  if (s.callback == 0x4107c8 || s.callback == 0x41086c) {
    if (count >= 148)
      s.callback = 0;
    else if (count < 48)
      s.pixels = a.frames_1496ae[count & 7];
    else
      s.pixels = s.callback == 0x4107c8 ? a.frame_150a6c : a.frame_150c4c;
    return;
  }
  if (s.callback == 0x410504) {
    if (count >= 41)
      s.callback = 0;
    else if (count < 24)
      s.pixels = a.frames_1474ee[count / 3];
    else if (count >= 29) {
      const unsigned level = 6 - (count - 29) / 2;
      // Original4060a4 table429a9c: alternating adjacent-pixel shades.
      for (unsigned i = 0; i < s.pixels.size(); ++i)
        s.pixels[i] = level / 2 + (((i % 96 + i / 96) & 1) && (level & 1));
    }
    return;
  }
  if (s.callback == 0x413a2c) {
    if (count >= 50) {
      s.callback = 0;
      return;
    }
    int frame = 0;
    for (auto flag : flags)
      frame += flag != 0;
    if (count & 2)
      --frame;
    s.pixels = a.frames_144bae.at(frame + 1);
    return;
  }
  if (s.callback == 0x413958) {
    if (count >= 105) {
      s.callback = 0;
      return;
    }
    if (count == 0) {
      for (auto &pixel : s.pixels)
        pixel = (~pixel) & 3;
    } else if (count >= 5) {
      if ((count - 5) & 1)
        s.pixels = a.frame_150e2c;
      else
        s.pixels.fill(0);
    }
    return;
  }
  if (s.callback == 0x41062c) {
    if (count >= 155) {
      s.callback = 0;
      return;
    }
    if (count < 40)
      s.pixels = a.frames_1483ee[count / 4];
    else if (count == 50) {
      for (auto &pixel : s.pixels)
        pixel = (~pixel) & 3;
    } else if (count >= 55) {
      if ((count - 55) & 1)
        s.pixels.fill(0);
      else
        draw_mean_score(font, s.pixels, s.field_050, 12, 4, 1);
    }
    return;
  }
  throw std::runtime_error("Unsupported Mean material5 DMD callback");
}
} // namespace slam

namespace slam {
MeanDisplayDispatch mean_material5_display_scheduled_step(MeanMaterial5Display &s,
    const MeanMaterial5DisplayAssets &assets, const MeanScoreFont &font,
    const std::array<std::uint8_t, 4> &flags) {
  const auto dispatch=mean_display_scheduler_begin(s.scheduler);
  if (dispatch == MeanDisplayDispatch::Callback) {
    mean_material5_display_step(s, assets, font, flags);
    s.scheduler.field_78c = static_cast<std::int32_t>(s.counter);
    s.scheduler.field_784 = s.callback ? 2 : 0;
  }
  mean_display_scheduler_finish(s.scheduler);
  return dispatch;
}
} // namespace slam
