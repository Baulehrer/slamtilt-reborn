#include "physics/mean_simulation.h"
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <stdexcept>
using json=nlohmann::json;
static unsigned mask(const slam::MeanSimulation&s){
 // Original Offroad pays changes from the preceding target, including a
 // revisited target. Six payouts are NOT six unique physical switches.
 bool offroad=s.offroad_stats().ends && s.offroad_stats().awards>=6 && s.offroad_stats().score>=90000000;
 return (s.chicken_stats().completions?1:0)|(s.monster_stats().completions?2:0)|(s.rally_stats().completions?4:0)|(s.minigame_completions()?8:0)|(offroad?16:0);
}
static void require(bool b,const char*m){if(!b)throw std::runtime_error(m);}
static void mix(std::uint64_t&h,std::uint64_t v){for(unsigned i=0;i<8;++i){h^=(v>>(8*i))&255;h*=1099511628211ull;}}
int main(int argc,char**argv){if(argc!=6&&argc!=7)return 2;try{
 if(argc==7)require(std::string(argv[6])=="--observe-contacts"||std::string(argv[6])=="--observe-pairs","Unknown marathon option");
 json fixture;std::ifstream(argv[4])>>fixture;json cases=json::array(),admission_runs=json::array(),speed_runs=json::array();
 for(unsigned repeat=0;repeat<2;++repeat){
  slam::MeanSimulation s(argv[1],argv[2],argv[3]);s.set_retail_minigame(true);s.reset();s.set_continuous_play(true);s.set_endless_play(false);
  unsigned observed=0;
  if(argc==7){
   if(std::string(argv[6])=="--observe-pairs")s.set_pair_observer([&](const slam::MeanPairTrace&){++observed;});
   else s.set_contact_observer([&](const slam::MeanContactTrace&){++observed;});
  }
  unsigned tick=0,previous=0,nudges=0,formula_wins=0;
  bool formula_tracking=false;std::uint64_t formula_entry_score=0;unsigned formula_entry_prizes=0;
  std::uint64_t hash=1469598103934665603ull;json events=json::array(),admissions=json::array();
  unsigned upper=0,lit=0,goals=0,peak_balls=0;
  auto step=[&](unsigned a){
   const bool formula=s.minigame_active()&&!s.minigame2_active();const unsigned mini=s.minigame_completions();
   if(formula && !formula_tracking){formula_tracking=true;formula_entry_score=s.score();formula_entry_prizes=s.pending_extra_ball_prizes();}
   s.set_launch(a&8);s.set_flippers(a&1,a&2);if(a&4)s.press_plunger();
   if(a&16){s.nudge(1,false);++nudges;}if(a&64){s.nudge(-1,false);++nudges;}if(a&32){s.nudge(0,true);++nudges;}
   require(s.step()||s.game_over(),s.status());++tick;
   if(s.ball_count()>peak_balls)peak_balls=s.ball_count();
   const auto&raw=s.shared_raw_state().fields;
   const auto word=[&](unsigned o){return unsigned(raw[o])|(unsigned(raw[o+1])<<8);};
   if(upper!=s.upper_captures() || lit!=word(0x394) || goals!=word(0x1f2)){
    upper=s.upper_captures();lit=word(0x394);goals=word(0x1f2);
    admissions.push_back({{"tick",tick},{"upper_captures",upper},{"field_394",lit},{"field_1f2",goals},{"ball",s.ball_number()},{"mode",s.table_mode()},{"selected",s.selected_mode()}});
   }
   if(formula && s.minigame_completions()>mini){
    require(s.score()==formula_entry_score+120000000 && s.pending_extra_ball_prizes()==formula_entry_prizes+1,"Formula1 completion was not a Retail win");
    ++formula_wins;formula_tracking=false;
   }
   unsigned current=mask(s);if(!formula_wins)current&=~8u;
   mix(hash,a);mix(hash,s.score());mix(hash,s.ball_count());mix(hash,current);
   for(unsigned i=0;i<s.ball_count();++i)for(auto b:s.ball(i).bytes){hash^=b;hash*=1099511628211ull;}
   for(const auto&q:s.take_audio_requests()){mix(hash,q.service);mix(hash,q.bank);mix(hash,q.order);mix(hash,q.descriptor);}
   if(current!=previous){events.push_back({{"tick",tick},{"completed_mask",current},{"ball",s.ball_number()},{"score",s.score()}});previous=current;}
  };
  for(const auto&r:fixture.at("actions_rle"))for(unsigned i=0;i<r.at("ticks").get<unsigned>();++i)step(r.at("actions"));
  if(tick!=fixture.at("ticks") || previous!=fixture.at("completed_mask"))throw std::runtime_error("Marathon checkpoint: tick="+std::to_string(tick)+" mask="+std::to_string(previous)+" formula="+std::to_string(formula_wins)+" minis="+std::to_string(s.minigame_completions()));
  if(argc==7)require(observed>0,"Contact observer was not executed");
  require(formula_wins && s.offroad_stats().awards>=6 && s.offroad_stats().ends && s.chicken_stats().completions,"Three distinct actual mode wins missing");
  const unsigned required=fixture.at("completed_mask");
  if(required&2){
   const auto&m=s.monster_stats();
   require(m.completions && m.score>=125000000,"Monster completion/125M missing");
   for(auto hits:m.hits)require(hits,"Monster distinct target missing");
  }
  if(required&4)require(s.rally_stats().completions && s.rally_stats().correct>=6,"Rally six-turn completion missing");
  const json speed={{"starts",s.mode6_starts()},{"checkpoint_mode",s.table_mode()},{"checkpoint_goals",s.speed_letters()},{"peak_balls",peak_balls}};
  if(fixture.contains("expected_speed"))require(speed==fixture.at("expected_speed"),"SPEED composition contract changed");
  speed_runs.push_back(speed);
  const auto checkpoint_score=s.score();while(!s.game_over()&&tick<200000)step(8);
  require(s.game_over()&&!s.ball_count()&&s.bonus_completions()>=3&&!s.tilted(),"Marathon finite lifecycle failed");
  const auto final_score=s.score();const auto fields=s.shared_raw_state().fields;const auto ball=s.ball().bytes;
  for(unsigned i=0;i<64;++i){s.set_flippers(true,true);s.press_plunger();s.nudge(1,false);require(!s.step()&&s.score()==final_score&&s.shared_raw_state().fields==fields&&s.ball().bytes==ball,"Marathon GameOver changed");}
  cases.push_back({{"events",events},{"completed_mask",previous},{"formula_wins",formula_wins},{"checkpoint_score",checkpoint_score},{"final_tick",tick},{"final_score",final_score},{"bonuses",s.bonus_completions()},{"nudges",nudges},{"state_audio_hash",hash}});
  admission_runs.push_back(admissions);
  s.reset();require(!s.game_over()&&!s.score()&&!s.minigame_completions()&&!s.offroad_stats().starts&&!s.chicken_stats().starts&&!s.monster_stats().starts&&!s.rally_stats().starts,"Marathon newgame leaked progress");
 }
 require(cases[0]==cases[1],"Fresh marathon runs are nondeterministic");
 require(admission_runs[0]==admission_runs[1],"Fresh upper-capture admissions are nondeterministic");
 require(speed_runs[0]==speed_runs[1],"Fresh SPEED composition is nondeterministic");
 if(fixture.contains("expected_admissions"))require(admission_runs[0]==fixture.at("expected_admissions"),"Upper-capture admission golden changed");
 if(fixture.contains("expected"))require(cases[0]==fixture.at("expected"),"Marathon golden result changed");
 std::ofstream output(argv[5]);output<<json({{"scope","Two independent fresh legal-input finite games. Required completion mask verified, including actual Formula1 Retail win and six-paid-change Offroad/end. Completion counters, not started-record flags; no ball/state injection. Bounded native composition, not Original whole-trajectory equivalence."},{"cases",cases},{"admissions",admission_runs[0]},{"speed",speed_runs[0]}}).dump(2)<<'\n';require(bool(output),"Cannot write marathon report");
 std::cout<<"PASS repeated finite mode marathon mask="<<cases[0]["completed_mask"]<<" "<<cases[0]["final_tick"]<<" ticks / "<<cases[0]["final_score"]<<" points\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
