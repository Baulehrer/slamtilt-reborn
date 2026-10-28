#include "frontend/pirate_highscores.h"
#include "core/atomic_file.h"

#include <nlohmann/json.hpp>

#include <cerrno>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#include <system_error>
#ifdef _WIN32
#include <atomic>
#include <fcntl.h>
#include <io.h>
#include <sys/stat.h>
#include <windows.h>
#else
#include <unistd.h>
#endif
#include <vector>

namespace {
void validate(const PirateHighscores::Records &records) {
  for (std::size_t base = 0; base < records.size(); base += 10) {
    for (std::size_t i = 0; i < 6; ++i) {
      const auto byte = records[base + i];
      if ((byte >> 4) > 9 || (byte & 15) > 9)
        throw std::runtime_error("Invalid Pirate highscore BCD");
    }
    // Original 405d54's lookup accepts A-Z, digits and space. NUL bytes also
    // occur in short names and the unloaded, entirely zero original table.
    for (std::size_t i = 6; i < 9; ++i) {
      const auto c = records[base + i];
      if (c != 0 && c != ' ' && !(c >= 'A' && c <= 'Z') &&
          !(c >= '0' && c <= '9'))
        throw std::runtime_error("Invalid Pirate highscore initials");
    }
    // Original insertion explicitly writes zero at 405e63, record+9.
    if (records[base + 9] != 0)
      throw std::runtime_error("Invalid Pirate highscore terminator");
  }
}

[[noreturn]] void io_error(const char *operation) {
  throw std::system_error(errno, std::generic_category(), operation);
}

// mkstemp creates a private file beside the destination without following an
// existing temporary symlink. Each save owns its temporary file, including
// when another writer is saving to the same destination.
class TemporaryFile {
public:
  explicit TemporaryFile(const std::filesystem::path &target) {
#ifdef _WIN32
    static std::atomic<unsigned long> serial{0};
    for (unsigned attempt = 0; attempt < 100; ++attempt) {
      path_ = target;
      path_ += ".tmp." + std::to_string(GetCurrentProcessId()) + "." +
               std::to_string(serial++);
      descriptor_ =
          ::_wopen(path_.c_str(), _O_CREAT | _O_EXCL | _O_WRONLY | _O_BINARY,
                   _S_IREAD | _S_IWRITE);
      if (descriptor_ >= 0)
        return;
      if (errno != EEXIST)
        io_error("Create Pirate highscore temporary file");
    }
    io_error("Create Pirate highscore temporary file");
#else
    const auto pattern = target.string() + ".tmp.XXXXXX";
    std::vector<char> name(pattern.begin(), pattern.end());
    name.push_back('\0');
    descriptor_ = ::mkstemp(name.data());
    if (descriptor_ < 0)
      io_error("Create Pirate highscore temporary file");
    path_ = name.data();
#endif
  }
  TemporaryFile(const TemporaryFile &) = delete;
  TemporaryFile &operator=(const TemporaryFile &) = delete;
  ~TemporaryFile() {
    if (descriptor_ >= 0)
      ::close(descriptor_);
    std::error_code ignored;
    if (!path_.empty())
      std::filesystem::remove(path_, ignored);
  }
  void write(const std::string &data) {
    std::size_t offset = 0;
    while (offset < data.size()) {
      const auto count =
          ::write(descriptor_, data.data() + offset, data.size() - offset);
      if (count < 0) {
        if (errno == EINTR)
          continue;
        io_error("Write Pirate highscore temporary file");
      }
      if (count == 0)
        throw std::runtime_error("Pirate highscore write stalled");
      offset += static_cast<std::size_t>(count);
    }
#ifdef _WIN32
    if (::_commit(descriptor_) != 0)
#else
    if (::fsync(descriptor_) != 0)
#endif
      io_error("Flush Pirate highscore temporary file");
    const int descriptor = descriptor_;
    descriptor_ = -1;
    if (::close(descriptor) != 0)
      io_error("Close Pirate highscore temporary file");
  }
  void replace(const std::filesystem::path &target) {
    slam::atomic_replace_file(path_, target);
    path_.clear();
  }

private:
  int descriptor_ = -1;
  std::filesystem::path path_;
};
} // namespace

std::optional<PirateHighscores::Records>
PirateHighscores::load(const std::filesystem::path &path) {
  error.clear();
  try {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
      std::error_code ec;
      const bool exists = std::filesystem::exists(path, ec);
      if (!exists && !ec)
        return std::nullopt;
      throw std::runtime_error("Cannot open Pirate highscore file");
    }
    // The native format is small; bound reads even for damaged or hostile
    // files.
    std::array<char, 4097> buffer{};
    input.read(buffer.data(), buffer.size());
    if (input.bad())
      throw std::runtime_error("Cannot read Pirate highscore file");
    if (input.gcount() > 4096)
      throw std::runtime_error("Pirate highscore file is too large");
    const auto root =
        nlohmann::json::parse(buffer.data(), buffer.data() + input.gcount());
    if (!root.is_object() || root.size() != 2 || !root.contains("version") ||
        !root.at("version").is_number_integer() || root.at("version") != 1)
      throw std::runtime_error("Unsupported Pirate highscore version");
    const auto &bytes = root.at("records");
    Records records{};
    if (!bytes.is_array() || bytes.size() != records.size())
      throw std::runtime_error("Invalid Pirate highscore table size");
    for (std::size_t i = 0; i < records.size(); ++i) {
      if (!bytes[i].is_number_integer() || bytes[i] < 0 || bytes[i] > 255)
        throw std::runtime_error("Invalid Pirate highscore byte");
      records[i] = bytes[i].get<std::uint8_t>();
    }
    validate(records);
    return records;
  } catch (const std::exception &ex) {
    error = ex.what();
    return std::nullopt;
  }
}

bool PirateHighscores::save(const std::filesystem::path &path,
                            const Records &records) {
  error.clear();
  try {
    validate(records);
    const auto data =
        nlohmann::json{{"version", 1}, {"records", records}}.dump() + '\n';
    TemporaryFile temporary(path);
    temporary.write(data);
    temporary.replace(path);
    return true;
  } catch (const std::exception &ex) {
    error = ex.what();
    return false;
  }
}
