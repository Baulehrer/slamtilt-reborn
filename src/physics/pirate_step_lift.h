#pragma once
#include "physics/flipper_lift.h"
#include <functional>
#include <sstream>
namespace slam {
// Temporary static intermediate for the Retail gameplay island; no CPU decoder.
struct PirateStepLift:FlipperLift {
  std::vector<std::uint8_t> runtime,dat;
  std::function<void(PirateStepLift&,std::uint32_t)> external_service;
  std::function<void(PirateStepLift&,std::uint32_t)> instruction_observer;
  std::function<void(PirateStepLift&,std::uint32_t)> call_observer;
  bool direction=false;
  std::uint32_t last_entry=0;
  PirateStepLift():runtime(0x10000) {}
  std::uint8_t& byte(std::uint32_t address) {
    if(address>=0x1000000&&address-0x1000000<runtime.size())return runtime[address-0x1000000];
    if(address>=0x1100000&&address-0x1100000<dat.size())return dat[address-0x1100000];
    if(address>=0x400000&&address-0x400000<image.size())return image[address-0x400000];
    if(address>=0x2000000&&address-0x2000000<stack.size())return stack[address-0x2000000];
    std::ostringstream out;out<<"Pirate memory 0x"<<std::hex<<address<<" in entry 0x"<<last_entry;
    throw std::out_of_range(out.str());
  }
  std::uint32_t rd(std::uint32_t address,unsigned count) {
    std::uint32_t value=0;for(unsigned i=0;i<count;++i)value|=std::uint32_t(byte(address+i))<<(i*8);return value;
  }
  void wr(std::uint32_t address,std::uint32_t value,unsigned count) { for(unsigned i=0;i<count;++i)byte(address+i)=value>>(i*8); }
  void push(std::uint32_t value){r[4]-=4;wr(r[4],value,4);}
  std::uint32_t pop(){auto value=rd(r[4],4);r[4]+=4;return value;}
  std::uint32_t adc(std::uint32_t a,std::uint32_t b,unsigned n) {
    const auto carry=c?1u:0u;const auto value=std::uint64_t(a&mask(n))+(b&mask(n))+carry;
    const auto result=std::uint32_t(value)&mask(n);c=value>mask(n);
    o=(~(a^b)&(a^result)&(1u<<(n*8-1)))!=0;return flags(result,n);
  }
  void call(std::uint32_t);
  void external(std::uint32_t address) {
    if(external_service){external_service(*this,address);return;}
    std::ostringstream out;out<<"Unsupported Pirate call 0x"<<std::hex<<address;
    throw std::runtime_error(out.str());
  }
  void invoke(std::uint32_t address,std::uint32_t eax=0) {
    r[0]=eax;r[4]=0x200f004;push(0x2100000);call(address);
    if(r[4]!=0x200f004)throw std::runtime_error("Pirate native stack mismatch");
  }
};
}
