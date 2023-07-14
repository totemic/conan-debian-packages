cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(gpioDetect gpioDetect.cpp)
target_link_libraries(gpioDetect ${CONAN_LIBS})
target_compile_features(gpioDetect PUBLIC cxx_std_11)