#include "renderer/presentation.h"
#include <SDL3/SDL.h>
#include <nlohmann/json.hpp>
#include <array>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <vector>
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
std::vector<unsigned char> capture(SDL_Renderer* r) {
  SDL_Surface* raw=SDL_RenderReadPixels(r,nullptr);require(raw,"Cannot read presentation output");
  SDL_Surface* s=SDL_ConvertSurface(raw,SDL_PIXELFORMAT_RGBA32);SDL_DestroySurface(raw);require(s,"Cannot convert screenshot");
  std::vector<unsigned char> out;
  for(int y=0;y<s->h;++y){auto* p=static_cast<unsigned char*>(s->pixels)+y*s->pitch;out.insert(out.end(),p,p+s->w*4);}
  SDL_DestroySurface(s);return out;
}
std::uint64_t hash(const std::vector<unsigned char>& bytes) {
  std::uint64_t h=1469598103934665603ull;for(auto c:bytes){h^=c;h*=1099511628211ull;}return h;
}
int main(int argc,char** argv) {
  try {
    const bool required=argc>1 && std::string(argv[1])=="--require-gpu";
    require(SDL_Init(SDL_INIT_VIDEO),SDL_GetError());
    SDL_Window* w=SDL_CreateWindow("Presentation verification",640,480,0);require(w,SDL_GetError());
    SDL_Renderer* r=slam::create_presentation_renderer(w,true);require(r,SDL_GetError());
    {
      slam::Presentation fx(r);require(!required || fx.available(),fx.status().c_str());
      std::vector<unsigned char> pixels(96*80*4,255);
      for(int y=0;y<80;++y)for(int x=0;x<96;++x) {
        auto* p=&pixels[(y*96+x)*4];const bool stripe=x>38 && x<45;
        p[0]=stripe?255:(x/4+y/4)%2?74:12;p[1]=stripe?190:28;p[2]=stripe?80:50;
      }
      auto* t=SDL_CreateTexture(r,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STATIC,96,80);require(t,SDL_GetError());
      require(SDL_UpdateTexture(t,nullptr,pixels.data(),96*4),SDL_GetError());
      SDL_SetTextureBlendMode(t,SDL_BLENDMODE_NONE);SDL_SetTextureScaleMode(t,SDL_SCALEMODE_NEAREST);
      const SDL_FRect dest{32,24,576,432};
      auto begin=[&]{SDL_SetRenderTarget(r,nullptr);SDL_SetRenderDrawColor(r,0,0,0,255);require(SDL_RenderClear(r),SDL_GetError());};
      begin();require(SDL_RenderTexture(r,t,nullptr,&dest),SDL_GetError());const auto original=capture(r);SDL_RenderPresent(r);
      nlohmann::json cases=nlohmann::json::array();std::set<std::uint64_t> hashes;
      for(int preset=0;preset<6;++preset)for(int quality=0;quality<3;++quality) {
        slam::VisualSettings v;slam::visual_preset(v,preset);v.quality=quality;
        begin();fx.draw(t,dest,v);const auto frame=capture(r);const auto h=hash(frame);
        require(preset!=0 || frame==original,"Original preset changed pixels");
        require(fx.available() || frame==original,"Fallback changed pixels");
        if(fx.available() && preset!=0)require(frame!=original,"GPU effect produced unchanged pixels");
        // A repeated frame must have identical pixels and must preserve the clip state.
        require(SDL_RenderPresent(r),SDL_GetError());
        begin();SDL_Rect clip{0,0,640,480};SDL_SetRenderClipRect(r,&clip);fx.draw(t,dest,v);
        SDL_Rect after{};SDL_GetRenderClipRect(r,&after);
        require(SDL_RenderClipEnabled(r) && after.w==640 && after.h==480,"Effect lost render clipping");
        SDL_SetRenderClipRect(r,nullptr);require(capture(r)==frame,"Shader frame is nondeterministic");SDL_RenderPresent(r);
        if(quality==1)hashes.insert(h);
        cases.push_back({{"preset",slam::visual_preset_name(preset)},{"quality",quality},{"hash",h}});
      }
      if(fx.available())require(hashes.size()==6,"Presets are not visually distinct");
      // DMD ignores table-only geometry and CRT parameters.
      slam::VisualSettings a,b;a.preset=b.preset=6;b.curvature=.3f;b.chromatic=2;b.mask=1;b.scanlines=1;b.saturation=2;b.sharpness=1;
      begin();fx.draw(t,dest,a,true);const auto dmd=capture(r);SDL_RenderPresent(r);
      begin();fx.draw(t,dest,b,true);require(capture(r)==dmd,"Table CRT effects leaked into DMD");SDL_RenderPresent(r);
      // Identity at zero strength and actual render-target reallocation.
      b.strength=0;begin();fx.draw(t,dest,b);require(capture(r)==original,"Zero strength is not identity");SDL_RenderPresent(r);
      for(const auto& size:std::array<SDL_FRect,3>{{{0,0,320,240},{0,0,1024,768},{0,0,640,480}}}) {
        begin();fx.draw(t,size,a);require(SDL_RenderPresent(r),SDL_GetError());
      }
      if(argc>2){std::ofstream report(argv[2]);report<<nlohmann::json({{"gpu",fx.available()},{"status",fx.status()},{"cases",cases},{"original_exact",true},{"dmd_isolated",true},{"zero_strength_exact",true},{"resize_pass",true}}).dump(2)<<'\n';require(bool(report),"Cannot write shader report");}
      std::cout<<"PASS 18 preset/quality combinations, repeat/identity/DMD/resize; "<<fx.status()<<'\n';
      SDL_DestroyTexture(t);
    }
    SDL_DestroyRenderer(r);SDL_DestroyWindow(w);SDL_Quit();
  }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
