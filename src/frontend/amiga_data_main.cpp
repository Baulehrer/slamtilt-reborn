#include "assets/amiga_assets.h"
#include "assets/amiga_disk.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("Usage: slamadf-data ADF_FOLDER NEW_OUTPUT");
 const std::filesystem::path output=argv[2];if(std::filesystem::exists(output)||std::filesystem::is_symlink(output))throw std::runtime_error("Destination exists");
 auto files=slam::read_amiga_adf_set(argv[1]);
 for(auto& entry:files)if(entry.second.size()>=4&&entry.second[0]=='S'&&entry.second[1]=='L'&&entry.second[2]=='A'&&entry.second[3]=='M')entry.second=slam::decode_slam(entry.second);
 auto assets=slam::build_amiga_assets(files);std::filesystem::create_directories(output);
 for(const auto& entry:assets.files){std::ofstream f(output/entry.first,std::ios::binary);f.write(reinterpret_cast<const char*>(entry.second.data()),entry.second.size());if(!f)throw std::runtime_error("Cannot write normalized Amiga data");}
 std::cout<<"Amiga assets normalized from ADFs only\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
