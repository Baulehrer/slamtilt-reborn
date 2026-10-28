#include <SDL3/SDL.h>
#include <iostream>
int main() {
 for(int i=0;i<SDL_GetNumVideoDrivers();++i) std::cout << "video: " << SDL_GetVideoDriver(i) << '\n';
 for(int i=0;i<SDL_GetNumAudioDrivers();++i) std::cout << "audio: " << SDL_GetAudioDriver(i) << '\n';
 if (!SDL_Init(SDL_INIT_AUDIO)) { std::cerr << SDL_GetError() << '\n'; return 1; }
 SDL_AudioSpec spec{SDL_AUDIO_S16,2,44100};
 auto *stream=SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK,&spec,nullptr,nullptr);
 if(!stream) { std::cerr << SDL_GetError() << '\n'; return 1; }
 SDL_DestroyAudioStream(stream); SDL_Quit();
}
