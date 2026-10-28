#include "mean_pit_stop.h"
namespace slam {
MeanPitStopEvents mean_pit_stop(MeanBallResetState &s,unsigned id,const std::function<std::uint32_t(const MeanPitStopRequest &)> &admit) {
  MeanPitStopEvents e;
  if(id>3)return e;
  auto &f=s.fields;
  auto word=[&](unsigned o){return std::uint16_t(f[o]|unsigned(f[o+1])<<8);};
  auto put=[&](unsigned o,std::uint32_t v,unsigned n=2){for(unsigned i=0;i<n;++i)f[o+i]=v>>(8*i);};
  auto request=[&](std::uint32_t cb,unsigned eax,unsigned edx){
    e.requests.push_back({cb,eax,edx,2});
    const auto admission=admit(e.requests.back());put(0x038,admission,4);
    if(admission){put(0x024,0,4);e.clear_capture_delays=true;}
  };
  if(static_cast<std::int16_t>(word(0x398))<0) {
    if(f[0x1d4+id])return e;
    f[0x1d4+id]=1;put(0x1d8,std::uint16_t(word(0x1d8)-1));
    e.scores.push_back(2500000);request(0x4133d4,4,3);
    f[0x208+id*4]=1;
    for(unsigned i=0;i<4;++i)if(f[0x1d4+i]!=1)return e;
    for(unsigned i=0;i<4;++i){f[0x1d4+i]=0;f[0x060+i]=0;
      f[0x208+i*4]=4;f[0x209+i*4]=4;f[0x20a+i*4]=1+2*i;f[0x20b+i*4]=0;}
    put(0x1d8,4);put(0x3ac,0);put(0x398,1500);s.field_438af8=0;
    request(0x413518,5,4);
  } else {
    if(f[0x060+id])return e;
    f[0x060+id]=1;e.scores.push_back(10000000);request(0x4132d4,5,4);
    f[0x208+id*4]=2;put(0x3ac,std::uint16_t(word(0x3ac)+1));
    for(unsigned i=0;i<4;++i)if(f[0x060+i]!=1)return e;
    for(unsigned i=0;i<4;++i)f[0x060+i]=0;
    e.scores.push_back(15000000);put(0x398,0xffff);request(0x4131cc,5,4);
  }
  return e;
}
MeanPitStopEvents mean_pit_stop(MeanBallResetState &s,unsigned id,std::uint32_t value) {
  return mean_pit_stop(s,id,[&](const MeanPitStopRequest &){return value;});
}

void mean_pit_stop_tick(MeanBallResetState &s,std::uint32_t service1c) {
  if(service1c)return;
  auto &f=s.fields;
  auto v=static_cast<std::int16_t>(std::uint16_t(f[0x398]|unsigned(f[0x399])<<8));
  if(v<0)return;
  const auto next=std::uint16_t(v-1);f[0x398]=next;f[0x399]=next>>8;
  if(static_cast<std::int16_t>(next)<0)
    for(unsigned i=0;i<4;++i)f[0x208+4*i]=2;
}

}
