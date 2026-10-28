#include "rules/mean_award_bank.h"
#include "rules/mean_flipper_actions.h"
#include "rules/mean_material5.h"
#include <iostream>
#include <stdexcept>
using namespace slam;
static void require(bool ok, const char* what) { if (!ok) throw std::runtime_error(what); }
int main() {
  try {
    MeanLampCommands lamps{};
    std::array<std::uint8_t,5> flags{};
    std::int16_t timer=-1;
    std::uint32_t value=0;
    const int lane_x[]{22,44,159,274,275};
    for(unsigned i=0;i<5;++i) {
      const bool started=mean_award_bank_target(lane_x[i]*65536,2,flags,timer,value,lamps);
      require(started==(i==4),"five distinct lanes activation");
      if(i<4) require(timer==-1 && value==0,"premature activation");
    }
    require(flags==std::array<std::uint8_t,5>{} && timer==6000,"start state");
    require(value==60000000 && value!=75000000,"binary60M differs from manual75M");
    require(lamps[62]==std::array<std::uint8_t,4>{4,6,1,0},"blue target lit");
    require(!mean_award_bank_target(22*65536,2,flags,timer,value,lamps),"active bank does not relight lanes");
    require(flags==std::array<std::uint8_t,5>{},"active bank flags untouched");
    for(unsigned i=0;i<100;++i) require(mean_award_bank_tick(timer,value,lamps)==0,"early tick callback");
    require(timer==5900 && value==59000000,"100tick decay");
    MeanMaterial5State target;target.field_37a=timer;target.field_054=value;target.mode=2;
    auto hit=mean_material5_rules(161*65536,351*65536,target);
    require(hit.score_add==59000000 && hit.callback==0x41062c && hit.stop84 && hit.sample,"blue target collection");
    require(target.field_37a==-1,"collection ends timer");
    require(mean_material5_rules(161*65536,351*65536,target).score_add==0,"once-only collection");
    target.field_37a=5900;target.mode=4;
    hit=mean_material5_rules(161*65536,351*65536,target);
    require(hit.sample && !hit.stop84 && !hit.score_add && !hit.callback && target.field_37a==5900,"mode4 collection excluded");
    for(int mode:{5,6}) {
      flags.fill(1);timer=-1;value=123;
      require(!mean_award_bank_target(22*65536,mode,flags,timer,value,lamps) && timer==-1 && value==123,"special mode activation excluded");
    }
    // Original target accepts mode4; pre-ball caller and collection require mode<4.
    flags.fill(1);timer=-1;value=0;
    require(mean_award_bank_target(22*65536,4,flags,timer,value,lamps) && timer==6000,"mode4 target gate preserved");
    timer=3001;require(mean_award_bank_tick(timer,value,lamps)==0x41086c && timer==3000 && value==30000000,"half-time callback");
    timer=1000;mean_award_bank_tick(timer,value,lamps);require(value==10000000,"minimum award floor");
    timer=0;require(mean_award_bank_tick(timer,value,lamps)==0x410504 && timer==-1 && lamps[62][0]==2,"expiry retires target");
    // SDL Shift edges invoke this existing original flipper-action adapter.
    MeanBallResetState raw;raw.fields[0x1ec]=1;raw.fields[0x1ed]=1;
    mean_flipper_actions(raw,2,0,false,0);
    const std::array<std::uint8_t,5> rotated{1,0,0,0,1};
    for(unsigned i=0;i<5;++i)require(raw.fields[0x1ec+i]==rotated[i] && raw.fields[0x28c+i*4]==2-rotated[i],"five lane flipper rotation");
    const auto prior=raw.fields;
    mean_flipper_actions(raw,2,-1,false,0);require(raw.fields==prior,"release edge no rotation");
    mean_flipper_actions(raw,2,0,true,1);require(raw.fields==prior,"Tilt blocks flipper rotation");
    std::cout << "Overheat original-backed lane/rotation/decay/collection/expiry gates PASS; binary60M\n";
  } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}
