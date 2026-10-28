#pragma once
#include <SDL3/SDL.h>
#include "assets/asset_source.h"
#include <nlohmann/json.hpp>
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

// Native-only storage. Never opens or rewrites original STTF / SLAMTILT.CFG.
class MeanHighscores {
public:
  struct Entry { std::uint64_t score; std::string initials; };
  bool editing = false;
  std::string error;
  const std::vector<Entry>& entries() const { return entries_; }
  void load(bool persistent) {
    persistent_ = persistent;
    if (!persistent) return;
    char* dir = SDL_GetPrefPath("SlamTiltNative", "SlamTilt");
    if (!dir) { error = SDL_GetError(); return; }
    const auto path=std::filesystem::path(dir)/slam::highscore_filename("mean");SDL_free(dir);
    load_path(path);
  }
  // Explicit native destination also permits isolated persistence tests.
  void load_path(const std::filesystem::path& path) {
    path_ = path; persistent_ = true; entries_.clear(); error.clear();
    try {
      std::ifstream input(path_); if (!input) return;
      nlohmann::json root; input >> root;
      if (root.at("version").get<int>() != 1) throw std::runtime_error("Unsupported highscore version");
      const auto& list = root.at("entries");
      if (!list.is_array() || list.size() > 5) throw std::runtime_error("Invalid highscore list");
      std::vector<Entry> loaded;
      for (const auto& item : list) {
        const auto& value = item.at("score");
        if (!value.is_number_unsigned()) throw std::runtime_error("Invalid highscore value");
        auto initials = item.at("initials").get<std::string>();
        if (initials.size() != 3 || !std::all_of(initials.begin(), initials.end(), valid_character))
          throw std::runtime_error("Invalid highscore initials");
        loaded.push_back({value.get<std::uint64_t>(), initials});
      }
      std::stable_sort(loaded.begin(), loaded.end(), descending); entries_ = std::move(loaded);
    } catch (const std::exception& ex) { error = ex.what(); entries_.clear(); }
  }
  bool begin(std::uint64_t score) {
    if (session_seen_) return editing;
    session_seen_ = true;
    if (score == 0 || (entries_.size() == 5 && score <= entries_.back().score)) return false;
    pending_score_ = score; initials_.clear(); editing = true; return true;
  }
  void reset_session() { editing = false; session_seen_ = false; initials_.clear(); }
  bool handle(const SDL_Event& event) {
    if (!editing) return false;
    if (event.type == SDL_EVENT_KEY_UP) return true;
    if (event.type != SDL_EVENT_KEY_DOWN) return false;
    // Repeats belong to this modal too: leaking R/P/Escape would reset/pause
    // the game or open a menu while the player is typing initials.
    if (event.key.repeat) return true;
    const auto key = event.key.scancode;
    if (key == SDL_SCANCODE_RETURN || key == SDL_SCANCODE_KP_ENTER) confirm();
    else if (key == SDL_SCANCODE_ESCAPE) { initials_ = "---"; confirm(); }
    else if (key == SDL_SCANCODE_BACKSPACE) { if (!initials_.empty()) initials_.pop_back(); }
    else if (initials_.size() < 3 && key >= SDL_SCANCODE_A && key <= SDL_SCANCODE_Z)
      initials_.push_back(char('A' + key - SDL_SCANCODE_A));
    else if (initials_.size() < 3 && key == SDL_SCANCODE_SPACE) initials_.push_back(' ');
    return true;
  }
  void draw(SDL_Renderer* renderer, int width, int height) const {
    const float scale = width >= 960 && height >= 600 ? 2.f : 1.f;
    SDL_SetRenderScale(renderer, scale, scale);
    const float w = std::min(440.f, width / scale), h = std::min(248.f, height / scale);
    const float x = (width / scale - w) / 2, y = (height / scale - h) / 2;
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND);
    SDL_SetRenderDrawColor(renderer, 12, 16, 24, 245);
    SDL_FRect panel{x, y, w, h}; SDL_RenderFillRect(renderer, &panel);
    SDL_SetRenderDrawColor(renderer, 255, 220, 140, 255);
    SDL_RenderDebugText(renderer, x + 12, y + 12, "MEAN MACHINES - HIGHSCORES");
    for (std::size_t i = 0; i < entries_.size(); ++i) {
      const std::string line = std::to_string(i + 1) + ". " + entries_[i].initials + "  " + std::to_string(entries_[i].score);
      SDL_RenderDebugText(renderer, x + 12, y + 40 + float(i) * 24, line.c_str());
    }
    if (editing) {
      const std::string score = "Your score: " + std::to_string(pending_score_);
      SDL_RenderDebugText(renderer, x + 12, y + h - 88, score.c_str());
    }
    const std::string line = editing ? "Initials: " + initials_ + std::string(3 - initials_.size(), '_') : "R: new game";
    SDL_RenderDebugText(renderer, x + 12, y + h - 64, line.c_str());
    SDL_RenderDebugText(renderer, x + 12, y + h - 40, editing ? "Enter: save  Esc: anonymous" : "Esc: options");
    if (!error.empty()) SDL_RenderDebugText(renderer, x + 12, y + h - 20, "Highscores could not be saved/loaded");
    SDL_SetRenderScale(renderer, 1.f, 1.f);
  }
private:
  static bool valid_character(char c) { return (c >= 'A' && c <= 'Z') || c == ' ' || c == '-'; }
  static bool descending(const Entry& a, const Entry& b) { return a.score > b.score; }
  bool persistent_ = false, session_seen_ = false;
  std::uint64_t pending_score_ = 0;
  std::string initials_;
  std::vector<Entry> entries_;
  std::filesystem::path path_;
  void confirm() {
    initials_.resize(3, ' ');
    entries_.push_back({pending_score_, initials_});
    std::stable_sort(entries_.begin(), entries_.end(), descending);
    if (entries_.size() > 5) entries_.resize(5);
    editing = false;
    if (!persistent_ || path_.empty()) return;
    const auto temporary = path_.string() + ".tmp";
    try {
      nlohmann::json list = nlohmann::json::array();
      for (const auto& entry : entries_) list.push_back({{"score", entry.score}, {"initials", entry.initials}});
      std::ofstream output(temporary, std::ios::trunc);
      output << nlohmann::json{{"version", 1}, {"entries", list}}.dump(2) << '\n';
      output.close(); if (!output) throw std::runtime_error("Highscore write failed");
      if (!SDL_RenamePath(temporary.c_str(), path_.string().c_str())) throw std::runtime_error(SDL_GetError());
      error.clear();
    } catch (const std::exception& ex) {
      error = ex.what(); std::error_code ignored; std::filesystem::remove(temporary, ignored);
    }
  }
};
