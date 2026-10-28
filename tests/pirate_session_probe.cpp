#include "physics/pirate_session.h"
#include "core/sha256.h"
#include "core/pirate_input_replay.h"
#include "core/pirate_shot_replay.h"
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
int main(int argc,char**argv) {
  if(argc<4)return 2;
  unsigned step=0;
  try {
    bool full=false,inputs=false,lamps=false,full_state=false;std::string replay_path,shot_path;
    for(int i=5;i<argc;++i){const std::string arg=argv[i];if(arg=="--full")full=true;else if(arg=="--full-state-trace")full_state=true;else if(arg=="--flippers")inputs=true;else if(arg=="--lamps")lamps=true;else if(arg=="--replay"&&i+1<argc)replay_path=argv[++i];else if(arg=="--diagnostic-shots"&&i+1<argc)shot_path=argv[++i];else return 2;}
    slam::PirateSession session(argv[1],argv[2],full?slam::PirateTickMode::Full:slam::PirateTickMode::PhysicsOnly);
    session.enable_lamps(lamps);
    const unsigned count=argc>=5?std::stoul(argv[4]):1000;
    slam::PirateInputReplay replay;slam::PirateShotReplay shots;bool left=false,right=false;
    const auto profile=slam::load_table_profile(slam::default_table_profiles(),"pirate");
    if(!shot_path.empty())shots.load(shot_path);
    if(!replay_path.empty())replay.load(replay_path);
    const auto input=[&](unsigned tick){if(!shot_path.empty())shots.apply(session,profile);if(!replay_path.empty()){replay.apply(session,tick,left,right);return;}if(tick==200)session.launch();if(inputs&&(tick==400||tick==440||tick==600||tick==640))session.flippers(tick>=400&&tick<440,tick>=600&&tick<640);};
    nlohmann::json states=nlohmann::json::array({session.ball()});
    nlohmann::json nudge=nlohmann::json::array(),magnasaver=nlohmann::json::array();
    nlohmann::json timing=nlohmann::json::array();
    nlohmann::json dmd=nlohmann::json::array();
    nlohmann::json lifecycle=nlohmann::json::array(),highscores=nlohmann::json::array(),lamp_states=nlohmann::json::array(),rules=nlohmann::json::array(),video=nlohmann::json::array(),ball_pool=nlohmann::json::array();
    for(;step<count;++step){input(step);session.step();if(full_state||!shot_path.empty()){magnasaver.push_back(session.magnasaver_state());rules.push_back(slam::sha256(session.rule_state()));video.push_back(slam::sha256(session.video_state()));ball_pool.push_back(slam::sha256(session.ball_pool_state()));}states.push_back(session.ball());timing.push_back(session.timing_state());nudge.push_back(session.nudge_state());if(full){const auto pixels=session.dmd_pixels();dmd.push_back(slam::sha256({pixels.begin(),pixels.end()}));lifecycle.push_back(session.lifecycle_state());const auto records=session.highscores();highscores.push_back(slam::sha256({records.begin(),records.end()}));lamp_states.push_back(slam::sha256(session.lamp_states()));}}
    const auto first=states;
    session.reset();replay.reset();shots.reset();left=right=false;
    for(unsigned tick=0;tick<count;++tick){input(tick);session.step();if(nlohmann::json(session.nudge_state())!=nudge.at(tick))throw std::runtime_error("Non-deterministic nudge reset");if((full_state||!shot_path.empty())&&nlohmann::json(session.magnasaver_state())!=magnasaver.at(tick))throw std::runtime_error("Non-deterministic Magnasaver reset");if((full_state||!shot_path.empty())&&slam::sha256(session.rule_state())!=rules.at(tick))throw std::runtime_error("Non-deterministic rule reset");if((full_state||!shot_path.empty())&&slam::sha256(session.video_state())!=video.at(tick))throw std::runtime_error("Non-deterministic video reset");if((full_state||!shot_path.empty())&&slam::sha256(session.ball_pool_state())!=ball_pool.at(tick))throw std::runtime_error("Non-deterministic ball pool reset");if(nlohmann::json(session.ball())!=first.at(tick+1)||nlohmann::json(session.timing_state())!=timing.at(tick))throw std::runtime_error("Non-deterministic reset");if(full){const auto pixels=session.dmd_pixels();if(slam::sha256({pixels.begin(),pixels.end()})!=dmd.at(tick))throw std::runtime_error("Non-deterministic DMD reset");const auto records=session.highscores();if(nlohmann::json(session.lifecycle_state())!=lifecycle.at(tick)||slam::sha256({records.begin(),records.end()})!=highscores.at(tick))throw std::runtime_error("Non-deterministic lifecycle reset");if(slam::sha256(session.lamp_states())!=lamp_states.at(tick))throw std::runtime_error("Non-deterministic lamp reset");}}
    nlohmann::json trace={{"tick_count",count},{"phase",session.phase()},{"states",states},{"timing",timing},{"nudge",nudge},{"dmd_sha256",dmd},{"lifecycle",lifecycle},{"highscore_sha256",highscores},{"lamp_sha256",lamp_states},{"rule_sha256",rules},{"video_sha256",video},{"ball_pool_sha256",ball_pool}};
    if(full_state||!shot_path.empty())trace["magnasaver_state"]=magnasaver;
    std::ofstream out(argv[3]);out<<trace.dump()<<'\n';
    if(!out)throw std::runtime_error("Cannot write native Pirate trace");
    std::cout<<count<<(shot_path.empty()?" native input steps, reset/replay exact\n":" native diagnostic steps, reset/replay exact\n");
  }catch(const std::exception&e){std::cerr<<"Step "<<step<<": "<<e.what()<<'\n';return 1;}
}
