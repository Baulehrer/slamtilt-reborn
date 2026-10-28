#include "physics/mean_simulation.h"
#include <iostream>
#include <stdexcept>
static void require(bool value,const char *msg){if(!value)throw std::runtime_error(msg);}
static unsigned word(const slam::MeanSimulation&s,unsigned o){const auto&f=s.shared_raw_state().fields;return f[o]|(unsigned(f[o+1])<<8);}
int main(int argc,char**argv){
 if(argc!=4)return 2;
 try{
  for(unsigned mode:{2u,4u,5u,6u}){
   slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.reset();
   if(mode==2)s.debug_nudge_warning();
   if(mode==4)s.debug_start_mode4_right(false);
   if(mode==5)s.debug_start_shared_mode(1);
   if(mode==6){s.debug_start_multiball(false,true);for(unsigned i=0;i<200 && s.table_mode()!=6;++i)require(s.step(),"Mode6 initialization stopped");}
   require(s.table_mode()==int(mode),"Diagnostic mode seed mismatch");
   const auto score=s.score();const auto pit_before=s.pit_stop_stats();
   for(unsigned id=0;id<4;++id){s.debug_pit_stop_event(id);if(id<3){const auto before=s.score();s.debug_pit_stop_event(id);require(s.score()==before,"Duplicate PitStop route awards twice");}}
   require(word(s,0x398)==1500 && word(s,0x1d8)==4,"Four tyres did not start PitStop");
   require(s.score()==score+10000000,"PitStop puncture score mismatch");
   for(unsigned id=0;id<4;++id)s.debug_pit_stop_event(id);
   require(word(s,0x398)==65535 && word(s,0x3ac)==4,"Four repairs did not retire PitStop");
   require(s.score()==score+65000000,"PitStop repair/jackpot score mismatch");
   const auto&p=s.pit_stop_stats();
   require(p.score==pit_before.score+65000000 && p.starts==pit_before.starts+1 && p.completions==pit_before.completions+1,"PitStop telemetry does not match real dispatch");
   for(unsigned id=0;id<4;++id)require(p.punctures[id]==pit_before.punctures[id]+1 && p.repairs[id]==pit_before.repairs[id]+1,"PitStop route telemetry mismatch");
   require(s.table_mode()==int(mode),"PitStop changed main mode");
   if(mode>1 && mode!=3){s.apply_tilt();const auto before=s.score();s.debug_pit_stop_event(0);require(s.score()==before,"Tilt allows PitStop award");}
  }
  slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.reset();
  for(unsigned i=0;i<2;++i){s.debug_start_right_cancel();require(s.step(),"StockCar trigger stopped simulation");require(word(s,0x38a)==15*(i+1),"StockCar start/restart does not add fifteen");}
  const auto score=s.score();
  require(s.stock_car_stats().starts==2,"StockCar restart telemetry mismatch");
  for(unsigned i=0;i<30;++i){s.debug_stock_car_bumper(4);require(word(s,0x38a)==29-i,"StockCar does not count down");}
  require(s.score()==score+150000000,"Thirty StockCar hits do not award150M");
  require(s.stock_car_stats().hits==30 && s.stock_car_stats().completions==1 && s.stock_car_stats().score==150000000,"StockCar telemetry differs from actual awards");
  s.debug_stock_car_bumper(4);require(s.score()==score+150000000,"Finished StockCar keeps awarding");
  s.debug_nudge_warning();const auto selected=s.selected_mode();s.debug_stock_car_bumper(3);
  require(s.selected_mode()!=selected,"Bumper does not cycle selectable mode");
  s.press_plunger();const auto locked=s.selected_mode();s.debug_stock_car_bumper(3);
  require(s.selected_mode()==locked,"Bumper ignores Return mode lock");
  std::cout<<"PASS PitStop fourmode puncture/repair/jackpot/Tilt and StockCar15+15/countdown/selection/lock native dispatcher chains\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
