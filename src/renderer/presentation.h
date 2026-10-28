#pragma once
#include <SDL3/SDL.h>
#include "visual_settings.h"
#include <memory>
#include <string>
namespace slam {
class Presentation {
public:
  explicit Presentation(SDL_Renderer*);~Presentation();
  Presentation(const Presentation&)=delete;Presentation& operator=(const Presentation&)=delete;
  bool available() const;const std::string& status() const;
  // Source and destination coordinates remain entirely presentation-only.
  void draw(SDL_Texture*,const SDL_FRect&,const VisualSettings&,bool dmd=false);
private:
  struct Impl;std::unique_ptr<Impl> impl_;
};
SDL_Renderer* create_presentation_renderer(SDL_Window*,bool prefer_gpu);
}
