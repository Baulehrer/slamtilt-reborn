#include <SDL3/SDL.h>
#include <iostream>

int main() {
  for (int i = 0; i < SDL_GetNumVideoDrivers(); ++i)
    std::cout << "video: " << SDL_GetVideoDriver(i) << '\n';
  for (int i = 0; i < SDL_GetNumAudioDrivers(); ++i)
    std::cout << "audio: " << SDL_GetAudioDriver(i) << '\n';
  SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");
  if (!SDL_Init(SDL_INIT_AUDIO | SDL_INIT_GAMEPAD)) {
    std::cerr << SDL_GetError() << '\n';
    return 1;
  }
  struct Quit { ~Quit() { SDL_Quit(); } } quit;
  SDL_AudioSpec spec{SDL_AUDIO_S16, 2, 44100};
  auto* stream = SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, &spec, nullptr, nullptr);
  if (!stream) {
    std::cerr << SDL_GetError() << '\n';
    return 1;
  }
  SDL_DestroyAudioStream(stream);
  std::cout << "dummy audio stream: opened and closed\n";

  SDL_VirtualJoystickDesc desc;
  SDL_INIT_INTERFACE(&desc);
  desc.type = SDL_JOYSTICK_TYPE_GAMEPAD;
  desc.naxes = SDL_GAMEPAD_AXIS_COUNT;
  desc.nbuttons = SDL_GAMEPAD_BUTTON_COUNT;
  desc.axis_mask = (1u << SDL_GAMEPAD_AXIS_COUNT) - 1u;
  desc.button_mask = (1u << SDL_GAMEPAD_BUTTON_COUNT) - 1u;
  desc.name = "Reborn virtual ARM controller probe";
  const auto id = SDL_AttachVirtualJoystick(&desc);
  if (!id) {
    std::cerr << SDL_GetError() << '\n';
    return 1;
  }
  auto* joystick = SDL_OpenJoystick(id);
  if (!joystick || !SDL_SetJoystickVirtualAxis(joystick, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER, SDL_JOYSTICK_AXIS_MIN)) {
    std::cerr << SDL_GetError() << '\n';
    return 1;
  }
  SDL_UpdateJoysticks();
  auto* gamepad = SDL_OpenGamepad(id);
  if (!gamepad || !SDL_IsGamepad(id) || SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER) != 0) {
    std::cerr << "Virtual gamepad detection or resting trigger failed: " << SDL_GetError() << '\n';
    return 1;
  }
  if (!SDL_SetJoystickVirtualButton(joystick, SDL_GAMEPAD_BUTTON_SOUTH, true)) {std::cerr<<"set A: "<<SDL_GetError()<<'\n';return 1;}
  SDL_UpdateJoysticks();
  if (!SDL_GetGamepadButton(gamepad, SDL_GAMEPAD_BUTTON_SOUTH)) {auto* mapping=SDL_GetGamepadMapping(gamepad);std::cerr<<"read A: raw="<<SDL_GetJoystickButton(joystick,0)<<" mapping="<<(mapping?mapping:"")<<'\n';SDL_free(mapping);return 1;}
  if (!SDL_SetJoystickVirtualButton(joystick, SDL_GAMEPAD_BUTTON_SOUTH, false) ||
      !SDL_SetJoystickVirtualAxis(joystick, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER, SDL_JOYSTICK_AXIS_MAX)) return 1;
  SDL_UpdateJoysticks();
  if (SDL_GetGamepadButton(gamepad, SDL_GAMEPAD_BUTTON_SOUTH) ||
      SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER) != SDL_JOYSTICK_AXIS_MAX) {std::cerr<<"trigger max: "<<SDL_GetGamepadAxis(gamepad,SDL_GAMEPAD_AXIS_RIGHT_TRIGGER)<<'\n';return 1;}
  if (!SDL_SetJoystickVirtualAxis(joystick, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER, SDL_JOYSTICK_AXIS_MIN)) return 1;
  SDL_UpdateJoysticks();
  if (SDL_GetGamepadAxis(gamepad, SDL_GAMEPAD_AXIS_RIGHT_TRIGGER) != 0) return 1;
  SDL_CloseGamepad(gamepad);
  SDL_CloseJoystick(joystick);
  if (!SDL_DetachVirtualJoystick(id)) return 1;
  std::cout << "virtual gamepad: detected; A press/release; right trigger 0 -> 32767 -> 0; detached\n";
  std::cout << "physical controller/Pi hardware: unverified\n";
}
