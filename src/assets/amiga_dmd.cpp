#include "assets/amiga_dmd.h"
#include <algorithm>
#include <stdexcept>
namespace slam {
namespace {
using Bytes=std::vector<std::uint8_t>;
unsigned be32(const Bytes& b,std::size_t at){
 if(at>b.size()||b.size()-at<4)throw std::runtime_error("Truncated Amiga DMD directory");
 unsigned v=0;for(unsigned i=0;i<4;++i)v=(v<<8)|b[at+i];return v;
}
struct DmdBank{unsigned target,directory,count;};
struct DmdFrame{unsigned target,source,limit;};
#include "assets/amiga_dmd_map.inc"
void frame(const Bytes& source,std::size_t cursor,std::size_t limit,Bytes& native,std::size_t target){
 if(target>native.size()||native.size()-target<480)throw std::runtime_error("Amiga DMD target outside assets");
 const auto data=decode_amiga_dmd_frame(source,cursor,limit);
 std::copy(data.begin(),data.end(),native.begin()+target);
}
template<std::size_t N,std::size_t M>
void banks(const Bytes& source,Bytes& native,const DmdBank(&entries)[N],const DmdFrame(&single)[M]){
 for(const auto& bank:entries){
  if(!bank.count)continue;
  if(be32(source,bank.directory)!=bank.count*4)throw std::runtime_error("Unsupported Amiga DMD bank layout");
  unsigned previous=bank.count*4;
  for(unsigned i=0;i<bank.count;++i){
   const auto offset=be32(source,bank.directory+i*4);
   if(offset<previous||offset>source.size()||bank.directory>source.size()-offset)throw std::runtime_error("Invalid Amiga DMD frame offset");
   const auto start=std::size_t(bank.directory)+offset;
   std::size_t limit=source.size();
   if(i+1<bank.count){const auto next=be32(source,bank.directory+(i+1)*4);if(next<=offset||next>source.size()-bank.directory)throw std::runtime_error("Invalid Amiga DMD frame limit");limit=bank.directory+next;}
   frame(source,start,limit,native,std::size_t(bank.target)+i*480);
   previous=offset;
  }
 }
 for(const auto& f:single)if(f.limit)frame(source,f.source,f.limit,native,f.target);
}
}
std::array<std::uint8_t,480> decode_amiga_dmd_frame(const Bytes& source,std::size_t& cursor,std::size_t limit){
 if(limit>source.size()||cursor>limit)throw std::runtime_error("Invalid Amiga DMD input range");
 std::array<std::uint8_t,480> out{};std::size_t used=0;
 while(used<out.size()){
  if(cursor==limit)throw std::runtime_error("Truncated Amiga DMD run");
  const auto control=source[cursor++];
  // Original writes once before testing DBRA/subq, including count zero.
  const auto count=std::min<std::size_t>(std::max<unsigned>(1,control&127),out.size()-used);
  if(!(control&128)){
   if(count>limit-cursor)throw std::runtime_error("Truncated Amiga DMD literals");
   std::copy_n(source.begin()+cursor,count,out.begin()+used);cursor+=count;
  }
  used+=count;
 }
 return out;
}
void build_amiga_dmd_frames(std::string_view table,const Bytes& source,Bytes& native){
 if(table=="mean")banks(source,native,mean_dmd_banks,mean_dmd_frames);
 else if(table=="pirate")banks(source,native,pirate_dmd_banks,pirate_dmd_frames);
 else if(table=="space")banks(source,native,space_dmd_banks,space_dmd_frames);
 else if(table=="demon")banks(source,native,demon_dmd_banks,demon_dmd_frames);
 else throw std::runtime_error("Unknown Amiga DMD table");
}
}
