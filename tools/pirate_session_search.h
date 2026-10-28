// Tool-only exact reachable-state branching. Verification must replay keys
// independently from reset; no runtime UI or gameplay injection interface.
#pragma once
#include "physics/pirate_session.h"
namespace slam {
struct PirateSessionSearch {
  struct State {PirateStepLift machine;bool left,right,lamps;std::uint64_t ticks;};
  static State capture(const PirateSession& s) {
    if(s.audio_enabled_||s.machine_.call_observer||s.machine_.instruction_observer||s.machine_.external_service)
      throw std::runtime_error("Search requires silent unobserved state");
    return {s.machine_,s.left_,s.right_,s.lamps_enabled_,s.ticks_};
  }
  static void restore(PirateSession& s,const State& state) {
    if(s.audio_enabled_)throw std::runtime_error("Cannot restore an audio session");
    s.machine_=state.machine;s.left_=state.left;s.right_=state.right;
    s.ticks_=state.ticks;s.lamps_enabled_=state.lamps;s.audio_requests_.clear();
  }
  static unsigned read(PirateSession& s,unsigned address,unsigned n=4){return s.machine_.rd(address,n);}
};
}
