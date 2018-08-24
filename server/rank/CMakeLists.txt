cmake_minimum_required(VERSION 3.7)
project(rank)

set(CMAKE_C_STANDARD 99)

set(SOURCE_FILES main.c)
add_executable(rank ${SOURCE_FILES})
target_link_libraries(rank curl)
target_link_libraries(rank json-c)
