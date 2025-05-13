cmake_minimum_required(VERSION 3.10)
project(intel_hw_decoder)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(VPL REQUIRED vpl)
pkg_check_modules(VA REQUIRED libva libva-drm)

set(SOURCE_FILES 
    main.cpp
)

add_executable(intel_decoder ${SOURCE_FILES})

target_include_directories(intel_decoder PRIVATE
    ${VPL_INCLUDE_DIRS}
    ${VA_INCLUDE_DIRS}
)

target_link_libraries(intel_decoder
    ${VPL_LIBRARIES}
    ${VA_LIBRARIES}
    dl
    pthread
)

target_compile_options(intel_decoder PRIVATE
    -Wall
    -Wextra
    ${VPL_CFLAGS_OTHER}
    ${VA_CFLAGS_OTHER}
)

install(TARGETS intel_decoder DESTINATION bin)