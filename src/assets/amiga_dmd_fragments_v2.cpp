#include "assets/amiga_dmd_fragments_v2.h"
#include "assets/amiga_dmd.h"
#include <algorithm>
#include <stdexcept>
namespace slam {
namespace {
using Bytes=std::vector<std::uint8_t>;
void raw_object(const Bytes& source,Bytes& native,std::size_t from,std::size_t to,std::size_t size){
 if(from>source.size()||source.size()-from<size||to>native.size()||native.size()-to<size)throw std::runtime_error("Truncated Amiga DMD source object");
 std::copy_n(source.begin()+from,size,native.begin()+to);
}
unsigned be32(const Bytes& b,std::size_t p){
 if(p>b.size()||b.size()-p<4)throw std::runtime_error("Truncated Amiga DMD variant directory");
 unsigned n=0;for(unsigned i=0;i<4;++i)n=(n<<8)|b[p+i];return n;
}
}
void build_amiga_dmd_fragments_v2(std::string_view table,const Bytes& bin,Bytes& native){
 if(table=="mean"){
  raw_object(bin,native,0xaaa59,0x1516c4,480);
  raw_object(bin,native,0xa2453,0x1525c4,480);
 }else if(table=="demon"){
  raw_object(bin,native,0x70ff6,0x10d8f0,480);
  raw_object(bin,native,0x867b6,0x10e070,480);
 }else if(table=="pirate"){
  raw_object(bin,native,0xa5ce7,0x140ddc,960);
  raw_object(bin,native,0xa6417,0x14173c,400);
  raw_object(bin,native,0xa6287,0x1418cc,400);
  // Original Pirate.Bin5bab4..5bb04: count<52 selects count>>2;
  // otherwise entry12, then ends at77. Directory binds via a4+54-39d08.
  constexpr unsigned directory=0x6b85f,target=0xfb91c,count=13;
  if(be32(bin,directory)!=count*4||target>native.size()||native.size()-target<count*480)throw std::runtime_error("Unsupported Amiga Pirate scene");
  for(unsigned i=0;i<count;++i){
   const auto offset=be32(bin,directory+i*4);
   if(offset<count*4||offset>bin.size()||directory>bin.size()-offset)throw std::runtime_error("Invalid Amiga Pirate scene pointer");
   std::size_t cursor=directory+offset;
   // Entry0 deliberately consumes one byte of entry1. The Original routine
   // stops on480 output bytes, not on the next directory pointer.
   const auto pixels=decode_amiga_dmd_frame(bin,cursor,bin.size());
   std::copy(pixels.begin(),pixels.end(),native.begin()+target+i*480);
  }
 }else if(table!="space")throw std::runtime_error("Unknown Amiga fragment table");
}
}
