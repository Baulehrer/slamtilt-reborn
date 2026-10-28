#include "physics/mean_minigame_lift.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
std::vector<std::uint8_t> read(const char *p){std::ifstream f(p,std::ios::binary);return {std::istreambuf_iterator<char>(f),{}};}
int main(int argc,char **argv){
 if(argc!=5 && argc!=6)return 2;
 try{
  slam::MeanMinigameLift m;if(argc==6)m.revision=slam::MeanMinigameRevision::Retail;m.image=read(argv[1]);const auto r=read(argv[2]);std::copy(r.begin(),r.end(),m.runtime.begin());m.dat=read(argv[3]);
  std::ifstream input(argv[4]);nlohmann::json fixture;input>>fixture;auto rows=nlohmann::json::array();
  for(auto key:fixture.at("keys")){
   const auto k=key.get<unsigned>();m.wr(0x1001054,k==1?0xffffffff:0,4);m.wr(0x1001058,k==2?0xffffffff:0,4);
   m.r[4]=0x200f000;m.push(0x200fff0);slam::minigame_4180d0(m);m.audio_requests.clear();
   std::array<std::uint32_t,24> fields{};for(unsigned i=0;i<fields.size();++i)fields[i]=m.rd(0x43efd8+4*i,4);
   std::uint64_t hash=14695981039346656037ull;for(unsigned i=0;i<480;++i)hash=(hash^m.byte(0x43ec3c+i))*1099511628211ull;
   rows.push_back({{"fields",fields},{"active",m.rd(0x1001044,4)},{"mode",m.rd(0x1001030,4)},{"field_1fa",m.rd(0x43f1fa,2)},{"points",m.points},{"callback",m.requested_display_callback},{"packed_frame_fnv",std::to_string(hash)}});
   if(!m.rd(0x1001044,4))break;
  }
  std::cout<<rows.dump();
 }catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 1;}
}
