#pragma once
#include <string_view>
namespace slam {
inline constexpr const char* native_amiga_pirate_image_sha256="a37fe7568247711718a8ff4a31a5f4411d3ca446a6986c7f75e2f870fc0570ef";
inline std::string_view amiga_table_sha256(std::string_view id){
 if(id=="mean")return "49754e4a274cc30c325bbfbd1c747f596a1299bf2fb1b67abcb1bc53d8a7806d";
 if(id=="pirate")return "e98edfc08d0891e872ad91974b0f81546a822b34c17c0fb7bd0a0d352b3fbe6d";
 if(id=="space")return "fb0ca1b88f6d752a928f10a3a31a740017cbb6a700a26e49d282de2e50ba6454";
 if(id=="demon")return "9ae25330df3f200e4fa19e3433cd95af2bb2813a9a88b46b35a99cfe9bcf1115";
 return {};
}
}
