// Native-only discovery, from reset then actual F1 continuations. No waypoints.
#include "physics/pirate_session.h"
#include "core/pirate_input_replay.h"
#include "core/sha256.h"
#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <set>
#include <nlohmann/json.hpp>
using nlohmann::json;
struct Policy {std::string seed;int a,b,period,offset,nudge;bool tilt;};
static json read_json(const std::filesystem::path& path) {
  std::ifstream in(path);if(!in)throw std::runtime_error("Missing sweep seed");
  json result;in>>result;return result;
}
static std::vector<std::uint8_t> read_bytes(const std::filesystem::path& path) {
  std::ifstream in(path,std::ios::binary);if(!in)throw std::runtime_error("Missing sweep input");
  return {std::istreambuf_iterator<char>(in),{}};
}
int main(int argc,char**argv) {try {
  if(argc<4||argc>6)return 2;
  const std::filesystem::path output=argv[3];std::filesystem::create_directories(output);
  const double budget=argc>4?std::stod(argv[4]):60.;
  const unsigned limit=argc>5?std::stoul(argv[5]):24;
  slam::PirateSession session(argv[1],argv[2],slam::PirateTickMode::Full);
  session.enable_lamps(true);
  std::vector<Policy> policies={
    {"",0,0,1,0,0,false},{"",0,2,40,0,0,false},
    {"",1,0,16,0,0,false},{"",1,2,60,0,0,false},
    {"",0,3,90,0,0,false},{"",0,3,120,17,240,false},
    {"",1,2,25,53,360,false},{"",0,2,40,0,0,true}};
  for(const std::string seed:{"natural-crocodile-game","natural-plank-two-ropes","natural-plank-nudge","legal-cave-game"})
    for(int variant=0;variant<4;++variant)
      policies.push_back({seed,variant&1,(variant+2)&3,40+variant*43,17*variant,
                         variant==1?240:0,variant==3});
  const auto begin=std::chrono::steady_clock::now();
  const auto elapsed=[&]{return std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();};
  json rows=json::array();unsigned total=0,failures=0;
  for(unsigned index=0;index<policies.size()&&index<limit&&elapsed()<budget;++index) {
    const auto p=policies[index];session.reset();bool left=false,right=false;
    slam::PirateInputReplay replay;json seed_events=json::array();unsigned seed_steps=0;std::size_t seed_cursor=0;
    std::string seed_sha;
    if(!p.seed.empty()) {
      const auto path=std::filesystem::path("analysis/traces")/("pirate-"+p.seed+".json");
      const auto f=read_json(path);
      if(!f.at("diagnostic_shots").empty())throw std::runtime_error("Sweep seed has waypoints");
      seed_steps=f.at("tick_count");seed_events=f.at("inputs");seed_sha=slam::sha256(read_bytes(path));
      replay.load(path);
    }
    json events=json::array(),marks=json::array();std::set<unsigned> phases;
    unsigned steps=0,game_overs=0,new_games=0,initials=0,max_balls=0,nudges=0,specials=0;
    unsigned last_phase=99,over_tick=0,letters=0;
    bool frozen=false,finished=false,admitted=false;
    std::array<std::uint8_t,100> frozen_ball{};
    std::array<std::uint8_t,50> frozen_scores{};
    std::string error;
    const auto mark=[&](const std::string& label) {
      marks.push_back({{"tick",session.ticks()},{"label",label},{"phase",session.phase()},
        {"ball_count",session.ball_count()},{"ball_number",session.ball_number()}});
    };
    const auto edge=[&](const std::string& action,bool down=true) {
      events.push_back({{"tick",session.ticks()},{"action",action},{"down",down}});
    };
    try {
      for(unsigned tick=0;tick<36000;++tick) {
        if(tick%256==0&&elapsed()>=budget)break;
        if(tick<seed_steps) {
          while(seed_cursor<seed_events.size()&&seed_events[seed_cursor].at("tick")==tick) {
            const auto& e=seed_events[seed_cursor++];
            events.push_back(e);
            if(e.at("action")=="new_game") {
              if(!frozen||session.ticks()-over_tick<64||session.highscores()!=frozen_scores)
                throw std::runtime_error("Seed restart outside retained GameOver");
              ++new_games;frozen=false;admitted=false;letters=0;
            }
          }
          replay.apply(session,tick,left,right);
        }else {
          if(session.game_over()) {
            if(!frozen||session.ball()!=frozen_ball||session.highscores()!=frozen_scores)
              throw std::runtime_error("GameOver ball/highscores changed");
            if(tick-over_tick>=64) {
              edge("new_game");
              if(!session.new_game()||session.highscores()!=frozen_scores)
                throw std::runtime_error("F1 restart/highscore mismatch");
              left=right=false;frozen=false;admitted=false;letters=0;++new_games;mark("new_game");
            }
          }
          if(session.initials_active()) {
            if(!admitted){admitted=true;++initials;letters=0;mark("initials_admitted");}
            if(tick%4==0&&letters<4) {
              constexpr unsigned scans[]={0x1e,0x30,0x2e,0x1c};
              events.push_back({{"tick",tick},{"action","key"},{"down",true},{"scan",scans[letters]}});
              if(!session.initials_key(scans[letters++]))throw std::runtime_error("Initials admission lost");
            }
          }else {
            if(session.phase()==1&&tick%200==0){edge("enter");session.launch();edge("enter",false);}
            const unsigned local=tick-seed_steps;
            // Release controls after40seconds so policies cannot intentionally
            // sustain a never-ending game. A remaining horizon is not a crash.
            const int mask=local<8000&&!session.game_over()?(((local+unsigned(p.offset))/unsigned(p.period))%2?p.b:p.a):0;
            const bool nl=mask&1,nr=mask&2;
            if(nl!=left)edge("left",nl);
            if(nr!=right)edge("right",nr);
            session.flippers(nl,nr);left=nl;right=nr;
            if(session.magnasaver_state()[0]&&tick%17==0&&!session.game_over()) {
              edge("special_left");session.special_left();edge("special_left",false);++specials;
            }
            const bool sparse=p.nudge&&local<8000&&local>0&&local%unsigned(p.nudge)==0;
            const bool triplet=p.tilt&&(local==400||local==404||local==408);
            if((sparse||triplet)&&!session.game_over()) {
              const int direction=triplet?(local==400?-1:local==404?1:0):int((local/unsigned(p.nudge))%3)-1;
              const std::string action=direction<0?"nudge_left":direction>0?"nudge_right":"nudge_up";
              edge(action);session.nudge(direction);edge(action,false);++nudges;
            }
          }
        }
        session.step();++steps;++total;const auto phase=session.phase();
        phases.insert(phase);max_balls=std::max(max_balls,session.ball_count());
        if(phase!=last_phase){mark("phase_change");last_phase=phase;}
        if(session.game_over()&&!frozen) {
          frozen=true;over_tick=unsigned(session.ticks());frozen_ball=session.ball();frozen_scores=session.highscores();
          ++game_overs;mark("game_over");
        }
        if(new_games>=2&&session.phase()==2&&session.ball()[0x58]==2) {finished=true;mark("third_game_free_ball");break;}
      }
    }catch(const std::exception& e){error=e.what();++failures;mark("native_failure");}
    const auto path=output/("policy-"+std::to_string(index)+".json");
    json policy={{"index",index},{"seed",p.seed},{"seed_sha256",seed_sha},{"seed_steps",seed_steps},
      {"a",p.a},{"b",p.b},{"period",p.period},{"offset",p.offset},{"nudge_period",p.nudge},{"tilt_triplet",p.tilt}};
    json row={{"policy",policy},{"tick_count",steps},{"status",!error.empty()?"NATIVE_ERROR":finished?"TWO_FINITE_GAMES":"BOUNDED_HORIZON"},
      {"error",error},{"game_overs",game_overs},{"new_games",new_games},{"initials_admissions",initials},
      {"max_balls",max_balls},{"phases",phases},{"tail_nudges",nudges},{"tail_specials",specials},{"milestones",marks}};
    std::ofstream(path)<<json({{"schema",1},{"inputs",events},{"diagnostic_shots",json::array()},
      {"tick_count",steps},{"policy",policy},{"result",row},
      {"scope","Native discovery only: actual Enter/Shift/LeftCtrl/Nudge/admitted initials/F1; no state or waypoint writes. Original/reset/SDL proof pending."}}).dump(2)<<'\n';
    row["candidate"]=path.string();rows.push_back(row);
    std::cout<<index<<' '<<row["status"]<<" steps="<<steps<<" games="<<game_overs<<" restarts="<<new_games<<" error="<<error<<'\n'<<std::flush;
  }
  json result={{"schema",1},{"status",failures?"NATIVE_FAILURES":"BOUNDED_NO_NATIVE_ERRORS"},
    {"policies",rows},{"total_steps",total},{"wall_seconds",elapsed()},{"failures",failures},
    {"scope","Bounded native-only legal-input discovery; horizon is not failure. Repeated games use F1 and retain original clock/RNG/highscores. No diagnostic or game-state injection; not an original-equivalence claim."}};
  std::ofstream(output/"sweep.json")<<result.dump(2)<<'\n';
  return failures?1:0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
