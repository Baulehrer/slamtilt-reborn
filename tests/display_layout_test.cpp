#ifdef NDEBUG
#undef NDEBUG
#endif
#include "renderer/display_layout.h"
#include <cassert>
#include <cmath>
int main() {
 for(auto wh:{SDL_Point{1366,768},{1920,1080},{1920,1200},{3840,2160},{320,240}})
  for(int pos=0;pos<4;++pos)for(float zoom:{.75f,1.f,2.f})for(float size:{.5f,1.f,2.f}) {
   auto l=slam::display_layout(wh.x,wh.y,pos,size,zoom,0,80,350);
   assert(l.viewport.w>0 && l.viewport.h>0);
   assert(std::abs(l.table.w/l.table.h-.8f)<.0001f);
   assert(std::abs(l.dmd.w/l.dmd.h-4.8f)<.0001f);
   assert(l.dmd.x>=0 && l.dmd.y>=0);
   assert(l.dmd.x+l.dmd.w<=wh.x+1 && l.dmd.y+l.dmd.h<=wh.y+1);
   if(pos==0)assert(l.dmd.y+l.dmd.h<=l.viewport.y);
  }
 // At 100% Crop, a wide laptop display clips vertically. Follow the ball
 // without exposing space outside the table, including 2x output pixels.
 for(auto wh:{SDL_Point{1366,768},{1920,1080},{2732,1536},{3840,2160}})
  for(int pos=0;pos<4;++pos)for(float zoom:{1.f,2.f})
   for(auto ball:{SDL_FPoint{8,8},SDL_FPoint{160,200},SDL_FPoint{312,392}}) {
    const auto l=slam::display_layout(wh.x,wh.y,pos,1.f,zoom,2,ball.x,ball.y);
    const auto &v=l.viewport; const auto &t=l.table;
    const float x=t.x+ball.x*t.w/320, y=t.y+ball.y*t.h/400;
    assert(x>=v.x-.01f && x<=v.x+v.w+.01f);
    assert(y>=v.y-.01f && y<=v.y+v.h+.01f);
    assert(t.x<=v.x+.01f && t.x+t.w>=v.x+v.w-.01f);
    assert(t.y<=v.y+.01f && t.y+t.h>=v.y+v.h-.01f);
   }
 // Retail whole-table presentation uses600 original rows, preserving geometry.
 for(auto wh:{SDL_Point{1366,768},SDL_Point{1920,1080},SDL_Point{320,240}})
  for(int pos=0;pos<4;++pos) {
   const auto fit=slam::display_layout(wh.x,wh.y,pos,1,1,0,160,300,600);
   assert(std::abs(fit.table.w/fit.table.h-320.f/600)<.0001f);
   assert(fit.table.x>=fit.viewport.x-.01f && fit.table.y>=fit.viewport.y-.01f);
   assert(fit.table.x+fit.table.w<=fit.viewport.x+fit.viewport.w+.01f);
   assert(fit.table.y+fit.table.h<=fit.viewport.y+fit.viewport.h+.01f);
   for(float zoom:{1.f,2.f})for(float ball_y:{8.f,300.f,592.f}) {
    const auto crop=slam::display_layout(wh.x,wh.y,pos,1,zoom,2,160,ball_y,600);
    const float y=crop.table.y+ball_y*crop.table.h/600;
    assert(y>=crop.viewport.y-.01f && y<=crop.viewport.y+crop.viewport.h+.01f);
    assert(crop.table.y<=crop.viewport.y+.01f && crop.table.y+crop.table.h>=crop.viewport.y+crop.viewport.h-.01f);
   }
  }
 // Cabinet output reserves no on-playfield DMD area and fits all600 rows.
 SDL_SetEnvironmentVariable(SDL_GetEnvironment(),"SLAMTILT_CABINET_DMD","1",true);
 for(int pos=0;pos<4;++pos){
  const auto l=slam::display_layout(2160,3840,pos,1,1,0,160,300,600);
  assert(l.viewport.x==0 && l.viewport.y==0);
  assert(l.viewport.w==2160 && l.viewport.h==3840);
  assert(std::abs(l.table.w/l.table.h-320.f/600)<.0001f);
  assert(l.table.y>=0 && l.table.y+l.table.h<=3840.01f);
 }
 SDL_UnsetEnvironmentVariable(SDL_GetEnvironment(),"SLAMTILT_CABINET_DMD");
}
