#cmake_minimum_required(VERSION 2.8.11)
cmake_minimum_required(VERSION 3.5)
project(ConanWrapper C)

message(STATUS "Conan CMake Wrapper")
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

#set_property(TARGET common_obj PROPERTY POSITION_INDEPENDENT_CODE ON)

set(lib_target_name hidapi)


message("CMAKE_SYSTEM_NAME: ${CMAKE_SYSTEM_NAME}")

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    message("Building for Linux")
    if(HIDAPI_BUILD_LIBUSB)
        message("Using libUsb")
        set(library_SOURCES sources/libusb/hid.c)
        set(lib_link_libraries CONAN_PKG::libusb)
    else()
        message("Using HID Raw")
        set(library_SOURCES sources/linux/hid.c)
        set(lib_link_libraries CONAN_PKG::libudev1)
    endif()
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    message("Building for OSX")
    set(library_SOURCES sources/mac/hid.c)
    if(HIDAPI_BUILD_SHARED)
        set(lib_link_libraries 
            "-framework CoreFoundation"
            "-framework IOKit")
    endif()

elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    message("Building for Windows")
    set(library_SOURCES sources/windows/hid.c)
else()
    message(FATAL_ERROR "CMAKE_SYSTEM_NAME: ${CMAKE_SYSTEM_NAME} not supported!")
endif()

message("HIDAPI_BUILD_SHARED: ${HIDAPI_BUILD_SHARED}")
if(HIDAPI_BUILD_SHARED)
    message("Building shared library")
    add_library(${lib_target_name} SHARED ${library_SOURCES})
else()
    message("Building static library")
    add_library(${lib_target_name} STATIC ${library_SOURCES})
endif()


target_include_directories(${lib_target_name} PUBLIC sources/hidapi)
target_link_libraries(${lib_target_name} PUBLIC ${lib_link_libraries}
        PRIVATE pthread
        )

set_target_properties(${lib_target_name} PROPERTIES PUBLIC_HEADER
        "sources/hidapi/hidapi.h")

install(TARGETS ${lib_target_name}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/hidapi
        COMPONENT library
        )