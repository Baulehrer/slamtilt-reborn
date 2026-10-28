#include "assets/amiga_dmd_fragments_v2.h"
#include <iostream>
#include <stdexcept>
namespace {
template<class F>void rejects(F f){bool bad=false;try{f();}catch(const std::runtime_error&){bad=true;}if(!bad)throw std::runtime_error("Invalid Amiga fragment accepted");}
}
int main(){
 std::vector<std::uint8_t> empty,source(0xb0000),target(0x180000);
 for(auto table:{"mean","pirate","demon"}){
  rejects([&]{slam::build_amiga_dmd_fragments_v2(table,empty,target);});
  rejects([&]{slam::build_amiga_dmd_fragments_v2(table,source,empty);});
 }
 rejects([&]{slam::build_amiga_dmd_fragments_v2("unknown",source,target);});
 // Correct directory length, first pointer outside the supplied source.
 source[0x6b862]=52;source[0x6b863]=0xff;
 rejects([&]{slam::build_amiga_dmd_fragments_v2("pirate",source,target);});
 slam::build_amiga_dmd_fragments_v2("space",empty,empty);
 std::cout<<"Amiga v2 source/target/directory rejection PASS\n";
}
