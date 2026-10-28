#include "core/sha256.h"
#include "physics/pirate_step_lift.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>

namespace {
std::vector<std::uint8_t> read(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  if (!input)
    throw std::runtime_error("Missing capture guard input: " + path.string());
  return {std::istreambuf_iterator<char>(input), {}};
}
void require(bool condition, const char *message) {
  if (!condition)
    throw std::runtime_error(message);
}
}

int main(int argc, char **argv) {
  if (argc != 6)
    return 2;
  try {
    const auto manifest_bytes = read(argv[1]);
    const auto fixture = nlohmann::json::parse(manifest_bytes);
    const std::filesystem::path folder(argv[2]);
    const auto dat = read(argv[3]);
    require(slam::sha256(dat) == fixture.at("dat_sha256"), "Capture guard DAT SHA mismatch");
    require(slam::sha256(read(argv[4])) == fixture.at("source_fixture_sha256"), "Capture guard source fixture SHA mismatch");
    require(slam::sha256(read(argv[5])) == fixture.at("build_sha256"), "Capture guard original build SHA mismatch");
    require(fixture.at("entry") == "0x42bae4" && fixture.at("eax") == 6 && fixture.at("edx") == "0x465a68", "Capture guard ABI mismatch");
    require(fixture.at("cases").size() == 5, "Capture guard case count mismatch");
    constexpr std::array<unsigned, 5> ticks = {1355, 1356, 1506, 1544, 1548};
    constexpr std::array<unsigned, 5> results = {1, 0, 0, 0, 1};
    unsigned index = 0;
    for (const auto &row : fixture.at("cases")) {
      require(row.at("tick") == ticks[index] && row.at("expected_eax") == results[index], "Capture guard expected checkpoint mismatch");
      require(row.at("original_game_memory_unchanged") == true, "Original capture guard changed game memory");
      slam::PirateStepLift machine;
      machine.image = read(folder / row.at("image_file").get<std::string>());
      machine.runtime = read(folder / row.at("runtime_file").get<std::string>());
      machine.dat = dat;
      require(machine.image.size() == 0x100000 && machine.runtime.size() == 0x10000, "Capture guard snapshot size mismatch");
      require(slam::sha256(machine.image) == row.at("image_sha256") && slam::sha256(machine.runtime) == row.at("runtime_sha256"), "Capture guard snapshot SHA mismatch");
      require(machine.rd(0x46c1b4, 2) == row.at("ball_state") && machine.rd(0x46c1b6, 2) == row.at("ball_substate"), "Capture guard actual ball state mismatch");
      require(machine.rd(0x465a68, 4) == row.at("cooldown") && machine.rd(0x465a6c, 4) == row.at("hold"), "Capture guard actual cooldown mismatch");
      const auto image = machine.image, runtime = machine.runtime;
      for (unsigned repeat = 0; repeat < 2; ++repeat) {
        machine.r[2] = 0x465a68;
        machine.invoke(0x42bae4, 6);
        require(machine.r[0] == results[index], "Native capture guard return mismatch");
        require(machine.image == image && machine.runtime == runtime && machine.dat == dat, "Native capture guard changed game memory");
      }
      std::cout << row.at("tick") << " original/native leaf EAX " << results[index]
                << "; game memory unchanged; repeated call exact\n";
      ++index;
    }
    return 0;
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
