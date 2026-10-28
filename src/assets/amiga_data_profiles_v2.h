#pragma once
#include <string_view>
namespace slam {
inline constexpr const char* native_amiga_v2_pirate_image_sha256="a37fe7568247711718a8ff4a31a5f4411d3ca446a6986c7f75e2f870fc0570ef";
inline std::string_view amiga_v2_table_sha256(std::string_view id){
 if(id=="mean")return "71c46f6f79a66fc5a65d6463e189dc3f1dd8f92a74e436a32ec048b6eb75187a";
 if(id=="pirate")return "a72344d3fdff63b4cd5ea9cbbdaab221f6e5711db296ddc8aae3562dee915afe";
 if(id=="space")return "fb0ca1b88f6d752a928f10a3a31a740017cbb6a700a26e49d282de2e50ba6454";
 if(id=="demon")return "e6e793992dc309229d2df988f34364192880b7e84586fb94af589c5f0aba135e";
 return {};
}
}
