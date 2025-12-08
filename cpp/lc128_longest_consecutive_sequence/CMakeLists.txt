cmake_minimum_required(VERSION 3.16)

project(lc128_longest_consecutive_sequence)

set(CMAKE_CXX_STANDARD 23)

include_directories(/opt/homebrew/Cellar/abseil/20250814.0/include)
include_directories(/opt/homebrew/Cellar/boost/1.89.0/include)
include_directories(/Users/antoxa/_Dev/meow)
link_directories(/opt/homebrew/Cellar/abseil/20250814.0/lib)

add_executable(lc128_longest_consecutive_sequence lc128_longest_consecutive_sequence.cpp)

file(GLOB ABSL_LIBS "/opt/homebrew/Cellar/abseil/20250814.0/lib/libabsl_*.dylib")
target_link_libraries(lc128_longest_consecutive_sequence ${ABSL_LIBS})
