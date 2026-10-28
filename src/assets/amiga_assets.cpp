#include "assets/amiga_assets.h"
#include "assets/amiga_contact.h"
#include "assets/amiga_dmd.h"
#include "assets/amiga_dmd_fragments_v2.h"
#include "assets/native_retail_data.h"
#include <algorithm>
#include <array>
#include <cctype>
#include <stdexcept>
namespace slam {
// Implemented by the shared Amiga-asset adapter, using data inside Game.exe
// from the user's disk set. It never executes the Amiga executable.
std::vector<std::uint8_t> build_amiga_main_data(const std::vector<std::uint8_t>&,const std::vector<std::uint8_t>&);
namespace {
using Bytes=std::vector<std::uint8_t>;
using Files=std::map<std::string,Bytes>;
std::string lower(std::string value){for(auto&c:value)c=char(std::tolower(static_cast<unsigned char>(c)));return value;}
const Bytes* file(const Files& files,std::string name){
 const Bytes* result=nullptr;
 for(const auto&entry:files){const auto key=lower(entry.first);if(key==name||(key.size()>name.size()&&key.substr(key.size()-name.size()-1)=="/"+name)){if(result&&*result!=entry.second)throw std::runtime_error("Conflicting Amiga asset: "+name);result=&entry.second;}}
 if(!result)throw std::runtime_error("Missing Amiga asset: "+name);
 return result;
}
unsigned be16(const Bytes& data,std::size_t p){if(p>data.size()||data.size()-p<2)throw std::runtime_error("Truncated Amiga asset word");return unsigned(data[p])*256+data[p+1];}
unsigned be32(const Bytes& data,std::size_t p){return (be16(data,p)<<16)|be16(data,p+2);}
void copy(const Bytes& source,std::size_t from,Bytes& target,std::size_t to,std::size_t size){
 if(from>source.size()||size>source.size()-from||to>target.size()||size>target.size()-to)throw std::runtime_error("Amiga asset conversion range outside input/output");
 std::copy_n(source.begin()+from,size,target.begin()+to);
}
void planar(const Bytes& source,std::size_t from,Bytes& target,std::size_t to,unsigned width,unsigned height,unsigned planes=8){
 if(!width||width%8||!height||!planes||planes>8)throw std::runtime_error("Invalid Amiga planar geometry");
 const std::size_t row=std::size_t(width/8)*planes,size=row*height,pixels=std::size_t(width)*height;
 if(from>source.size()||size>source.size()-from||to>target.size()||pixels>target.size()-to)throw std::runtime_error("Truncated Amiga planar pixels");
 for(unsigned y=0;y<height;++y)for(unsigned x=0;x<width;++x){unsigned index=0;for(unsigned p=0;p<planes;++p)index|=((source[from+y*row+p*(width/8)+x/8]>>(7-x%8))&1u)<<p;target[to+std::size_t(y)*width+x]=std::uint8_t(index);}
}
struct Copy{unsigned target,source,size;bool raw;};
#include "assets/amiga_copy_map.inc"
#include "assets/amiga_lamp_offsets.inc"
struct Flipper{const char* name;unsigned target,width,height,count;};
struct Table{const char* name;unsigned size,palette;const Copy* copies;std::size_t copy_count;std::array<Flipper,3> flippers;unsigned flipper_count,lamps,returned_descriptor;const unsigned* lamp_offsets;};
const Table tables[]={
 {"mean",1622024,0x1590c8,mean_copies,std::size(mean_copies),{{{"flippers/flpl3.raw",0x6eabe,64,45,10},{"flippers/flpr3.raw",0x75b3e,64,45,10},{"flippers/flpxr2.raw",0x7cbbe,64,49,8}}},3,63,0x464b98,mean_lamp_offsets},
 {"pirate",1543772,0x14605c,pirate_copies,std::size(pirate_copies),{{{"flippers/flpl1.raw",0x64484,64,45,10},{"flippers/flpr1.raw",0x6b504,64,45,10},{"flippers/flpxr1.raw",0x72584,64,51,7}}},3,53,0x465958,pirate_lamp_offsets},
 {"space",1568309,0x14c035,space_copies,std::size(space_copies),{{{"flippers/flpl2.raw",0x6fd15,64,45,10},{"flippers/flpr2.raw",0x76d95,64,45,10},{"flippers/flpxl1.raw",0x7de15,64,51,8}}},3,48,0x46664c,space_lamp_offsets},
 {"demon",1546096,0x146830,demon_copies,std::size(demon_copies),{{{"flippers/flpl1.raw",0x84bf6,64,45,10},{"flippers/flpr1.raw",0x8bc76,64,45,10},{nullptr,0,0,0,0}}},2,52,0x463b54,demon_lamp_offsets}
};
unsigned le(const Bytes& image,unsigned address,unsigned width=4){if(address<0x400000||address-0x400000+width>image.size())throw std::runtime_error("Native descriptor outside image");unsigned v=0;for(unsigned i=0;i<width;++i)v|=unsigned(image[address-0x400000+i])<<(i*8);return v;}
void lamps(const Table&t,const Bytes& raw,Bytes& target,unsigned section){
 const auto image=native_retail_data_image();const auto metadata=le(image,t.returned_descriptor+8),directory=le(image,metadata+16);const auto source_directory=section+be32(raw,section+16);
 for(unsigned i=0;i<t.lamps;++i){const auto d=le(image,directory+i*4),record=source_directory+be32(raw,source_directory+4*(i+1));const auto x=le(image,d,2),y=le(image,d+2,2),width=le(image,d+4,2)*16,height=le(image,d+6,2);
  const auto source_x=be16(raw,record)*8,source_y=be16(raw,record+2),source_width=be16(raw,record+4)*16,source_height=be16(raw,record+6);
  if(x!=source_x||y!=source_y||width!=source_width||source_height>height)throw std::runtime_error("Unsupported Amiga lamp descriptor layout");
  // Original source offsets are initialized by the existing startup recipe;
  // native descriptors reserve equal-sized padded mask slots per lamp.
  const auto offset=t.lamp_offsets[i],row=width/8;
  if(offset>target.size()||std::size_t(row)*height>target.size()-offset)throw std::runtime_error("Amiga lamp target outside native asset layout");
  std::fill_n(target.begin()+offset,std::size_t(row)*height,0);
  copy(raw,record+12,target,offset,std::size_t(row)*source_height);
 }
}
}
AmigaNativeAssets build_amiga_assets(const Files& input){
 AmigaNativeAssets result;
 for(const auto&t:tables){const std::string raw_name=std::string(t.name)+".raw",bin_name=std::string(t.name)+".bin";const auto&raw=*file(input,raw_name);const auto&bin=*file(input,bin_name);Bytes data(t.size);
  for(std::size_t i=0;i<t.copy_count;++i){const auto&c=t.copies[i];copy(c.raw?raw:bin,c.source,data,c.target,c.size);}
  const auto section=be32(raw,0);const auto pixels=section+be32(raw,section),palette=section+be32(raw,section+4);
  copy(raw,palette,data,t.palette,1024);planar(raw,pixels,data,t.palette+1024,320,600);
  lamps(t,raw,data,section);
  for(unsigned i=0;i<t.flipper_count;++i){const auto&f=t.flippers[i];const std::string source_name=f.name;const auto&source=*file(input,source_name);if(be16(source,6)*8!=f.width||be16(source,8)!=f.height||be16(source,14)!=f.count)throw std::runtime_error("Unsupported Amiga flipper header");for(unsigned n=0;n<f.count;++n)planar(source,16+std::size_t(n)*f.width*f.height,data,f.target+std::size_t(n)*f.width*f.height,f.width,f.height);}
  build_amiga_dmd_frames(t.name,bin,data);
  build_amiga_dmd_fragments_v2(t.name,bin,data);
  // Observed original shared-reader407020 consumes these complete480-byte
  // frames (callers410dae/413927); both are exact original Demon.Bin objects.
  if(std::string(t.name)=="demon"){
   copy(bin,0x65296,data,0x134b30,480);
   copy(bin,0x9bcba,data,0x1402f0,480);
  }
  if(std::string(t.name)=="mean")build_amiga_mean_contact_frames(raw,bin,data);
  auto name=std::string(t.name);std::transform(name.begin(),name.end(),name.begin(),[](unsigned char c){return char(std::toupper(c));});result.files[name+".DAT"]=std::move(data);
 }
 bool named_game=false;
 for(const auto& entry:input){const auto key=lower(entry.first);if(key=="game.exe"||(key.size()>9&&key.substr(key.size()-9)=="/game.exe"))named_game=true;}
 result.files["MAIN.DAT"]=build_amiga_main_data(*file(input,named_game?"game.exe":"slam-tilt"),*file(input,"matrix.dat"));
 return result;
}
}
