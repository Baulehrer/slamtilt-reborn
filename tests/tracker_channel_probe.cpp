#include <xmp.h>
#include <cstdint>
#include <cstdlib>
#include <iostream>

int main(int argc, char **argv) {
  if (argc != 4) return 1;
  const int order = std::atoi(argv[2]), selected = std::atoi(argv[3]);
  if (order < 0 || selected < 0 || selected >= 4) return 1;
  const auto ctx = xmp_create_context();
  if (!ctx) return 1;
  if (xmp_load_module(ctx, argv[1]) || xmp_start_player(ctx, 44100, 0) ||
      xmp_set_player(ctx, XMP_PLAYER_MIX, 0) ||
      xmp_set_player(ctx, XMP_PLAYER_INTERP, XMP_INTERP_NEAREST) ||
      xmp_set_player(ctx, XMP_PLAYER_VOLUME, 66) ||
      xmp_set_position(ctx, order) < 0) return 1;
  for (int channel = 0; channel < 4; ++channel)
    xmp_channel_mute(ctx, channel, channel != selected);
  if (xmp_play_frame(ctx)) return 1;
  xmp_frame_info frame{};
  xmp_get_frame_info(ctx, &frame);
  if (!frame.buffer || frame.buffer_size < 882 * 4) return 1;
  const auto period = static_cast<std::uint32_t>(frame.channel_info[selected].period);
  const unsigned char header[] = {static_cast<unsigned char>(period),
      static_cast<unsigned char>(period >> 8), static_cast<unsigned char>(period >> 16),
      static_cast<unsigned char>(period >> 24)};
  std::cout.write(reinterpret_cast<const char *>(header), 4);
  std::cout.write(static_cast<const char *>(frame.buffer), 882 * 4);
  xmp_end_player(ctx);
  xmp_release_module(ctx);
  xmp_free_context(ctx);
  return std::cout ? 0 : 1;
}
