cmake_minimum_required(VERSION 2.8)
project(ftpdownload)

if (CMAKE_VERSION VERSION_LESS "3.1")
    if (CMAKE_C_COMPILER_ID STREQUAL "GNU")
        set (CMAKE_C_FLAGS "-std=gnu99 ${CMAKE_C_FLAGS}")
    endif ()
else ()
    set (CMAKE_C_STANDARD 99)
endif ()

project(rank)

set(CMAKE_C_STANDARD 99)

set(SOURCE_FILES main.c)
add_executable(rank ${SOURCE_FILES})
target_link_libraries(rank curl)
target_link_libraries(rank json-c)
