#include "presentation.h"
#include <array>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#ifdef SLAM_GPU_EFFECTS
#include "bloom_shader.h"
#include "presentation_shader.h"
#endif
namespace slam {
SDL_Renderer* create_presentation_renderer(SDL_Window* window,bool prefer_gpu) {
#ifdef SLAM_GPU_EFFECTS
  const char* driver=SDL_GetCurrentVideoDriver();
  if(prefer_gpu && (!driver || SDL_strcmp(driver,"dummy"))) {
    SDL_PropertiesID props=SDL_CreateProperties();
    SDL_SetStringProperty(props,SDL_PROP_RENDERER_CREATE_NAME_STRING,"gpu");
    SDL_SetPointerProperty(props,SDL_PROP_RENDERER_CREATE_WINDOW_POINTER,window);
    SDL_SetBooleanProperty(props,SDL_PROP_RENDERER_CREATE_GPU_SHADERS_SPIRV_BOOLEAN,true);
    SDL_SetBooleanProperty(props,SDL_PROP_RENDERER_CREATE_GPU_SHADERS_DXIL_BOOLEAN,false);
    SDL_SetBooleanProperty(props,SDL_PROP_RENDERER_CREATE_GPU_SHADERS_MSL_BOOLEAN,false);
    auto* result=SDL_CreateRendererWithProperties(props);SDL_DestroyProperties(props);
    if(result)return result;
    SDL_Log("GPU presentation unavailable: %s; using classic SDL renderer",SDL_GetError());
  }
#else
  (void)prefer_gpu;
#endif
  return SDL_CreateRenderer(window,nullptr);
}
struct Presentation::Impl {
  SDL_Renderer* renderer;
  std::string message="Classic SDL renderer (GPU shaders unavailable)";
#ifdef SLAM_GPU_EFFECTS
  SDL_GPUDevice* device=nullptr;
  SDL_GPUShader* bloom_shader=nullptr;SDL_GPUShader* final_shader=nullptr;
  SDL_GPUSampler* sampler=nullptr;SDL_GPURenderState* bloom_state=nullptr;
  struct Layer {SDL_Texture* a=nullptr;SDL_Texture* b=nullptr;SDL_GPURenderState* composite=nullptr;int w=0,h=0;};
  std::array<Layer,2> layers;
  bool ready=false;
  void clear(Layer& l){if(l.composite)SDL_DestroyGPURenderState(l.composite);SDL_DestroyTexture(l.a);SDL_DestroyTexture(l.b);l=Layer{};}
  bool resize(Layer& l,int w,int h) {
    if(l.w==w && l.h==h)return true;
    clear(l);
    l.a=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_TARGET,w,h);
    l.b=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_RGBA32,SDL_TEXTUREACCESS_TARGET,w,h);
    if(!l.a || !l.b)return false;
    for(auto* t:{l.a,l.b}){SDL_SetTextureBlendMode(t,SDL_BLENDMODE_NONE);SDL_SetTextureScaleMode(t,SDL_SCALEMODE_LINEAR);}
    SDL_GPUTextureSamplerBinding binding{};
    binding.texture=static_cast<SDL_GPUTexture*>(SDL_GetPointerProperty(SDL_GetTextureProperties(l.a),SDL_PROP_TEXTURE_GPU_TEXTURE_POINTER,nullptr));
    binding.sampler=sampler;
    if(!binding.texture)return false;
    SDL_GPURenderStateCreateInfo info{};info.fragment_shader=final_shader;info.num_sampler_bindings=1;info.sampler_bindings=&binding;
    l.composite=SDL_CreateGPURenderState(renderer,&info);
    if(!l.composite)return false;
    l.w=w;l.h=h;return true;
  }
#endif
  explicit Impl(SDL_Renderer* r):renderer(r) {
#ifdef SLAM_GPU_EFFECTS
    device=SDL_GetGPURendererDevice(r);if(!device)return;
    const auto shader=[&](const unsigned char* code,std::size_t size,unsigned samplers) {
      SDL_GPUShaderCreateInfo info{};info.code=code;info.code_size=size;info.entrypoint="main";
      info.format=SDL_GPU_SHADERFORMAT_SPIRV;info.stage=SDL_GPU_SHADERSTAGE_FRAGMENT;info.num_samplers=samplers;info.num_uniform_buffers=1;
      return SDL_CreateGPUShader(device,&info);
    };
    bloom_shader=shader(bloom_shader_data,sizeof(bloom_shader_data),1);
    final_shader=shader(presentation_shader_data,sizeof(presentation_shader_data),2);
    SDL_GPUSamplerCreateInfo sampling{};sampling.min_filter=SDL_GPU_FILTER_LINEAR;sampling.mag_filter=SDL_GPU_FILTER_LINEAR;
    sampling.mipmap_mode=SDL_GPU_SAMPLERMIPMAPMODE_NEAREST;sampling.address_mode_u=sampling.address_mode_v=sampling.address_mode_w=SDL_GPU_SAMPLERADDRESSMODE_CLAMP_TO_EDGE;
    sampler=SDL_CreateGPUSampler(device,&sampling);
    if(bloom_shader){SDL_GPURenderStateCreateInfo info{};info.fragment_shader=bloom_shader;bloom_state=SDL_CreateGPURenderState(r,&info);}
    ready=bloom_shader && final_shader && sampler && bloom_state;
    message=ready?"GPU effects: Vulkan / SPIR-V":std::string("GPU shaders unavailable: ")+SDL_GetError();
#endif
  }
  ~Impl(){
#ifdef SLAM_GPU_EFFECTS
    for(auto& l:layers)clear(l);
    if(bloom_state)SDL_DestroyGPURenderState(bloom_state);
    if(sampler)SDL_ReleaseGPUSampler(device,sampler);
    if(bloom_shader)SDL_ReleaseGPUShader(device,bloom_shader);
    if(final_shader)SDL_ReleaseGPUShader(device,final_shader);
#endif
  }
};
Presentation::Presentation(SDL_Renderer* r):impl_(std::make_unique<Impl>(r)){}
Presentation::~Presentation()=default;
bool Presentation::available() const {
#ifdef SLAM_GPU_EFFECTS
  return impl_->ready;
#else
  return false;
#endif
}
const std::string& Presentation::status() const{return impl_->message;}
void Presentation::draw(SDL_Texture* source,const SDL_FRect& dest,const VisualSettings& settings,bool dmd) {
  auto* r=impl_->renderer;
#ifdef SLAM_GPU_EFFECTS
  if(available() && settings.preset!=0 && settings.strength>0) {
    auto& l=impl_->layers[dmd];
    const int divisor=settings.quality==0?8:settings.quality==1?4:2;
    const float bloom=dmd?settings.dmd_glow:settings.bloom;
    const int w=bloom>0?std::clamp(int(std::ceil(dest.w/divisor)),8,2048):8;
    const int h=bloom>0?std::clamp(int(std::ceil(dest.h/divisor)),8,2048):8;
    if(!impl_->resize(l,w,h)) {
      impl_->message=std::string("GPU effects disabled: ")+SDL_GetError();impl_->ready=false;
      SDL_Log("%s",impl_->message.c_str());SDL_RenderTexture(r,source,nullptr,&dest);return;
    }
    SDL_Texture* previous=SDL_GetRenderTarget(r);
    const bool clipped=SDL_RenderClipEnabled(r);SDL_Rect clip{};SDL_GetRenderClipRect(r,&clip);
    float scale_x=1,scale_y=1;SDL_GetRenderScale(r,&scale_x,&scale_y);
    SDL_SetRenderScale(r,1,1);SDL_SetRenderClipRect(r,nullptr);
    const auto pass=[&](SDL_Texture* target,SDL_Texture* input,std::array<float,4> uniform) {
      if(!SDL_SetRenderTarget(r,target) || !SDL_SetGPURenderStateFragmentUniforms(impl_->bloom_state,0,uniform.data(),sizeof(uniform)) ||
        !SDL_SetGPURenderState(r,impl_->bloom_state) || !SDL_RenderTexture(r,input,nullptr,nullptr) || !SDL_SetGPURenderState(r,nullptr))
        throw std::runtime_error(SDL_GetError());
    };
    if(bloom>0){pass(l.a,source,{0,0,0,1});pass(l.b,l.a,{1.f/w,0,0,0});pass(l.a,l.b,{0,1.f/h,0,0});}
    SDL_SetRenderTarget(r,previous);SDL_SetRenderScale(r,scale_x,scale_y);SDL_SetRenderClipRect(r,clipped?&clip:nullptr);
    float sw=1,sh=1;SDL_GetTextureSize(source,&sw,&sh);
    const std::array<float,16> uniforms{{1/sw,1/sh,dest.w,dest.h,settings.strength,bloom,dmd?0:settings.sharpness,dmd?1:settings.saturation,
      dmd?0:settings.scanlines,dmd?0:settings.mask,dmd?0:settings.curvature,dmd?0:settings.chromatic,
      !dmd && settings.preset==1?1.f:0.f,dmd?1.f:0.f,0,0}};
    if(!SDL_SetGPURenderStateFragmentUniforms(l.composite,0,uniforms.data(),sizeof(uniforms)) || !SDL_SetGPURenderState(r,l.composite) ||
       !SDL_RenderTexture(r,source,nullptr,&dest) || !SDL_SetGPURenderState(r,nullptr))throw std::runtime_error(SDL_GetError());
    return;
  }
#else
  (void)settings;(void)dmd;
#endif
  if(!SDL_RenderTexture(r,source,nullptr,&dest))throw std::runtime_error(SDL_GetError());
}
}
