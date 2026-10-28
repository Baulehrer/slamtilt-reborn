#pragma once
#include "assets/windows_table.h"
namespace slam {
// Original supported Windows Retail MENU.DAT, upright indexed main menu.
// Callers retain ownership of the user's original asset; none is embedded.
TableImage load_windows_menu(const std::filesystem::path &path);
} // namespace slam
