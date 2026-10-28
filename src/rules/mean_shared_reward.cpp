#include "mean_shared_reward.h"
namespace slam {
MeanSharedRewardEvents mean_shared_reward(MeanBallResetState &s, unsigned id,
                                         std::uint32_t returned) {
  MeanSharedRewardEvents e;
  if(id>5) return e;
  auto &f=s.fields;
  auto word=[&](unsigned o){return std::uint16_t(f[o]|(f[o+1]<<8));};
  auto signed_word=[&](unsigned o){return static_cast<std::int16_t>(word(o));};
  auto dword=[&](unsigned o){return std::uint32_t(word(o))|(std::uint32_t(word(o+2))<<16);};
  auto put=[&](unsigned o,std::uint32_t v,unsigned n=2){for(unsigned i=0;i<n;i++) f[o+i]=v>>(i*8);};
  auto score=[&](std::uint32_t v){e.scores.push_back(v);put(0x058,dword(0x058)+v,4);};
  auto callback=[&](std::uint32_t cb,int a=-1,int b=-1,unsigned control=0){e.callback=cb;e.callback_arg0=a;e.callback_arg1=b;e.control=true;e.control_arg1=control;put(0x038,returned,4);};
  auto finish=[&](){s.table_mode=2;e.service_419da4=e.service_419f6c=e.service_4194e4=true;put(0x366,0xffff);};
  if(s.table_mode==5){
    switch(word(0x1e6)){
    case 1:{
      if(!word(0x044+id*2)) break;
      put(0x044+id*2,0);f[0x23c+id*4]=2;
      auto old=signed_word(0x372);auto count=std::uint16_t(old+1);put(0x372,count);
      std::uint32_t award=count==6?50000000u:std::uint32_t(old)*5000000u+5000000u;
      score(award);put(0x050,award,4);callback(0x412fa8);
      if(count==6)finish();
      break;
    }
    case 2:{
      if(static_cast<std::int32_t>(id)==signed_word(0x38c)){
        score(15000000u);auto count=std::uint16_t(word(0x386)+1);put(0x386,count);
        if(static_cast<std::int16_t>(count)>=6){
          // Original signed divide truncates toward zero.
          auto award=std::uint32_t(signed_word(0x39c)/200)*1500000u;
          score(award);put(0x050,award,4);put(0x364,0xffff);
          callback(0x411db4,0x29,1,0x2bc);put(0x024,0xffffffffu,4);finish();
        }else{
          e.service_4169e4=true;put(0x39c,word(0x39c)+2000);
          callback(0x411c60,0xc,1);
        }
      }else if(id==1||id==2||id==4||id==5){callback(0x411824);e.callback_eax=6;e.callback_edx=5;}
      break;
    }
    case 4:{
      auto old=signed_word(0x388);if(static_cast<std::int32_t>(id)==old)break;
      if(old<0||old>5)break; // Invalid original lamp address domain.
      put(0x388,id);unsigned o=0x23c+old*4;f[o]=4;f[o+1]=6;f[o+2]=1;f[o+3]=0;
      f[0x23c+id*4]=2;score(15000000u);callback(0x41041c);break;
    }
    default:break;
    }
  }else if(s.table_mode==6&&id){
    if(id==2&&signed_word(0x35e)>=0){put(0x35e,word(0x35e)-1);return e;}
    unsigned count=1+(signed_word(0x38e)>=0)+(signed_word(0x368)>=0)+(signed_word(0x36c)>=0);
    auto award=count*10000000u;score(award);put(0x050,award,4);callback(0x410158);
  }
  return e;
}
bool mean_rally_target(MeanBallResetState &s, std::uint32_t engine_38,
                       const std::vector<std::uint32_t> &directory,
                       const std::vector<std::uint32_t> &targets) {
  auto &f = s.fields;
  auto word = [&](unsigned o) { return std::uint16_t(f[o] | (f[o + 1] << 8)); };
  auto previous = static_cast<std::int16_t>(word(0x38c));
  if (previous < 0 || previous > 5)
    return false;
  std::uint32_t next = 0;
  if (word(0x386) != 5) {
    if (static_cast<unsigned>(previous) >= directory.size()) return false;
    auto index = directory[previous] * 4u + ((engine_38 >> 4) % 3);
    if (index >= targets.size()) return false;
    next = targets[index];
    if (next > 5) return false;
  }
  f[0x23c + previous * 4] = 2;
  auto o = 0x23c + next * 4;
  f[o] = 4; f[o + 1] = 6; f[o + 2] = 1; f[o + 3] = 0;
  f[0x38c] = next; f[0x38d] = next >> 8;
  return true;
}

}
