#pragma once
#include <SDL3/SDL.h>

namespace slam {
inline bool apply_window_mode(SDL_Window* window, bool fullscreen,
                              const SDL_DisplayMode* mode, int width, int height) {
#ifdef __EMSCRIPTEN__
  // The persistent HTML document owns fullscreen, independently of SDL windows.
  (void)fullscreen;
  (void)mode;
  return SDL_SetWindowSize(window, width, height);
#else
  return SDL_SetWindowFullscreen(window, false) &&
         SDL_SetWindowFullscreenMode(window, mode) &&
         SDL_SetWindowSize(window, width, height) &&
         (!fullscreen || SDL_SetWindowFullscreen(window, true));
#endif
}
}
