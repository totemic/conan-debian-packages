cmake_minimum_required(VERSION 3.0)

project(CryptoAuthLibTest)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

find_package(cryptoauthlib REQUIRED)

add_compile_options(-fpermissive)

add_executable("${PROJECT_NAME}" "${PROJECT_NAME}.cpp")
target_link_libraries(${PROJECT_NAME} cryptoauthlib::cryptoauthlib)

enable_testing()
add_test(NAME ${PROJECT_NAME}
    COMMAND ${CMAKE_CROSSCOMPILING_EMULATOR} "$<TARGET_FILE:${PROJECT_NAME}>")
