cmake_minimum_required(VERSION 3.1)
project(test_package C)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(PROJ REQUIRED)

add_executable(test_package test_package.c)
target_link_libraries(test_package PROJ::proj)
