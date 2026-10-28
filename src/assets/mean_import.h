#pragma once
#include <filesystem>
#include <string>
#include "assets/asset_source.h"
namespace slam {
// An empty EXE path selects native initialization from DAT files only.
// Explicit EXE paths retain the verified legacy extraction/import behavior.
void import_mean(const std::filesystem::path& exe,const std::filesystem::path& dat,
                 const std::filesystem::path& output,const std::filesystem::path& recipe,
                 const std::filesystem::path& profile,AssetSource source=AssetSource::WindowsDat);
bool verify_retail_data(const std::filesystem::path& data,const std::filesystem::path& recipe,std::string* error=nullptr);
void import_retail(const std::filesystem::path& exe,const std::filesystem::path& dat,
                   const std::filesystem::path& output,const std::filesystem::path& recipe,
                   AssetSource source=AssetSource::WindowsDat);
// Atomic four-table import from original Amiga ADFs. Returns the new root.
void import_amiga_adfs(const std::filesystem::path& folder,const std::filesystem::path& output,
                      const std::filesystem::path& metadata,const std::filesystem::path& mean_profile);
bool verify_pirate_data(const std::filesystem::path& data,const std::filesystem::path& recipe,std::string* error=nullptr);
void import_pirate_retail(const std::filesystem::path& exe,const std::filesystem::path& dat,
                          const std::filesystem::path& output,const std::filesystem::path& recipe);
bool verify_mean_data(const std::filesystem::path& data,const std::filesystem::path& profile,std::string* error=nullptr);
void import_mean_demo(const std::filesystem::path& exe,const std::filesystem::path& dat,
                      const std::filesystem::path& output,const std::filesystem::path& recipe,
                      const std::filesystem::path& profile);
}
