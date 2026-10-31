#pragma once
#include <SDL3/SDL.h>
#include "renderer/cabinet_dmd.h"
#include <algorithm>
#include <cmath>
namespace slam {
struct DisplayLayout { SDL_FRect viewport{},table{},dmd{}; };
inline DisplayLayout display_layout(int w,int h,int position,float size,float zoom,int aspect,float ballx=160,float bally=200,float table_height=400) {
  DisplayLayout l;const float gap=8;
  l.viewport={0,0,float(w),float(h)};
  const float dw=std::min(float(w)*.95f,std::min(float(w)*.9f, float(h)*.8f)*size);
  const float dh=dw*20/96;
  l.dmd={(w-dw)/2,gap,dw,dh};
  if(!cabinet_dmd_enabled() && position==0) { l.viewport.y=dh+2*gap;l.viewport.h-=dh+2*gap; }
  if(!cabinet_dmd_enabled() && (position==1 || position==2)) {
    const float width=std::min(float(w)*.45f,std::min(float(w)*.32f,480.f)*size);
    l.dmd={position==1?gap:float(w)-width-gap,(h-width*20/96)/2,width,width*20/96};
    l.viewport.x=position==1?width+2*gap:0;l.viewport.w-=width+2*gap;
  }
  if(position==3) {l.dmd.w=std::min(float(w)*.95f,std::min(float(w)*.5f,480.f)*size);l.dmd.h=l.dmd.w*20/96;l.dmd.x=(w-l.dmd.w)/2;}
  const auto &v=l.viewport;
  float scale=aspect==2?std::max(v.w/320,v.h/table_height):std::min(v.w/320,v.h/table_height);
  scale*=zoom;
  float tw=aspect==1?v.w*zoom:320*scale,th=aspect==1?v.h*zoom:table_height*scale;
  float x=v.x+(v.w-tw)/2,y=v.y+(v.h-th)/2;
  // Crop can exceed the viewport even at 100% zoom; keep the ball visible.
  if(zoom>1 || aspect==2) {
    if(tw>v.w)x=std::clamp(v.x+v.w/2-ballx*tw/320,v.x+v.w-tw,v.x);
    if(th>v.h)y=std::clamp(v.y+v.h/2-bally*th/table_height,v.y+v.h-th,v.y);
  }
  l.table={x,y,tw,th};return l;
}
}
