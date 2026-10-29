#include "frontend/port_options.h"
#include <atomic>
#include <chrono>
#include <filesystem>
#include <iostream>
#include <thread>
#include <vector>
int slam_gamepad_view_main(int, char **);
int slam_gamepad_slice_main(int, char **);
int slam_gamepad_menu_main(int, char **);
namespace { std::atomic<bool> frontend_ready{false}; }
namespace slam {
void gamepad_frontend_probe_ready() { frontend_ready = true; }
}
int main(int argc, char **argv) {
#ifndef __linux__
  std::cerr << "This fixture requires Linux XDG preference isolation.\n";
  return 77;
#else
  if (argc != 6) {
    std::cerr << "TABLE DATA PREPARED INITIAL TRACE\n";
    return 2;
  }
  const std::string table = argv[1];
  const std::filesystem::path data = argv[2], prepared = argv[3],
                              initial = argv[4], trace = argv[5];
  SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");
  SDL_SetHint(SDL_HINT_GAMECONTROLLER_IGNORE_DEVICES_EXCEPT, "0xf00d/0x0042");
  if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMEPAD))
    return 3;
  SDL_VirtualJoystickDesc desc{};
  SDL_INIT_INTERFACE(&desc);
  desc.type = SDL_JOYSTICK_TYPE_GAMEPAD;
  desc.vendor_id = 0xf00d;
  desc.product_id = 0x0042;
  desc.naxes = SDL_GAMEPAD_AXIS_COUNT;
  desc.nbuttons = SDL_GAMEPAD_BUTTON_COUNT;
  desc.axis_mask = (1u << SDL_GAMEPAD_AXIS_COUNT) - 1;
  desc.button_mask = (1u << SDL_GAMEPAD_BUTTON_COUNT) - 1;
  desc.name = "Reborn frontend acceptance pad";
  const auto id = SDL_AttachVirtualJoystick(&desc);
  auto *joystick = SDL_OpenJoystick(id);
  if (!id || !joystick)
    return 4;
  SDL_SetJoystickVirtualAxis(joystick, SDL_GAMEPAD_AXIS_LEFT_TRIGGER,
                             SDL_JOYSTICK_AXIS_MIN);
  SDL_SetJoystickVirtualAxis(joystick, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER,
                             SDL_JOYSTICK_AXIS_MIN);
  SDL_UpdateJoysticks();
  PortOptions options;
  options.load(true);
  SDL_Event e{};
  e.type = SDL_EVENT_KEY_DOWN;
  e.key.key = SDLK_ESCAPE;
  options.handle(e);
  options.settings.fullscreen = false;
  options.select_option(PortOptions::Apply);
  e.key.key = SDLK_RETURN;
  options.handle(e);
  SDL_setenv_unsafe("SLAM_FRONTEND_SESSION", "1", 1);
  struct Entry {
    unsigned time;
    Uint32 type;
    int control;
    int value;
  };
  std::vector<Entry> events;
  auto button = [&](unsigned at, SDL_GamepadButton b, unsigned duration = 100) {
    events.push_back({at, SDL_EVENT_GAMEPAD_BUTTON_DOWN, b, 1});
    events.push_back({at + duration, SDL_EVENT_GAMEPAD_BUTTON_UP, b, 0});
  };
  if (table == "menu") {
    for (unsigned i = 0; i < 4; ++i)
      button(300 + i * 180, SDL_GAMEPAD_BUTTON_DPAD_DOWN, 60);
    button(1100, SDL_GAMEPAD_BUTTON_SOUTH);
    button(1350, SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER);
    button(1600, SDL_GAMEPAD_BUTTON_EAST);
    button(1900, SDL_GAMEPAD_BUTTON_DPAD_DOWN);
    button(2200, SDL_GAMEPAD_BUTTON_SOUTH);
  } else {
    if (table == "mean" || table == "space") {
      events.push_back({350, SDL_EVENT_GAMEPAD_AXIS_MOTION,
                        SDL_GAMEPAD_AXIS_RIGHT_TRIGGER, 32767});
      events.push_back({650, SDL_EVENT_GAMEPAD_AXIS_MOTION,
                        SDL_GAMEPAD_AXIS_RIGHT_TRIGGER, 0});
    } else
      button(650, SDL_GAMEPAD_BUTTON_SOUTH);
    button(950, SDL_GAMEPAD_BUTTON_LEFT_SHOULDER, 300);
    button(1300, SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER, 300);
    button(1750, SDL_GAMEPAD_BUTTON_START);
    button(2100, SDL_GAMEPAD_BUTTON_EAST);
    button(2400, SDL_GAMEPAD_BUTTON_LEFT_SHOULDER, 650);
    events.push_back({2500, SDL_EVENT_WINDOW_FOCUS_LOST, 0, 0});
    events.push_back({2850, SDL_EVENT_WINDOW_FOCUS_GAINED, 0, 0});
    button(3150, SDL_GAMEPAD_BUTTON_LEFT_SHOULDER, 150);
    button(3500, SDL_GAMEPAD_BUTTON_BACK);
  }
  std::sort(events.begin(), events.end(),
            [](const auto &a, const auto &b) { return a.time < b.time; });
  std::atomic<bool> done{false}, timeout{false};
  std::thread feeder([&] {
    const auto began = std::chrono::steady_clock::now();
    const auto millis = [](auto start) {
      return std::chrono::duration_cast<std::chrono::milliseconds>(
                 std::chrono::steady_clock::now() - start)
          .count();
    };
    while (!done && !frontend_ready && millis(began) < 10000)
      SDL_Delay(5);
    const auto started = std::chrono::steady_clock::now();
    std::size_t next = 0;
    while (!done) {
      const auto elapsed = millis(started);
      while (next < events.size() && elapsed >= events[next].time) {
        const auto &row = events[next++];
        SDL_Event event{};
        event.type = row.type;
        event.common.timestamp = SDL_GetTicksNS();
        if (row.type == SDL_EVENT_GAMEPAD_AXIS_MOTION) {
          event.gaxis.which = id;
          event.gaxis.axis = Uint8(row.control);
          event.gaxis.value = Sint16(row.value);
        } else if (row.type == SDL_EVENT_GAMEPAD_BUTTON_DOWN ||
                   row.type == SDL_EVENT_GAMEPAD_BUTTON_UP) {
          event.gbutton.which = id;
          event.gbutton.button = Uint8(row.control);
          event.gbutton.down = row.value;
        }
        SDL_PushEvent(&event);
      }
      if (elapsed > 10000) {
        timeout = true;
        SDL_Event quit{};
        quit.type = SDL_EVENT_QUIT;
        SDL_PushEvent(&quit);
        break;
      }
      SDL_Delay(3);
    }
  });
  std::vector<std::string> args;
  if (table == "menu")
    args = {"slamtilt", "--windowed",
            "--config", (trace.parent_path() / "menu.json").string(),
            "--trace",  trace.string()};
  else if (table == "mean" || table == "pirate")
    args = {"slamview",
            (data / (table == "mean" ? "MEAN.DAT" : "PIRATE.DAT")).string(),
            table == "mean" ? "--play" : "--pirate-play",
            prepared.string(),
            "--trace-output",
            trace.string()};
  else
    args = {"slamslice",
            table,
            prepared.string(),
            (data / (table == "space" ? "SPACE.DAT" : "DEMON.DAT")).string(),
            "--presentation",
            "--windowed",
            "--trace",
            trace.string()};
  if (table == "mean")
    args.insert(args.end(), {"--trace", initial.string(), "--retail-minigame"});
  std::vector<char *> a;
  for (auto &arg : args)
    a.push_back(arg.data());
  a.push_back(nullptr);
  const int result = table == "menu"
                         ? slam_gamepad_menu_main(int(args.size()), a.data())
                     : table == "mean" || table == "pirate"
                         ? slam_gamepad_view_main(int(args.size()), a.data())
                         : slam_gamepad_slice_main(int(args.size()), a.data());
  done = true;
  feeder.join();
  if (SDL_WasInit(SDL_INIT_GAMEPAD)) {
    SDL_CloseJoystick(joystick);
    SDL_DetachVirtualJoystick(id);
    SDL_Quit();
  }
  std::cout << "Controller frontend " << table << " result=" << result
            << " watchdog=" << timeout << '\n';
  return timeout ? 5 : result;
#endif
}
