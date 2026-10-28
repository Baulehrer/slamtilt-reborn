#include "ui_skin.h"
#define STB_TRUETYPE_IMPLEMENTATION
#include "stb_truetype.h"
#include "inter_regular.h"
#include "inter_semibold.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>
#include <vector>
namespace slam {
struct UiSkin::Impl {
  std::array<std::array<stbtt_bakedchar,95>,2> glyphs{};
  std::array<std::vector<unsigned char>,2> pixels;
  SDL_Renderer* renderer=nullptr;
  std::array<SDL_Texture*,2> textures{};
  Impl() {
    const unsigned char* fonts[]={inter_regular,inter_semibold};
    for(unsigned f=0;f<2;++f) {
      std::vector<unsigned char> alpha(512*512);
      if(stbtt_BakeFontBitmap(fonts[f],0,40,alpha.data(),512,512,32,95,glyphs[f].data())<=0)
        throw std::runtime_error("Menu font atlas overflow");
      pixels[f].resize(512*512*4);
      for(unsigned i=0;i<alpha.size();++i) {
        pixels[f][i*4]=pixels[f][i*4+1]=pixels[f][i*4+2]=255;pixels[f][i*4+3]=alpha[i];
      }
    }
  }
  ~Impl(){for(auto* t:textures)SDL_DestroyTexture(t);}
};
UiSkin::UiSkin():impl_(std::make_unique<Impl>()){}
UiSkin::~UiSkin()=default;
float UiSkin::width(const std::string& text,float size,bool bold) const {
  float w=0;for(unsigned char c:text)if(c>=32 && c<127)w+=impl_->glyphs[bold][c-32].xadvance;
  return w*size/40;
}
void UiSkin::text(SDL_Renderer* r,const std::string& text,float x,float y,float size,SDL_Color color,bool bold) {
  if(impl_->renderer!=r) {
    for(auto*& t:impl_->textures){SDL_DestroyTexture(t);t=nullptr;}
    impl_->renderer=r;
  }
  auto*& t=impl_->textures[bold];
  if(!t) {
    t=SDL_CreateTexture(r,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_STATIC,512,512);
    if(!t || !SDL_UpdateTexture(t,nullptr,impl_->pixels[bold].data(),512*4))throw std::runtime_error(SDL_GetError());
    SDL_SetTextureBlendMode(t,SDL_BLENDMODE_BLEND);SDL_SetTextureScaleMode(t,SDL_SCALEMODE_LINEAR);
  }
  SDL_SetTextureColorMod(t,color.r,color.g,color.b);SDL_SetTextureAlphaMod(t,color.a);
  float pen=0,baseline=0;const float scale=size/40;
  for(unsigned char c:text) {
    if(c<32 || c>=127)continue;
    stbtt_aligned_quad q{};stbtt_GetBakedQuad(impl_->glyphs[bold].data(),512,512,c-32,&pen,&baseline,&q,1);
    const SDL_FRect source{q.s0*512,q.t0*512,(q.s1-q.s0)*512,(q.t1-q.t0)*512};
    const SDL_FRect dest{x+q.x0*scale,y+size+q.y0*scale,(q.x1-q.x0)*scale,(q.y1-q.y0)*scale};
    SDL_RenderTexture(r,t,&source,&dest);
  }
}
void UiSkin::round_rect(SDL_Renderer* r,SDL_FRect box,float radius,SDL_Color c) {
  radius=std::min(radius,std::min(box.w,box.h)/2);
  std::vector<SDL_Vertex> vertices;std::vector<int> indices;
  const SDL_FColor color{c.r/255.f,c.g/255.f,c.b/255.f,c.a/255.f};
  vertices.push_back({{box.x+box.w/2,box.y+box.h/2},color,{0,0}});
  for(int corner=0;corner<4;++corner)for(int i=0;i<=8;++i) {
    const float angle=(corner*90+i*90.f/8)*3.14159265f/180;
    float cx=box.x+(corner==0 || corner==3?box.w-radius:radius);
    float cy=box.y+(corner<2?box.h-radius:radius);
    vertices.push_back({{cx+std::cos(angle)*radius,cy+std::sin(angle)*radius},color,{0,0}});
  }
  for(unsigned i=1;i<vertices.size();++i){indices.push_back(0);indices.push_back(i);indices.push_back(i+1<vertices.size()?i+1:1);}
  SDL_RenderGeometry(r,nullptr,vertices.data(),int(vertices.size()),indices.data(),int(indices.size()));
}
}
