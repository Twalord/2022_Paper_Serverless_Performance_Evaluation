cmake_minimum_required(VERSION 3.5)
project(baseline_test)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

set(SOURCE_FILES baseline_test.cpp)

find_package(OpenMP REQUIRED)

add_executable(baseline_test.o ${SOURCE_FILES})
add_definitions( -DMAGICKCORE_QUANTUM_DEPTH=16 )
add_definitions( -DMAGICKCORE_HDRI_ENABLE=0 )
find_package(ImageMagick COMPONENTS Magick++)
include_directories(${ImageMagick_INCLUDE_DIRS})
target_link_libraries(baseline_test.o ${ImageMagick_LIBRARIES}  OpenMP::OpenMP_CXX)