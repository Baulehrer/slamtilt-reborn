#pragma once
#include <SDL3/SDL.h>
#include <memory>
#include <string>
namespace slam {
class UiSkin {
public:
  UiSkin(); ~UiSkin();
  UiSkin(const UiSkin&)=delete; UiSkin& operator=(const UiSkin&)=delete;
  void text(SDL_Renderer*,const std::string&,float x,float y,float size,SDL_Color,bool bold=false);
  float width(const std::string&,float size,bool bold=false) const;
  static void round_rect(SDL_Renderer*,SDL_FRect,float radius,SDL_Color);
private:
  struct Impl; std::unique_ptr<Impl> impl_;
};
}
