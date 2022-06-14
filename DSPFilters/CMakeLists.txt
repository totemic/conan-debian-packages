cmake_minimum_required(VERSION 3.0)

project (DSPFiltersWrapper)
set (CMAKE_CXX_STANDARD 11)

set(TARGET_DIR shared/DSPFilters)
add_subdirectory(${TARGET_DIR})

# Set public headers for correct exporting
file(GLOB PUBLIC_HEADERS "${TARGET_DIR}/include/DspFilters/*.h")
set_target_properties(DSPFilters PROPERTIES PUBLIC_HEADER "${PUBLIC_HEADERS}")

install(TARGETS DSPFilters
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/DspFilters)
