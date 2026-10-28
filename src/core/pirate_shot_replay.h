#pragma once
#include "physics/pirate_session.h"
#include <fstream>
#include <nlohmann/json.hpp>

namespace slam {
// Separate from legal keyboard replay: explicitly labeled diagnostic ball
// waypoints exercise the actual DAT collision map and original engine tick.
class PirateShotReplay {
public:
  void load(const std::filesystem::path& path) {
    std::ifstream input(path);if(!input)throw std::runtime_error("Missing diagnostic Pirate shots");
    nlohmann::json data;input>>data;shots_=data.at("diagnostic_shots");
    if(!shots_.is_array())throw std::runtime_error("Invalid diagnostic Pirate shots");
    std::uint64_t previous=0;bool first=true;
    for(const auto& shot:shots_){
      if(!shot.at("tick").is_number_unsigned())throw std::runtime_error("Invalid diagnostic shot tick");
      const auto tick=shot.at("tick").get<std::uint64_t>();
      if(!first&&tick<=previous)throw std::runtime_error("Diagnostic shot ticks must increase");
      first=false;previous=tick;
      for(const auto key:{"layer","x","y"})if(!shot.at(key).is_number_integer()||shot.at(key)<0)
        throw std::runtime_error("Invalid diagnostic shot coordinate");
      if(shot.at("layer")>=3||shot.at("x")>=320||shot.at("y")>=600)
        throw std::runtime_error("Diagnostic shot outside table");
      if(shot.contains("ball")&&(!shot.at("ball").is_number_integer()||shot.at("ball")<0||shot.at("ball")>=8))
        throw std::runtime_error("Invalid diagnostic ball index");
    }
    reset();
  }
  void reset(){next_=0;}
  void apply(PirateSession& session,const TableProfile& profile) {
    if(next_>=shots_.size())return;
    const auto& shot=shots_[next_];const auto tick=shot.at("tick").get<std::uint64_t>();
    if(tick<session.ticks())throw std::runtime_error("Skipped diagnostic Pirate shot");
    if(tick==session.ticks()){
      session.diagnostic_waypoint(profile,shot.at("layer").get<unsigned>(),shot.at("x").get<int>(),shot.at("y").get<int>(),shot.value("ball",0u));
      ++next_;
    }
  }
private:
  nlohmann::json shots_=nlohmann::json::array();
  std::size_t next_=0;
};
}
