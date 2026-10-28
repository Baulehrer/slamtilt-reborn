#include <cmath>
#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <vector>
namespace slam {
namespace {
using Bytes=std::vector<std::uint8_t>;
unsigned be(const Bytes& b,std::size_t at,unsigned n=4){if(at>b.size()||n>b.size()-at)throw std::runtime_error("Truncated Amiga HUNK asset");unsigned v=0;for(unsigned i=0;i<n;++i)v=(v<<8)|b[at+i];return v;}
Bytes chip_data(const Bytes& file){
 std::size_t at=0;auto take=[&](){auto v=be(file,at);at+=4;return v;};
 auto skip=[&](std::size_t n){if(at>file.size()||n>file.size()-at)throw std::runtime_error("Amiga HUNK range outside file");at+=n;};
 if(take()!=0x3f3)throw std::runtime_error("Unsupported Amiga shared graphics container");
 for(unsigned n=take();n;n=take())skip(std::size_t(n)*4);
 const auto count=take(),first=take(),last=take();if(count>16||first>last||last>=count)throw std::runtime_error("Invalid Amiga HUNK directory");
 for(unsigned i=first;i<=last;++i){const auto n=take();if((n&0x3fffffffu)>0x100000)throw std::runtime_error("Amiga HUNK too large");}
 Bytes data;unsigned segments=0;
 while(at<file.size()){
  const auto type=take()&0x3fffffffu;
  if(type==0x3e9||type==0x3ea){const auto n=std::size_t(take())*4;const auto start=at;skip(n);if(type==0x3ea&&segments==1)data=Bytes(file.begin()+start,file.begin()+at);++segments;}
  else if(type==0x3eb){take();++segments;}
  else if(type==0x3ec||type==0x3ed||type==0x3ee){for(unsigned n=take();n;n=take()){take();skip(std::size_t(n)*4);}}
  else if(type==0x3f0){for(unsigned n=take();n;n=take()){skip(std::size_t(n)*4);take();}}
  else if(type==0x3f1)skip(std::size_t(take())*4);
  else if(type!=0x3f2)throw std::runtime_error("Unsupported Amiga HUNK record");
 }
 if(data.size()!=27316)throw std::runtime_error("Unsupported Amiga shared graphics revision");
 return data;
}
}
std::vector<std::uint8_t> build_amiga_main_data(const Bytes& executable,const Bytes& matrix){
 const auto source=chip_data(executable);Bytes result(0xf028);
 // Original hunk0:4108/43c6 bind these hunk1 font tables. The small
 // glyphs are five monochrome rows; large digits have two planes + mask.
 for(unsigned c=0;c<48;++c)for(unsigned y=0;y<5;++y){const auto row=be(source,0x2bce + c*12+y*2,2);for(unsigned x=0;x<8;++x)result[0x91b4 + c*96+y*16+x]=((row>>(14-2*x))&3)?3:0;}
 for(unsigned c=0;c<10;++c)for(unsigned y=0;y<13;++y){const auto a=be(source,0x2f1e + c*78+y*6,2),b=be(source,0x2f1e + c*78+y*6+2,2);for(unsigned x=0;x<8;++x){const auto bit=15-2*x;result[0x8994 + c*208+y*16+x]=((a>>bit)&1)|(((b>>bit)&1)<<1);}}
 // Hunk0:80a6..8110 binds Matrix.Dat directory entry8;6afa..6b12
 // selects (screenY/8)*128. Four interleaved16-bit planes,15rows.
 const auto ball=be(matrix,32);
 if(ball>matrix.size()||75u*128u>matrix.size()-ball)throw std::runtime_error("Truncated Amiga ball bank");
 for(unsigned frame=0;frame<75;++frame)for(unsigned y=0;y<15;++y)for(unsigned x=0;x<16;++x){
  unsigned index=0;for(unsigned plane=0;plane<4;++plane)index|=((matrix[ball+frame*128+y*8+plane*2+x/8]>>(7-x%8))&1u)<<plane;
  result[0x3da4 + frame*256+y*16+x]=std::uint8_t(index);
  if(frame==0)result[0x88a4 + y*16+x]=index?0:255;
 }
 return result;
}
}
