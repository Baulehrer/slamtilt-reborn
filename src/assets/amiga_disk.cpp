#include "assets/amiga_disk.h"
#include <algorithm>
#include <array>
#include <fstream>
#include <set>
#include <stdexcept>

namespace slam { namespace {
using Bytes = std::vector<std::uint8_t>;
std::string lower(std::string name) {
  for(auto& c:name)if(c>='A'&&c<='Z')c=char(c-'A'+'a');
  return name;
}
std::uint32_t be32(const Bytes& bytes,std::size_t offset) {
  if(offset>bytes.size()||bytes.size()-offset<4)throw std::runtime_error("Truncated Amiga data");
  return (std::uint32_t(bytes[offset])<<24)|(std::uint32_t(bytes[offset+1])<<16)|
         (std::uint32_t(bytes[offset+2])<<8)|bytes[offset+3];
}
Bytes read(const std::filesystem::path& path) {
  std::ifstream f(path,std::ios::binary|std::ios::ate);
  if(!f||f.tellg()!=901120)throw std::runtime_error("Expected standard 880 KiB ADF: "+path.filename().string());
  Bytes bytes(901120);f.seekg(0);
  if(!f.read(reinterpret_cast<char*>(bytes.data()),bytes.size()))throw std::runtime_error("Cannot read ADF");
  return bytes;
}
class Disk {
  const Bytes& bytes_;
  bool ffs_;
  std::set<unsigned> metadata_,data_;
  std::uint32_t word(unsigned block,unsigned index)const {
    if(block<2||block>=1760||index>=128)throw std::runtime_error("ADF block pointer outside disk");
    return be32(bytes_,std::size_t(block)*512+index*4);
  }
  void checksum(unsigned block)const {
    std::uint32_t sum=0;for(unsigned i=0;i<128;++i)sum+=word(block,i);
    if(sum)throw std::runtime_error("Invalid ADF block checksum");
  }
  void claim_metadata(unsigned block) {
    if(data_.count(block)||!metadata_.insert(block).second)throw std::runtime_error("Repeated/cyclic ADF metadata block");
    checksum(block);
  }
  std::string name(unsigned block)const {
    const auto at=std::size_t(block)*512+432;
    const unsigned size=bytes_.at(at);
    if(!size||size>30)throw std::runtime_error("Unsupported ADF filename");
    std::string result(bytes_.begin()+at+1,bytes_.begin()+at+1+size);
    if(result=="."||result==".."||result.find_first_of("/\\:")!=std::string::npos||
       std::any_of(result.begin(),result.end(),[](unsigned char c){return c<32||c==127;}))
      throw std::runtime_error("Invalid ADF filename");
    return lower(result);
  }
  Bytes file(unsigned header) {
    const auto size=word(header,81);
    if(size>bytes_.size())throw std::runtime_error("ADF file size exceeds disk");
    const unsigned payload=ffs_?512:488;
    const auto expected=(size+payload-1)/payload;
    std::vector<unsigned> blocks;
    unsigned list=header;
    while(list) {
      if(list!=header) {
        claim_metadata(list);
        if(word(list,0)!=16||word(list,127)!=0xfffffffdu||word(list,1)!=list||word(list,125)!=header)
          throw std::runtime_error("Invalid ADF file extension");
      }
      const auto count=word(list,2);
      if(count>72||blocks.size()+count>expected)throw std::runtime_error("Invalid ADF file block count");
      for(unsigned i=0;i<count;++i)blocks.push_back(word(list,77-i));
      list=word(list,126);
      if(blocks.size()==expected&&list)throw std::runtime_error("Unexpected ADF extension");
    }
    if(blocks.size()!=expected)throw std::runtime_error("Truncated ADF file block list");
    Bytes result;result.reserve(size);
    for(unsigned i=0;i<blocks.size();++i) {
      const auto block=blocks[i];
      if(block<2||block>=1760||metadata_.count(block)||!data_.insert(block).second)
        throw std::runtime_error("Repeated/invalid ADF file data block");
      unsigned offset=0,amount=std::min<unsigned>(payload,size-result.size());
      if(!ffs_) {
        checksum(block);offset=24;
        if(word(block,0)!=8||word(block,1)!=header||word(block,2)!=i+1||word(block,3)!=amount||
           word(block,4)!=(i+1<blocks.size()?blocks[i+1]:0))throw std::runtime_error("Invalid OFS data sequence");
      }
      const auto start=std::size_t(block)*512+offset;
      result.insert(result.end(),bytes_.begin()+start,bytes_.begin()+start+amount);
    }
    return result;
  }
  void directory(unsigned block,const std::string& prefix,AmigaFiles& files,unsigned depth) {
    if(depth>32)throw std::runtime_error("ADF directory nesting limit");
    const unsigned count=block==880?word(block,3):72;
    if(count!=72)throw std::runtime_error("Unsupported ADF directory hash size");
    std::set<std::string> names;
    for(unsigned bucket=0;bucket<count;++bucket) {
      auto entry=word(block,6+bucket);
      while(entry) {
        claim_metadata(entry);
        if(word(entry,0)!=2||word(entry,1)!=entry||word(entry,125)!=block)
          throw std::runtime_error("Invalid ADF directory entry");
        auto leaf=name(entry);
        if(!names.insert(leaf).second)throw std::runtime_error("Ambiguous ADF filename");
        const auto path=prefix+leaf;
        const auto type=word(entry,127);
        if(type==2)directory(entry,path+"/",files,depth+1);
        else if(type==0xfffffffdu) {
          if(!files.emplace(path,file(entry)).second)throw std::runtime_error("Duplicate ADF path");
        }else throw std::runtime_error("Unsupported ADF link/entry type");
        entry=word(entry,124);
      }
    }
  }
 public:
  explicit Disk(const Bytes& bytes):bytes_(bytes),ffs_(bytes.at(3)&1) {
    if(bytes[0]!='D'||bytes[1]!='O'||bytes[2]!='S'||bytes[3]>5)
      throw std::runtime_error("Unsupported ADF filesystem (OFS/FFS expected)");
    const auto root=be32(bytes,8);
    if(root&&root!=880)throw std::runtime_error("Unsupported ADF root position");
    // A zero boot checksum is valid for non-bootable data disks.
    const auto stored=be32(bytes,4);
    if(stored) {
      std::uint64_t sum=0;
      for(unsigned i=0;i<256;++i)if(i!=1){sum+=be32(bytes,i*4);if(sum>0xffffffffu)sum=(sum+1)&0xffffffffu;}
      if(std::uint32_t(~sum)!=stored)throw std::runtime_error("Invalid ADF boot checksum");
    }
    claim_metadata(880);
    if(word(880,0)!=2||word(880,127)!=1)throw std::runtime_error("Invalid ADF root block");
  }
  unsigned slot()const {
    const auto volume=name(880);
    if(volume.find("slam")==std::string::npos||volume.back()<'1'||volume.back()>'5')
      throw std::runtime_error("ADF is not a recognized Slam Tilt disk volume");
    return unsigned(volume.back()-'0');
  }
  AmigaFiles files() {AmigaFiles result;directory(880,"",result,0);return result;}
};
}

AmigaFiles read_amiga_adf_set(const std::filesystem::path& folder) {
  if(!std::filesystem::is_directory(folder))throw std::runtime_error("Choose a folder containing five Slam Tilt ADFs");
  std::map<unsigned,AmigaFiles> disks;
  for(const auto& entry:std::filesystem::directory_iterator(folder)) {
    if(!entry.is_regular_file()||lower(entry.path().extension().string())!=".adf")continue;
    const auto bytes=read(entry.path());Disk disk(bytes);const auto slot=disk.slot();
    if(!disks.emplace(slot,disk.files()).second)throw std::runtime_error("Ambiguous ADF set: duplicate disk "+std::to_string(slot));
  }
  for(unsigned i=1;i<=5;++i)if(!disks.count(i))throw std::runtime_error("Missing Slam Tilt ADF disk "+std::to_string(i)+" of 5");
  AmigaFiles result;
  for(auto& [slot,files]:disks)for(auto& [name,bytes]:files) {
    result.emplace("slam"+std::to_string(slot)+"/"+name,bytes);
    const auto ext=lower(std::filesystem::path(name).extension().string());
    if(ext==".bin"||ext==".raw"||ext==".dat") {
      const auto found=result.find(name);
      if(found!=result.end()&&found->second!=bytes)throw std::runtime_error("Conflicting ADF game asset: "+name);
      if(found==result.end())result.emplace(name,bytes);
    }
  }
  return result;
}

// Bounded SLAM/StoneCracker generation-8 decoder; native translation of this
// project's tools/slamdecode.py. Consulted ancient's BSD-2-Clause reference;
// retain LICENSES/ancient-BSD-2-Clause.txt and docs/amiga-overlays.md attribution.
std::vector<std::uint8_t> decode_slam(const std::vector<std::uint8_t>& data,std::size_t max_output) {
  if(data.size()<22||data[0]!='S'||data[1]!='L'||data[2]!='A'||data[3]!='M')throw std::runtime_error("Not a SLAM container");
  const auto marker=be32(data,4),size=be32(data,8),packed=be32(data,12);
  if(marker!=0x50||!size||size>max_output)throw std::runtime_error("Unsupported SLAM marker/output size");
  const std::uint64_t end64=12ull+packed;
  if(end64<16||end64+6>data.size())throw std::runtime_error("Truncated SLAM payload/trailer");
  std::size_t cursor=std::size_t(end64);
  auto word=[&](std::size_t at){return (unsigned(data.at(at))<<8)|data.at(at+1);};
  const unsigned mode=word(cursor),initial=word(cursor+2);unsigned available=word(cursor+4),reservoir=initial;
  if(mode<10||mode>14||available>16)throw std::runtime_error("Invalid SLAM distance mode/bit count");
  auto bits=[&](unsigned count){unsigned value=0;for(unsigned i=0;i<count;++i){if(!available){if(cursor<18)throw std::runtime_error("SLAM bitstream exhausted");cursor-=2;reservoir=word(cursor);available=16;}value=(value<<1)|((reservoir>>15)&1);reservoir=(reservoir<<1)&0xffff;--available;}return value;};
  Bytes result(size);std::size_t pos=size;
  while(pos) {
    bool literal=false;std::size_t count;
    if(!bits(1)){literal=true;count=1;}
    else if(bits(1))count=2+bits(1);
    else if(bits(1))count=4+bits(2);
    else if(!bits(1)) {
      count=23+bits(8);
      if(count==278)for(;;){const auto extra=bits(8);count+=extra;if(count>pos)throw std::runtime_error("SLAM literal run exceeds output");if(extra!=255)break;}
    }else{const auto extra=bits(4);if(extra<15)count=8+extra;else{literal=true;count=14+bits(5);}}
    if(count>pos)throw std::runtime_error("SLAM run exceeds output");
    if(literal)for(std::size_t i=0;i<count;++i){--pos;result[pos]=std::uint8_t(bits(8));}
    else {
      unsigned distance;if(bits(1))distance=545+bits(mode);else if(bits(1))distance=1+bits(5);else distance=33+bits(9);
      if(distance>result.size()-pos)throw std::runtime_error("SLAM backreference outside output");
      for(std::size_t i=0;i<count;++i){--pos;result[pos]=result[pos+distance];}
    }
  }
  return result;
}
}
