#pragma once
#include "input/gamepad_input.h"
namespace slam {
inline void draw_gamepad_pull(SDL_Renderer *renderer, const GamepadInput &input,
                              int height) {
  const float pull = input.pull();
  if (pull < .03f)
    return;
  SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
  SDL_SetRenderDrawColor(renderer, 8, 16, 25, 225);
  const SDL_FRect panel{10, float(height - 38), 160, 30};
  SDL_RenderFillRect(renderer, &panel);
  SDL_SetRenderDrawColor(renderer, 180, 220, 215, 255);
  SDL_RenderDebugText(renderer, 16, float(height - 35), "RT: PULL / RELEASE");
  SDL_SetRenderDrawColor(renderer, 35, 60, 68, 255);
  const SDL_FRect track{16, float(height - 20), 145, 7};
  SDL_RenderFillRect(renderer, &track);
  SDL_SetRenderDrawColor(renderer, pull > .55f ? 80 : 235,
                         pull > .55f ? 225 : 180, 145, 255);
  const SDL_FRect fill{track.x, track.y, track.w * pull, track.h};
  SDL_RenderFillRect(renderer, &fill);
}
} // namespace slam
