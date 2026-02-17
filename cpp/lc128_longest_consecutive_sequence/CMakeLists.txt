cmake_minimum_required(VERSION 3.16)

project(lc128_longest_consecutive_sequence LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE INTERNAL "always generate compile_commands.json for IDEs")

add_executable(lc128_longest_consecutive_sequence lc128_longest_consecutive_sequence.cpp)
target_compile_features(lc128_longest_consecutive_sequence PRIVATE cxx_std_23)

# Help package discovery on Homebrew-based systems without hardcoding versions.
find_program(BREW_EXECUTABLE brew)
if(BREW_EXECUTABLE)
    execute_process(
        COMMAND "${BREW_EXECUTABLE}" --prefix
        OUTPUT_VARIABLE HOMEBREW_PREFIX
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    if(HOMEBREW_PREFIX)
        list(PREPEND CMAKE_PREFIX_PATH "${HOMEBREW_PREFIX}")
        message(STATUS "Homebrew prefix detected: ${HOMEBREW_PREFIX}")
    endif()
else()
    message(STATUS "Homebrew not detected; relying on default CMake search paths")
endif()


# meow is a local dependency; allow override and provide a practical default.
set(MEOW_ROOT "" CACHE PATH "Path to the meow repository root")
if(MEOW_ROOT)
    if(EXISTS "${MEOW_ROOT}/meow/stopwatch.hpp"
        AND EXISTS "${MEOW_ROOT}/meow/api_call_error.hpp"
        AND EXISTS "${MEOW_ROOT}/meow/ptr_list.hpp"
    )
        target_include_directories(lc128_longest_consecutive_sequence PRIVATE "${MEOW_ROOT}")
        message(STATUS "Found meow headers: ${MEOW_ROOT}")
    else()
        message(FATAL_ERROR "Could not find required meow headers. Set -DMEOW_ROOT=/path/to/meow")
    endif()
else()
    message(FATAL_ERROR "Meow path is not specified, please pass -DMEOW_ROOT=/path/to/meow")
endif()


find_package(absl CONFIG REQUIRED)
if(TARGET absl::flat_hash_map)
    target_link_libraries(lc128_longest_consecutive_sequence PRIVATE absl::flat_hash_map)
    message(STATUS "Found Abseil ${absl_VERSION}: using target absl::flat_hash_map")
else()
    message(FATAL_ERROR "Found Abseil package, but target absl::flat_hash_map is missing")
endif()

# Keep Boost detection explicit (meow headers may depend on it).
find_package(Boost CONFIG REQUIRED)
if(TARGET Boost::headers)
    target_link_libraries(lc128_longest_consecutive_sequence PRIVATE Boost::headers)
    message(STATUS "Found Boost ${Boost_VERSION_STRING}: ${Boost_INCLUDE_DIRS}")
else()
    message(FATAL_ERROR "Boost found by CMake, but no usable imported target or include dirs were provided")
endif()
