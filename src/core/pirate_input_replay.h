#pragma once
#include "physics/pirate_session.h"
#include <fstream>
#include <nlohmann/json.hpp>
#include <vector>

namespace slam {
// Only recorded legal input actions; never writes physics or rule state.
class PirateInputReplay {
public:
  void load(const std::filesystem::path& path) {
    std::ifstream input(path);if(!input)throw std::runtime_error("Missing Pirate input replay");
    nlohmann::json data;input>>data;
    events_=data.at("inputs").get<std::vector<nlohmann::json>>();
    std::uint64_t previous=0;
    for(const auto& event:events_){
      if(!event.at("tick").is_number_unsigned()||event.at("tick").get<std::uint64_t>()<previous)
        throw std::runtime_error("Pirate replay ticks must be ordered unsigned values");
      previous=event.at("tick").get<std::uint64_t>();
      const auto action=event.at("action").get<std::string>();
      if(action!="enter"&&action!="left"&&action!="right"&&action!="special_left"&&action!="key"&&action!="new_game"&&action!="nudge_left"&&action!="nudge_right"&&action!="nudge_up")
        throw std::runtime_error("Unsupported Pirate replay action");
      (void)event.at("down").get<bool>();
      if(action=="key"&&(!event.at("scan").is_number_unsigned()||event.at("scan").get<unsigned>()>255))
        throw std::runtime_error("Invalid Original key scan code");
    }
    reset();
  }
  void reset(){next_=0;}
  void apply(PirateSession& session,std::uint64_t tick,bool& left,bool& right) {
    while(next_<events_.size()&&events_[next_].at("tick").get<std::uint64_t>()==tick){
      const auto& event=events_[next_++];
      const auto action=event.at("action").get<std::string>();const bool down=event.at("down").get<bool>();
      if(action=="left"||action=="right"){
        (action=="left"?left:right)=down;session.flippers(left,right);
      }else if(down){
        if(action=="enter")session.launch();
        else if(action=="special_left")session.special_left();
        else if(action=="nudge_left"||action=="nudge_right"||action=="nudge_up")
          session.nudge(action=="nudge_left"?-1:action=="nudge_right"?1:0);
        else if(action=="key"){if(!session.initials_key(event.at("scan").get<unsigned>()))throw std::runtime_error("Initials input outside Original admission");}
        else if(action=="new_game"){
          if(!session.new_game())throw std::runtime_error("New game outside Original F1 admission");
          left=right=false;
        }
      }
    }
    if(next_<events_.size()&&events_[next_].at("tick").get<std::uint64_t>()<tick)
      throw std::runtime_error("Pirate replay skipped an input");
  }
private:
  std::vector<nlohmann::json> events_;
  std::size_t next_=0;
};
}
