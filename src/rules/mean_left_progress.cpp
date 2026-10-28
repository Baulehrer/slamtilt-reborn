#include "rules/mean_left_progress.h"
namespace slam {
MeanLeftProgressEvent mean_left_progress(MeanBallResetState& s,std::uint32_t admitted){
 MeanLeftProgressEvent e;if(s.table_mode>4)return e;
 auto& f=s.fields;auto w=[&](unsigned o){return std::int16_t(unsigned(f[o])|(unsigned(f[o+1])<<8));};
 auto put=[&](unsigned o,std::uint32_t v,unsigned n=2){for(unsigned i=0;i<n;++i)f[o+i]=v>>(8*i);};
 auto cmd=[&](unsigned o,unsigned a,unsigned b,unsigned c,unsigned d){f[o]=a;f[o+1]=b;f[o+2]=c;f[o+3]=d;};
 const auto old=w(0x3ba);if(old<0||old>2)return e;
 f[0x218+old*4]=2;const auto next=old==2?0:old+1;put(0x3ba,next);cmd(0x218+next*4,4,6,1,0);
 if(next==2){put(0x392,0xffff);cmd(0x230,4,6,5,0);cmd(0x234,4,6,3,0);}
 if(next==0){put(0x392,0);f[0x230]=f[0x234]=2;const auto count=w(0x1f2);if(count>=5)return e;if(count<0)return e;
  put(0x1f2,count+1);cmd(0x2a0+(count+1)*4,5,1,0,32);if(count+1==5)cmd(0x2b8,4,4,1,0);
  put(0x038,admitted,4);e.display_request=e.capture_delay_request=true;e.callback=0x412df0;
 }return e;
}
}
