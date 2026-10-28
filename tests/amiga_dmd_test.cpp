#include "assets/amiga_dmd.h"
#include <algorithm>
#include <iostream>
#include <stdexcept>
namespace {
void require(bool ok){if(!ok)throw std::runtime_error("Amiga DMD regression");}
template<class F>void rejects(F f){bool bad=false;try{f();}catch(const std::runtime_error&){bad=true;}require(bad);}
}
int main(){
 using Bytes=std::vector<std::uint8_t>;std::size_t cursor=0;
 Bytes zeros{255,255,255,227};const auto blank=slam::decode_amiga_dmd_frame(zeros,cursor,zeros.size());
 require(cursor==4&&std::all_of(blank.begin(),blank.end(),[](auto x){return x==0;}));
 // Zero count still writes once; literal output is clamped at the display edge.
 Bytes input{0,91,128,255,255,255,127};
 for(unsigned i=0;i<127;++i)input.push_back(std::uint8_t(i+1));
 cursor=0;auto frame=slam::decode_amiga_dmd_frame(input,cursor,input.size());
 require(frame[0]==91&&frame[1]==0&&frame[382]==0&&frame[383]==1&&frame[479]==97);
 require(cursor==input.size()-30);
 for(std::size_t limit=0;limit<cursor;++limit)rejects([&]{std::size_t at=0;slam::decode_amiga_dmd_frame(input,at,limit);});
 rejects([&]{std::size_t at=0;slam::decode_amiga_dmd_frame(input,at,input.size()+1);});
 rejects([&]{std::size_t at=input.size()+1;slam::decode_amiga_dmd_frame(input,at,input.size());});
 Bytes short_source(32),target(4096);rejects([&]{slam::build_amiga_dmd_frames("mean",short_source,target);});
 rejects([&]{slam::build_amiga_dmd_frames("unknown",short_source,target);});
 std::cout<<"Amiga DMD literal/zero/edge/range regressions PASS\n";
}
