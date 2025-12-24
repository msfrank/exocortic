cmake_minimum_required(VERSION 3.27)

project(exocortic)

#######################################################################
#
# find required and optional dependencies
#
#######################################################################

# find required Tempo dependencies
find_package(tempo REQUIRED)

# find required Lyric dependencies
find_package(lyric REQUIRED)

# find required Zuri dependencies
find_package(zuri REQUIRED)

# find required Chord dependencies
#find_package(chord REQUIRED)

# find python installation
find_package(Python3 REQUIRED)

# include needed CMake features
include(CTest)
include(GNUInstallDirs)

#######################################################################
#
# define build constants
#
#######################################################################

# define individual version components and version string
string(REGEX REPLACE "([0-9]+)\\.[0-9]+\\.[0-9]+" "\\1"
    MAJOR_VERSION
    "${EXOCORTIC_VERSION}")
string(REGEX REPLACE "[0-9]+\\.([0-9]+)\\.[0-9]+" "\\1"
    MINOR_VERSION
    "${EXOCORTIC_VERSION}")
string(REGEX REPLACE "[0-9]+\\.[0-9]+\\.([0-9]+)" "\\1"
    PATCH_VERSION
    "${EXOCORTIC_VERSION}")
set(FULL_VERSION "${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}")
message(STATUS "version is ${FULL_VERSION}")

set(PLUGIN_SUFFIX "${CMAKE_SYSTEM_NAME}-${CMAKE_SYSTEM_PROCESSOR}${CMAKE_SHARED_LIBRARY_SUFFIX}")

#######################################################################
#
# include cmake helper functions
#
#######################################################################

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(install_lyric_bootstrap)
include(install_zuri_package)


#######################################################################
#
# build the distribution
#
#######################################################################

set(DESTINATION_ROOT "${CMAKE_BINARY_DIR}/distro/")

set(SYSTEM_ROOT_OPTS)

list(APPEND SYSTEM_ROOT_OPTS "/lib")
list(APPEND SYSTEM_ROOT_OPTS "/lib64")
list(APPEND SYSTEM_ROOT_OPTS "/usr/lib")
list(APPEND SYSTEM_ROOT_OPTS "/System")

list(TRANSFORM SYSTEM_ROOT_OPTS PREPEND "--system-root=")

set(VENDOR_ROOT_OPTS ${CONAN_RUNTIME_LIB_DIRS})
list(FILTER VENDOR_ROOT_OPTS INCLUDE REGEX "\/conan_packages\/")
list(TRANSFORM VENDOR_ROOT_OPTS REPLACE "\(\/.*\/conan_packages\/\(b\/\)?[a-zA-Z0-9]\+\/p\)\/.*" "\\1")
list(TRANSFORM VENDOR_ROOT_OPTS PREPEND "--vendor-root=")

get_target_property(TEMPO_GENERATE_KEYPAIR_PATH tempo::tempo-generate-keypair LOCATION)
get_target_property(LYRIC_DUMP_OBJECT_PATH lyric::lyric-dump-object LOCATION)
get_target_property(ZURI_BUILD_PATH zuri::zuri-build LOCATION)
get_target_property(ZURI_PKG_PATH zuri::zuri-pkg LOCATION)
get_target_property(ZURI_RUN_PATH zuri::zuri-run LOCATION)
get_target_property(ZURI_ZPK_PATH zuri::zuri-zpk LOCATION)

set(DISTRO_JSON_PATH "${CMAKE_BINARY_DIR}/distro.json")
add_custom_command(
    OUTPUT ${DISTRO_JSON_PATH}
    COMMAND
      ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/generate_distro_conf
        --binary ${TEMPO_GENERATE_KEYPAIR_PATH}
        --binary ${LYRIC_DUMP_OBJECT_PATH}
        --binary ${ZURI_BUILD_PATH}
        --binary ${ZURI_PKG_PATH}
        --binary ${ZURI_RUN_PATH}
        --binary ${ZURI_ZPK_PATH}
        ${SYSTEM_ROOT_OPTS}
        ${VENDOR_ROOT_OPTS}
        --destination-root ${DESTINATION_ROOT}
        ${DISTRO_JSON_PATH}
    COMMAND_EXPAND_LISTS
    COMMENT "generating ${DISTRO_JSON_PATH}"
)

add_custom_target(generate-distro-conf DEPENDS ${DISTRO_JSON_PATH})

add_custom_target(distro
    ALL
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tools/make_distro --clean ${DISTRO_JSON_PATH}
    DEPENDS generate-distro-conf
    )

#######################################################################
#
# install distribution
#
#######################################################################

install(DIRECTORY ${DESTINATION_ROOT}/bin/
    DESTINATION "bin"
    USE_SOURCE_PERMISSIONS
    )

install(DIRECTORY ${DESTINATION_ROOT}/lib/
    DESTINATION "lib"
    USE_SOURCE_PERMISSIONS
)


#######################################################################
#
# build package
#
#######################################################################

set(CPACK_PACKAGE_NAME "exocortic-runtime")
set(CPACK_PACKAGE_VENDOR "Exocortic Systems")
set(CPACK_PACKAGE_VERSION_MAJOR ${MAJOR_VERSION})
set(CPACK_PACKAGE_VERSION_MINOR ${MINOR_VERSION})
set(CPACK_PACKAGE_VERSION_PATCH ${PATCH_VERSION})
set(CPACK_PACKAGE_CHECKSUM "SHA256")
set(CPACK_GENERATOR "TGZ")

set(PLATFORM_ID "${CMAKE_SYSTEM_NAME}-${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_BUILD_TYPE}")
set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${EXOCORTIC_VERSION}.${PLATFORM_ID}")
set(CPACK_PACKAGE_DIRECTORY ${DISTRO_PACKAGE_DIRECTORY})

include(CPack)
