#include "physics/mean_mode6_capture.h"
#include "physics/mean_mode6_side.h"
#include "rules/mean_shared_reward.h"
#include <iostream>
#include <stdexcept>
using namespace slam;
static void check(bool v,const char* s){if(!v)throw std::runtime_error(s);}
static void word(MeanBallResetState& s,unsigned o,std::int16_t v){s.fields[o]=v;s.fields[o+1]=std::uint16_t(v)>>8;}
static unsigned award(const MeanMode5LeftState& m,unsigned id=1){
 MeanBallResetState r;r.table_mode=6;word(r,0x38e,m.field_43f38e);word(r,0x368,m.field_43f368);word(r,0x36c,m.field_43f36c);word(r,0x35e,-1);
 const auto e=mean_shared_reward(r,id,1);check(e.scores.size()==1 && e.callback==0x410158,"jackpot event");return e.scores[0];
}
int main(){try{
 MeanMode5LeftState locks;MeanUpperCaptureState upper;MeanMode6CaptureEvent event;MeanObject top;
 check(award(locks)==10000000,"base jackpot");
 top.put16(0x58,3);top.put16(0x5a,1);upper.field_43f36a=-1;
 check(mean_mode6_capture_tick(top,locks,upper,4,event) && top.u16(0x58)==6 && locks.field_43f38e==2000,"upper lock2000");
 check(award(locks)==20000000,"double jackpot");
 MeanMode6SideState side;side.active_count=4;side.field_43f38e=locks.field_43f38e;side.field_43f380=-1;
 MeanMode6SideEvent se;MeanObject left;left.put16(0x58,3);left.put16(0x5a,2);
 check(mean_mode6_side_tick(left,side,se) && left.u16(0x58)==6 && side.field_43f368==2000,"left lock2000");
 locks.field_43f368=side.field_43f368;check(award(locks)==30000000,"triple jackpot");
 MeanObject right;right.put16(0x58,3);right.put16(0x5a,4);side.field_43f370=0;side.field_438b38=1;
 check(mean_mode6_side_tick(right,side,se) && right.u16(0x58)==6 && side.field_43f36c==2000,"right lock2000");
 locks.field_43f36c=side.field_43f36c;check(award(locks)==40000000,"quadruple jackpot");
 // Each state's callback runs once per200Hz physics step:2000 decrements=10s.
 for(unsigned i=0;i<2000;++i){
  for(auto* ball:{&top,&left,&right}){check(mean_mode6_capture_tick(*ball,locks,upper,4,event),"held callback");check(!event.transfer,"no early timer transfer");}
 }
 check(locks.field_43f38e==0 && locks.field_43f368==0 && locks.field_43f36c==0 && award(locks)==40000000,"zero inclusive active boundary");
 for(auto* ball:{&top,&left,&right}){mean_mode6_capture_tick(*ball,locks,upper,4,event);check(!event.transfer,"decrement0 to minus1 not transfer");}
 check(award(locks)==10000000,"expired locks remove multiplier");
 for(auto* ball:{&top,&left,&right}){mean_mode6_capture_tick(*ball,locks,upper,4,event);check(event.transfer && event.lamp_reset,"negative entry requests transfer and lamp reset");}
 // With threeheld and onlythree active balls, a held callback ejects immediately.
 locks.field_43f38e=locks.field_43f368=locks.field_43f36c=2000;
 mean_mode6_capture_tick(top,locks,upper,3,event);check(event.transfer && locks.field_43f38e==-1,"allballs held protection");
 // Side entry keeps one free: twoactive withone existing lock refusessecond.
 side={};side.active_count=2;side.field_43f38e=2000;side.field_43f380=-1;
 left.put16(0x58,3);left.put16(0x5a,2);mean_mode6_side_tick(left,side,se);
 check(left.u16(0x58)==3 && side.field_43f368==-1,"last free ball not side locked");
 // Original ID0 is not a SPEED shot;ID2 may consume35e exclusion first.
 MeanBallResetState raw;raw.table_mode=6;word(raw,0x38e,-1);word(raw,0x368,-1);word(raw,0x36c,-1);word(raw,0x35e,0);
 check(mean_shared_reward(raw,0,1).scores.empty(),"ID0 excluded");check(mean_shared_reward(raw,2,1).scores.empty(),"ID2 guarded shot");
 check(mean_shared_reward(raw,2,1).scores==std::vector<std::uint32_t>{10000000},"ID2 after guard expiry");
 std::cout<<"SPEED three locks2000ticks/10s,10M multipliers,expiry and held protection PASS\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
