cmake_minimum_required(VERSION 3.20)
project(slamtilt_reborn VERSION 1.2.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
# Opt-in release experiments: developer/reference builds keep their defaults.
option(SLAM_SHARED_ENGINE "Share the lifted engine between native Linux frontends" OFF)
if(SLAM_SHARED_ENGINE)
  set(CMAKE_BUILD_RPATH_USE_ORIGIN ON)
endif()
if(SLAM_SHARED_ENGINE AND (NOT CMAKE_SYSTEM_NAME STREQUAL "Linux" OR EMSCRIPTEN))
  message(FATAL_ERROR "Shared engine experiment currently supports native Linux only")
endif()
option(SLAM_RELEASE_COMPACT "Discard unreachable native code and data" OFF)
option(SLAM_RELEASE_LTO "Enable supported interprocedural optimization" OFF)
if(SLAM_RELEASE_LTO)
  include(CheckIPOSupported)
  check_ipo_supported(RESULT SLAM_IPO_SUPPORTED OUTPUT SLAM_IPO_ERROR)
  if(NOT SLAM_IPO_SUPPORTED)
    message(FATAL_ERROR "Requested LTO is unsupported: ${SLAM_IPO_ERROR}")
  endif()
  set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELEASE ON)
endif()
if(SLAM_RELEASE_COMPACT AND NOT EMSCRIPTEN)
  if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang" AND NOT APPLE)
    add_compile_options("$<$<CONFIG:Release>:-ffunction-sections>"
                        "$<$<CONFIG:Release>:-fdata-sections>")
    add_link_options("$<$<CONFIG:Release>:-Wl,--gc-sections>")
  else()
    message(FATAL_ERROR "Compact release profile unsupported by this toolchain")
  endif()
endif()

find_package(SDL3 REQUIRED CONFIG)
find_package(nlohmann_json REQUIRED CONFIG)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(SLAM_EMBED_DIR "${CMAKE_CURRENT_BINARY_DIR}/embedded")
file(MAKE_DIRECTORY "${SLAM_EMBED_DIR}")
function(slam_embed INPUT OUTPUT SYMBOL)
  add_custom_command(OUTPUT "${SLAM_EMBED_DIR}/${OUTPUT}"
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/embed_binary.py" "${INPUT}" "${SLAM_EMBED_DIR}/${OUTPUT}" "${SYMBOL}"
    DEPENDS "${INPUT}" "${CMAKE_SOURCE_DIR}/tools/embed_binary.py" VERBATIM)
endfunction()
slam_embed("${CMAKE_SOURCE_DIR}/assets/fonts/Inter-Regular.ttf" inter_regular.h inter_regular)
slam_embed("${CMAKE_SOURCE_DIR}/assets/fonts/Inter-SemiBold.ttf" inter_semibold.h inter_semibold)
add_library(slamui src/frontend/ui_skin.cpp "${SLAM_EMBED_DIR}/inter_regular.h" "${SLAM_EMBED_DIR}/inter_semibold.h")
target_include_directories(slamui PRIVATE third_party/stb "${SLAM_EMBED_DIR}" PUBLIC src)
target_link_libraries(slamui PUBLIC SDL3::SDL3)
target_compile_options(slamui PRIVATE -Wall -Wextra -Wpedantic)
add_library(slampresentation src/renderer/presentation.cpp)
target_include_directories(slampresentation PUBLIC src PRIVATE "${SLAM_EMBED_DIR}")
target_link_libraries(slampresentation PUBLIC SDL3::SDL3 nlohmann_json::nlohmann_json)
target_compile_options(slampresentation PRIVATE -Wall -Wextra -Wpedantic)
option(SLAM_ENABLE_GPU_EFFECTS "Build optional SDL GPU presentation shaders" ON)
find_program(SLAM_GLSLC glslc)
if(SLAM_ENABLE_GPU_EFFECTS AND SLAM_GLSLC AND SDL3_VERSION VERSION_GREATER_EQUAL "3.4.0")
  foreach(SHADER bloom presentation)
    add_custom_command(OUTPUT "${SLAM_EMBED_DIR}/${SHADER}.spv"
      COMMAND "${SLAM_GLSLC}" -O "${CMAKE_SOURCE_DIR}/src/renderer/shaders/${SHADER}.frag" -o "${SLAM_EMBED_DIR}/${SHADER}.spv"
      DEPENDS "${CMAKE_SOURCE_DIR}/src/renderer/shaders/${SHADER}.frag" VERBATIM)
    slam_embed("${SLAM_EMBED_DIR}/${SHADER}.spv" "${SHADER}_shader.h" "${SHADER}_shader_data")
    target_sources(slampresentation PRIVATE "${SLAM_EMBED_DIR}/${SHADER}_shader.h")
  endforeach()
  target_compile_definitions(slampresentation PRIVATE SLAM_GPU_EFFECTS=1)
endif()

add_library(slamassets src/physics/mean_lane_saver.cpp src/physics/pirate_contact.cpp src/assets/table_flippers.cpp src/assets/table_profile.cpp src/assets/windows_table.cpp src/assets/amiga_table.cpp src/assets/ball_mask.cpp src/assets/ball_occlusion.cpp src/assets/mean_flippers.cpp src/assets/mean_score_font.cpp src/assets/mean_lamps.cpp src/rules/mean_lamp_events.cpp src/rules/mean_lamp_mode.cpp src/rules/mean_ball_reset.cpp src/rules/mean_bonus_turn.cpp src/rules/mean_turn_clock.cpp src/rules/mean_material5.cpp src/rules/mean_award_bank.cpp src/rules/mean_switch_reward.cpp src/rules/mean_flipper_actions.cpp src/rules/mean_mode4_input.cpp src/rules/mean_mode4_clock.cpp src/rules/mean_mode4_switch.cpp src/physics/mean_state7.cpp src/physics/mean_mode4_capture.cpp src/physics/mean_mode4_right_entry.cpp src/physics/mean_right_gate.cpp src/physics/mean_point_force.cpp src/assets/mean_point_forces.cpp src/rules/mean_shared_reward.cpp src/rules/mean_right_progress.cpp src/rules/mean_right_cancel.cpp src/rules/mean_mode4_events.cpp src/rules/mean_minigame2_input.cpp src/rules/mean_turn_entry.cpp src/rules/mean_restart_gate.cpp src/rules/mean_game_end.cpp src/rules/mean_bonus_display.cpp src/dmd/mean_bonus_pixels.cpp src/dmd/mean_idle_hud.cpp src/dmd/mean_main_mode_hud.cpp src/dmd/mean_player_hud.cpp src/dmd/mean_material5_display.cpp src/dmd/mean_mode4_idle.cpp src/dmd/mean_mode4_phase1.cpp src/physics/mean_step.cpp src/physics/mean_material_bundle.cpp src/physics/mean_ramp_bundle.cpp src/physics/mean_switch_bundle.cpp src/physics/mean_baseline_one_bundle.cpp src/physics/mean_baseline_three_bundle.cpp src/physics/mean_capture_bundle.cpp src/physics/mean_capture_tick.cpp src/physics/mean_upper_capture.cpp src/physics/mean_upper_entry.cpp src/physics/mean_mode5_left.cpp src/physics/mean_mode_reset.cpp src/physics/mean_mode5_clock.cpp src/physics/mean_reward_display.cpp src/physics/mean_minigame_input.cpp src/physics/mean_multiball_release.cpp src/physics/mean_mode6_capture.cpp src/physics/mean_mode6_side.cpp src/physics/mean_upper_release.cpp src/physics/mean_simulation.cpp src/physics/ball_trace.cpp src/collision/mean_bitmap.cpp)
target_include_directories(slamassets PUBLIC src)
target_compile_definitions(slamassets PRIVATE SLAM_TABLE_PROFILES_PATH="${CMAKE_SOURCE_DIR}/analysis/table-profiles.json")
target_link_libraries(slamassets PRIVATE nlohmann_json::nlohmann_json)
target_compile_options(slamassets PRIVATE -Wall -Wextra -Wpedantic)
add_executable(slamview src/renderer/main.cpp)
add_executable(slampirate-setup src/frontend/mean_setup.cpp)
target_compile_definitions(slampirate-setup PRIVATE SLAM_SETUP_PIRATE=1)
target_link_libraries(slampirate-setup PRIVATE slamui slamimportlib SDL3::SDL3)
add_executable(slamsetup src/frontend/mean_setup.cpp)
add_library(slamimportlib src/assets/mean_import.cpp src/assets/native_retail_data.cpp src/assets/native_math_tables.cpp src/core/sha256.cpp)
add_executable(slamnative-data src/frontend/native_data_main.cpp)
target_link_libraries(slamnative-data PRIVATE slamimportlib)
target_sources(slamimportlib PRIVATE src/assets/amiga_disk.cpp src/assets/amiga_assets.cpp src/assets/amiga_main.cpp src/assets/amiga_dmd.cpp src/assets/amiga_contact.cpp src/assets/amiga_dmd_fragments_v2.cpp)
add_executable(slamadf-data src/frontend/amiga_data_main.cpp)
target_link_libraries(slamadf-data PRIVATE slamimportlib)
add_executable(amiga_disk_test tests/amiga_disk_test.cpp)
target_link_libraries(amiga_disk_test PRIVATE slamimportlib)
target_include_directories(slamimportlib PUBLIC src)
target_link_libraries(slamimportlib PRIVATE nlohmann_json::nlohmann_json)
target_compile_options(slamimportlib PRIVATE -Wall -Wextra -Wpedantic)
add_executable(slamspace-import src/frontend/space_import_main.cpp)
target_link_libraries(slamspace-import PRIVATE slamimportlib)
target_compile_options(slamspace-import PRIVATE -Wall -Wextra -Wpedantic)
target_compile_definitions(slamspace-import PRIVATE SLAM_SPACE_IMPORT_RECIPE="${CMAKE_SOURCE_DIR}/analysis/import/space-retail-startup.json")
add_executable(slamspace-setup src/frontend/mean_setup.cpp)
target_compile_definitions(slamspace-setup PRIVATE SLAM_SETUP_SPACE=1)
target_link_libraries(slamspace-setup PRIVATE slamui slamimportlib SDL3::SDL3)
set_target_properties(slamspace-import slamspace-setup PROPERTIES INSTALL_RPATH "$ORIGIN/../lib")
add_executable(slamdemon-import src/frontend/demon_import_main.cpp)
target_link_libraries(slamdemon-import PRIVATE slamimportlib)
target_compile_options(slamdemon-import PRIVATE -Wall -Wextra -Wpedantic)
target_compile_definitions(slamdemon-import PRIVATE SLAM_DEMON_IMPORT_RECIPE="${CMAKE_SOURCE_DIR}/analysis/import/demon-retail-startup.json")
add_executable(slamdemon-setup src/frontend/mean_setup.cpp)
target_compile_definitions(slamdemon-setup PRIVATE SLAM_SETUP_DEMON=1)
target_link_libraries(slamdemon-setup PRIVATE slamui slamimportlib SDL3::SDL3)
set_target_properties(slamdemon-import slamdemon-setup PROPERTIES INSTALL_RPATH "$ORIGIN/../lib")
add_executable(slampirate-import src/frontend/pirate_import_main.cpp)
target_link_libraries(slampirate-import PRIVATE slamimportlib)
target_compile_options(slampirate-import PRIVATE -Wall -Wextra -Wpedantic)
target_compile_definitions(slampirate-import PRIVATE SLAM_PIRATE_IMPORT_RECIPE="${CMAKE_SOURCE_DIR}/analysis/import/pirate-retail-startup.json")
if(EXISTS "${CMAKE_SOURCE_DIR}/build/compat/pirate-build.json")
  add_test(NAME pirate_compat_runtime COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_compat.py" --output "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-realtime-compat.json" --host-output "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-realtime-compat-package.json")
  set_tests_properties(pirate_compat_runtime PROPERTIES TIMEOUT 180)
endif()
add_test(NAME pirate_completion_contract COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_completion.py")
add_test(NAME pirate_knife_auto COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_knife_auto.py")
set_tests_properties(pirate_knife_auto PROPERTIES TIMEOUT 120)
add_test(NAME pirate_mermaid_chains COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_mermaid.py")
set_tests_properties(pirate_mermaid_chains PROPERTIES TIMEOUT 180)
add_test(NAME pirate_window_chains COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_windows.py")
set_tests_properties(pirate_window_chains PROPERTIES TIMEOUT 120)
add_test(NAME pirate_rule_chains COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_rule_chains.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
set_tests_properties(pirate_rule_chains PROPERTIES TIMEOUT 120)
add_test(NAME pirate_realtime_exact_stop COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/pirate_realtime_stop.py")
set_tests_properties(pirate_realtime_exact_stop PROPERTIES TIMEOUT 15)
add_test(NAME pirate_render_cache COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_render_cache.py")
set_tests_properties(pirate_render_cache PROPERTIES TIMEOUT 60)
add_test(NAME pirate_host_dummy COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_host.py" --dummy --repeat 1)
set_tests_properties(pirate_host_dummy PROPERTIES TIMEOUT 60)
add_test(NAME pirate_firststart_package COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_firststart.py")
set_tests_properties(pirate_firststart_package PROPERTIES TIMEOUT 180)
add_test(NAME space_replay_input COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_replay_input.py")
set_tests_properties(space_replay_input PROPERTIES TIMEOUT 60)
add_test(NAME space_import_acceptance COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_import.py")
set_tests_properties(space_import_acceptance PROPERTIES TIMEOUT 120)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/compat/space-build.json")
  add_test(NAME space_package_acceptance COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_package.py")
  add_test(NAME space_compat_acceptance COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_compat.py")
  set_tests_properties(space_package_acceptance space_compat_acceptance PROPERTIES TIMEOUT 240)
endif()
add_test(NAME pirate_import_acceptance COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_import.py" --native "$<TARGET_FILE:slampirate-import>" --viewer "$<TARGET_FILE:slamview>")
set_tests_properties(pirate_import_acceptance PROPERTIES TIMEOUT 120)
add_executable(slamimport src/frontend/mean_import_main.cpp)
target_link_libraries(slamimport PRIVATE slamimportlib)
target_compile_options(slamimport PRIVATE -Wall -Wextra -Wpedantic)
target_compile_definitions(slamimport PRIVATE SLAM_IMPORT_SOURCE_RECIPE="${CMAKE_SOURCE_DIR}/analysis/import/mean-demo-startup.json" SLAM_IMPORT_SOURCE_PROFILE="${CMAKE_SOURCE_DIR}/packaging/mean-data.sha256")
install(TARGETS slamimport RUNTIME DESTINATION . COMPONENT Runtime)
target_link_libraries(slamsetup PRIVATE slamui slamimportlib SDL3::SDL3)
target_sources(slamassets PRIVATE src/assets/table_definition.cpp src/assets/table_sprites.cpp src/assets/table_lamps.cpp)
target_link_libraries(slamassets PRIVATE slamimportlib)
target_compile_options(slamsetup PRIVATE -Wall -Wextra -Wpedantic)
set_target_properties(slamsetup PROPERTIES INSTALL_RPATH "$ORIGIN/../lib")
install(TARGETS slamsetup RUNTIME DESTINATION bin COMPONENT Runtime)
target_link_libraries(slamview PRIVATE slamassets slamui slampresentation SDL3::SDL3 nlohmann_json::nlohmann_json)
target_compile_options(slamview PRIVATE -Wall -Wextra -Wpedantic)
set_target_properties(slamview PROPERTIES INSTALL_RPATH "$ORIGIN/../lib")
set_target_properties(slampirate-import slampirate-setup PROPERTIES INSTALL_RPATH "$ORIGIN/../lib")
install(TARGETS slamview slampirate-import slampirate-setup RUNTIME DESTINATION bin COMPONENT PirateRuntime)
install(TARGETS slamview RUNTIME DESTINATION bin COMPONENT Runtime)
install(PROGRAMS tools/slamplay DESTINATION . COMPONENT Runtime)
install(FILES analysis/import/mean-demo-startup.json analysis/import/mean-retail-startup.json DESTINATION share/slamtilt COMPONENT Runtime)
install(FILES analysis/import/pirate-dat-startup.json analysis/import/space-dat-startup.json analysis/import/demon-dat-startup.json DESTINATION share/slamtilt COMPONENT Runtime)
install(FILES analysis/import/pirate-dat-startup.json DESTINATION share/slamtilt COMPONENT PirateRuntime)
install(FILES analysis/import/space-dat-startup.json DESTINATION share/slamtilt COMPONENT SpaceRuntime)
install(FILES analysis/import/demon-dat-startup.json DESTINATION share/slamtilt COMPONENT DemonRuntime)
install(FILES analysis/table-profiles.json DESTINATION share/slamtilt COMPONENT Runtime)
install(FILES packaging/mean-initial.json DESTINATION share/slamtilt RENAME initial-state.json COMPONENT Runtime)
install(FILES packaging/mean-data.sha256 packaging/mean-retail-data.sha256 DESTINATION share/slamtilt COMPONENT Runtime)
install(FILES packaging/README.txt DESTINATION . COMPONENT Runtime)
install(FILES packaging/DATA-README.txt DESTINATION data RENAME README.txt COMPONENT Runtime)
install(DIRECTORY assets/fonts/ DESTINATION LICENSES/fonts COMPONENT Runtime FILES_MATCHING PATTERN "*.txt")
install(FILES third_party/stb/stb_truetype.h DESTINATION LICENSES COMPONENT Runtime)
install(FILES LICENSES/nlohmann-json-MIT.txt LICENSES/ancient-BSD-2-Clause.txt DESTINATION LICENSES COMPONENT Runtime)
enable_testing()
add_executable(table_definition_tests tests/table_definition_tests.cpp)
target_link_libraries(table_definition_tests PRIVATE slamassets)
add_test(NAME table_definition_metadata COMMAND table_definition_tests)
add_executable(table_sprite_tests tests/table_sprite_tests.cpp)
target_link_libraries(table_sprite_tests PRIVATE slamassets)
add_test(NAME table_sprite_metadata COMMAND table_sprite_tests)
add_executable(table_lamp_tests tests/table_lamp_tests.cpp)
target_link_libraries(table_lamp_tests PRIVATE slamassets)
add_test(NAME table_lamp_metadata COMMAND table_lamp_tests)
add_executable(table_flipper_composite_probe tests/table_flipper_composite_probe.cpp)
target_link_libraries(table_flipper_composite_probe PRIVATE slamassets)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-flipper-lamps/pattern-0-image.bin")
  add_test(NAME pirate_flipper_lamps_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_flipper_lamp_composite.py" --native "$<TARGET_FILE:table_flipper_composite_probe>")
endif()
if(EXISTS "${CMAKE_SOURCE_DIR}/build/generated/pirate_step.cpp")
  if(SLAM_SHARED_ENGINE)
    add_library(pirate_step_lift SHARED build/generated/pirate_step.cpp)
    set_target_properties(pirate_step_lift PROPERTIES OUTPUT_NAME slamtilt_engine)
    install(TARGETS pirate_step_lift LIBRARY DESTINATION lib COMPONENT Runtime)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
      # Internal engine: bind its own calls locally instead of through the PLT.
      # Symbol interposition is not a supported gameplay extension mechanism.
      target_compile_options(pirate_step_lift PRIVATE -fno-semantic-interposition)
      target_link_options(pirate_step_lift PRIVATE -Wl,-Bsymbolic-functions)
    endif()
  else()
    add_library(pirate_step_lift build/generated/pirate_step.cpp)
  endif()
  add_executable(demon_legal_search tools/demon_legal_search.cpp)
  target_link_libraries(demon_legal_search PRIVATE pirate_step_lift nlohmann_json::nlohmann_json)
  target_include_directories(demon_legal_search PRIVATE src)
  target_compile_options(demon_legal_search PRIVATE -Wall -Wextra -Wpedantic)

  target_include_directories(pirate_step_lift PUBLIC src)
  add_executable(pirate_step_probe tests/pirate_step_probe.cpp)
  target_link_libraries(pirate_step_probe PRIVATE pirate_step_lift nlohmann_json::nlohmann_json)
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/demon-completion-contract.json")
    add_test(NAME demon_completion_audit COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_completion.py")
    set_tests_properties(demon_completion_audit PROPERTIES DEPENDS "demon_legal_session;demon_variants;demon_banks;demon_video;demon_final;demon_modes;demon_clock;demon_base_rules")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-legal-game-rewards.json")
    add_test(NAME demon_legal_session COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_legal.py")
    set_tests_properties(demon_legal_session PROPERTIES TIMEOUT 240)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-witch-force-on-rewards.json")
    add_test(NAME demon_variants COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_variants.py")
    set_tests_properties(demon_variants PROPERTIES TIMEOUT 360)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-kickback-on-rewards.json")
    add_test(NAME demon_banks COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_banks.py")
    set_tests_properties(demon_banks PROPERTIES TIMEOUT 360)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-video-brain-win-rewards.json")
    add_test(NAME demon_video COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_video.py")
    set_tests_properties(demon_video PROPERTIES TIMEOUT 360)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-final-campaign-rewards.json")
    add_test(NAME demon_final COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_final.py")
    set_tests_properties(demon_final PROPERTIES TIMEOUT 360)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-mode-bat-rewards.json")
    add_test(NAME demon_modes COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_modes.py")
    set_tests_properties(demon_modes PROPERTIES TIMEOUT 360)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-clock-tower-rewards.json")
    add_test(NAME demon_clock COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_clock.py")
    set_tests_properties(demon_clock PROPERTIES TIMEOUT 240)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-base-rules-rewards.json")
    add_test(NAME demon_base_rules COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_base.py")
    add_test(NAME demon_session COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_session.py")
    set_tests_properties(demon_base_rules demon_session PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-sabre-variants-rewards.json")
    add_test(NAME space_variants COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_variants.py")
    set_tests_properties(space_variants PROPERTIES TIMEOUT 300)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-mission-campaign-rewards.json")
    add_test(NAME space_mission_campaign COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_mission_campaign.py")
    set_tests_properties(space_mission_campaign PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-lane-default-rewards.json")
    add_test(NAME space_lane_kickback COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_lane_kickback.py")
    set_tests_properties(space_lane_kickback PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-weapons-ladder-rewards.json")
    add_test(NAME space_weapons COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_weapons.py")
    add_test(NAME space_special_input COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_special_input.py")
    set_tests_properties(space_weapons space_special_input PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/manual-rules/space-complete.txt")
    add_test(NAME space_completion_audit COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_completion.py")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-base-rules-rewards.json")
    add_test(NAME space_base_rules COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_base_rules.py")
    set_tests_properties(space_base_rules PROPERTIES TIMEOUT 240)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-bigblam-rewards.json")
    add_test(NAME space_bigblam COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_bigblam.py")
    set_tests_properties(space_bigblam PROPERTIES TIMEOUT 240)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-planet-success-rewards.json")
    add_test(NAME space_planet_success COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_planet_success.py")
    set_tests_properties(space_planet_success PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-sabre-rewards.json")
    add_test(NAME space_mode_family COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_mode_family.py")
    set_tests_properties(space_mode_family PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-multiball-rewards.json")
    add_test(NAME space_multiball_rewards COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_multiball_rewards.py")
    set_tests_properties(space_multiball_rewards PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-multiball.json")
    add_test(NAME space_multiball COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_multiball.py")
    set_tests_properties(space_multiball PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/blam.json")
    add_test(NAME space_mission_family COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_missions.py")
    set_tests_properties(space_mission_family PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/asteroid-chain.json")
    add_test(NAME space_asteroid_chain COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_asteroid.py" --viewer "$<TARGET_FILE:slamslice>")
    set_tests_properties(space_asteroid_chain PROPERTIES TIMEOUT 180)
    if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/asteroid-traps.json")
      add_test(NAME space_asteroid_traps COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_asteroid.py" --case traps --viewer "$<TARGET_FILE:slamslice>")
      set_tests_properties(space_asteroid_traps PROPERTIES TIMEOUT 180)
    endif()
  endif()
  foreach(RETAIL_TABLE IN ITEMS space demon)
    if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/${RETAIL_TABLE}-full-game/human-image.bin")
      add_test(NAME retail_${RETAIL_TABLE}_slice COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_retail_slice.py" --table ${RETAIL_TABLE} --viewer "$<TARGET_FILE:slamslice>")
      set_tests_properties(retail_${RETAIL_TABLE}_slice PROPERTIES TIMEOUT 120)
    endif()
  endforeach()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin")
    add_test(NAME space_session COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_session.py")
    set_tests_properties(space_session PROPERTIES TIMEOUT 180)
  endif()
  add_executable(slamslice src/frontend/retail_slice.cpp)
  set_target_properties(slamslice PROPERTIES INSTALL_RPATH "$ORIGIN/../lib")
  install(TARGETS slamslice slamspace-import slamspace-setup RUNTIME DESTINATION bin COMPONENT SpaceRuntime)
  install(TARGETS slamslice slamdemon-import slamdemon-setup RUNTIME DESTINATION bin COMPONENT DemonRuntime)
  target_link_libraries(slamslice PRIVATE pirate_step_lift slamassets slamui slampresentation SDL3::SDL3 nlohmann_json::nlohmann_json)
  target_compile_options(slamslice PRIVATE -Wall -Wextra -Wpedantic)
  add_library(pirate_session src/physics/pirate_session.cpp)
  target_include_directories(pirate_session PUBLIC src)
  target_link_libraries(pirate_session PUBLIC pirate_step_lift PRIVATE slamimportlib slamassets)
  target_compile_options(pirate_session PRIVATE -Wall -Wextra -Wpedantic)
  add_executable(pirate_session_probe tests/pirate_session_probe.cpp)
  target_link_libraries(pirate_session_probe PRIVATE pirate_session nlohmann_json::nlohmann_json)
  add_executable(pirate_capture_guard_test tests/pirate_capture_guard_test.cpp)
  target_link_libraries(pirate_capture_guard_test PRIVATE pirate_step_lift slamimportlib nlohmann_json::nlohmann_json)
  target_compile_options(pirate_capture_guard_test PRIVATE -Wall -Wextra -Wpedantic)
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-magna-capture-guard.json" AND EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-capture-guard/tick-1355-image.bin")
    add_test(NAME pirate_capture_guard_original_native COMMAND pirate_capture_guard_test
      "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-magna-capture-guard.json"
      "${CMAKE_SOURCE_DIR}/build/oracle/pirate-capture-guard"
      "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT"
      "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-magna-capture-cooldown.json"
      "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE")
  endif()
  target_sources(slamview PRIVATE src/frontend/pirate_play.cpp)
  add_library(pirate_highscores src/frontend/pirate_highscores.cpp)
  target_include_directories(pirate_highscores PUBLIC src)
  target_link_libraries(pirate_highscores PRIVATE nlohmann_json::nlohmann_json)
  target_compile_options(pirate_highscores PRIVATE -Wall -Wextra -Wpedantic)
  add_executable(pirate_highscores_test tests/pirate_highscores_test.cpp)
  target_link_libraries(pirate_highscores_test PRIVATE pirate_highscores nlohmann_json::nlohmann_json)
  add_test(NAME pirate_highscore_storage COMMAND pirate_highscores_test)
  target_link_libraries(slamview PRIVATE pirate_highscores)
  target_link_libraries(slamslice PRIVATE pirate_highscores)
  target_link_libraries(slamview PRIVATE pirate_session)
  target_compile_definitions(slamview PRIVATE SLAM_PIRATE_SESSION=1)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-human/trace.json")
    add_test(NAME pirate_original_native_sdl_1000 COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_session.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
  endif()
  foreach(PIRATE_CASE IN ITEMS pirate-full-tick pirate-full-10000 pirate-full-input)
    if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/${PIRATE_CASE}/trace.json")
      set(PIRATE_STEPS 1000)
      set(PIRATE_INPUT_ARGS)
      if(PIRATE_CASE STREQUAL "pirate-full-10000")
        set(PIRATE_STEPS 10000)
      elseif(PIRATE_CASE STREQUAL "pirate-full-input")
        set(PIRATE_INPUT_ARGS --flippers)
      endif()
      add_test(NAME ${PIRATE_CASE}_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_full_tick.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>" --steps ${PIRATE_STEPS} ${PIRATE_INPUT_ARGS})
    endif()
  endforeach()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-adventure/success/trace.json" AND EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-adventure/timeout/trace.json")
    add_test(NAME pirate_plank_adventure_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_adventure.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/pirate-final-feedback-a-boundary.json" AND EXISTS "${CMAKE_SOURCE_DIR}/analysis/pirate-final-feedback-b-boundary.json")
    add_test(NAME pirate_final_feedback_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_final_feedback.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_final_feedback_native_sdl PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/pirate-magnasaver-boundary.json")
    add_test(NAME pirate_magnasaver_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_magnasaver.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_magnasaver_native_sdl PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/pirate-magna-capture-boundary.json")
    add_test(NAME pirate_magna_capture_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_magna_capture.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_magna_capture_native_sdl PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-acceptance-multiball.json")
    add_test(NAME pirate_acceptance_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_acceptance.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_acceptance_native_sdl PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/pirate-campaign-magnets-boundary.json")
    add_test(NAME pirate_campaign_magnets_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_campaign_magnets.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_campaign_magnets_native_sdl PROPERTIES TIMEOUT 240)
  endif()
  set(PIRATE_MODES_READY TRUE)
  foreach(PIRATE_MODE IN ITEMS sword dive-success dive-timeout monkey-success monkey-timeout shark-success shark-timeout)
    if(NOT EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/${PIRATE_MODE}/trace.json")
      set(PIRATE_MODES_READY FALSE)
    endif()
  endforeach()
  if(PIRATE_MODES_READY)
    add_test(NAME pirate_four_adventures_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_modes.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/pirate-mode-feedback-boundary.json")
    add_test(NAME pirate_mode_feedback_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_mode_feedback.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_mode_feedback_native_sdl PROPERTIES TIMEOUT 90)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/knife-success/trace.json" AND EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/knife-failure/trace.json")
    add_test(NAME pirate_knife_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_knife.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/crocodile/trace.json" AND EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/cannon-miss/trace.json")
    add_test(NAME pirate_multiball_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_multiball.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/multiball-campaign/trace.json")
    add_test(NAME pirate_multiball_campaign_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_multiball_campaign.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-natural-crocodile-game.json")
    add_test(NAME pirate_natural_crocodile_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_natural_croc.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_natural_crocodile_native_sdl PROPERTIES TIMEOUT 120)
  endif()
  add_executable(pirate_crocodile_key_search tools/pirate_crocodile_key_search.cpp)
  target_link_libraries(pirate_crocodile_key_search PRIVATE pirate_session nlohmann_json::nlohmann_json)
  target_compile_options(pirate_crocodile_key_search PRIVATE -Wall -Wextra -Wpedantic)
  add_executable(pirate_plank_key_search tools/pirate_plank_key_search.cpp)
  target_link_libraries(pirate_plank_key_search PRIVATE pirate_session nlohmann_json::nlohmann_json)
  target_compile_options(pirate_plank_key_search PRIVATE -Wall -Wextra -Wpedantic)
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-natural-plank-game.json")
    add_test(NAME pirate_natural_plank_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_natural_plank.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_natural_plank_native_sdl PROPERTIES TIMEOUT 120)
  endif()
  add_executable(pirate_legal_key_search tools/pirate_legal_key_search.cpp)
  add_executable(pirate_acceptance_sweep tools/pirate_acceptance_sweep.cpp)
  target_link_libraries(pirate_acceptance_sweep PRIVATE pirate_session slamimportlib nlohmann_json::nlohmann_json)
  target_compile_options(pirate_acceptance_sweep PRIVATE -Wall -Wextra -Wpedantic)
  target_link_libraries(pirate_legal_key_search PRIVATE pirate_session nlohmann_json::nlohmann_json)
  target_compile_options(pirate_legal_key_search PRIVATE -Wall -Wextra -Wpedantic)
  if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/pirate-legal-feedback-boundary.json" AND EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-legal-cave-game.json")
    add_test(NAME pirate_legal_play_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_legal_play.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_legal_play_native_sdl PROPERTIES TIMEOUT 180)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/locks-storm-4/trace.json")
    add_test(NAME pirate_lock_matrix_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_lock_matrix.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_lock_matrix_native_sdl PROPERTIES TIMEOUT 120)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/multiball-surplus/trace.json")
    add_test(NAME pirate_multiball_surplus_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_surplus.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_multiball_surplus_native_sdl PROPERTIES COST 100)
  endif()
  set(PIRATE_MAGNA_ELIGIBILITY_READY TRUE)
  foreach(PIRATE_MAGNA_ELIGIBILITY_CASE IN ITEMS magna-mode-lit magna-bonus-held magna-kickback-lit magna-all-played)
    if(NOT EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/${PIRATE_MAGNA_ELIGIBILITY_CASE}/trace.json")
      set(PIRATE_MAGNA_ELIGIBILITY_READY FALSE)
    endif()
  endforeach()
  if(PIRATE_MAGNA_ELIGIBILITY_READY)
    add_test(NAME pirate_magna_eligibility_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_magna_eligibility.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_magna_eligibility_native_sdl PROPERTIES COST 120)
  endif()
  add_executable(pirate_magna_key_search tools/pirate_magna_key_search.cpp)
  target_link_libraries(pirate_magna_key_search PRIVATE pirate_session nlohmann_json::nlohmann_json)
  target_compile_options(pirate_magna_key_search PRIVATE -Wall -Wextra -Wpedantic)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/nudge-tilt-crocodile/trace.json")
    add_test(NAME pirate_nudge_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_nudge.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_nudge_native_sdl PROPERTIES TIMEOUT 120)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/magna-key-reward/trace.json")
    add_test(NAME pirate_magna_keys_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_magna_keys.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
  endif()
  set(PIRATE_MAGNA_READY TRUE)
  foreach(PIRATE_MAGNA_CASE IN ITEMS
      magna-slot-0 magna-slot-1 magna-slot-2 magna-escape magna-expired magna-idle
      magna-award-0 magna-award-1 magna-award-2 magna-award-3 magna-award-4 magna-award-5
      magna-award-6 magna-award-7 magna-award-8 magna-award-9 magna-award-10 magna-award-11
      magna-natural-both magna-natural-left)
    if(NOT EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/${PIRATE_MAGNA_CASE}/trace.json")
      set(PIRATE_MAGNA_READY FALSE)
    endif()
  endforeach()
  if(PIRATE_MAGNA_READY)
    add_test(NAME pirate_magna_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_magna.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/final-campaign/trace.json")
    add_test(NAME pirate_final_campaign_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_final.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_final_campaign_native_sdl PROPERTIES COST 120)
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-complete-game-lamps-ready/trace.json")
    add_test(NAME pirate_complete_game_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_complete_game.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-modes/campaign-finite/trace.json")
    add_test(NAME pirate_campaign_finite_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_campaign_finite.py" --native "$<TARGET_FILE:pirate_session_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_campaign_finite_native_sdl PROPERTIES TIMEOUT 240)
  endif()
endif()
add_executable(sha256_tests tests/sha256_test.cpp)
target_link_libraries(sha256_tests PRIVATE slamimportlib)
add_test(NAME sha256_known_vectors COMMAND sha256_tests)
add_executable(asset_tests tests/asset_tests.cpp)
target_link_libraries(asset_tests PRIVATE slamassets)
add_test(NAME assets COMMAND asset_tests)
add_executable(mean_probe tests/mean_probe.cpp)
target_link_libraries(mean_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_executable(mean_upper_reward_cycle_probe tests/mean_upper_reward_cycle_probe.cpp)
target_link_libraries(mean_upper_reward_cycle_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_executable(mean_reward3_display_probe tests/mean_reward3_display_probe.cpp)
target_link_libraries(mean_reward3_display_probe PRIVATE slamassets)

add_executable(mean_reward_display_probe tests/mean_reward_display_probe.cpp)
target_include_directories(mean_reward_display_probe PRIVATE src/physics)
target_link_libraries(mean_reward_display_probe PRIVATE slamassets)

add_executable(mean_upper_reward_probe tests/mean_upper_reward_probe.cpp)
target_link_libraries(mean_upper_reward_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_executable(mean_mode5_begin_probe tests/mean_mode5_begin_probe.cpp)
target_link_libraries(mean_mode5_begin_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_executable(mean_mode_island_probe tests/mean_mode_island_probe.cpp)
target_link_libraries(mean_mode_island_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_executable(mean_upper_cycle_probe tests/mean_upper_cycle_probe.cpp)
target_link_libraries(mean_upper_cycle_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_executable(mean_capture_tick_probe tests/mean_capture_tick_probe.cpp)
target_link_libraries(mean_capture_tick_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_executable(mean_sim_probe tests/mean_sim_probe.cpp)
target_link_libraries(mean_sim_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/generated/mean_flippers.cpp")
  add_library(mean_flipper_lift build/generated/mean_flippers.cpp)
  target_include_directories(mean_flipper_lift PUBLIC src)
  target_link_libraries(slamassets PUBLIC mean_flipper_lift)
  target_compile_definitions(slamassets PUBLIC SLAM_MEAN_FLIPPER_LIFT=1)
  add_executable(flipper_probe tests/flipper_probe.cpp)
  target_link_libraries(flipper_probe PRIVATE mean_flipper_lift nlohmann_json::nlohmann_json)
endif()
if(EXISTS "${CMAKE_SOURCE_DIR}/build/generated/mean_minigame.cpp")
  add_library(mean_minigame_lift build/generated/mean_minigame.cpp src/physics/mean_minigame_lift.cpp)
  target_include_directories(mean_minigame_lift PUBLIC src)
  target_link_libraries(slamassets PUBLIC mean_minigame_lift)
  target_compile_definitions(slamassets PUBLIC SLAM_MEAN_MINIGAME_LIFT=1)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/generated/mean_ball_pair.cpp")
    add_executable(mean_multiball_flight_probe tests/mean_multiball_flight_probe.cpp)
    target_link_libraries(mean_multiball_flight_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
    add_executable(mean_multiball_probe tests/mean_multiball_probe.cpp)
    target_link_libraries(mean_multiball_probe PRIVATE slamassets mean_ball_pair_lift nlohmann_json::nlohmann_json)
    add_library(mean_ball_pair_lift build/generated/mean_ball_pair.cpp)
    target_include_directories(mean_ball_pair_lift PUBLIC src)
    target_link_libraries(slamassets PUBLIC mean_ball_pair_lift)
    target_compile_definitions(slamassets PUBLIC SLAM_MEAN_BALL_PAIR_LIFT=1)
  endif()
  add_executable(mean_minigame_terminal_probe tests/mean_minigame_terminal_probe.cpp)
  target_link_libraries(mean_minigame_terminal_probe PRIVATE mean_minigame_lift nlohmann_json::nlohmann_json)
  add_executable(mean_minigame_probe tests/mean_minigame_probe.cpp)
  target_link_libraries(mean_minigame_probe PRIVATE mean_minigame_lift nlohmann_json::nlohmann_json)
endif()
add_executable(windows_dmd_probe tests/windows_dmd_probe.cpp)
target_include_directories(windows_dmd_probe PRIVATE src)
add_executable(mean_minigame_input_probe tests/mean_minigame_input_probe.cpp)
target_link_libraries(mean_minigame_input_probe PRIVATE slamassets)

add_executable(mean_ball_reset_probe tests/mean_ball_reset_probe.cpp)
target_link_libraries(mean_ball_reset_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_ball_reset_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_ball_reset.py" --probe "$<TARGET_FILE:mean_ball_reset_probe>")
add_executable(mean_bonus_turn_probe tests/mean_bonus_turn_probe.cpp)
target_link_libraries(mean_bonus_turn_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_bonus_turn_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_bonus_turn.py" --native "$<TARGET_FILE:mean_bonus_turn_probe>" --replay)
add_executable(mean_lamp_mode_probe tests/mean_lamp_mode_probe.cpp)
target_link_libraries(mean_lamp_mode_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_lamp_mode_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_lamp_mode.py" --probe "$<TARGET_FILE:mean_lamp_mode_probe>")
add_test(NAME mean_top_target_reward_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_lamp_events_replay.py" "$<TARGET_FILE:mean_lamp_events_probe>" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-top-target-reward-original.json")
add_executable(mean_lamp_events_probe tests/mean_lamp_events_probe.cpp)
target_link_libraries(mean_lamp_events_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_lamp_rule_gameplay_bundle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/probe_mean_routes.py" --steps 400000 --require-active --require-targets --output "${CMAKE_SOURCE_DIR}/analysis/traces/mean-lamp-rule-gameplay-validation.json")
add_test(NAME mean_lamp_events_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_lamp_events_replay.py" "$<TARGET_FILE:mean_lamp_events_probe>")
add_executable(mean_lamp_pixels_probe tests/mean_lamp_pixels_probe.cpp)
target_link_libraries(mean_lamp_pixels_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
add_test(NAME mean_lamp_pixels_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_lamp_pixels_replay.py" "$<TARGET_FILE:mean_lamp_pixels_probe>")
endif()
add_executable(mean_lamp_clock_probe tests/mean_lamp_clock_probe.cpp)
target_link_libraries(mean_lamp_clock_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_lamp_clock_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_lamp_clock_replay.py" "$<TARGET_FILE:mean_lamp_clock_probe>")
add_executable(mean_score_font_probe tests/mean_score_font_probe.cpp)
target_link_libraries(mean_score_font_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MAIN.DAT")
  add_test(NAME mean_score_font_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_score_font_replay.py" "$<TARGET_FILE:mean_score_font_probe>")
endif()
add_executable(mean_mode6_side_probe tests/mean_mode6_side_probe.cpp)
target_link_libraries(mean_mode6_side_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode6_side_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode6_side_replay.py" "$<TARGET_FILE:mean_mode6_side_probe>")
add_executable(mean_mode6_probe tests/mean_mode6_probe.cpp)
target_link_libraries(mean_mode6_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode6_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode6_replay.py" "$<TARGET_FILE:mean_mode6_probe>")

add_executable(mean_mode4_probe tests/mean_mode4_probe.cpp)
target_link_libraries(mean_mode4_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_executable(mean_mode4_transfer_probe tests/mean_mode4_transfer_probe.cpp)
target_link_libraries(mean_mode4_transfer_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_executable(ball_bank_tests tests/ball_bank_tests.cpp)
target_link_libraries(ball_bank_tests PRIVATE slamassets)
add_test(NAME ball_bank_pixels COMMAND ball_bank_tests "${CMAKE_SOURCE_DIR}/build/imported/pirate-retail/MAIN.DAT")
add_executable(ball_display_tests tests/ball_display_tests.cpp)
target_include_directories(ball_display_tests PRIVATE src)
target_link_libraries(ball_display_tests PRIVATE nlohmann_json::nlohmann_json)
add_test(NAME ball_display COMMAND ball_display_tests "${CMAKE_SOURCE_DIR}/analysis/traces/mean-ball-render-anchor-validation.json")
add_executable(pirate_camera_tests tests/pirate_camera_tests.cpp)
target_include_directories(pirate_camera_tests PRIVATE src)
target_link_libraries(pirate_camera_tests PRIVATE nlohmann_json::nlohmann_json)
target_compile_options(pirate_camera_tests PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME pirate_camera_original COMMAND pirate_camera_tests "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-camera-original.json")
if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-camera-sdl-original.json")
  add_test(NAME pirate_camera_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/pirate_camera_sdl_test.py" "$<TARGET_FILE:slamview>")
  set_tests_properties(pirate_camera_sdl PROPERTIES TIMEOUT 120)
endif()
add_executable(pirate_scene_tests tests/pirate_scene_tests.cpp)
target_include_directories(pirate_scene_tests PRIVATE src)
target_link_libraries(pirate_scene_tests PRIVATE nlohmann_json::nlohmann_json)
add_test(NAME pirate_nudge_presentation COMMAND pirate_scene_tests "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-nudge-presentation-original.json")


# Original assets and generated lift remain local; enable the oracle regression
# only when its user-provided inputs are available.
if(TARGET mean_flipper_lift AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/pe-data.bin"
   AND EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
  find_package(Python3 QUIET COMPONENTS Interpreter)
  if(Python3_Interpreter_FOUND)
    if(TARGET mean_multiball_probe)
      add_test(NAME mean_multiball_oracle COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_SOURCE_DIR}/tools/verify_mean_multiball_replay.py" "$<TARGET_FILE:mean_multiball_probe>")
      add_test(NAME mean_multiball_flight_oracle COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_SOURCE_DIR}/tools/verify_mean_multiball_replay.py" "$<TARGET_FILE:mean_multiball_flight_probe>" --flight)
      add_test(NAME mean_multiball_gameplay_bundle COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_SOURCE_DIR}/tools/probe_mean_routes.py" --scenario multiball --steps 225000 --require-active --require-multiball
        --output "${CMAKE_SOURCE_DIR}/analysis/traces/mean-multiball-gameplay-validation.json")
    endif()
    add_test(NAME mean_mode6_gameplay_bundle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/probe_mean_routes.py" --scenario mode6 --steps 400000 --require-active --require-mode6
      --output "${CMAKE_SOURCE_DIR}/analysis/traces/mean-mode6-gameplay-validation.json")
    add_test(NAME mean_mode4_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_replay.py" "$<TARGET_FILE:mean_mode4_probe>")
    add_test(NAME mean_mode4_transfer_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_replay.py" "$<TARGET_FILE:mean_mode4_transfer_probe>" --transfer)
    add_test(NAME windows_dmd_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_windows_dmd_replay.py" "$<TARGET_FILE:windows_dmd_probe>")
    add_test(NAME mean_minigame_input_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame_input_replay.py" "$<TARGET_FILE:mean_minigame_input_probe>")
    if(TARGET mean_minigame_lift AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-minigame-prepared/image.bin")
      add_test(NAME mean_minigame_terminal_oracle COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame_replay.py"
        "$<TARGET_FILE:mean_minigame_terminal_probe>" --terminal)
      add_test(NAME mean_minigame_oracle COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame_replay.py" "$<TARGET_FILE:mean_minigame_probe>")
      add_test(NAME mean_minigame_gameplay_bundle COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_SOURCE_DIR}/tools/probe_mean_routes.py"
        --scenario minigame --steps 200000 --require-active --require-capture --require-minigame
        --output "${CMAKE_SOURCE_DIR}/analysis/traces/mean-minigame-gameplay-validation.json")
    endif()

    add_test(NAME mean_mode_island_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode_replay.py"
      --probe "$<TARGET_FILE:mean_mode_island_probe>"
      --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/mean-mode-island-fixture.json")
    add_test(NAME mean_upper_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_upper_replay.py"
      --probe "$<TARGET_FILE:mean_upper_cycle_probe>"
      --fixtures "${CMAKE_SOURCE_DIR}/analysis/traces")
    add_test(NAME mean_upper_reward_cycle_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_upper_reward_cycle_replay.py"
      "$<TARGET_FILE:mean_upper_reward_cycle_probe>")
    add_test(NAME mean_reward3_display_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_reward_display_replay.py"
      "$<TARGET_FILE:mean_reward3_display_probe>" --reward3)
    add_test(NAME mean_reward_display_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_reward_display_replay.py"
      "$<TARGET_FILE:mean_reward_display_probe>")
    add_test(NAME mean_reward2_display_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_reward_display_replay.py"
      "$<TARGET_FILE:mean_reward_display_probe>" --reward2)
    add_test(NAME mean_upper_reward_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode_replay.py"
      --probe "$<TARGET_FILE:mean_upper_reward_probe>"
      --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/mean-upper-rewards-fixture.json")
    add_test(NAME mean_mode_begin_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_begin_replay.py"
      --probe "$<TARGET_FILE:mean_mode5_begin_probe>"
      --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/mean-mode5-begin-fixture.json")
    add_test(NAME mean_sixth_capture_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_capture_replay.py"
      --probe "$<TARGET_FILE:mean_capture_tick_probe>"
      --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/mean-sixth-capture-fixture.json")
    add_test(NAME mean_capture_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_capture_replay.py"
      --probe "$<TARGET_FILE:mean_capture_tick_probe>"
      --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/mean-capture-release-cycle.json")
    add_test(NAME mean_contact_oracle COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_simulation.py"
      --probe "$<TARGET_FILE:mean_sim_probe>"
      --trace "${CMAKE_SOURCE_DIR}/analysis/traces/mean-contact-live-100.json")
    if(EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/normals-4.bin")
      add_test(NAME mean_gameplay_bundle COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_SOURCE_DIR}/tools/probe_mean_routes.py"
        --scenario mode5 --steps 120000 --require-active --require-capture --require-mode5 --require-reward
        --output "${CMAKE_SOURCE_DIR}/analysis/traces/mean-gameplay-bundle-validation.json")
    endif()
  endif()
endif()

add_executable(mean_turn_clock_probe tests/mean_turn_clock_probe.cpp)
target_link_libraries(mean_turn_clock_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_turn_clock_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_turn_clock.py" --probe "$<TARGET_FILE:mean_turn_clock_probe>")
add_executable(mean_turn_entry_probe tests/mean_turn_entry_probe.cpp)
target_link_libraries(mean_turn_entry_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_turn_entry_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_turn_entry.py" --native "$<TARGET_FILE:mean_turn_entry_probe>" --replay)

if(TARGET mean_flipper_lift AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/pe-data.bin"
   AND EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
  add_test(NAME mean_turn_gameplay_bundle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/probe_mean_routes.py" --steps 400000 --require-active --require-turn --require-material5 --output "${CMAKE_SOURCE_DIR}/analysis/traces/mean-turn-gameplay-validation.json")
endif()

add_executable(mean_restart_gate_probe tests/mean_restart_gate_probe.cpp)
target_link_libraries(mean_restart_gate_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_restart_gate_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_restart_gate.py" --native "$<TARGET_FILE:mean_restart_gate_probe>")

add_executable(mean_game_end_probe tests/mean_game_end_probe.cpp)
target_link_libraries(mean_game_end_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_game_end_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_game_end.py" --native "$<TARGET_FILE:mean_game_end_probe>")

if(TARGET mean_flipper_lift AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/pe-data.bin"
   AND EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
  add_test(NAME mean_lifecycle_gameplay_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_lifecycle_integration.py" --native "$<TARGET_FILE:mean_sim_probe>")
endif()

add_executable(mean_bonus_display_probe tests/mean_bonus_display_probe.cpp)
target_link_libraries(mean_bonus_display_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_bonus_display_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_bonus_display.py" --native "$<TARGET_FILE:mean_bonus_display_probe>" --replay)
add_executable(mean_bonus_pixels_probe tests/mean_bonus_pixels_probe.cpp)
target_link_libraries(mean_bonus_pixels_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MAIN.DAT")
  add_test(NAME mean_bonus_pixels_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_bonus_pixels.py" --native "$<TARGET_FILE:mean_bonus_pixels_probe>" --dat "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MAIN.DAT" --mean-dat "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
endif()

find_path(XMP_INCLUDE_DIR xmp.h HINTS "${CMAKE_SOURCE_DIR}/build/libxmp/include")
find_library(XMP_LIBRARY NAMES xmp HINTS "${CMAKE_SOURCE_DIR}/build/libxmp-stim-build" "${CMAKE_SOURCE_DIR}/build/libxmp-build")
if(XMP_INCLUDE_DIR AND XMP_LIBRARY)
  add_library(slamaudio src/audio/stim_player.cpp src/audio/native_audio.cpp src/audio/mean_sound_assets.cpp src/audio/mean_sample_mixer.cpp src/audio/pirate_sound_assets.cpp src/audio/space_sound_assets.cpp src/audio/demon_sound_assets.cpp)
  target_include_directories(slamaudio PUBLIC src "${XMP_INCLUDE_DIR}")
  target_link_libraries(slamaudio PUBLIC SDL3::SDL3 "${XMP_LIBRARY}")
  target_compile_options(slamaudio PRIVATE -Wall -Wextra -Wpedantic)
  target_link_libraries(slamview PRIVATE slamaudio)
  target_compile_definitions(slamview PRIVATE SLAM_AUDIO_XMP=1)
  add_executable(demon_audio_assets tests/demon_audio_assets.cpp)
  target_link_libraries(demon_audio_assets PRIVATE slamaudio slamassets nlohmann_json::nlohmann_json)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin")
    add_test(NAME demon_audio_assets COMMAND demon_audio_assets "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/DEMON.DAT" "${CMAKE_SOURCE_DIR}/analysis/demon-audio-profile.json")
  endif()
  add_executable(space_audio_assets tests/space_audio_assets.cpp)
  target_link_libraries(space_audio_assets PRIVATE slamaudio slamassets nlohmann_json::nlohmann_json)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin")
    add_test(NAME space_audio_assets COMMAND space_audio_assets "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT" "${CMAKE_SOURCE_DIR}/analysis/space-audio-reuse.json")
    add_test(NAME space_audio_events COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_space_audio.py")
    set_tests_properties(space_audio_events PROPERTIES TIMEOUT 180)
  endif()
  if(TARGET slamslice)
    target_link_libraries(slamslice PRIVATE slamaudio)
    target_compile_definitions(slamslice PRIVATE SLAM_AUDIO_XMP=1)
  endif()
else()
  message(STATUS "libxmp not found: native music playback disabled")
endif()
if(TARGET slamaudio)
  if(TARGET pirate_session AND EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-audio-events.json")
    add_executable(pirate_audio_probe tests/pirate_audio_probe.cpp)
    target_link_libraries(pirate_audio_probe PRIVATE pirate_session slamaudio nlohmann_json::nlohmann_json)
    target_compile_options(pirate_audio_probe PRIVATE -Wall -Wextra -Wpedantic)
    add_test(NAME pirate_knife_auto_audio COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_audio.py" --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-knife-auto-audio.json" --all-sdl-cases --work "${CMAKE_SOURCE_DIR}/build/oracle/pirate-knife-auto-audio" --native "$<TARGET_FILE:pirate_audio_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_knife_auto_audio PROPERTIES TIMEOUT 120)
    add_test(NAME pirate_mermaid_audio COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_audio.py" --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-mermaid-audio.json" --all-sdl-cases --work "${CMAKE_SOURCE_DIR}/build/oracle/pirate-mermaid-audio" --native "$<TARGET_FILE:pirate_audio_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_mermaid_audio PROPERTIES TIMEOUT 180)
    add_test(NAME pirate_window_audio COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_audio.py" --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-window-audio.json" --all-sdl-cases --work "${CMAKE_SOURCE_DIR}/build/oracle/pirate-window-audio" --native "$<TARGET_FILE:pirate_audio_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_window_audio PROPERTIES TIMEOUT 120)
    add_test(NAME pirate_extra_use_audio COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_audio.py" --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-extra-use-audio.json" --all-sdl-cases --work "${CMAKE_SOURCE_DIR}/build/oracle/pirate-extra-use-audio" --native "$<TARGET_FILE:pirate_audio_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_extra_use_audio PROPERTIES TIMEOUT 120)
    add_test(NAME pirate_multiplier_payout_audio COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_audio.py" --fixture "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-multiplier-payout-audio.json" --cases bonus-multiplier-payout --work "${CMAKE_SOURCE_DIR}/build/oracle/pirate-payout-audio" --native "$<TARGET_FILE:pirate_audio_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_multiplier_payout_audio PROPERTIES TIMEOUT 90)
    add_test(NAME pirate_audio_original_native_sdl COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_audio.py" --native "$<TARGET_FILE:pirate_audio_probe>" --viewer "$<TARGET_FILE:slamview>")
    set_tests_properties(pirate_audio_original_native_sdl PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}" TIMEOUT 240 COST 120)
  endif()
  add_executable(stim_audio_probe tests/stim_audio_probe.cpp)
  target_link_libraries(stim_audio_probe PRIVATE slamaudio)
  add_executable(native_audio_probe tests/native_audio_probe.cpp)
  target_link_libraries(native_audio_probe PRIVATE slamaudio)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/Music.Bin" AND EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/IntroMusic.Bin")
    add_test(NAME native_music_pcm COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_native_music.py" --native "$<TARGET_FILE:stim_audio_probe>")
    add_test(NAME native_audio_queue COMMAND native_audio_probe "${CMAKE_SOURCE_DIR}/build/decoded/Music.Bin")
    set_tests_properties(native_audio_queue PROPERTIES ENVIRONMENT "SDL_AUDIODRIVER=dummy")
  endif()
endif()

if(TARGET pirate_step_lift)
  add_executable(demon_sfx_callback_probe tests/demon_sfx_callback_probe.cpp)
  target_link_libraries(demon_sfx_callback_probe PRIVATE pirate_step_lift nlohmann_json::nlohmann_json)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-runtime.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-dat.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/summary.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE")
    add_test(NAME demon_sfx_callback_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_demon_sfx_callback.py"
      --native "$<TARGET_FILE:demon_sfx_callback_probe>"
      --output "${CMAKE_CURRENT_BINARY_DIR}/demon-sfx-callback")
  endif()
endif()

if(TARGET slamslice AND EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/DEMON.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/base-rules-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/kickback-off-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/race-variants-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/twice-cycles-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/legal-game-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/video-wolf-shoot-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-base-rules-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-kickback-off-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-race-variants-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-twice-cycles-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-legal-game-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-video-wolf-shoot-rewards.json")
  add_test(NAME retail_sfx_coverage_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_retail_sfx_coverage.py" --native "$<TARGET_FILE:slamslice>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/retail-sfx-coverage")
  set_tests_properties(retail_sfx_coverage_original PROPERTIES TIMEOUT 300)
endif()

if(TARGET pirate_audio_probe AND TARGET slamview AND EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-knife-auto-audio.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-audio-pcm.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-dat.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT")
  add_test(NAME pirate_sfx_coverage_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_pirate_sfx_coverage.py"
    --native "$<TARGET_FILE:pirate_audio_probe>" --viewer "$<TARGET_FILE:slamview>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/pirate-sfx-coverage")
  set_tests_properties(pirate_sfx_coverage_original PROPERTIES TIMEOUT 300)
endif()

if(TARGET slamaudio)
  target_sources(slamaudio PRIVATE src/audio/mean_music_sequencer.cpp)
  add_executable(mean_music_sequencer_probe tests/mean_music_sequencer_probe.cpp)
  target_link_libraries(mean_music_sequencer_probe PRIVATE slamaudio)
  add_test(NAME mean_music_sequencer COMMAND mean_music_sequencer_probe)
endif()

if(TARGET slamaudio)
  add_executable(mean_sound_assets_probe tests/mean_sound_assets_probe.cpp)
  target_link_libraries(mean_sound_assets_probe PRIVATE slamaudio)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
    add_test(NAME native_mean_banks COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_native_mean_banks.py" --native "$<TARGET_FILE:mean_sound_assets_probe>" --dat "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
    set_tests_properties(native_mean_banks PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
  endif()
endif()

if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/pe-data.bin")
  add_test(NAME mean_audio_base_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_audio_base.py")
endif()
if(TARGET slamaudio)
  add_executable(mean_sample_mixer_probe tests/mean_sample_mixer_probe.cpp)
  target_link_libraries(mean_sample_mixer_probe PRIVATE slamaudio)
  add_test(NAME mean_sample_mixer COMMAND mean_sample_mixer_probe)
endif()
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/pe-data.bin")
  add_test(NAME mean_sample_consumer_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_sample_consumer.py")
endif()
if(TARGET native_audio_probe AND EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/Music.Bin" AND EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
  add_test(NAME native_sfx_queue COMMAND native_audio_probe "${CMAKE_SOURCE_DIR}/build/decoded/Music.Bin" "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
  set_tests_properties(native_sfx_queue PROPERTIES ENVIRONMENT "SDL_AUDIODRIVER=dummy")
endif()
if(TARGET slamaudio)
  add_executable(mean_sample_resampler_probe tests/mean_sample_resampler_probe.cpp)
  target_link_libraries(mean_sample_resampler_probe PRIVATE slamaudio nlohmann_json::nlohmann_json)
  add_test(NAME mean_sample_resampler_pcm COMMAND mean_sample_resampler_probe "${CMAKE_SOURCE_DIR}/analysis/traces/mean-sample-resampler-original.json")
endif()
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/pe-data.bin")
  add_test(NAME mean_sample_resampler_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_sample_resampler.py")
endif()
add_executable(mean_material5_probe tests/mean_material5_probe.cpp)
target_link_libraries(mean_material5_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/pe-data.bin")
  add_test(NAME mean_material5_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5.py" --native "$<TARGET_FILE:mean_material5_probe>")
endif()
add_executable(mean_material5_display_probe tests/mean_material5_display_probe.cpp)
target_link_libraries(mean_material5_display_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/pe-data.bin")
  add_test(NAME mean_material5_display_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
endif()

add_executable(mean_award_bank_probe tests/mean_award_bank_probe.cpp)
target_link_libraries(mean_award_bank_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
  add_test(NAME mean_award_bank_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_award_bank.py" --native "$<TARGET_FILE:mean_award_bank_probe>")
endif()
add_executable(mean_side_extra_probe tests/mean_side_extra_probe.cpp)
target_link_libraries(mean_side_extra_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
  add_test(NAME mean_side_extra_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_side_extra.py" --native "$<TARGET_FILE:mean_side_extra_probe>")
endif()
add_executable(mean_switch_reward_probe tests/mean_switch_reward_probe.cpp)
target_link_libraries(mean_switch_reward_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_switch_reward_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_switch_reward.py" --native "$<TARGET_FILE:mean_switch_reward_probe>")
endif()
add_executable(mean_flipper_actions_probe tests/mean_flipper_actions_probe.cpp)
target_link_libraries(mean_flipper_actions_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_flipper_actions_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_flipper_actions.py" --native "$<TARGET_FILE:mean_flipper_actions_probe>")
endif()

add_executable(mean_mode4_input_probe tests/mean_mode4_input_probe.cpp)
target_link_libraries(mean_mode4_input_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_executable(mean_state7_probe tests/mean_state7_probe.cpp)
target_link_libraries(mean_state7_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_mode4_input_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_input.py" --native "$<TARGET_FILE:mean_mode4_input_probe>")
 add_test(NAME mean_state7_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_state7.py" "$<TARGET_FILE:mean_state7_probe>")
 add_test(NAME mean_mode4_display_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
endif()

add_executable(mean_mode4_clock_probe tests/mean_mode4_clock_probe.cpp)
target_link_libraries(mean_mode4_clock_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_mode4_clock_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_clock.py" --native "$<TARGET_FILE:mean_mode4_clock_probe>")
endif()

add_executable(mean_mode4_capture_probe tests/mean_mode4_capture_probe.cpp)
target_link_libraries(mean_mode4_capture_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_mode4_capture_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_capture.py" "$<TARGET_FILE:mean_mode4_capture_probe>")
endif()

add_executable(mean_mode4_idle_probe tests/mean_mode4_idle_probe.cpp)
target_link_libraries(mean_mode4_idle_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_mode4_idle_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_idle.py" --native "$<TARGET_FILE:mean_mode4_idle_probe>")
endif()

add_executable(mean_mode4_switch_probe tests/mean_mode4_switch_probe.cpp)
target_link_libraries(mean_mode4_switch_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_mode4_switch_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_switch.py" "$<TARGET_FILE:mean_mode4_switch_probe>")
endif()

add_test(NAME mean_mode4_gameplay_bundle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_gameplay.py" "$<TARGET_FILE:mean_sim_probe>")

add_executable(mean_mode4_right_entry_probe tests/mean_mode4_right_entry_probe.cpp)
target_link_libraries(mean_mode4_right_entry_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_executable(mean_mode4_events_probe tests/mean_mode4_events_probe.cpp)
target_link_libraries(mean_mode4_events_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_mode4_right_entry_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_right_entry.py" "$<TARGET_FILE:mean_mode4_right_entry_probe>")
 add_test(NAME mean_mode4_events_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_events.py" --native "$<TARGET_FILE:mean_mode4_events_probe>")
endif()

add_executable(mean_minigame2_input_probe tests/mean_minigame2_input_probe.cpp)
target_link_libraries(mean_minigame2_input_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_minigame2_input_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame2_input.py" --native "$<TARGET_FILE:mean_minigame2_input_probe>")

add_executable(mean_mode4_phase1_probe tests/mean_mode4_phase1_probe.cpp)
target_link_libraries(mean_mode4_phase1_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode4_phase1_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_phase1.py" --native "$<TARGET_FILE:mean_mode4_phase1_probe>")
add_test(NAME mean_mode4_right_gameplay_bundle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_right_gameplay.py" "$<TARGET_FILE:mean_sim_probe>")
if(TARGET mean_minigame_lift AND EXISTS "${CMAKE_SOURCE_DIR}/build/mean-minigame2-prepared/image.bin")
 add_executable(mean_minigame2_probe tests/mean_minigame2_probe.cpp)
 target_link_libraries(mean_minigame2_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
 add_test(NAME mean_minigame2_oracle COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame2_replay.py" "$<TARGET_FILE:mean_minigame2_probe>")
endif()

add_executable(mean_right_gate_probe tests/mean_right_gate_probe.cpp)
target_link_libraries(mean_right_gate_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_executable(mean_right_progress_probe tests/mean_right_progress_probe.cpp)
target_link_libraries(mean_right_progress_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_right_gate_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_right_gate.py" "$<TARGET_FILE:mean_right_gate_probe>")
add_test(NAME mean_right_progress_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_right_progress.py" "$<TARGET_FILE:mean_right_progress_probe>")

add_executable(ball_occlusion_probe tests/ball_occlusion_probe.cpp)
target_link_libraries(ball_occlusion_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME ball_occlusion_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_ball_occlusion.py" "$<TARGET_FILE:ball_occlusion_probe>")
add_executable(mean_right_path_probe tests/mean_right_path_probe.cpp)
target_link_libraries(mean_right_path_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_test(NAME mean_right_path_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_right_path.py" "$<TARGET_FILE:mean_right_path_probe>")
set_tests_properties(mean_right_path_oracle PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")

add_test(NAME mean_switch_boundary_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_switch_boundary.py")

add_executable(mean_right_cancel_probe tests/mean_right_cancel_probe.cpp)
target_link_libraries(mean_right_cancel_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_right_cancel_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_right_cancel.py" "$<TARGET_FILE:mean_right_cancel_probe>")

add_executable(mean_point_force_probe tests/mean_point_force_probe.cpp)
target_link_libraries(mean_point_force_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_point_force_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_point_force.py" "$<TARGET_FILE:mean_point_force_probe>")

add_test(NAME mean_point_force_flight_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_point_force_flight.py" "$<TARGET_FILE:mean_right_path_probe>")
set_tests_properties(mean_point_force_flight_oracle PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")

add_test(NAME mean_point_force_gameplay COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_point_force_gameplay.py" "$<TARGET_FILE:mean_sim_probe>")

add_test(NAME mean_mode4_phase1_numeric_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_phase1.py" --native "$<TARGET_FILE:mean_mode4_phase1_probe>" --numeric)

add_executable(mean_phase1_chain_probe tests/mean_phase1_chain_probe.cpp)
target_link_libraries(mean_phase1_chain_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_phase1_chain_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_phase1_chain.py" --native "$<TARGET_FILE:mean_phase1_chain_probe>")
add_executable(mean_phase1_gameplay_probe tests/mean_phase1_gameplay_probe.cpp)
target_link_libraries(mean_phase1_gameplay_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_test(NAME mean_phase1_gameplay COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_phase1_gameplay.py" "$<TARGET_FILE:mean_phase1_gameplay_probe>")

add_executable(mean_shared_reward_probe tests/mean_shared_reward_probe.cpp)
target_link_libraries(mean_shared_reward_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_shared_reward_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_shared_reward.py" "$<TARGET_FILE:mean_shared_reward_probe>")
add_executable(pirate_engine_probe tests/pirate_engine_probe.cpp)
target_link_libraries(pirate_engine_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME pirate_engine_validation COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/validate_pirate_engine.py")

add_test(NAME mean_rally_target_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_rally_target.py" "$<TARGET_FILE:mean_shared_reward_probe>")
add_test(NAME mean_manual_reward_chains COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_manual_reward_chains.py" "$<TARGET_FILE:mean_shared_reward_probe>")
add_executable(mean_shared_gameplay_probe tests/mean_shared_gameplay_probe.cpp)
target_link_libraries(mean_shared_gameplay_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_shared_gameplay COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_shared_gameplay.py" "$<TARGET_FILE:mean_shared_gameplay_probe>")
add_executable(mean_right_common_probe tests/mean_right_common_probe.cpp)
target_link_libraries(mean_right_common_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_right_common_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_right_common.py" "$<TARGET_FILE:mean_right_common_probe>")

add_executable(table_profile_probe tests/table_profile_probe.cpp)
target_link_libraries(table_profile_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME table_profile_layer_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_table_profiles.py" "$<TARGET_FILE:table_profile_probe>")
add_executable(pirate_contact_probe tests/pirate_contact_probe.cpp)
target_link_libraries(pirate_contact_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_executable(pirate_wall_probe tests/pirate_wall_probe.cpp)
target_link_libraries(pirate_wall_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_test(NAME pirate_contact_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_contact.py")
add_test(NAME pirate_wall_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_pirate_wall.py" "$<TARGET_FILE:pirate_wall_probe>")

if(TARGET mean_flipper_lift)
 add_executable(table_flipper_probe tests/table_flipper_probe.cpp)
 target_link_libraries(table_flipper_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
 add_test(NAME table_flipper_pose_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_table_flippers.py" --native "$<TARGET_FILE:table_flipper_probe>")
endif()
if(EXISTS "${CMAKE_SOURCE_DIR}/build/generated/retail_flippers.cpp")
 add_library(retail_flipper_lift build/generated/retail_flippers.cpp)
 target_include_directories(retail_flipper_lift PUBLIC src)
 add_executable(retail_flipper_contact_probe tests/retail_flipper_contact_probe.cpp)
 target_link_libraries(slamassets PUBLIC retail_flipper_lift)
 target_compile_definitions(slamassets PUBLIC SLAM_RETAIL_FLIPPER_LIFT=1)
 target_link_libraries(retail_flipper_contact_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
 add_test(NAME retail_flipper_contact_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_retail_flipper_contacts.py" "$<TARGET_FILE:retail_flipper_contact_probe>")
endif()

add_test(NAME mean_shared_reward_display_oracle COMMAND "${CMAKE_COMMAND}" -E env SLAM_SHARED_DISPLAY_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")

add_test(NAME mean_rally_display_oracle COMMAND "${CMAKE_COMMAND}" -E env SLAM_RALLY_DISPLAY_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")

add_executable(mean_mode4_upper_probe tests/mean_mode4_upper_probe.cpp)
target_link_libraries(mean_mode4_upper_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode4_upper_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_upper.py" "$<TARGET_FILE:mean_mode4_upper_probe>")
add_test(NAME mean_finite_input_coverage COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_finite_coverage.py" "$<TARGET_FILE:mean_sim_probe>")

add_executable(mean_capture_flight_probe tests/mean_capture_flight_probe.cpp)
target_link_libraries(mean_capture_flight_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_executable(mean_restart_reuse_probe tests/mean_restart_reuse_probe.cpp)
target_link_libraries(mean_restart_reuse_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

add_test(NAME mean_capture_flight_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_capture_flight.py" "$<TARGET_FILE:mean_capture_flight_probe>" "$<TARGET_FILE:mean_right_path_probe>")
add_test(NAME mean_restart_reuse_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_restart_reuse.py" "$<TARGET_FILE:mean_restart_reuse_probe>")
set_tests_properties(mean_restart_reuse_oracle PROPERTIES DEPENDS mean_capture_flight_oracle)

add_executable(mean_drain_chain_probe tests/mean_drain_chain_probe.cpp)
target_link_libraries(mean_drain_chain_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_drain_chain_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_drain_chain.py" "$<TARGET_FILE:mean_drain_chain_probe>")

add_executable(mean_bonus_input_probe tests/mean_bonus_input_probe.cpp)
target_link_libraries(mean_bonus_input_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_bonus_input_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_bonus_input.py" "$<TARGET_FILE:mean_bonus_input_probe>")
add_test(NAME mean_runtime_cadence_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_runtime_cadence.py")
add_executable(mean_bonus_skip_probe tests/mean_bonus_skip_probe.cpp)
target_link_libraries(mean_bonus_skip_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_bonus_skip_gameplay COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_bonus_skip.py" "$<TARGET_FILE:mean_bonus_skip_probe>")

target_sources(slamassets PRIVATE src/renderer/mean_camera.cpp)
add_executable(mean_camera_probe tests/mean_camera_probe.cpp)
target_link_libraries(mean_camera_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_camera_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_camera.py" "$<TARGET_FILE:mean_camera_probe>")
add_test(NAME mean_runtime_transition_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_runtime_transition.py")
set_tests_properties(mean_drain_chain_oracle mean_runtime_transition_oracle PROPERTIES DEPENDS mean_capture_flight_oracle)
add_test(NAME mean_natural_advanced_gameplay COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_natural_modes.py" "$<TARGET_FILE:mean_sim_probe>" "$<TARGET_FILE:mean_speed_finite>")
add_test(NAME mean_upper_announcement_oracle COMMAND "${CMAKE_COMMAND}" -E env SLAM_UPPER_DISPLAY_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_test(NAME mean_upper_announcement_gameplay COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --demo-minigame --natural-mode-preview upper --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-upper-announcement.bmp")

add_test(NAME mean_upper_modes_oracle COMMAND "${CMAKE_COMMAND}" -E env SLAM_UPPER_MODES_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_test(NAME mean_upper_modes_gameplay COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview upper-mode --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-upper-mode.bmp")
add_executable(mean_display_scheduler_probe tests/mean_display_scheduler_probe.cpp)
target_link_libraries(mean_display_scheduler_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_display_scheduler_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_display_scheduler.py" --native "$<TARGET_FILE:mean_display_scheduler_probe>")
add_executable(mean_display_overlap_probe tests/mean_display_overlap_probe.cpp)
target_link_libraries(mean_display_overlap_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_display_overlap_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_display_overlap.py" --native "$<TARGET_FILE:mean_display_overlap_probe>")

add_test(NAME mean_reward_mode6_pixels_oracle COMMAND "${CMAKE_COMMAND}" -E env SLAM_REWARD_PIXELS_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_test(NAME mean_reward_owner_oracle COMMAND "${CMAKE_COMMAND}" -E env SLAM_REWARD_OWNER_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_display_overlap.py" --native "$<TARGET_FILE:mean_display_overlap_probe>")
add_test(NAME mean_mode6_visible_gameplay COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --mode6-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-mode6-dmd.bmp")

add_test(NAME mean_display_owner_boundaries_oracle COMMAND "${CMAKE_COMMAND}" -E env SLAM_DISPLAY_OWNERS_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_display_scheduler.py" --native "$<TARGET_FILE:mean_display_scheduler_probe>")

target_sources(slamassets PRIVATE src/rules/mean_return_pass.cpp)
add_executable(mean_return_pass_probe tests/mean_return_pass_probe.cpp)
target_link_libraries(mean_return_pass_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_return_pass_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_return_pass.py" "$<TARGET_FILE:mean_return_pass_probe>")
add_test(NAME mean_return_pass_display_oracle COMMAND "${CMAKE_COMMAND}" -E env SLAM_RETURN_PASS_DISPLAY_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_executable(mean_return_pass_gameplay tests/mean_return_pass_gameplay.cpp)
target_link_libraries(mean_return_pass_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_return_pass_gameplay COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_return_pass_gameplay.py" "$<TARGET_FILE:mean_return_pass_gameplay>")
add_test(NAME mean_return_pass_visible_gameplay COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --return-pass-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-return-pass.bmp")
add_executable(mean_return_pass_cycle_probe tests/mean_return_pass_cycle_probe.cpp)
target_link_libraries(mean_return_pass_cycle_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_return_pass_cycle_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_return_pass_cycle.py" --native "$<TARGET_FILE:mean_return_pass_cycle_probe>")
add_executable(mean_player_record_probe tests/mean_player_record_probe.cpp)
target_link_libraries(mean_player_record_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_player_record_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_player_record.py" "$<TARGET_FILE:mean_player_record_probe>")
add_executable(mean_minigame2_player_gameplay tests/mean_minigame2_player_gameplay.cpp)
target_link_libraries(mean_minigame2_player_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_minigame2_player_gameplay COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame2_player_gameplay.py" "$<TARGET_FILE:mean_minigame2_player_gameplay>")
add_test(NAME mean_natural_mode6_eight_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview multiball --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-natural-eight.bmp")

target_sources(slamassets PRIVATE src/dmd/mean_minigame_text.cpp)
add_executable(mean_minigame_text_probe tests/mean_minigame_text_probe.cpp)
target_link_libraries(mean_minigame_text_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_minigame_text_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame_text.py" --native "$<TARGET_FILE:mean_minigame_text_probe>")
add_test(NAME mean_minigame2_terminal_pixels_oracle COMMAND "${CMAKE_COMMAND}" -E env SLAM_MINIGAME2_TERMINAL_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_test(NAME mean_minigame2_success_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --minigame2-result-preview success --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-minigame2-success.bmp")
add_test(NAME mean_minigame2_failure_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --minigame2-result-preview failure --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-minigame2-failure.bmp")
add_test(NAME mean_minigame2_goal_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --minigame2-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-minigame2-goal.bmp")

if(TARGET mean_minigame2_probe AND EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_minigame_samples_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame2.py" "$<TARGET_FILE:mean_minigame2_probe>" --sounds)
endif()

if(TARGET mean_minigame2_probe AND EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python")
 add_test(NAME mean_minigame_composed_pixels_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame_pixels.py" "$<TARGET_FILE:mean_minigame2_probe>")
endif()

add_test(NAME mean_minigame1_terminal_pixels_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
set_tests_properties(mean_minigame1_terminal_pixels_oracle PROPERTIES ENVIRONMENT "SLAM_MINIGAME1_TERMINAL_ONLY=1")

add_test(NAME mean_minigame1_result_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --demo-minigame --minigame-result-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-minigame1-result.bmp")
add_executable(mean_minigame1_result_gameplay tests/mean_minigame1_result_gameplay.cpp)
target_link_libraries(mean_minigame1_result_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_minigame1_result_gameplay COMMAND mean_minigame1_result_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-minigame1-terminal-pixels-original.json")
set_tests_properties(mean_minigame1_result_gameplay PROPERTIES DEPENDS mean_minigame1_terminal_pixels_oracle)

add_executable(mean_minigame1_winning_lift tests/mean_minigame1_winning_lift.cpp)
target_link_libraries(mean_minigame1_winning_lift PRIVATE mean_minigame_lift nlohmann_json::nlohmann_json)
add_test(NAME mean_minigame1_winning_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame1_winning_input.py" "$<TARGET_FILE:mean_minigame1_winning_lift>")
add_executable(mean_minigame1_winning_gameplay tests/mean_minigame1_winning_gameplay.cpp)
target_link_libraries(mean_minigame1_winning_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_minigame1_winning_gameplay COMMAND mean_minigame1_winning_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-minigame1-winning-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-minigame1-terminal-pixels-original.json")
set_tests_properties(mean_minigame1_winning_gameplay PROPERTIES DEPENDS "mean_minigame1_winning_original;mean_minigame1_terminal_pixels_oracle")
add_test(NAME mean_minigame1_win_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --demo-minigame --minigame-win-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-minigame1-win.bmp")

add_test(NAME mean_minigame_retail_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_minigame_retail.py" "$<TARGET_FILE:mean_minigame1_winning_lift>")
add_test(NAME mean_minigame_retail_terminal_pixels COMMAND "${CMAKE_COMMAND}" -E env SLAM_MINIGAME_RETAIL_TERMINAL_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_test(NAME mean_minigame_retail_gameplay COMMAND mean_minigame1_winning_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-minigame1-winning-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-minigame-retail-terminal-pixels.json" retail)
set_tests_properties(mean_minigame_retail_gameplay PROPERTIES DEPENDS "mean_minigame_retail_original;mean_minigame_retail_terminal_pixels")
add_test(NAME mean_minigame_retail_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --retail-minigame --minigame-win-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-minigame-retail-win.bmp")

add_test(NAME mean_minigame_retail_abort_gameplay COMMAND mean_minigame1_winning_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-minigame1-winning-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-minigame-retail-terminal-pixels.json" retail-abort)
set_tests_properties(mean_minigame_retail_abort_gameplay PROPERTIES DEPENDS "mean_minigame_retail_original;mean_minigame_retail_terminal_pixels")

add_test(NAME mean_rule_reuse_oracle COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_rule_reuse.py")
add_test(NAME mean_launcher_retail_win COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --minigame-win-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-launcher-retail-win.bmp")

add_executable(mean_minigame_finite tests/mean_minigame_finite.cpp)
target_link_libraries(mean_minigame_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_minigame_finite COMMAND mean_minigame_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-minigame1-winning-input.json")
add_test(NAME mean_natural_finite_minigame2_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview minigame2 --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-natural-finite-minigame2.bmp")
add_executable(mean_natural_minigame_oracle_probe tests/mean_natural_minigame_oracle_probe.cpp)
target_link_libraries(mean_natural_minigame_oracle_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_natural_minigame_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_natural_minigame.py" "$<TARGET_FILE:mean_natural_minigame_oracle_probe>")

target_sources(slamassets PRIVATE src/input/mean_nudge.cpp src/input/mean_nudge_tilt.cpp)
add_executable(mean_nudge_probe tests/mean_nudge_probe.cpp)
target_link_libraries(mean_nudge_probe PRIVATE slamassets)
add_test(NAME mean_nudge_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_nudge.py" --native "$<TARGET_FILE:mean_nudge_probe>")
add_executable(mean_nudge_tilt_probe tests/mean_nudge_tilt_probe.cpp)
target_link_libraries(mean_nudge_tilt_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_nudge_tilt_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_nudge_tilt.py" "$<TARGET_FILE:mean_nudge_tilt_probe>")
target_sources(slamassets PRIVATE src/input/mean_nudge_table.cpp)
add_executable(mean_nudge_table_probe tests/mean_nudge_table_probe.cpp)
target_link_libraries(mean_nudge_table_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_nudge_table_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_nudge_table.py" "$<TARGET_FILE:mean_nudge_table_probe>")
add_test(NAME mean_nudge_warning_pixels COMMAND "${CMAKE_COMMAND}" -E env SLAM_NUDGE_WARNING_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_test(NAME mean_nudge_warning_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --nudge-warning-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-nudge-warning.bmp")
if(TARGET slamaudio)
 add_executable(mean_tilt_audio tests/mean_tilt_audio.cpp)
 target_link_libraries(mean_tilt_audio PRIVATE slamaudio)
 add_test(NAME mean_tilt_audio COMMAND "${CMAKE_COMMAND}" -E env SDL_AUDIODRIVER=dummy "$<TARGET_FILE:mean_tilt_audio>" "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT")
endif()
add_executable(mean_capture_tilt_probe tests/mean_capture_tilt_probe.cpp)
target_link_libraries(mean_capture_tilt_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_capture_tilt_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_capture_tilt.py" "$<TARGET_FILE:mean_capture_tilt_probe>")
add_test(NAME mean_tilt_multiball_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_tilt_multiball.py" "$<TARGET_FILE:mean_multiball_probe>")
add_test(NAME mean_tilt_right_capture_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_tilt_right_capture.py" "$<TARGET_FILE:mean_mode4_right_entry_probe>")
add_executable(mean_tilt_upper_probe tests/mean_tilt_upper_probe.cpp)
target_link_libraries(mean_tilt_upper_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_tilt_upper_capture_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_tilt_upper_capture.py" "$<TARGET_FILE:mean_tilt_upper_probe>")
add_test(NAME mean_tilt_release_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --tilt-release-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-tilt-release.bmp")
add_executable(mean_tilt_gameplay tests/mean_tilt_gameplay.cpp)
target_link_libraries(mean_tilt_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_tilt_gameplay COMMAND mean_tilt_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")
set_tests_properties(mean_tilt_gameplay PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_executable(mean_nudge_gameplay tests/mean_nudge_gameplay.cpp)
target_link_libraries(mean_nudge_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_nudge_gameplay COMMAND mean_nudge_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")
set_tests_properties(mean_nudge_gameplay PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_executable(mean_special_tilt_gameplay tests/mean_special_tilt_gameplay.cpp)
target_link_libraries(mean_special_tilt_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_special_tilt_gameplay COMMAND mean_special_tilt_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")
set_tests_properties(mean_special_tilt_gameplay PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_test(NAME mean_tilt_mode6_side_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_tilt_mode6_side.py" "$<TARGET_FILE:mean_mode6_side_probe>")
add_executable(mean_mode5_left_tilt_probe tests/mean_mode5_left_tilt_probe.cpp)
target_link_libraries(mean_mode5_left_tilt_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode5_left_tilt_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode5_left_tilt.py" "$<TARGET_FILE:mean_mode5_left_tilt_probe>")
add_test(NAME mean_mode4_capture_tilt_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode4_capture_tilt.py" "$<TARGET_FILE:mean_mode4_capture_probe>")
add_executable(mean_capture_delay_probe tests/mean_capture_delay_probe.cpp)
target_link_libraries(mean_capture_delay_probe PRIVATE nlohmann_json::nlohmann_json)
target_include_directories(mean_capture_delay_probe PRIVATE src)
add_test(NAME mean_capture_delay_original COMMAND mean_capture_delay_probe "${CMAKE_SOURCE_DIR}/analysis/traces/mean-capture-delay-original.json")
add_test(NAME mean_mode5_award_pixels_original COMMAND "${CMAKE_COMMAND}" -E env SLAM_MODE5_LEFT_AWARD_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_executable(mean_mode5_award_gameplay tests/mean_mode5_award_gameplay.cpp)
target_link_libraries(mean_mode5_award_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode5_award_gameplay COMMAND mean_mode5_award_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")
set_tests_properties(mean_mode5_award_gameplay PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_test(NAME mean_mode5_award_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --mode5-award-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-mode5-award.bmp")
add_executable(port_options_test tests/port_options_test.cpp)
target_include_directories(port_options_test PRIVATE src)
target_link_libraries(port_options_test PRIVATE slamui SDL3::SDL3 nlohmann_json::nlohmann_json)
add_test(NAME port_options COMMAND port_options_test)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-image.bin")
  add_test(NAME pirate_special_frontend COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tests/pirate_special_sdl_test.py" "$<TARGET_FILE:slamview>")
endif()
add_executable(mean_dmd_palette_probe tests/mean_dmd_palette_probe.cpp)
target_include_directories(mean_dmd_palette_probe PRIVATE src)
add_test(NAME mean_dmd_palette_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_dmd_palette.py" --native "$<TARGET_FILE:mean_dmd_palette_probe>")
add_test(NAME mean_options_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --options-preview --mode5-award-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-options.bmp")
add_executable(display_layout_test tests/display_layout_test.cpp)
target_include_directories(display_layout_test PRIVATE src)
target_link_libraries(display_layout_test PRIVATE SDL3::SDL3)
add_test(NAME display_layout COMMAND display_layout_test)
add_test(NAME mean_options_menu_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --menu-preview --mode5-award-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-options-menu.bmp")
add_executable(audio_levels tests/audio_levels.cpp)
target_include_directories(audio_levels PRIVATE src)
add_test(NAME audio_levels COMMAND audio_levels)

add_executable(retail_final_mix_probe tests/retail_final_mix_probe.cpp src/audio/mean_sample_mixer.cpp)
target_include_directories(retail_final_mix_probe PRIVATE src)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE")
  add_test(NAME retail_final_mix_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_retail_final_mix.py"
    --native "$<TARGET_FILE:retail_final_mix_probe>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/retail-final-mix.json")
  add_test(NAME retail_game_mixer_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_retail_game_mixer.py"
    --output "${CMAKE_CURRENT_BINARY_DIR}/retail-game-mixer.json")
  add_test(NAME retail_loop_resampler_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_retail_loop_resampler.py"
    --output "${CMAKE_CURRENT_BINARY_DIR}/retail-loop-resampler.json")
endif()
add_executable(mean_highscores_test tests/mean_highscores_test.cpp)
target_include_directories(mean_highscores_test PRIVATE src)
target_link_libraries(mean_highscores_test PRIVATE SDL3::SDL3 nlohmann_json::nlohmann_json)
add_test(NAME mean_highscores COMMAND mean_highscores_test)
add_executable(mean_upper_delay_probe tests/mean_upper_delay_probe.cpp)
target_link_libraries(mean_upper_delay_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_upper_delay_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_upper_delay.py" "$<TARGET_FILE:mean_upper_delay_probe>")
target_sources(slamassets PRIVATE src/input/mean_mode_lock.cpp)
add_executable(mean_mode_lock_probe tests/mean_mode_lock_probe.cpp)
target_link_libraries(mean_mode_lock_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode_lock_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode_lock.py" "$<TARGET_FILE:mean_mode_lock_probe>")
add_test(NAME mean_mode_lock_pixels_original COMMAND "${CMAKE_COMMAND}" -E env SLAM_MODE_LOCK_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_executable(mean_mode_lock_gameplay tests/mean_mode_lock_gameplay.cpp)
target_link_libraries(mean_mode_lock_gameplay PRIVATE slamassets)
add_test(NAME mean_mode_lock_gameplay COMMAND mean_mode_lock_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")
if(TARGET mean_flipper_lift AND EXISTS "${CMAKE_SOURCE_DIR}/build/generated/mean_normal_lift.cpp")
 add_library(mean_normal_lift build/generated/mean_normal_lift.cpp)
 target_include_directories(mean_normal_lift PUBLIC src)
 target_compile_definitions(slamassets PUBLIC SLAM_MEAN_NORMAL_LIFT=1)
 target_link_libraries(slamassets PUBLIC mean_normal_lift)
 add_executable(mean_normal_probe tests/mean_normal_probe.cpp)
 target_link_libraries(mean_normal_probe PRIVATE mean_normal_lift)
 add_test(NAME mean_normal_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_normal.py" "$<TARGET_FILE:mean_normal_probe>")
 set_tests_properties(mean_normal_original PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
 add_test(NAME mean_normal_boundaries_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_normal.py" "$<TARGET_FILE:mean_normal_probe>" --boundary-extension --output "${CMAKE_SOURCE_DIR}/analysis/traces/mean-normal-boundaries-original.json")
 set_tests_properties(mean_normal_boundaries_original PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
 add_test(NAME mean_natural_components_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_natural_components.py" --native-sim "$<TARGET_FILE:mean_sim_probe>" --native-integrator "$<TARGET_FILE:mean_probe>" --output "${CMAKE_SOURCE_DIR}/analysis/traces/mean-natural-component-original.json")
 set_tests_properties(mean_natural_components_original PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
endif()
add_executable(mean_bitmap_linear_probe tests/mean_bitmap_linear_probe.cpp)
target_link_libraries(mean_bitmap_linear_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_bitmap_linear_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_bitmap_linear.py" "$<TARGET_FILE:mean_bitmap_linear_probe>")

add_test(NAME mean_mode4_exit_input_pixels_original COMMAND "${CMAKE_COMMAND}" -E env SLAM_MODE4_EXIT_INPUT_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")

set_tests_properties(mean_minigame_finite PROPERTIES DEPENDS "mean_minigame_retail_original;mean_minigame_retail_terminal_pixels")
add_executable(mean_formula1_extra_ball tests/mean_formula1_extra_ball.cpp)
target_link_libraries(mean_formula1_extra_ball PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_formula1_extra_ball_gameplay COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_formula1_extra_ball.py" "$<TARGET_FILE:mean_formula1_extra_ball>")
set_tests_properties(mean_formula1_extra_ball_gameplay PROPERTIES DEPENDS mean_minigame_finite)
target_sources(slamassets PRIVATE src/rules/mean_stock_car.cpp)
add_executable(mean_stock_car_probe tests/mean_stock_car_probe.cpp)
target_link_libraries(mean_stock_car_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_executable(mean_overheat_chain tests/mean_overheat_chain.cpp)
target_link_libraries(mean_overheat_chain PRIVATE slamassets)
add_test(NAME mean_overheat_chain COMMAND mean_overheat_chain)
target_sources(slamassets PRIVATE src/rules/mean_pit_stop.cpp)
add_executable(mean_pit_stop_probe tests/mean_pit_stop_probe.cpp)
target_link_libraries(mean_pit_stop_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_pit_stop_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_pit_stop.py" "$<TARGET_FILE:mean_pit_stop_probe>")
add_test(NAME mean_stock_car_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_stock_car.py" "$<TARGET_FILE:mean_stock_car_probe>")
add_test(NAME mean_pit_stop_pixels_original COMMAND "${CMAKE_COMMAND}" -E env SLAM_PIT_STOP_PIXELS_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_test(NAME mean_stock_car_pixels_original COMMAND "${CMAKE_COMMAND}" -E env SLAM_STOCK_CAR_PIXELS_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_executable(mean_short_modes_gameplay tests/mean_short_modes_gameplay.cpp)
target_link_libraries(mean_short_modes_gameplay PRIVATE slamassets)
add_test(NAME mean_short_modes_gameplay COMMAND mean_short_modes_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")
add_test(NAME mean_pit_jackpot_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --short-mode-preview pit-jackpot --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-pit-jackpot.bmp")
add_test(NAME mean_stock_car_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --short-mode-preview stock-car --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-stock-car.bmp")
add_executable(mean_speed_locks tests/mean_speed_locks.cpp)
target_link_libraries(mean_speed_locks PRIVATE slamassets)
add_test(NAME mean_speed_locks COMMAND mean_speed_locks)
add_test(NAME mean_speed_jackpot_pixels_original COMMAND "${CMAKE_COMMAND}" -E env SLAM_SPEED_JACKPOT_PIXELS_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_executable(mean_speed_rules_probe tests/mean_speed_rules_probe.cpp)
target_link_libraries(mean_speed_rules_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_speed_rules_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_speed_rules.py" "$<TARGET_FILE:mean_speed_rules_probe>")
add_executable(mean_speed_gameplay tests/mean_speed_gameplay.cpp)
target_link_libraries(mean_speed_gameplay PRIVATE slamassets)
add_test(NAME mean_speed_gameplay COMMAND mean_speed_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")
add_test(NAME mean_speed_jackpot_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --short-mode-preview speed-jackpot --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-speed-jackpot.bmp")

add_executable(mean_cliff_gameplay tests/mean_cliff_gameplay.cpp)
target_link_libraries(mean_cliff_gameplay PRIVATE slamassets)
add_test(NAME mean_cliff_gameplay COMMAND mean_cliff_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")
add_test(NAME mean_cliff_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --short-mode-preview cliff-jumper --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-cliff-jumper.bmp")
add_executable(mean_cliff_route_probe tests/mean_cliff_route_probe.cpp)
target_link_libraries(mean_cliff_route_probe PRIVATE slamassets nlohmann_json::nlohmann_json)

target_sources(slamassets PRIVATE src/rules/mean_left_progress.cpp)
add_executable(mean_left_progress_probe tests/mean_left_progress_probe.cpp)
target_link_libraries(mean_left_progress_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_left_progress_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_left_progress.py" "$<TARGET_FILE:mean_left_progress_probe>")

add_executable(mean_left_progress_gameplay tests/mean_left_progress_gameplay.cpp)
target_link_libraries(mean_left_progress_gameplay PRIVATE slamassets)
add_test(NAME mean_left_progress_gameplay COMMAND mean_left_progress_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")
add_test(NAME mean_left_speed_pixels_original COMMAND "${CMAKE_COMMAND}" -E env SLAM_LEFT_SPEED_PIXELS_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_executable(mean_cliff_finite tests/mean_cliff_finite.cpp)
target_link_libraries(mean_cliff_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_cliff_natural_finite COMMAND mean_cliff_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-cliff-natural-entry.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-cliff-natural-finite.json")

add_test(NAME mean_cliff_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview cliff --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-cliff-natural.bmp")

add_test(NAME mean_kickstart_pixels_original COMMAND "${CMAKE_COMMAND}" -E env SLAM_KICKSTART_PIXELS_ONLY=1 "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_material5_display.py" --native "$<TARGET_FILE:mean_material5_display_probe>")
add_executable(mean_kickstart_finite tests/mean_kickstart_finite.cpp)
target_link_libraries(mean_kickstart_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_kickstart_natural_finite COMMAND mean_kickstart_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-kickstart-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-kickstart-natural-finite.json")

target_compile_definitions(slamview PRIVATE SLAM_MEAN_KICKSTART_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-kickstart-natural-input.json")
add_test(NAME mean_kickstart_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview kickstart --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-kickstart-natural.bmp")
add_executable(mean_pit_finite tests/mean_pit_finite.cpp)
target_link_libraries(mean_pit_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_pit_natural_finite COMMAND mean_pit_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-pit-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-pit-natural-finite.json")

target_compile_definitions(slamview PRIVATE SLAM_MEAN_PIT_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-pit-natural-input.json")
add_test(NAME mean_pit_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview pit-stop --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-pit-natural.bmp")

add_executable(mean_stock_finite tests/mean_stock_finite.cpp)
target_link_libraries(mean_stock_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_stock_natural_finite COMMAND mean_stock_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-stock-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-stock-natural-finite.json")
target_compile_definitions(slamview PRIVATE SLAM_MEAN_STOCK_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-stock-natural-input.json")
add_test(NAME mean_stock_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview stock-car --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-stock-natural.bmp")

add_executable(mean_speed_finite tests/mean_speed_finite.cpp)
target_link_libraries(mean_speed_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_speed_natural_finite COMMAND mean_speed_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-speed-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-speed-natural-finite.json")

target_compile_definitions(slamview PRIVATE SLAM_MEAN_SPEED_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-speed-natural-input.json")
add_test(NAME mean_speed_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview speed --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-speed-natural.bmp")

add_executable(mean_monster_finite tests/mean_monster_finite.cpp)
target_link_libraries(mean_monster_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_monster_natural_finite COMMAND mean_monster_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-monster-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-monster-natural-finite.json" win)
add_test(NAME mean_monster_natural_timeout COMMAND mean_monster_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-monster-natural-timeout-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-monster-natural-timeout-finite.json" timeout)

target_compile_definitions(slamview PRIVATE SLAM_MEAN_MONSTER_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-monster-natural-input.json")
add_test(NAME mean_monster_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview monster --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-monster-natural.bmp")

add_executable(mean_rally_finite tests/mean_rally_finite.cpp)
target_link_libraries(mean_rally_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_rally_natural_finite COMMAND mean_rally_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-rally-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-rally-natural-finite.json" win)
add_test(NAME mean_rally_natural_timeout COMMAND mean_rally_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-rally-natural-timeout-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-rally-natural-timeout-finite.json" timeout)

target_compile_definitions(slamview PRIVATE SLAM_MEAN_RALLY_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-rally-natural-input.json")
add_test(NAME mean_rally_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview rally --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-rally-natural.bmp")

add_executable(mean_offroad_finite tests/mean_offroad_finite.cpp)
target_link_libraries(mean_offroad_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_offroad_natural_finite COMMAND mean_offroad_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-offroad-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-offroad-natural-finite.json")

target_compile_definitions(slamview PRIVATE SLAM_MEAN_OFFROAD_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-offroad-natural-preview-input.json")
add_test(NAME mean_offroad_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview offroad --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-offroad-natural.bmp")

add_executable(mean_chicken_finite tests/mean_chicken_finite.cpp)
target_link_libraries(mean_chicken_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_chicken_natural_finite COMMAND mean_chicken_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-chicken-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-chicken-natural-finite.json" win)
add_test(NAME mean_chicken_natural_max COMMAND mean_chicken_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-chicken-natural-max-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-chicken-natural-max-finite.json" max)
add_test(NAME mean_chicken_natural_timeout COMMAND mean_chicken_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-chicken-natural-timeout-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-chicken-natural-timeout-finite.json" timeout)

target_compile_definitions(slamview PRIVATE SLAM_MEAN_CHICKEN_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-chicken-natural-input.json")
add_test(NAME mean_chicken_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview chicken --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-chicken-natural.bmp")
add_test(NAME mean_chicken_display_timer_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_chicken_display_timer.py")

add_executable(mean_gear_display_probe tests/mean_gear_display_probe.cpp)
target_link_libraries(mean_gear_display_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_gear_display_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_gear_display.py" --native "$<TARGET_FILE:mean_gear_display_probe>")

add_executable(mean_gears_finite tests/mean_gears_finite.cpp)
target_link_libraries(mean_gears_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_gears_natural_finite COMMAND mean_gears_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-gears-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-gears-natural-finite.json")

target_compile_definitions(slamview PRIVATE SLAM_MEAN_GEARS_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-gears-natural-ready-input.json")
add_test(NAME mean_gears_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview gears --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-gears-natural.bmp")

add_executable(mean_kickback_finite tests/mean_kickback_finite.cpp)
target_link_libraries(mean_kickback_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_kickback_natural_finite COMMAND mean_kickback_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-kickback-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-kickback-natural-finite.json")
add_executable(mean_kickback_display_probe tests/mean_kickback_display_probe.cpp)
target_link_libraries(mean_kickback_display_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_kickback_display_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_kickback_display.py" --native "$<TARGET_FILE:mean_kickback_display_probe>")

target_compile_definitions(slamview PRIVATE SLAM_MEAN_KICKBACK_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-kickback-natural-input.json")
add_test(NAME mean_kickback_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview kickback --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-kickback-natural.bmp")

add_executable(mean_lane_saver_probe tests/mean_lane_saver_probe.cpp)
target_link_libraries(mean_lane_saver_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_lane_saver_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_lane_saver.py" --native "$<TARGET_FILE:mean_lane_saver_probe>")
add_executable(mean_lap_display_probe tests/mean_lap_display_probe.cpp)
target_link_libraries(mean_lap_display_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_lap_display_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_lap_display.py" --native "$<TARGET_FILE:mean_lap_display_probe>")
add_executable(mean_lane_saver_gameplay tests/mean_lane_saver_gameplay.cpp)
target_link_libraries(mean_lane_saver_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_lane_saver_gameplay COMMAND mean_lane_saver_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-lane-saver-gameplay.json")
add_test(NAME mean_lane_saver_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --lane-saver-preview --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-lane-saver.bmp")

add_executable(mean_lap_goal_finite tests/mean_lap_goal_finite.cpp)
target_link_libraries(mean_lap_goal_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_lap_goal_natural_finite COMMAND mean_lap_goal_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-lap-goal-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-lap-goal-natural-finite.json")
target_compile_definitions(slamview PRIVATE SLAM_MEAN_LAP_GOAL_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-lap-goal-natural-input.json")
add_test(NAME mean_lap_goal_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview laps --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-lap-goal-natural.bmp")

add_test(NAME mean_lap_hold_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_lap_hold.py")
add_executable(mean_goal_ladder_finite tests/mean_goal_ladder_finite.cpp)
target_link_libraries(mean_goal_ladder_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_goal_ladder_natural_finite COMMAND mean_goal_ladder_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-goal-ladder-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-goal-ladder-natural-finite.json")
target_compile_definitions(slamview PRIVATE SLAM_MEAN_GOAL_LADDER_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-goal-ladder-natural-input.json")
add_test(NAME mean_goal_ladder_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview goals --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-goal-ladder-natural.bmp")

add_executable(mean_skull_display_probe tests/mean_skull_display_probe.cpp)
target_link_libraries(mean_skull_display_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_skull_display_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_skull_display.py" --native "$<TARGET_FILE:mean_skull_display_probe>")
add_executable(mean_skull_clock_probe tests/mean_skull_clock_probe.cpp)
target_link_libraries(mean_skull_clock_probe PRIVATE nlohmann_json::nlohmann_json)
target_include_directories(mean_skull_clock_probe PRIVATE src)
add_test(NAME mean_skull_clock_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_skull_clock.py" "$<TARGET_FILE:mean_skull_clock_probe>")

add_executable(mean_skull_finite tests/mean_skull_finite.cpp)
target_link_libraries(mean_skull_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_skull_natural_finite COMMAND mean_skull_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-skull-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-skull-natural-finite.json")
target_compile_definitions(slamview PRIVATE SLAM_MEAN_SKULL_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-skull-natural-preview-input.json")
add_test(NAME mean_skull_natural_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --natural-mode-preview skull --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-skull-natural.bmp")

add_executable(mean_skillshot_launch tests/mean_skillshot_launch.cpp)
target_link_libraries(mean_skillshot_launch PRIVATE slamassets)
add_test(NAME mean_skillshot_launch COMMAND mean_skillshot_launch "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json")

target_sources(slamassets PRIVATE src/dmd/mean_skillshot_display.cpp)
add_executable(mean_skillshot_display_probe tests/mean_skillshot_display_probe.cpp)
target_link_libraries(mean_skillshot_display_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_skillshot_display_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_skillshot_display.py" --native "$<TARGET_FILE:mean_skillshot_display_probe>")

target_compile_definitions(slamview PRIVATE SLAM_MEAN_SKILLSHOT_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-skillshot-natural-input.json")
add_test(NAME mean_skillshot_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --skillshot-preview --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-skillshot-natural.bmp")

add_executable(mean_skillshot_finite tests/mean_skillshot_finite.cpp)
target_link_libraries(mean_skillshot_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_skillshot_natural_finite COMMAND mean_skillshot_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-skillshot-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-skillshot-natural-finite.json")

add_test(NAME mean_skillshot_choice_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --skillshot-choice-preview --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-skillshot-choice.bmp")

add_executable(mean_ramp_progression_finite tests/mean_ramp_progression_finite.cpp)
target_link_libraries(mean_ramp_progression_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_ramp_progression_natural_finite COMMAND mean_ramp_progression_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-ramp-progression-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-ramp-progression-natural-finite.json")

add_executable(mean_mode5_right_finite tests/mean_mode5_right_finite.cpp)
target_link_libraries(mean_mode5_right_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode5_right_finite COMMAND mean_mode5_right_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-mode5-right-finite.json")

add_executable(mean_finite_sweep tests/mean_finite_sweep.cpp)
target_link_libraries(mean_finite_sweep PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_100_games_finite COMMAND mean_finite_sweep "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-100-games-finite.json")

add_test(NAME mean_mode_audio_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode_audio.py")
add_executable(mean_mode_audio_gameplay tests/mean_mode_audio_gameplay.cpp)
target_link_libraries(mean_mode_audio_gameplay PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode_audio_gameplay COMMAND mean_mode_audio_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-mode-audio-gameplay.json")
if(TARGET slamaudio)
 add_executable(mean_audio_gameplay tests/mean_audio_gameplay.cpp)
 target_link_libraries(mean_audio_gameplay PRIVATE slamassets slamaudio SDL3::SDL3 nlohmann_json::nlohmann_json)
 add_test(NAME mean_audio_gameplay COMMAND mean_audio_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-skillshot-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-speed-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-audio-gameplay.json")
 add_test(NAME mean_reward_audio_lifecycle COMMAND mean_audio_gameplay "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-skillshot-rewards-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-reward-audio-lifecycle.json")
endif()

add_executable(mean_display_audio_probe tests/mean_display_audio_probe.cpp)
target_link_libraries(mean_display_audio_probe PRIVATE nlohmann_json::nlohmann_json)
target_include_directories(mean_display_audio_probe PRIVATE src)
add_test(NAME mean_display_audio_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_display_audio.py" "$<TARGET_FILE:mean_display_audio_probe>")

add_executable(mean_frontend_lifecycle tests/mean_frontend_lifecycle.cpp)
target_link_libraries(mean_frontend_lifecycle PRIVATE slamassets SDL3::SDL3 nlohmann_json::nlohmann_json)
add_test(NAME mean_frontend_lifecycle COMMAND mean_frontend_lifecycle "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-skillshot-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-frontend-lifecycle.json")
add_test(NAME mean_frontend_sdl_acceptance COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --frontend-acceptance "${CMAKE_SOURCE_DIR}/build/frontend-acceptance/report.json" --no-audio --frames 14 --capture "${CMAKE_SOURCE_DIR}/build/mean-frontend-acceptance.bmp")
if(TARGET slamaudio)
add_test(NAME mean_frontend_audio_sdl_acceptance COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --frontend-acceptance "${CMAKE_SOURCE_DIR}/build/frontend-audio-acceptance/report.json" --frames 14 --capture "${CMAKE_SOURCE_DIR}/build/mean-frontend-audio-acceptance.bmp")
endif()

add_executable(mean_mode_total_display_probe tests/mean_mode_total_display_probe.cpp)
target_link_libraries(mean_mode_total_display_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_mode_total_display_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode_total_display.py" --native "$<TARGET_FILE:mean_mode_total_display_probe>")
add_executable(mean_mode_total_idle_probe tests/mean_mode_total_idle_probe.cpp)
target_link_libraries(mean_mode_total_idle_probe PRIVATE nlohmann_json::nlohmann_json)
target_include_directories(mean_mode_total_idle_probe PRIVATE src)
add_test(NAME mean_mode_total_idle_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_mode_total_idle.py" --native "$<TARGET_FILE:mean_mode_total_idle_probe>")

add_executable(mean_combined_modes_finite tests/mean_combined_modes_finite.cpp)
target_link_libraries(mean_combined_modes_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_combined_modes_finite COMMAND mean_combined_modes_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-combined-modes-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-combined-modes-native.json")
target_compile_definitions(slamview PRIVATE SLAM_MEAN_COMBINED_MODES_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-combined-modes-input.json")
add_test(NAME mean_mode_total_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --mode-total-preview --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-mode-total.bmp")

add_executable(mean_idle_hud_probe tests/mean_idle_hud_probe.cpp)
target_link_libraries(mean_idle_hud_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_idle_hud_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_idle_hud.py" --native "$<TARGET_FILE:mean_idle_hud_probe>")

add_executable(mean_idle_hud_finite tests/mean_idle_hud_finite.cpp)
target_link_libraries(mean_idle_hud_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_idle_hud_finite COMMAND mean_idle_hud_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-pit-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-idle-hud-finite.json")
foreach(page score pit-stop)
 add_test(NAME mean_idle_hud_${page}_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --idle-hud-preview ${page} --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-idle-hud-${page}.bmp")
endforeach()

add_executable(mean_main_mode_hud_probe tests/mean_main_mode_hud_probe.cpp)
target_link_libraries(mean_main_mode_hud_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_main_mode_hud_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_main_mode_hud.py" --native "$<TARGET_FILE:mean_main_mode_hud_probe>")

add_executable(mean_main_mode_hud_finite tests/mean_main_mode_hud_finite.cpp)
target_link_libraries(mean_main_mode_hud_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_main_mode_hud_finite COMMAND mean_main_mode_hud_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-main-mode-hud-finite.json")
foreach(page chicken monster rally offroad speed)
 add_test(NAME mean_main_mode_hud_${page}_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --main-mode-hud-preview ${page} --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-main-mode-hud-${page}.bmp")
endforeach()

add_executable(mean_player_hud_probe tests/mean_player_hud_probe.cpp)
target_link_libraries(mean_player_hud_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_player_hud_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_player_hud.py" --native "$<TARGET_FILE:mean_player_hud_probe>")

add_executable(mean_player_hud_finite tests/mean_player_hud_finite.cpp)
target_link_libraries(mean_player_hud_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_player_hud_finite COMMAND mean_player_hud_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-skillshot-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-goal-ladder-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-player-hud-finite.json")

foreach(page intro choices score extra)
 add_test(NAME mean_player_hud_${page}_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --player-hud-preview ${page} --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-player-hud-${page}.bmp")
endforeach()

add_executable(mean_player_extra_hud tests/mean_player_extra_hud.cpp)
target_link_libraries(mean_player_extra_hud PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_player_extra_hud COMMAND mean_player_extra_hud "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-goal-ladder-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-player-extra-hud.json")

add_executable(mean_overheat_admission_probe tests/mean_overheat_admission_probe.cpp)
target_link_libraries(mean_overheat_admission_probe PRIVATE nlohmann_json::nlohmann_json)
add_test(NAME mean_overheat_admission_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_overheat_admission.py" --native "$<TARGET_FILE:mean_overheat_admission_probe>")
target_include_directories(mean_overheat_admission_probe PRIVATE src)
add_executable(mean_overheat_finite tests/mean_overheat_finite.cpp)
target_link_libraries(mean_overheat_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_overheat_natural_finite COMMAND mean_overheat_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-overheat-natural-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-overheat-natural-finite.json")
add_executable(mean_overheat_timeout tests/mean_overheat_timeout.cpp)
target_link_libraries(mean_overheat_timeout PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_overheat_timeout_finite COMMAND mean_overheat_timeout "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-overheat-timeout-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-overheat-timeout-finite.json")
target_compile_definitions(slamview PRIVATE SLAM_MEAN_OVERHEAT_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-overheat-natural-input.json" SLAM_MEAN_OVERHEAT_TIMEOUT_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-overheat-timeout-input.json")
foreach(page collect early late timeout)
 add_test(NAME mean_overheat_${page}_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --overheat-preview ${page} --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-overheat-${page}.bmp")
endforeach()
add_test(NAME mean_idle_hud_bank_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --idle-hud-preview bank --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-idle-hud-bank.bmp")

add_executable(mean_gear_cap_finite tests/mean_gear_cap_finite.cpp)
target_link_libraries(mean_gear_cap_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_gear_cap_finite COMMAND mean_gear_cap_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-gear-cap-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-gear-cap-finite.json")
target_compile_definitions(slamview PRIVATE SLAM_MEAN_GEAR_CAP_TRACE_PATH="${CMAKE_SOURCE_DIR}/analysis/traces/mean-gear-cap-input.json")
foreach(page cap bonus)
 add_test(NAME mean_gear_cap_${page}_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --gear-cap-preview ${page} --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-gear-cap-${page}.bmp")
endforeach()

add_executable(mean_skillshot_admission_probe tests/mean_skillshot_admission_probe.cpp)
target_include_directories(mean_skillshot_admission_probe PRIVATE src)
target_link_libraries(mean_skillshot_admission_probe PRIVATE nlohmann_json::nlohmann_json)
add_test(NAME mean_skillshot_admission_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_skillshot_admission.py" --native "$<TARGET_FILE:mean_skillshot_admission_probe>")
add_executable(mean_skillshot_rewards_finite tests/mean_skillshot_rewards_finite.cpp)
target_link_libraries(mean_skillshot_rewards_finite PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_skillshot_rewards_finite COMMAND mean_skillshot_rewards_finite "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-skillshot-rewards-finite.json")
target_compile_definitions(slamview PRIVATE SLAM_MEAN_SKILLSHOT_REWARDS_DIR="${CMAKE_SOURCE_DIR}/analysis/traces")
foreach(reward RANGE 1 7)
 add_test(NAME mean_skillshot_reward_${reward}_visible COMMAND "${CMAKE_COMMAND}" -E env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "${CMAKE_SOURCE_DIR}/tools/slamplay" --skillshot-reward-preview ${reward} --options-preview --no-audio --frames 2 --capture "${CMAKE_SOURCE_DIR}/build/mean-skillshot-reward-${reward}.bmp")
endforeach()

add_executable(presentation_probe tests/presentation_probe.cpp)
target_link_libraries(presentation_probe PRIVATE slampresentation)
add_test(NAME presentation_fallback COMMAND presentation_probe)
set_tests_properties(presentation_fallback PROPERTIES ENVIRONMENT "SDL_VIDEODRIVER=dummy")

add_executable(mean_extended_soak tests/mean_extended_soak.cpp)
target_link_libraries(mean_extended_soak PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_extended_soak COMMAND mean_extended_soak "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-extended-soak.json")
set_tests_properties(mean_extended_soak PROPERTIES LABELS "mean;soak" TIMEOUT 600 RUN_SERIAL TRUE)

add_executable(mean_reset_input tests/mean_reset_input.cpp)
target_link_libraries(mean_reset_input PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_reset_input COMMAND mean_reset_input "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-reset-input.json")

add_executable(mean_mode_marathon tests/mean_mode_marathon.cpp)
target_link_libraries(mean_mode_marathon PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_three_modes_finite COMMAND mean_mode_marathon "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-three-modes-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-three-modes-finite.json")
add_test(NAME mean_four_modes_finite COMMAND mean_mode_marathon "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-four-modes-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-four-modes-finite.json")
add_test(NAME mean_four_modes_speed_finite COMMAND mean_mode_marathon "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-four-modes-speed-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-four-modes-speed-finite.json")
add_test(NAME mean_five_modes_finite COMMAND mean_mode_marathon "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-five-modes-input.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-five-modes-finite.json")
add_executable(mean_contact_context_probe tests/mean_contact_context_probe.cpp)
target_link_libraries(mean_contact_context_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_contact_observer_finite COMMAND mean_mode_marathon "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-five-modes-input.json" "${CMAKE_SOURCE_DIR}/build/oracle/mean-observed-finite.json" --observe-contacts)
add_test(NAME mean_live_contacts_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_live_contacts.py" --probe "$<TARGET_FILE:mean_contact_context_probe>")
add_executable(mean_pair_context_probe tests/mean_pair_context_probe.cpp)
target_link_libraries(mean_pair_context_probe PRIVATE slamassets nlohmann_json::nlohmann_json)
add_test(NAME mean_pair_observer_finite COMMAND mean_mode_marathon "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" "${CMAKE_SOURCE_DIR}/build/mean-prepared" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" "${CMAKE_SOURCE_DIR}/analysis/traces/mean-five-modes-input.json" "${CMAKE_SOURCE_DIR}/build/oracle/mean-pair-observed-finite.json" --observe-pairs)
add_test(NAME mean_live_pairs_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python" "${CMAKE_SOURCE_DIR}/tools/verify_mean_live_pairs.py" --probe "$<TARGET_FILE:mean_pair_context_probe>")
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  add_test(NAME mean_package_acceptance COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_mean_package.py" --build "${CMAKE_BINARY_DIR}")
  add_test(NAME mean_import_acceptance COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_mean_import.py" --native "$<TARGET_FILE:slamimport>")
  add_test(NAME mean_setup_acceptance COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_mean_setup.py" --setup "$<TARGET_FILE:slamsetup>")
endif()

if(TARGET slamdemon-import AND TARGET slamslice AND EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/legal-game-rewards.json")
  add_test(NAME demon_native_import COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_import.py" --native "$<TARGET_FILE:slamdemon-import>" --viewer "$<TARGET_FILE:slamslice>")
  set_tests_properties(demon_native_import PROPERTIES TIMEOUT 180)
endif()

if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/demon-rc-island.json")
  add_test(NAME demon_release_gate COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_demon_release_gate.py" --negative-tests)
  set_tests_properties(demon_release_gate PROPERTIES DEPENDS demon_completion_audit TIMEOUT 60)
endif()

add_executable(slamtilt src/frontend/main_menu.cpp src/frontend/reborn_menu.cpp src/assets/menu_assets.cpp)
target_link_libraries(slamtilt PRIVATE slamui slamassets slamimportlib SDL3::SDL3 nlohmann_json::nlohmann_json)
target_compile_definitions(slamtilt PRIVATE SLAM_MENU_SOURCE="${CMAKE_SOURCE_DIR}")
target_compile_options(slamtilt PRIVATE -Wall -Wextra -Wpedantic)
set_target_properties(slamtilt PROPERTIES INSTALL_RPATH "$ORIGIN/../lib")
install(TARGETS slamtilt slamslice RUNTIME DESTINATION bin COMPONENT FrontendRuntime)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MENU.DAT")
  add_test(NAME main_menu_flow COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_main_menu.py" --native "$<TARGET_FILE:slamtilt>" --report "${CMAKE_BINARY_DIR}/main-menu-latest.json")
  set_tests_properties(main_menu_flow PROPERTIES TIMEOUT 180)
endif()
add_executable(menu_assets_test tests/menu_assets_test.cpp src/assets/menu_assets.cpp)
target_link_libraries(menu_assets_test PRIVATE slamimportlib)
if(EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MENU.DAT")
  add_test(NAME original_menu_pixels COMMAND menu_assets_test "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MENU.DAT")
endif()
add_executable(frontend_runtime_test tests/frontend_runtime_test.cpp)
target_link_libraries(frontend_runtime_test PRIVATE slamimportlib SDL3::SDL3)
target_compile_options(frontend_runtime_test PRIVATE -Wall -Wextra -Wpedantic)
add_test(NAME frontend_runtime_safety COMMAND frontend_runtime_test)
add_test(NAME mean_retail_import_acceptance COMMAND "${Python3_EXECUTABLE}"
  "${CMAKE_SOURCE_DIR}/tools/verify_mean_retail_import.py" --build "${CMAKE_BINARY_DIR}" --report "${CMAKE_BINARY_DIR}/mean-retail-import-latest.json")
add_test(NAME dat_only_import_acceptance COMMAND "${Python3_EXECUTABLE}"
  "${CMAKE_SOURCE_DIR}/tools/verify_dat_only_import.py" --build "${CMAKE_BINARY_DIR}" --report "${CMAKE_BINARY_DIR}/dat-only-import-latest.json")
set_tests_properties(dat_only_import_acceptance PROPERTIES TIMEOUT 240 RUN_SERIAL TRUE)
set_tests_properties(mean_retail_import_acceptance PROPERTIES TIMEOUT 300 RUN_SERIAL TRUE)
if(EXISTS "${CMAKE_SOURCE_DIR}/analysis/reborn-release-island.json")
  add_test(NAME reborn_release_integrity COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_reborn_release.py" --negative-tests)
  set_tests_properties(reborn_release_integrity PROPERTIES TIMEOUT 60)
endif()

install(FILES analysis/import/pirate-amiga-startup.json analysis/import/space-amiga-startup.json analysis/import/demon-amiga-startup.json packaging/mean-amiga-data.sha256 DESTINATION share/slamtilt COMPONENT Runtime)

add_test(NAME amiga_disk_bounds COMMAND amiga_disk_test)

foreach(component PirateRuntime SpaceRuntime DemonRuntime)
 install(FILES analysis/import/mean-retail-startup.json analysis/import/pirate-amiga-startup.json analysis/import/space-amiga-startup.json analysis/import/demon-amiga-startup.json packaging/mean-data.sha256 packaging/mean-amiga-data.sha256 DESTINATION share/slamtilt COMPONENT ${component})
endforeach()
if(Python3_EXECUTABLE AND EXISTS "${CMAKE_SOURCE_DIR}/amiga/historical-mods/DLM")
 add_test(NAME amiga_import_acceptance COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_amiga_import.py" --build "${CMAKE_BINARY_DIR}" --report "${CMAKE_BINARY_DIR}/amiga-import-latest.json")
endif()

foreach(target slamsetup slampirate-setup slamspace-setup slamdemon-setup)
 target_compile_definitions(${target} PRIVATE SLAM_ADF_METADATA="${CMAKE_SOURCE_DIR}/analysis/import" SLAM_ADF_PROFILE="${CMAKE_SOURCE_DIR}/packaging/mean-data.sha256")
endforeach()

add_executable(amiga_dmd_test tests/amiga_dmd_test.cpp)
target_link_libraries(amiga_dmd_test PRIVATE slamimportlib)
add_test(NAME amiga_dmd_bounds COMMAND amiga_dmd_test)

install(FILES docs/amiga-adf-import.md docs/amiga-pc-comparison.md DESTINATION share/slamtilt COMPONENT Runtime)

install(FILES analysis/import/pirate-amiga-v2-startup.json analysis/import/space-amiga-v2-startup.json analysis/import/demon-amiga-v2-startup.json packaging/mean-amiga-v2-data.sha256 DESTINATION share/slamtilt COMPONENT Runtime)

foreach(component PirateRuntime SpaceRuntime DemonRuntime)
 install(FILES analysis/import/pirate-amiga-v2-startup.json analysis/import/space-amiga-v2-startup.json analysis/import/demon-amiga-v2-startup.json packaging/mean-amiga-v2-data.sha256 DESTINATION share/slamtilt COMPONENT ${component})
endforeach()

add_executable(amiga_fragments_v2_test tests/amiga_fragments_v2_test.cpp)
target_link_libraries(amiga_fragments_v2_test PRIVATE slamimportlib)
add_test(NAME amiga_fragments_v2_bounds COMMAND amiga_fragments_v2_test)

if(EXISTS "${CMAKE_SOURCE_DIR}/build/generated/pirate_step.cpp")
 set(SLAM_ASSET_AUDIT_DIR "${CMAKE_BINARY_DIR}/asset-audit")
 add_custom_command(OUTPUT "${SLAM_ASSET_AUDIT_DIR}/pirate_step_audit.cpp" "${SLAM_ASSET_AUDIT_DIR}/physics/pirate_step_lift.h" "${SLAM_ASSET_AUDIT_DIR}/physics/pirate_session.h" "${SLAM_ASSET_AUDIT_DIR}/pirate_session_audit.cpp"
 COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/build_asset_read_audit.py" "${CMAKE_SOURCE_DIR}" "${SLAM_ASSET_AUDIT_DIR}"
 DEPENDS tools/build_asset_read_audit.py src/physics/pirate_step_lift.h src/physics/pirate_session.h src/physics/pirate_session.cpp build/generated/pirate_step.cpp)
 add_executable(asset_read_audit EXCLUDE_FROM_ALL tools/asset_read_audit.cpp "${SLAM_ASSET_AUDIT_DIR}/pirate_session_audit.cpp" src/core/sha256.cpp "${SLAM_ASSET_AUDIT_DIR}/pirate_step_audit.cpp")
 target_include_directories(asset_read_audit BEFORE PRIVATE "${SLAM_ASSET_AUDIT_DIR}" src)
 target_compile_options(asset_read_audit PRIVATE -O1 -g0 -Wall -Wextra -Wpedantic)
 set_source_files_properties("${SLAM_ASSET_AUDIT_DIR}/pirate_step_audit.cpp" PROPERTIES COMPILE_OPTIONS "-Wno-unused-label;-Wno-parentheses")
 set_source_files_properties("${SLAM_ASSET_AUDIT_DIR}/pirate_session_audit.cpp" PROPERTIES COMPILE_OPTIONS "-ffunction-sections;-fdata-sections")
 target_link_options(asset_read_audit PRIVATE -Wl,--gc-sections)
 target_link_libraries(asset_read_audit PRIVATE nlohmann_json::nlohmann_json)
endif()

foreach(component Runtime PirateRuntime SpaceRuntime DemonRuntime)
 install(FILES analysis/import/demon-amiga-v3-startup.json DESTINATION share/slamtilt COMPONENT ${component})
endforeach()

if(Python3_EXECUTABLE AND EXISTS "${CMAKE_SOURCE_DIR}/amiga/historical-mods/DLM" AND EXISTS "${CMAKE_SOURCE_DIR}/build/reborn-playtest/demon/primary-oracle.json")
 add_test(NAME asset_read_coverage_gate COMMAND "${Python3_EXECUTABLE}" "${CMAKE_SOURCE_DIR}/tools/verify_asset_read_island.py" --build "${CMAKE_BINARY_DIR}" --ticks 4000 --report "${CMAKE_BINARY_DIR}/asset-read-gate-latest.json")
endif()

if(EMSCRIPTEN)
 include("${CMAKE_SOURCE_DIR}/packaging/web/targets.cmake")
endif()

add_executable(gamepad_input_test tests/gamepad_input_test.cpp)
target_include_directories(gamepad_input_test PRIVATE src)
target_link_libraries(gamepad_input_test PRIVATE slamui SDL3::SDL3 nlohmann_json::nlohmann_json)
add_test(NAME gamepad_input COMMAND gamepad_input_test "${CMAKE_CURRENT_BINARY_DIR}/gamepad-input.json")
set_tests_properties(gamepad_input PROPERTIES SKIP_RETURN_CODE 77 ENVIRONMENT "SDL_VIDEODRIVER=dummy;SDL_AUDIODRIVER=dummy")

if(NOT EMSCRIPTEN)
# In-process virtual-controller acceptance uses the actual native frontends.
add_library(gamepad_view_frontend OBJECT src/renderer/main.cpp src/frontend/pirate_play.cpp)
get_target_property(_gamepad_view_defs slamview COMPILE_DEFINITIONS)
get_target_property(_gamepad_view_libs slamview LINK_LIBRARIES)
target_compile_definitions(gamepad_view_frontend PRIVATE ${_gamepad_view_defs} main=slam_gamepad_view_main)
target_link_libraries(gamepad_view_frontend PRIVATE ${_gamepad_view_libs})
add_library(gamepad_slice_frontend OBJECT src/frontend/retail_slice.cpp)
get_target_property(_gamepad_slice_defs slamslice COMPILE_DEFINITIONS)
get_target_property(_gamepad_slice_libs slamslice LINK_LIBRARIES)
if(_gamepad_slice_defs)
  target_compile_definitions(gamepad_slice_frontend PRIVATE ${_gamepad_slice_defs})
endif()
target_compile_definitions(gamepad_slice_frontend PRIVATE main=slam_gamepad_slice_main)
target_link_libraries(gamepad_slice_frontend PRIVATE ${_gamepad_slice_libs})
add_library(gamepad_menu_frontend OBJECT src/frontend/main_menu.cpp src/frontend/reborn_menu.cpp src/assets/menu_assets.cpp)
get_target_property(_gamepad_menu_defs slamtilt COMPILE_DEFINITIONS)
get_target_property(_gamepad_menu_libs slamtilt LINK_LIBRARIES)
target_compile_definitions(gamepad_menu_frontend PRIVATE ${_gamepad_menu_defs} main=slam_gamepad_menu_main)
target_link_libraries(gamepad_menu_frontend PRIVATE ${_gamepad_menu_libs})
add_executable(gamepad_frontend_probe tests/gamepad_frontend_probe.cpp $<TARGET_OBJECTS:gamepad_view_frontend> $<TARGET_OBJECTS:gamepad_slice_frontend> $<TARGET_OBJECTS:gamepad_menu_frontend>)
foreach(probe_target gamepad_view_frontend gamepad_slice_frontend gamepad_menu_frontend gamepad_frontend_probe)
  target_compile_definitions(${probe_target} PRIVATE SLAM_GAMEPAD_FRONTEND_PROBE=1)
endforeach()
find_package(Threads REQUIRED)
target_link_libraries(gamepad_frontend_probe PRIVATE ${_gamepad_view_libs} ${_gamepad_slice_libs} ${_gamepad_menu_libs} Threads::Threads)
endif()

# Original Retail x86 single-voice PCM versus the actual native mixer.
if(TARGET slamaudio)
  add_executable(native_audio_deferred_probe tests/native_audio_deferred_probe.cpp)
  target_link_libraries(native_audio_deferred_probe PRIVATE slamaudio)
  target_compile_options(native_audio_deferred_probe PRIVATE -Wall -Wextra -Wpedantic)
  add_test(NAME native_audio_deferred_queue COMMAND "${CMAKE_COMMAND}" -E env SDL_AUDIODRIVER=dummy
    "$<TARGET_FILE:native_audio_deferred_probe>")
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE")
    add_test(NAME retail_audio_deferred_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_retail_audio_deferred.py"
      --output "${CMAKE_CURRENT_BINARY_DIR}/retail-audio-deferred-original.json")
  endif()
  add_executable(retail_sample_pcm_probe tests/retail_sample_pcm_probe.cpp)
  target_link_libraries(retail_sample_pcm_probe PRIVATE slamaudio slamassets nlohmann_json::nlohmann_json)
  target_compile_options(retail_sample_pcm_probe PRIVATE -Wall -Wextra -Wpedantic)
  add_executable(sfx_profiles_probe tests/sfx_profiles_probe.cpp)
  target_link_libraries(sfx_profiles_probe PRIVATE slamaudio nlohmann_json::nlohmann_json)
  add_executable(sfx_dynamic_probe tests/sfx_dynamic_probe.cpp)
  target_link_libraries(sfx_dynamic_probe PRIVATE slamaudio)
  add_executable(pirate_overlap_pcm_probe tests/pirate_overlap_pcm_probe.cpp)
  target_link_libraries(pirate_overlap_pcm_probe PRIVATE slamaudio)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE")
    add_test(NAME pirate_overlap_pcm_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_pirate_overlap_pcm.py"
      --native "$<TARGET_FILE:pirate_overlap_pcm_probe>"
      --output "${CMAKE_CURRENT_BINARY_DIR}/pirate-overlap-pcm.json")
  endif()
  add_executable(mean_display_sfx_probe tests/mean_display_sfx_probe.cpp)
  target_include_directories(mean_display_sfx_probe PRIVATE src)
  target_link_libraries(mean_display_sfx_probe PRIVATE nlohmann_json::nlohmann_json)
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
     EXISTS "${CMAKE_SOURCE_DIR}/analysis/pirate-audio-static.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/analysis/space-audio-reuse.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/analysis/demon-audio-profile.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/pirate-audio-events.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-audio-events.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-image.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/DEMON.DAT")
    add_test(NAME sfx_descriptor_audit COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/audit_sfx_descriptors.py" --native "$<TARGET_FILE:sfx_profiles_probe>"
      --output "${CMAKE_CURRENT_BINARY_DIR}/sfx-descriptor-audit-ctest.json")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT")
    add_test(NAME mean_retail_sfx_dynamic_pcm COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_dynamic_sfx_pcm.py" --native "$<TARGET_FILE:sfx_dynamic_probe>"
      --output "${CMAKE_CURRENT_BINARY_DIR}/mean-dynamic-sfx")
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/pe-data.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/cd-gamer-03-1997/SLAMTILT/SLAMTILT/SLAMTILT.EXE" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT")
    add_test(NAME mean_sample_pcm_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_sample_pcm_original.py"
      --native "$<TARGET_FILE:retail_sample_pcm_probe>"
      --output "${CMAKE_CURRENT_BINARY_DIR}/mean-sample-pcm-original.json")
    add_test(NAME mean_display_sfx_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_display_sfx.py"
      --native "$<TARGET_FILE:mean_display_sfx_probe>"
      --output "${CMAKE_CURRENT_BINARY_DIR}/mean-display-sfx-original.json")
    add_test(NAME mean_remaining_sfx_static COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_mean_remaining_sfx.py"
      --output "${CMAKE_CURRENT_BINARY_DIR}/mean-remaining-sfx-static.json")
    if(EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MEAN.DAT" AND
       EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/demo-1997/Slam Tilt Demo (Windows, 1996) - SLAMTILT/DAT/MAIN.DAT")
      add_test(NAME mean_sfx_descriptor_access_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
        "${CMAKE_SOURCE_DIR}/tools/trace_mean_sfx_descriptor_access.py"
        --output "${CMAKE_CURRENT_BINARY_DIR}/mean-sfx-access.json")
      add_test(NAME mean_sfx_mode_access_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
        "${CMAKE_SOURCE_DIR}/tools/trace_mean_sfx_mode_access.py"
        --output "${CMAKE_CURRENT_BINARY_DIR}/mean-sfx-mode-access.json")
      if(TARGET mean_contact_context_probe)
        add_test(NAME mean_sfx_contact_access_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
          "${CMAKE_SOURCE_DIR}/tools/trace_mean_sfx_contact_access.py"
          --probe "$<TARGET_FILE:mean_contact_context_probe>"
          --output "${CMAKE_CURRENT_BINARY_DIR}/mean-sfx-contact-access.json")
        set_tests_properties(mean_sfx_contact_access_original PROPERTIES TIMEOUT 120)
      endif()
      if(TARGET mean_minigame2_probe)
        add_test(NAME mean_sfx_minigame_access_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
          "${CMAKE_SOURCE_DIR}/tools/trace_mean_sfx_minigame_access.py"
          --native "$<TARGET_FILE:mean_minigame2_probe>"
          --output "${CMAKE_CURRENT_BINARY_DIR}/mean-sfx-minigame-access.json")
        set_tests_properties(mean_sfx_minigame_access_original PROPERTIES TIMEOUT 120 RESOURCE_LOCK mean_minigame_fixture)
        if(TEST mean_minigame_samples_oracle)
          set_tests_properties(mean_minigame_samples_oracle PROPERTIES RESOURCE_LOCK mean_minigame_fixture)
        endif()
      endif()
    endif()
    if(EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/DEMON.DAT" AND
       EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/INTRO.DAT" AND
       EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MAIN.DAT" AND
       EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MENU.DAT" AND
       EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MENU2.DAT" AND
       EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT" AND
       EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT" AND
       EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE")
      add_test(NAME mean_sfx_reference_surfaces COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
        "${CMAKE_SOURCE_DIR}/tools/verify_mean_sfx_reference_surfaces.py"
        --output "${CMAKE_CURRENT_BINARY_DIR}/mean-sfx-reference-surfaces.json")
      if(EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Fix_Win_EN/Game Files/Slam_Tilt_Fix/SLAMTILT.EXE")
        add_test(NAME mean_sfx_fix_reference_surfaces COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
          "${CMAKE_SOURCE_DIR}/tools/verify_mean_sfx_reference_surfaces.py"
          --fix "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Fix_Win_EN/Game Files/Slam_Tilt_Fix/SLAMTILT.EXE"
          --output "${CMAKE_CURRENT_BINARY_DIR}/mean-sfx-fix-reference-surfaces.json")
      endif()
    endif()
  endif()
  if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
     EXISTS "${CMAKE_SOURCE_DIR}/analysis/space-audio-reuse.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/analysis/demon-audio-profile.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/analysis/pirate-audio-static.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-image.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-dat.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/summary.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-dat.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/summary.json" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-dat.bin" AND
     EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/summary.json")
    add_test(NAME retail_sample_pcm_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_retail_sample_pcm.py" --native "$<TARGET_FILE:retail_sample_pcm_probe>")
    set_tests_properties(retail_sample_pcm_original PROPERTIES TIMEOUT 180)
  endif()
endif()

if(Python3_EXECUTABLE AND EXISTS "${CMAKE_SOURCE_DIR}/build/amiga-read-verified-data/amiga-import.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/full/Mean.Raw" AND EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/full/Mean.Bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/full/Pirate.Raw" AND EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/full/Pirate.Bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/full/Space.Raw" AND EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/full/Space.Bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/full/Demon.Raw" AND EXISTS "${CMAKE_SOURCE_DIR}/build/decoded/full/Demon.Bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/amiga-read-verified-data/mean/MEAN.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/amiga-read-verified-data/pirate/PIRATE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/amiga-read-verified-data/space/SPACE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/amiga-read-verified-data/demon/DEMON.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/DEMON.DAT")
  add_test(NAME amiga_windows_music_banks COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_SOURCE_DIR}/tools/verify_amiga_music_banks.py"
    --output "${CMAKE_CURRENT_BINARY_DIR}/amiga-windows-music-banks.json")
  add_test(NAME amiga_music_integrity COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_SOURCE_DIR}/tests/amiga_music_integrity.py")
endif()

# Bounded Space station sequence: retained original trace versus live SDL replay.
if(TARGET slamaudio AND TARGET slamslice AND
   EXISTS "${CMAKE_SOURCE_DIR}/tools/verify_space_post_jackpot.py" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/table-profiles.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-mission-campaign-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/mission-campaign-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-runtime.bin")
  add_test(NAME space_post_jackpot_original COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_SOURCE_DIR}/tools/verify_space_post_jackpot.py" --native "$<TARGET_FILE:slamslice>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/space-post-jackpot"
    --report "${CMAKE_CURRENT_BINARY_DIR}/space-post-jackpot/report.json")
  set_tests_properties(space_post_jackpot_original PROPERTIES TIMEOUT 300)
endif()

# Original Retail integration on naturally reached native snapshots; private
# game data stays local and reports stay in the build directory.
if(TARGET mean_sim_probe AND TARGET mean_probe AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/manifest.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/mean-prepared/lookup.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/mean-flight-100.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT")
  add_test(NAME mean_retail_natural_integration COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_mean_natural_components.py" --original-build retail
    --native-sim "$<TARGET_FILE:mean_sim_probe>" --native-integrator "$<TARGET_FILE:mean_probe>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/mean-retail-natural-integration.json")
  set_tests_properties(mean_retail_natural_integration PROPERTIES TIMEOUT 180)
endif()

# Consecutive Demon videos: private, hash-pinned Original plus SDL replay.
if(TARGET slamaudio AND TARGET slamslice AND
   EXISTS "${CMAKE_SOURCE_DIR}/tools/verify_demon_video_consecutive.py" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/table-profiles.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-video-consecutive-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/video-consecutive-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/DEMON.DAT")
  add_test(NAME demon_video_consecutive_original COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_SOURCE_DIR}/tools/verify_demon_video_consecutive.py" --native "$<TARGET_FILE:slamslice>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/demon-video-consecutive"
    --report "${CMAKE_CURRENT_BINARY_DIR}/demon-video-consecutive/report.json")
  set_tests_properties(demon_video_consecutive_original PROPERTIES TIMEOUT 300)
endif()

# Verify original Retail startup music selection and SDL requests, including a
# fresh DAT-only import. Original game files and prepared oracle states are local.
if(TARGET slamaudio)
  add_executable(music_order_position tests/music_order_position.cpp)
  target_link_libraries(music_order_position PRIVATE slamaudio slamassets)
  target_compile_options(music_order_position PRIVATE -Wall -Wextra -Wpedantic)
  add_executable(tracker_channel_probe tests/tracker_channel_probe.cpp)
  target_link_libraries(tracker_channel_probe PRIVATE slamaudio)
  set(_retail_music_dat "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT")
  if(EXISTS "${_retail_music_dat}/MEAN.DAT" AND EXISTS "${_retail_music_dat}/PIRATE.DAT" AND
     EXISTS "${_retail_music_dat}/SPACE.DAT" AND EXISTS "${_retail_music_dat}/DEMON.DAT")
    add_test(NAME music_all_order_positions COMMAND music_order_position "${_retail_music_dat}")
    if(TARGET stim_audio_probe AND EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
       EXISTS "${_retail_music_dat}/../SLAMTILT.EXE")
      add_test(NAME retail_tracker_native_pcm COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
        "${CMAKE_SOURCE_DIR}/tools/verify_retail_tracker_native.py"
        --native "$<TARGET_FILE:stim_audio_probe>"
        --output "${CMAKE_CURRENT_BINARY_DIR}/retail-tracker-comparison")
      add_test(NAME mean_tracker_sample_phase COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
        "${CMAKE_SOURCE_DIR}/tools/verify_mean_tracker_phase.py"
        --native "$<TARGET_FILE:stim_audio_probe>"
        --work "${CMAKE_CURRENT_BINARY_DIR}/mean-tracker-phase")
      if(EXISTS "${CMAKE_SOURCE_DIR}/build/tracker-floor-experiment/generated-libxmp-build/libxmp.so.4")
        add_test(NAME pirate_tracker_channel_periods COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
          "${CMAKE_SOURCE_DIR}/tools/verify_pirate_tracker_channels.py"
          --native "$<TARGET_FILE:tracker_channel_probe>"
          --floor-library "${CMAKE_SOURCE_DIR}/build/tracker-floor-experiment/generated-libxmp-build/libxmp.so.4"
          --work "${CMAKE_CURRENT_BINARY_DIR}/pirate-tracker-channels"
          --output "${CMAKE_CURRENT_BINARY_DIR}/pirate-tracker-channels.json")
      endif()
    endif()
  endif()
endif()
if(Python3_EXECUTABLE)
  add_test(NAME retail_audio_fixture_adapter COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_SOURCE_DIR}/tests/retail_audio_fixture_test.py")
endif()
if(TARGET mean_phase1_gameplay_probe AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE")
  add_test(NAME mean_retail_music_transitions COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_mean_retail_music_transitions.py")
endif()
if(EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/docs/verification/retail-music-start-2026-10-30.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/docs/verification/unobserved-music-stops-2026-10-30.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/space-full-tick-boundary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-dat.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-dat.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-dat.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE")
  add_test(NAME retail_music_stop_pointers COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_music_stop_pointers.py"
    --output "${CMAKE_CURRENT_BINARY_DIR}/retail-music-stop-pointers.json")
  add_test(NAME retail_music_stop_wrappers COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_music_stop_wrapper.py"
    --output "${CMAKE_CURRENT_BINARY_DIR}/retail-music-stop-wrappers.json")
endif()
if(TARGET slamslice AND TARGET slamaudio AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/table-profiles.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-dat.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-dat.bin" AND
   EXISTS "${_retail_music_dat}/MAIN.DAT" AND
   EXISTS "${_retail_music_dat}/SPACE.DAT" AND EXISTS "${_retail_music_dat}/DEMON.DAT" AND
   EXISTS "${_retail_music_dat}/../SLAMTILT.EXE")
  foreach(_tilt_table IN ITEMS space demon)
    add_test(NAME ${_tilt_table}_tilt_music_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_space_tilt_music.py" --table "${_tilt_table}"
      --native "$<TARGET_FILE:slamslice>" --output "${CMAKE_CURRENT_BINARY_DIR}/${_tilt_table}-tilt-music")
    set_tests_properties(${_tilt_table}_tilt_music_original PROPERTIES TIMEOUT 180)
    string(TOUPPER "${_tilt_table}" _tilt_upper)
    set(_tilt_amiga "${CMAKE_SOURCE_DIR}/build/amiga-read-verified-data/${_tilt_table}")
    if(EXISTS "${_tilt_amiga}/${_tilt_upper}.DAT" AND EXISTS "${_tilt_amiga}/MAIN.DAT" AND
       EXISTS "${_tilt_amiga}/${_tilt_table}-prepared/human-image.bin" AND
       EXISTS "${_tilt_amiga}/${_tilt_table}-prepared/human-runtime.bin" AND
       EXISTS "${_tilt_amiga}/${_tilt_table}-prepared/summary.json")
      add_test(NAME ${_tilt_table}_tilt_music_amiga_adapter COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
        "${CMAKE_SOURCE_DIR}/tools/verify_space_tilt_music.py" --table "${_tilt_table}"
        --native "$<TARGET_FILE:slamslice>" --amiga-root "${_tilt_amiga}"
        --output "${CMAKE_CURRENT_BINARY_DIR}/${_tilt_table}-tilt-music-amiga")
      set_tests_properties(${_tilt_table}_tilt_music_amiga_adapter PROPERTIES TIMEOUT 180)
    endif()
  endforeach()
endif()
if(TARGET slamslice AND TARGET slamaudio AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-bigblam-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-mission-campaign-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-multiball-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-final-campaign-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-video-consecutive-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-kickback-on-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-clock-award-4-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-clock-rewards-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/bigblam-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/mission-campaign-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/multiball-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/final-campaign-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/video-consecutive-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/kickback-on-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/clock-award-4-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/clock-rewards-rewards.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
   EXISTS "${_retail_music_dat}/SPACE.DAT" AND EXISTS "${_retail_music_dat}/DEMON.DAT" AND
   EXISTS "${_retail_music_dat}/../SLAMTILT.EXE")
  add_test(NAME retail_music_event_sequences COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_retail_music_events.py" --native "$<TARGET_FILE:slamslice>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/retail-music-events")
  set_tests_properties(retail_music_event_sequences PROPERTIES TIMEOUT 360)
endif()
set(_demon_clock_audio_ready TRUE)
foreach(_clock_index RANGE 0 11)
  if(NOT EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-clock-award-${_clock_index}-rewards.json" OR
     NOT EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/clock-award-${_clock_index}-rewards.json")
    set(_demon_clock_audio_ready FALSE)
  endif()
endforeach()
if(_demon_clock_audio_ready AND TARGET slamslice AND TARGET slamaudio AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
   EXISTS "${_retail_music_dat}/DEMON.DAT" AND EXISTS "${_retail_music_dat}/../SLAMTILT.EXE")
  add_test(NAME demon_clock_audio_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_demon_clock_audio.py" --native "$<TARGET_FILE:slamslice>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/demon-clock-audio")
  set_tests_properties(demon_clock_audio_original PROPERTIES TIMEOUT 180)
endif()
if(TARGET slamaudio AND TARGET slamview AND TARGET slamslice AND
   TARGET slampirate-import AND TARGET slamspace-import AND TARGET slamdemon-import AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MAIN.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/DEMON.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/pirate-full-tick/human-dat.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-full-game/human-dat.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/summary.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-image.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-runtime.bin" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-full-game/human-dat.bin")
  add_test(NAME retail_original_music_start COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_retail_original_music_start.py" --frontend
    --native-dir "$<TARGET_FILE_DIR:slamslice>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/retail-original-music-start.json")
  set_tests_properties(retail_original_music_start PROPERTIES TIMEOUT 180)
endif()

# Private Retail x86 replays: sample parameters at Space sound request entry.
set(_space_sfx_state_available TRUE)
foreach(_space_sfx_state_path IN ITEMS
    "build/venv/bin/python"
    "build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE"
    "build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT"
    "analysis/table-profiles.json" "analysis/space-audio-reuse.json"
    "analysis/traces/space-audio-events.json" "build/oracle/space-full-tick/trace.json"
    "build/oracle/space-full-game/summary.json" "build/oracle/space-full-game/human-image.bin"
    "build/oracle/space-full-game/human-runtime.bin" "build/oracle/space-full-game/human-dat.bin")
  if(NOT EXISTS "${CMAKE_SOURCE_DIR}/${_space_sfx_state_path}")
    set(_space_sfx_state_available FALSE)
  endif()
endforeach()
foreach(_space_sfx_state_case IN ITEMS base-rules kickback-off race-variants mission-campaign lane-shift planet-success)
  if(NOT EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/space-modes/${_space_sfx_state_case}-rewards.json" OR
     NOT EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/space-${_space_sfx_state_case}-rewards.json")
    set(_space_sfx_state_available FALSE)
  endif()
endforeach()
if(TARGET sfx_profiles_probe AND _space_sfx_state_available)
  add_test(NAME space_sfx_descriptor_state COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_space_sfx_descriptor_state.py"
    --native "$<TARGET_FILE:sfx_profiles_probe>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/space-sfx-descriptor-state.json")
  set_tests_properties(space_sfx_descriptor_state PROPERTIES TIMEOUT 180)
endif()
unset(_space_sfx_state_available)
unset(_space_sfx_state_path)
unset(_space_sfx_state_case)

if(TARGET slamaudio AND TARGET pirate_overlap_pcm_probe AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT")
  add_executable(pirate_combined_audio_probe tests/pirate_combined_audio_probe.cpp)
  target_link_libraries(pirate_combined_audio_probe PRIVATE slamaudio)
  add_test(NAME pirate_combined_audio_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_pirate_combined_audio.py"
    --native "$<TARGET_FILE:pirate_combined_audio_probe>" --sfx "$<TARGET_FILE:pirate_overlap_pcm_probe>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/pirate-combined-audio")
  set_tests_properties(pirate_combined_audio_original PROPERTIES TIMEOUT 120)
endif()

# Private Retail Demon sound requests with original descriptor fields.
set(_demon_sfx_state_available TRUE)
foreach(_demon_sfx_state_path IN ITEMS
    "build/venv/bin/python"
    "build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE"
    "build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/DEMON.DAT"
    "analysis/table-profiles.json" "analysis/demon-audio-profile.json"
    "build/oracle/demon-full-game/summary.json" "build/oracle/demon-full-game/human-image.bin"
    "build/oracle/demon-full-game/human-runtime.bin" "build/oracle/demon-full-game/human-dat.bin")
  if(NOT EXISTS "${CMAKE_SOURCE_DIR}/${_demon_sfx_state_path}")
    set(_demon_sfx_state_available FALSE)
  endif()
endforeach()
foreach(_demon_sfx_state_case IN ITEMS legal-game video-wolf-shoot clock-award-4)
  if(NOT EXISTS "${CMAKE_SOURCE_DIR}/build/oracle/demon-modes/${_demon_sfx_state_case}-rewards.json" OR
     NOT EXISTS "${CMAKE_SOURCE_DIR}/analysis/traces/demon-${_demon_sfx_state_case}-rewards.json")
    set(_demon_sfx_state_available FALSE)
  endif()
endforeach()
if(TARGET sfx_profiles_probe AND _demon_sfx_state_available)
  add_test(NAME demon_sfx_descriptor_state COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_demon_sfx_descriptor_state.py"
    --native "$<TARGET_FILE:sfx_profiles_probe>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/demon-sfx-descriptor-state.json")
  set_tests_properties(demon_sfx_descriptor_state PROPERTIES TIMEOUT 180)
endif()

if(TEST space_sfx_descriptor_state)
  add_test(NAME space_sfx_queue_timing_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_space_sfx_queue_timing.py"
    --output "${CMAKE_CURRENT_BINARY_DIR}/space-sfx-queue-timing.json")
  add_test(NAME space_sfx_mutations_original COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/trace_space_sfx_mutations.py" --native "$<TARGET_FILE:sfx_profiles_probe>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/space-sfx-mutations.json")
  set_tests_properties(space_sfx_queue_timing_original space_sfx_mutations_original PROPERTIES TIMEOUT 120)
endif()

# Isolated libxmp experiment; it never alters the port's linked library.
if(TARGET stim_audio_probe AND TARGET tracker_channel_probe AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/venv/bin/python" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/libxmp/src/period.c" AND
   EXISTS "${CMAKE_SOURCE_DIR}/docs/verification/tracker-floor-experiment-2026-10-31.json" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/SLAMTILT.EXE" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/MEAN.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/PIRATE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/SPACE.DAT" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/corpus/win95/_dokumente/Slam_Tilt_Win_RIP_EN/Game Files/SLAMTILT/DAT/DEMON.DAT")
  add_test(NAME tracker_period_experiment COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_tracker_period_experiment.py"
    --native "$<TARGET_FILE:stim_audio_probe>" --channel-probe "$<TARGET_FILE:tracker_channel_probe>"
    --work "${CMAKE_CURRENT_BINARY_DIR}/tracker-period-experiment"
    --output "${CMAKE_CURRENT_BINARY_DIR}/tracker-period-experiment/report.json")
  set_tests_properties(tracker_period_experiment PROPERTIES TIMEOUT 180 RESOURCE_LOCK tracker_period_experiment)
endif()

if(TEST tracker_period_experiment AND TARGET stim_audio_probe)
  add_test(NAME tracker_five_tick_experiment COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_tracker_five_tick_experiment.py"
    --native "$<TARGET_FILE:stim_audio_probe>"
    --library "${CMAKE_CURRENT_BINARY_DIR}/tracker-period-experiment/build/libxmp.so.4"
    --work "${CMAKE_CURRENT_BINARY_DIR}/tracker-five-tick-experiment"
    --output "${CMAKE_CURRENT_BINARY_DIR}/tracker-five-tick-experiment/report.json")
  set_tests_properties(tracker_five_tick_experiment PROPERTIES TIMEOUT 180 DEPENDS tracker_period_experiment RESOURCE_LOCK tracker_period_experiment)
endif()

if(TEST tracker_period_experiment)
  add_test(NAME tracker_stim_rate_experiment COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_tracker_period_experiment.py" --stim-only --original-rate
    --native "$<TARGET_FILE:stim_audio_probe>" --channel-probe "$<TARGET_FILE:tracker_channel_probe>"
    --work "${CMAKE_CURRENT_BINARY_DIR}/tracker-stim-rate-experiment"
    --output "${CMAKE_CURRENT_BINARY_DIR}/tracker-stim-rate-experiment/report.json")
  set_tests_properties(tracker_stim_rate_experiment PROPERTIES TIMEOUT 180 RESOURCE_LOCK tracker_stim_rate)
  add_test(NAME tracker_stim_rate_five_tick COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_tracker_five_tick_experiment.py"
    --native "$<TARGET_FILE:stim_audio_probe>" --library "${CMAKE_CURRENT_BINARY_DIR}/tracker-stim-rate-experiment/build/libxmp.so.4"
    --work "${CMAKE_CURRENT_BINARY_DIR}/tracker-stim-rate-five-tick"
    --output "${CMAKE_CURRENT_BINARY_DIR}/tracker-stim-rate-five-tick/report.json")
  set_tests_properties(tracker_stim_rate_five_tick PROPERTIES TIMEOUT 180 DEPENDS tracker_stim_rate_experiment RESOURCE_LOCK tracker_stim_rate)
  foreach(_loop_note IN ITEMS 13 24 25 28)
    add_test(NAME tracker_stim_rate_loop_${_loop_note} COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
      "${CMAKE_SOURCE_DIR}/tools/verify_tracker_long_loop.py" --native "$<TARGET_FILE:stim_audio_probe>"
      --library "${CMAKE_CURRENT_BINARY_DIR}/tracker-stim-rate-experiment/build/libxmp.so.4"
      --work "${CMAKE_CURRENT_BINARY_DIR}/tracker-stim-rate-loop-${_loop_note}"
      --output "${CMAKE_CURRENT_BINARY_DIR}/tracker-stim-rate-loop-${_loop_note}/report.json" --expect-stable --note ${_loop_note})
    set_tests_properties(tracker_stim_rate_loop_${_loop_note} PROPERTIES TIMEOUT 180 DEPENDS tracker_stim_rate_experiment RESOURCE_LOCK tracker_stim_rate)
  endforeach()
endif()

if(TARGET stim_audio_probe AND EXISTS "${CMAKE_SOURCE_DIR}/build/libxmp-build/libxmp.so.4" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/libxmp-stim-build/libxmp.so.4" AND
   EXISTS "${CMAKE_SOURCE_DIR}/build/libxmp/test-dev/data/Gaffeltruck.mod")
  add_test(NAME stim_non_stim_isolation COMMAND python3 "${CMAKE_SOURCE_DIR}/tools/verify_stim_isolation.py"
    --probe "$<TARGET_FILE:stim_audio_probe>" --baseline "${CMAKE_SOURCE_DIR}/build/libxmp-build/libxmp.so.4"
    --fixed "${CMAKE_SOURCE_DIR}/build/libxmp-stim-build/libxmp.so.4"
    --module "${CMAKE_SOURCE_DIR}/build/libxmp/test-dev/data/Gaffeltruck.mod"
    --output "${CMAKE_CURRENT_BINARY_DIR}/stim-non-stim-isolation.json")
endif()

if(TEST tracker_period_experiment)
  add_test(NAME stim_four_table_long_play COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_stim_long_play.py" --probe "$<TARGET_FILE:stim_audio_probe>"
    --work "${CMAKE_CURRENT_BINARY_DIR}/stim-long-play"
    --output "${CMAKE_CURRENT_BINARY_DIR}/stim-long-play/report.json")
  set_tests_properties(stim_four_table_long_play PROPERTIES TIMEOUT 180)
endif()

if(TEST tracker_period_experiment AND XMP_LIBRARY MATCHES "stim")
  add_test(NAME stim_four_table_original_quality COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_stim_original_quality.py" --native "$<TARGET_FILE:stim_audio_probe>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/stim-original-quality")
  set_tests_properties(stim_four_table_original_quality PROPERTIES TIMEOUT 180)
endif()

if(TEST pirate_combined_audio_original AND XMP_LIBRARY MATCHES "stim")
  add_test(NAME pirate_combined_stim_quality COMMAND "${CMAKE_SOURCE_DIR}/build/venv/bin/python"
    "${CMAKE_SOURCE_DIR}/tools/verify_pirate_combined_audio.py"
    --native "$<TARGET_FILE:pirate_combined_audio_probe>" --sfx "$<TARGET_FILE:pirate_overlap_pcm_probe>"
    --output "${CMAKE_CURRENT_BINARY_DIR}/pirate-combined-stim-quality" --min-correlation 0.999)
  set_tests_properties(pirate_combined_stim_quality PROPERTIES TIMEOUT 120)
endif()
