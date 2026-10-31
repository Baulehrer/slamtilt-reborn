#pragma once
#include <SDL3/SDL.h>
#include <stdexcept>
#include <string>
namespace slam {
// Opt-in cabinet output. No extra window or layout changes in normal builds.
inline bool cabinet_dmd_enabled() {
  const char* value=SDL_getenv("SLAMTILT_CABINET_DMD");
  return value && value[0]=='1';
}
class CabinetDmd {
  SDL_Window* window_=nullptr;
  SDL_Renderer* renderer_=nullptr;
  SDL_Texture* texture_=nullptr;
public:
  CabinetDmd()=default;
  CabinetDmd(const CabinetDmd&)=delete;
  CabinetDmd& operator=(const CabinetDmd&)=delete;
  ~CabinetDmd(){ close(); }
  void close(){
    if(texture_)SDL_DestroyTexture(texture_);
    if(renderer_)SDL_DestroyRenderer(renderer_);
    if(window_)SDL_DestroyWindow(window_);
    texture_=nullptr;renderer_=nullptr;window_=nullptr;
  }
  void draw(const void* rgba){
    if(!cabinet_dmd_enabled())return;
    if(!window_){
      window_=SDL_CreateWindow("Slamtilt Cabinet DMD",1920,400,
        SDL_WINDOW_BORDERLESS|SDL_WINDOW_NOT_FOCUSABLE);
      if(window_)renderer_=SDL_CreateRenderer(window_,nullptr);
      if(renderer_)texture_=SDL_CreateTexture(renderer_,SDL_PIXELFORMAT_RGBA32,
        SDL_TEXTUREACCESS_STREAMING,96,20);
      if(!texture_){const auto error=std::string(SDL_GetError());close();
        throw std::runtime_error("Cabinet DMD: "+error);}
      SDL_SetRenderVSync(renderer_,0);
      SDL_SetTextureScaleMode(texture_,SDL_SCALEMODE_NEAREST);
      SDL_SetRenderLogicalPresentation(renderer_,96,20,SDL_LOGICAL_PRESENTATION_LETTERBOX);
    }
    if(!SDL_UpdateTexture(texture_,nullptr,rgba,96*4) ||
       !SDL_SetRenderDrawColor(renderer_,0,0,0,255) || !SDL_RenderClear(renderer_) ||
       !SDL_RenderTexture(renderer_,texture_,nullptr,nullptr) || !SDL_RenderPresent(renderer_))
      throw std::runtime_error(SDL_GetError());
  }
};
}
