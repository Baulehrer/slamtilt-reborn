#include "assets/amiga_contact.h"
#include <array>
#include <stdexcept>
namespace slam {
namespace {
using Bytes=std::vector<std::uint8_t>;
unsigned word(const Bytes& b,std::size_t p){if(p>b.size()||b.size()-p<2)throw std::runtime_error("Truncated Mean contact descriptor");return unsigned(b[p])*256+b[p+1];}
unsigned longword(const Bytes& b,std::size_t p){return (word(b,p)<<16)|word(b,p+2);}
struct Contact{unsigned index,target,x,y,width,height;};
constexpr std::array<Contact,4> contacts{{{0,0x85cfe,0,549,64,51},{1,0x91dee,240,550,64,50},{4,0x82dbe,0,140,48,66},{5,0x852de,272,473,32,27}}};
}
void build_amiga_mean_contact_frames(const Bytes& raw,const Bytes& bin,Bytes& native){
 if(bin.empty())throw std::runtime_error("Missing decoded Mean.Bin");
 const std::size_t section=longword(raw,0),directory=section+longword(raw,section+20);
 for(const auto& c:contacts){
  const std::size_t descriptor=directory+longword(raw,directory+c.index*4),pixels=descriptor+16;
  const auto size=std::size_t(c.width)*c.height*3;
  if(word(raw,descriptor)!=0xffff||word(raw,descriptor+2)*16!=c.width||word(raw,descriptor+4)!=c.height||longword(raw,descriptor+6)!=c.y*320+c.x/8||longword(raw,descriptor+12)!=size+16)
   throw std::runtime_error("Unsupported Mean contact descriptor");
  if(pixels>raw.size()||size>raw.size()-pixels||c.target>native.size()||size>native.size()-c.target)throw std::runtime_error("Truncated Mean contact frames");
  for(unsigned n=0;n<3;++n)for(unsigned y=0;y<c.height;++y)for(unsigned x=0;x<c.width;++x){
   unsigned v=0;
   for(unsigned p=0;p<8;++p)v|=((raw[pixels+std::size_t(n)*c.width*c.height+(y*8+p)*(c.width/8)+x/8]>>(7-x%8))&1u)<<p;
   native[c.target+std::size_t(n)*c.width*c.height+y*c.width+x]=std::uint8_t(v);
  }
 }
}
}
