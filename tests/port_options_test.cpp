#ifdef NDEBUG
#undef NDEBUG
#endif
#include "frontend/port_options.h"
#include <cassert>
#include <cstdlib>
#include <filesystem>
#include <fstream>
static void key(PortOptions& o,SDL_Keycode code) {
  SDL_Event e{};e.type=SDL_EVENT_KEY_DOWN;e.key.key=code;assert(o.handle(e));
}
static void choose(PortOptions& o,PortOptions::Option id,SDL_Keycode action=SDLK_RIGHT) {o.select_option(id);key(o,action);}
int main() {
  const auto root=std::filesystem::absolute("build/options-test-data");
  std::filesystem::remove_all(root);setenv("XDG_DATA_HOME",root.c_str(),1);
  setenv("SDL_VIDEODRIVER","dummy",1);assert(SDL_Init(SDL_INIT_VIDEO));
  {
    PortOptions o;o.load(true);assert(o.settings.fullscreen && o.settings.visual.preset==2);
    assert(o.settings.key(PortAction::SpecialLeft)==SDL_SCANCODE_LCTRL);
    key(o,SDLK_ESCAPE);choose(o,PortOptions::Fullscreen);assert(!o.settings.fullscreen);
    key(o,SDLK_BACKSPACE);assert(o.settings.fullscreen && !o.open);
    key(o,SDLK_ESCAPE);choose(o,PortOptions::Zoom);
    o.settings.fullscreen_mode=1;o.settings.overlay_x=.8f;o.settings.overlay_y=.3f;
    o.settings.music_volume=.4f;o.settings.sfx_volume=.7f;o.settings.color=3;
    o.settings.custom_r=12;o.settings.custom_g=34;o.settings.custom_b=56;
    choose(o,PortOptions::Preset);assert(o.settings.visual.preset==3);
    choose(o,PortOptions::Bloom);assert(o.settings.visual.preset==6);
    choose(o,PortOptions::Apply,SDLK_RETURN);assert(!o.open && o.error.empty());
    PortOptions loaded;loaded.load(true);
    assert(loaded.settings.zoom==o.settings.zoom && loaded.settings.fullscreen_mode==1);
    assert(loaded.settings.overlay_x==.8f && loaded.settings.overlay_y==.3f);
    assert(loaded.settings.music_volume==.4f && loaded.settings.sfx_volume==.7f);
    assert(loaded.settings.color==3 && loaded.settings.custom_r==12 && loaded.settings.custom_g==34 && loaded.settings.custom_b==56);
    assert(loaded.settings.visual.preset==6 && loaded.settings.visual.bloom==o.settings.visual.bloom);
    const auto saved=loaded.settings;
    key(loaded,SDLK_ESCAPE);loaded.settings.zoom=1.8f;loaded.settings.visual.bloom=0;
    choose(loaded,PortOptions::Cancel,SDLK_RETURN);
    assert(!loaded.open && loaded.settings.zoom==saved.zoom && loaded.settings.visual.bloom==saved.visual.bloom);
    PortOptions after_cancel;after_cancel.load(true);assert(after_cancel.settings.zoom==saved.zoom);
    key(loaded,SDLK_ESCAPE);choose(loaded,PortOptions::Reset,SDLK_RETURN);
    assert(loaded.open && loaded.settings.zoom==1 && loaded.settings.visual.preset==2 && loaded.settings.custom_r==255);
    key(loaded,SDLK_BACKSPACE);assert(loaded.settings.custom_r==12 && loaded.settings.zoom==saved.zoom);
    key(loaded,SDLK_ESCAPE);loaded.settings.window_width=1366;loaded.settings.window_height=768;
    loaded.settings.dmd_position=3;loaded.settings.aspect=2;loaded.settings.keys[0]=SDL_SCANCODE_A;
    choose(loaded,PortOptions::Apply,SDLK_RETURN);
    PortOptions persisted;persisted.load(true);
    assert(persisted.settings.window_width==1366 && persisted.settings.window_height==768 && persisted.settings.dmd_position==3 && persisted.settings.aspect==2);
    assert(persisted.settings.key(PortAction::LeftFlipper)==SDL_SCANCODE_A);
    // Older version-one files retain all settings and receive only missing visual defaults.
    const auto path=std::filesystem::path(SDL_GetPrefPath("SlamTiltNative","SlamTilt"))/"options.json";
    nlohmann::json j;std::ifstream(path)>>j;j.erase("visual");std::ofstream(path)<<j;
    PortOptions old;old.load(true);assert(old.settings.custom_r==12 && old.settings.visual.preset==2);
    // Six-key version-one profiles preserve every custom binding and setting.
    auto legacy=j;while(legacy["keys"].size()>6)legacy["keys"].erase(legacy["keys"].end()-1);
    std::ofstream(path)<<legacy;old.load(true);
    assert(old.settings.custom_r==12 && old.settings.zoom==saved.zoom);
    for(std::size_t i=0;i<6;++i)assert(old.settings.keys[i]==legacy["keys"][i]);
    assert(old.settings.key(PortAction::SpecialLeft)==SDL_SCANCODE_LCTRL);
    // A legacy Left Ctrl binding belongs to its existing action. Give only
    // Left special a free fallback, then persist and reload all seven keys.
    legacy["keys"][0]=SDL_SCANCODE_LCTRL;legacy["keys"][1]=SDL_SCANCODE_A;
    std::ofstream(path)<<legacy;old.load(true);
    for(std::size_t i=0;i<6;++i)assert(old.settings.keys[i]==legacy["keys"][i]);
    assert(old.settings.key(PortAction::SpecialLeft)==SDL_SCANCODE_B);
    key(old,SDLK_ESCAPE);choose(old,PortOptions::Apply,SDLK_RETURN);
    PortOptions migrated;migrated.load(true);assert(migrated.settings.keys==old.settings.keys);
    assert(migrated.settings.custom_r==12 && migrated.settings.zoom==saved.zoom);
    auto seven=j;seven["keys"].erase(seven["keys"].end()-1);seven["keys"][0]=SDL_SCANCODE_RCTRL;
    std::ofstream(path)<<seven;PortOptions seven_loaded;seven_loaded.load(true);
    for(std::size_t i=0;i<7;++i)assert(seven_loaded.settings.keys[i]==seven["keys"][i]);
    assert(seven_loaded.settings.key(PortAction::SpecialRight)!=SDL_SCANCODE_RCTRL);
    j["visual"]={{"bloom",3}};std::ofstream(path)<<j;old.load(true);assert(old.settings.custom_r==255);
    std::ofstream(path)<<"{broken";loaded.load(true);assert(loaded.settings.zoom==1);
    PortOptions remap;remap.load(false);key(remap,SDLK_ESCAPE);
    choose(remap,PortOptions::LeftFlipper,SDLK_RETURN);
    SDL_Event binding{};binding.type=SDL_EVENT_KEY_DOWN;binding.key.scancode=SDL_SCANCODE_A;
    assert(remap.handle(binding));assert(remap.settings.key(PortAction::LeftFlipper)==SDL_SCANCODE_A);
    key(remap,SDLK_RETURN);binding.key.scancode=SDL_SCANCODE_P;assert(remap.handle(binding));
    assert(!remap.error.empty() && remap.settings.key(PortAction::LeftFlipper)==SDL_SCANCODE_A);
    key(remap,SDLK_ESCAPE);assert(remap.open);choose(remap,PortOptions::RightFlipper,SDLK_RETURN);
    binding.key.scancode=SDL_SCANCODE_A;assert(remap.handle(binding));assert(!remap.error.empty());
    key(remap,SDLK_ESCAPE);key(remap,SDLK_BACKSPACE);assert(remap.settings.key(PortAction::LeftFlipper)==SDL_SCANCODE_LSHIFT);
    key(remap,SDLK_ESCAPE);remap.select_category(4);
    for(int i=0;i<6;++i)key(remap,SDLK_DOWN);
    assert(remap.selected_option()==PortOptions::SpecialLeft);
    key(remap,SDLK_RETURN);binding.key.scancode=SDL_SCANCODE_Z;assert(remap.handle(binding));
    assert(remap.settings.key(PortAction::SpecialLeft)==SDL_SCANCODE_Z);
    key(remap,SDLK_RETURN);binding.key.scancode=SDL_SCANCODE_RSHIFT;assert(remap.handle(binding));
    assert(!remap.error.empty() && remap.settings.key(PortAction::SpecialLeft)==SDL_SCANCODE_Z);
    key(remap,SDLK_ESCAPE);choose(remap,PortOptions::Cancel,SDLK_RETURN);
    assert(remap.settings.key(PortAction::SpecialLeft)==SDL_SCANCODE_LCTRL);
    PortOptions space;space.full_controls=false;space.space_specials=true;key(space,SDLK_ESCAPE);space.select_category(4);
    for(int i=0;i<4;++i)key(space,SDLK_DOWN);assert(space.selected_option()==PortOptions::SpecialRight);
    key(space,SDLK_RETURN);binding.key.scancode=SDL_SCANCODE_Z;assert(space.handle(binding));assert(space.settings.key(PortAction::SpecialRight)==SDL_SCANCODE_Z);
    // Every category and footer remains reachable; menu draws at small/HiDPI sizes.
    SDL_Window* window=nullptr;SDL_Renderer* renderer=nullptr;
    assert(SDL_CreateWindowAndRenderer("Menu acceptance",1366,768,0,&window,&renderer));
    {
      PortOptions ui;ui.load(false);key(ui,SDLK_ESCAPE);
      for(int c=0;c<5;++c){ui.select_category(c);ui.draw(renderer,1366,768);assert(SDL_RenderPresent(renderer));}
      ui.select_category(0);key(ui,SDLK_TAB);assert(ui.selected_option()==PortOptions::Preset);
      key(ui,SDLK_RIGHT);assert(ui.settings.visual.preset==3);
      ui.draw(renderer,320,240);ui.draw(renderer,2732,1536);
      // Mouse category click and slider drag, using the documented logical layout.
      ui.select_category(0);ui.draw(renderer,1366,768);
      SDL_Event click{};click.type=SDL_EVENT_MOUSE_BUTTON_DOWN;click.button.button=SDL_BUTTON_LEFT;
      // Resolve UI scale/panel geometry at this test resolution.
      const float scale=std::min(1366/1120.f,768/800.f),x=(1366/scale-1020)/2,y=(768/scale-704)/2;
      click.button.x=(x+35)*scale;click.button.y=(y+110+54+20)*scale;assert(ui.handle(click));
      assert(ui.selected_option()==PortOptions::Preset);ui.select_option(PortOptions::Bloom);ui.draw(renderer,1366,768);
      const float row_x=x+196+24,row_w=1020-196-48;
      // Bloom is fourth row in Effects, all rows fit only partly; selected row remains visible.
      click.button.x=(row_x+row_w-14)*scale;click.button.y=(y+110+3*52+35)*scale;
      assert(ui.handle(click));assert(ui.settings.visual.bloom>.95f && ui.settings.visual.preset==6);
      SDL_Event up{};up.type=SDL_EVENT_MOUSE_BUTTON_UP;assert(ui.handle(up));
      key(ui,SDLK_ESCAPE);assert(ui.settings.visual.preset==2);
    }
    SDL_DestroyRenderer(renderer);SDL_DestroyWindow(window);
  }
  {
    PortOptions session;session.main_menu_available=true;session.load(false);
    SDL_Event pending;while(SDL_PollEvent(&pending)){}
    key(session,SDLK_F10);bool quit=false;while(SDL_PollEvent(&pending))quit|=pending.type==SDL_EVENT_QUIT;assert(quit);
    key(session,SDLK_ESCAPE);choose(session,PortOptions::Zoom);assert(session.settings.zoom>1.f);
    choose(session,PortOptions::MainMenu,SDLK_RETURN);assert(!session.open && session.settings.zoom==1.f);
    quit=false;while(SDL_PollEvent(&pending))quit|=pending.type==SDL_EVENT_QUIT;assert(quit);
    PortOptions standalone;standalone.main_menu_available=false;SDL_Event f10{};f10.type=SDL_EVENT_KEY_DOWN;f10.key.key=SDLK_F10;assert(!standalone.handle(f10));
  }
  {
    PortOptions options;options.load(false);assert(options.settings.modern_menu&&!options.settings.reduced_motion);
    key(options,SDLK_ESCAPE);choose(options,PortOptions::MenuStyle);choose(options,PortOptions::ReducedMotion);assert(!options.settings.modern_menu&&options.settings.reduced_motion);
    key(options,SDLK_BACKSPACE);assert(options.settings.modern_menu&&!options.settings.reduced_motion);
    PortOptions persisted;persisted.load(true);key(persisted,SDLK_ESCAPE);persisted.settings.modern_menu=false;persisted.settings.reduced_motion=true;choose(persisted,PortOptions::Apply,SDLK_RETURN);
    PortOptions loaded;loaded.load(true);assert(!loaded.settings.modern_menu&&loaded.settings.reduced_motion);
  }
  SDL_Quit();std::filesystem::remove_all(root);
}
