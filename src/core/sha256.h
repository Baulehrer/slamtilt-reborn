#pragma once
#include <cstdint>
#include <string>
#include <vector>
namespace slam {
std::string sha256(const std::vector<std::uint8_t>& data);
}
