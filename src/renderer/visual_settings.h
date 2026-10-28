#pragma once
#include <algorithm>
#include <cmath>
#include <nlohmann/json.hpp>
namespace slam {
struct VisualSettings {
  int preset=2, quality=1; // Original / Clean HD / Soft Glow / Neon / CRT / CRT Deluxe / Custom
  float strength=1, bloom=.16f, sharpness=.12f, saturation=1.04f;
  float scanlines=0, mask=0, curvature=0, chromatic=0, dmd_glow=.2f;
};
inline const char* visual_preset_name(int p) {
  static const char* names[]={"Original","Clean HD","Soft Glow","Neon Arcade","CRT Classic","CRT Deluxe","Custom"};
  return names[std::clamp(p,0,6)];
}
inline void visual_preset(VisualSettings& v,int p) {
  const int quality=v.quality;const float dmd=v.dmd_glow;
  v=VisualSettings{};v.preset=p;v.quality=quality;v.dmd_glow=dmd;
  switch(p) {
  case 0:v.bloom=0;v.sharpness=0;v.saturation=1;break;
  case 1:v.bloom=0;v.sharpness=.35f;v.saturation=1;break;
  case 2:break;
  case 3:v.bloom=.65f;v.sharpness=.18f;v.saturation=1.28f;break;
  case 4:v.bloom=.25f;v.sharpness=.08f;v.saturation=1.1f;v.scanlines=.32f;v.mask=.20f;break;
  case 5:v.bloom=.45f;v.sharpness=.12f;v.saturation=1.15f;v.scanlines=.38f;v.mask=.28f;v.curvature=.12f;v.chromatic=.65f;break;
  default:v.preset=6;break;
  }
}
inline bool valid_visual(const VisualSettings& v) {
  const auto within=[](float x,float hi){return std::isfinite(x)&&x>=0&&x<=hi;};
  return v.preset>=0&&v.preset<=6&&v.quality>=0&&v.quality<=2&&within(v.strength,1)&&within(v.bloom,1)&&within(v.sharpness,1)&&within(v.saturation,2)&&within(v.scanlines,1)&&within(v.mask,1)&&within(v.curvature,.3f)&&within(v.chromatic,2)&&within(v.dmd_glow,1);
}
inline void to_json(nlohmann::json& j,const VisualSettings& v) {
  j={{"preset",v.preset},{"quality",v.quality},{"strength",v.strength},{"bloom",v.bloom},{"sharpness",v.sharpness},{"saturation",v.saturation},{"scanlines",v.scanlines},{"mask",v.mask},{"curvature",v.curvature},{"chromatic",v.chromatic},{"dmd_glow",v.dmd_glow}};
}
inline void from_json(const nlohmann::json& j,VisualSettings& v) {
  v.preset=j.value("preset",2);v.quality=j.value("quality",1);
  v.strength=j.value("strength",1.f);v.bloom=j.value("bloom",.16f);v.sharpness=j.value("sharpness",.12f);v.saturation=j.value("saturation",1.04f);
  v.scanlines=j.value("scanlines",0.f);v.mask=j.value("mask",0.f);v.curvature=j.value("curvature",0.f);v.chromatic=j.value("chromatic",0.f);v.dmd_glow=j.value("dmd_glow",.2f);
}
}
