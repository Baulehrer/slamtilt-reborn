#pragma once
#include <filesystem>
#include <system_error>
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif
namespace slam {
// Replace an existing regular file without deleting it before the replacement.
inline void atomic_replace_file(const std::filesystem::path &from,
                                const std::filesystem::path &to) {
#ifdef _WIN32
  if (!MoveFileExW(from.c_str(), to.c_str(),
                   MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH))
    throw std::system_error(static_cast<int>(GetLastError()),
                            std::system_category(), "Replace file");
#else
  std::filesystem::rename(from, to);
#endif
}
} // namespace slam
