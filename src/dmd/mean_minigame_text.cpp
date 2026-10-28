#include "mean_minigame_text.h"
#include <string>
#include <algorithm>
#include <stdexcept>
namespace slam {
unsigned draw_mean_numeric_text(const MeanBonusPixels &font, WindowsDmdPixels &out,
    std::string_view digits, int x, int y, int align, unsigned mask) {
  const auto count=digits.size();
  x=x*4-align*int(count)*4;
  int group=int((count-1)%3)+2;
  for(unsigned char c:digits){
    if(--group==0){
      group=3;
      if(c!=' ' && x>0 && x<=96 && y+5>=0 && y+5<20) out[(y+5)*96+x-1]=mask;
    }
    if(c!=' ' && c>=48 && c<91)
      for(int row=0;row<5;++row) for(int col=0;col<8;++col){
        auto v=font.text[c-48][row*8+col];
        if(v && x+col>=0 && x+col<96 && y+row>=0 && y+row<20)
          out[(y+row)*96+x+col]=v&mask;
      }
    x+=8;
  }
  return count;
}
void mean_minigame_text_service(const MeanBonusPixels &font, WindowsDmdPixels &out,
    std::uint32_t target,std::array<std::uint32_t,8> &r,
    const std::function<std::uint32_t(std::uint32_t,unsigned)> &read) {
  if(target==0x4060f8){
    std::string text;
    for(unsigned i=0;i<128;++i){const auto c=read(r[3]+i,1);if(!c)break;text+=char(c);}
    draw_mean_bonus_text(font,out,text,static_cast<int>(r[0]),static_cast<int>(r[2]));
  }else if(target==0x40617c){
    std::string digits;
    if(r[3]!=0xffffffffu) digits=std::to_string(r[3]);
    else{
      const auto address=read(r[4]+8,4);
      for(unsigned i=0;i<6;++i){const auto v=read(address+i,1);digits+=char('0'+(v>>4));digits+=char('0'+(v&15));}
      const auto first=digits.find_first_not_of('0');digits=digits.substr(first==std::string::npos?10:std::min<std::size_t>(first,10));
    }
    r[0]=draw_mean_numeric_text(font,out,digits,static_cast<int>(read(r[4]+4,4)),
        static_cast<int>(r[2]),static_cast<int>(r[0]),r[1]);
  }else if(target==0x406280)
    draw_mean_score(font.score,out,r[3],static_cast<int>(r[1]),static_cast<int>(r[2]),static_cast<int>(r[0]));
  else throw std::runtime_error("Unknown mini-game text service");
}
} // namespace slam
