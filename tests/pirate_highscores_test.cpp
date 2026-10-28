#ifdef NDEBUG
#undef NDEBUG
#endif
#include "frontend/pirate_highscores.h"

#include <nlohmann/json.hpp>

#include <cassert>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <vector>

namespace {
class TestDirectory {
public:
  TestDirectory() {
    const auto pattern =
        (std::filesystem::temp_directory_path() / "slam-pirate-scores-XXXXXX")
            .string();
    std::vector<char> name(pattern.begin(), pattern.end());
    name.push_back('\0');
    const auto result = ::mkdtemp(name.data());
    if (!result)
      throw std::runtime_error("Cannot create test directory");
    path = result;
  }
  ~TestDirectory() {
    std::error_code ignored;
    std::filesystem::remove_all(path, ignored);
  }
  std::filesystem::path path;
};

std::string read(const std::filesystem::path &path) {
  std::ifstream input(path, std::ios::binary);
  return {std::istreambuf_iterator<char>(input), {}};
}
void write(const std::filesystem::path &path, const std::string &contents) {
  std::ofstream output(path, std::ios::binary | std::ios::trunc);
  output << contents;
  output.close();
  assert(output);
}
} // namespace

int main() {
  TestDirectory directory;
  const auto path = directory.path / "pirate-highscores.json";
  PirateHighscores storage;
  assert(!storage.load(path) && storage.error.empty());
  assert(std::filesystem::is_empty(directory.path));

  PirateHighscores::Records records{};
  assert(storage.save(path, records));
  assert(storage.error.empty() && storage.load(path) == records);
  const auto zero_contents = read(path);

  // A hard link keeps the old inode observable after replacement. An in-place
  // truncation would also change this link and fail the check below.
  const auto old_file = directory.path / "old-inode.json";
  std::filesystem::create_hard_link(path, old_file);
  for (std::size_t row = 0; row < 5; ++row) {
    const auto base = row * 10;
    for (std::size_t i = 0; i < 6; ++i)
      records[base + i] = static_cast<std::uint8_t>(0x99 - row * 0x11 - i);
    records[base + 6] = static_cast<std::uint8_t>('A' + row);
    records[base + 7] = static_cast<std::uint8_t>('0' + row);
    records[base + 8] = ' ';
  }
  // Short original initials and uninitialised lower ranks keep their zeros.
  records[17] = records[18] = 0;
  assert(storage.save(path, records));
  assert(read(old_file) == zero_contents);
  assert(storage.load(path) == records && storage.error.empty());
  const auto valid = nlohmann::json::parse(read(path));

  std::size_t rejected = 0;
  const auto reject = [&](const std::string &text) {
    write(path, text);
    assert(!storage.load(path));
    assert(!storage.error.empty());
    assert(read(path) == text); // Loading damaged data never replaces it.
    ++rejected;
  };
  for (const auto &version :
       std::vector<nlohmann::json>{0, 2, -1, 1.0, "1", nullptr, true,
                                   std::numeric_limits<std::uint64_t>::max()}) {
    auto root = valid;
    root["version"] = version;
    reject(root.dump());
  }
  for (const auto &text : {"", "{", "[]", "{}", "null", "true"})
    reject(text);
  reject(valid.dump() + " trailing data");
  reject(std::string(4097, ' '));
  auto changed = valid;
  changed.erase("version");
  reject(changed.dump());
  changed = valid;
  changed.erase("records");
  reject(changed.dump());
  changed = valid;
  changed["unexpected"] = true;
  reject(changed.dump());
  for (std::size_t count : {std::size_t(0), std::size_t(49), std::size_t(51)}) {
    changed = valid;
    changed["records"] = std::vector<unsigned>(count, 0);
    reject(changed.dump());
  }
  changed = valid;
  changed["records"] = nlohmann::json::object();
  reject(changed.dump());
  for (const auto &byte :
       std::vector<nlohmann::json>{-1, 256, 0.0, "0", nullptr, true,
                                   std::numeric_limits<std::uint64_t>::max()}) {
    changed = valid;
    changed["records"][0] = byte;
    reject(changed.dump());
  }
  for (std::size_t row = 0; row < 5; ++row) {
    for (std::size_t digit = 0; digit < 6; ++digit) {
      for (const auto byte : {0xa0, 0x0a, 0xff}) {
        changed = valid;
        changed["records"][row * 10 + digit] = byte;
        reject(changed.dump());
      }
    }
    for (std::size_t name = 6; name < 9; ++name) {
      for (const auto byte : std::vector<int>{'a', '-', '\n', 0x7f, 0x80}) {
        changed = valid;
        changed["records"][row * 10 + name] = static_cast<int>(byte);
        reject(changed.dump());
      }
    }
    changed = valid;
    changed["records"][row * 10 + 9] = 1;
    reject(changed.dump());
  }

  // Invalid saves also leave an existing destination and its directory intact.
  assert(storage.save(path, records));
  const auto before = read(path);
  auto bad_records = records;
  bad_records[0] = 0xfa;
  assert(!storage.save(path, bad_records) && !storage.error.empty());
  assert(read(path) == before);
  bad_records = records;
  bad_records[6] = '!';
  assert(!storage.save(path, bad_records) && !storage.error.empty());
  assert(read(path) == before);
  bad_records = records;
  bad_records[49] = 1;
  assert(!storage.save(path, bad_records) && !storage.error.empty());
  assert(read(path) == before);
  assert(!storage.save(directory.path / "missing" / "scores.json", records));
  assert(!storage.error.empty());
  const auto blocked = directory.path / "blocked.json";
  std::filesystem::create_directory(blocked);
  write(blocked / "sentinel", "untouched");
  assert(!storage.save(blocked, records) && !storage.error.empty());
  assert(read(blocked / "sentinel") == "untouched");
  for (const auto &entry : std::filesystem::directory_iterator(directory.path))
    assert(entry.path().filename().string().find(".tmp.") == std::string::npos);
  assert(!storage.load(blocked) && !storage.error.empty());
  assert(!storage.load(directory.path / "absent.json") &&
         storage.error.empty());
  assert(storage.load(path) == records && storage.error.empty());
  std::cout << "Pirate highscore storage passed; " << rejected
            << " invalid inputs rejected without rewriting\n";
}
