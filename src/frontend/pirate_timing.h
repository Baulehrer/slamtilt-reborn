#pragma once
#include <SDL3/SDL.h>
#include <nlohmann/json.hpp>
#include <array>
#include <fstream>
#include <string>
namespace slam {
struct PirateTiming {
  std::uint64_t start=SDL_GetTicksNS(),uploads=0,ball_reads=0;
  nlohmann::json frames=nlohmann::json::array(),inputs=nlohmann::json::array();
  void input(unsigned side,std::uint64_t queued,unsigned pose){
    inputs.push_back({{"side",side},{"queued_ns",queued},{"handled_ns",SDL_GetTicksNS()},{"before",pose}});
  }
  void observe(const std::array<std::uint16_t,3>& poses,std::uint64_t tick){
    for(auto& row:inputs)if(!row.contains("observed_ns")&&poses[row["side"].get<unsigned>()]!=row["before"].get<unsigned>()){
      row["observed_ns"]=SDL_GetTicksNS();row["tick"]=tick;
    }
  }
  void write(const std::string& path,const std::string& error,SDL_Window* window,SDL_Renderer* renderer){
    std::ofstream out(path);out<<nlohmann::json({{"frame_columns",{"elapsed_ns","frame_work_ns","simulation_audio_wall_ns","render_wall_ns","present_wall_ns","ticks","steps","advancing","audio_queue_bytes","accepted_elapsed_ns","raw_elapsed_ns"}},{"frames",frames},{"inputs",inputs},{"uploads",uploads},{"ball_file_reads",ball_reads},
      {"video",SDL_GetCurrentVideoDriver()?SDL_GetCurrentVideoDriver():""},{"renderer",SDL_GetRendererName(renderer)},
      {"fullscreen",bool(SDL_GetWindowFlags(window)&SDL_WINDOW_FULLSCREEN)},{"error",error},
      {"scope","Instrumented wall time around simulation/audio/render/present and queued-SDL-input to native pose change; not CPU counters, physical input-to-photon or GPU execution timing"}}).dump()<<'\n';
    if(!out)throw std::runtime_error("Cannot write Pirate timing");
  }
};
}
