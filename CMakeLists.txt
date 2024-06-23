cmake_minimum_required(VERSION 3.27)

project(xoco-dist)

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
find_package(chord REQUIRED)

# include needed CMake features
include(CTest)
include(GNUInstallDirs)

#######################################################################
#
# define build constants
#
#######################################################################

set(FULL_PLATFORM "${CMAKE_SYSTEM_NAME}.${CMAKE_SYSTEM_VERSION}-${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_CXX_COMPILER_ID}")
message(STATUS "full platform is ${FULL_PLATFORM}")

# define individual version components and version string
string(REGEX REPLACE "([0-9]+)\\.[0-9]+\\.[0-9]+" "\\1"
    MAJOR_VERSION
    "${XOCO_DIST_VERSION}")
string(REGEX REPLACE "[0-9]+\\.([0-9]+)\\.[0-9]+" "\\1"
    MINOR_VERSION
    "${XOCO_DIST_VERSION}")
string(REGEX REPLACE "[0-9]+\\.[0-9]+\\.([0-9]+)" "\\1"
    PATCH_VERSION
    "${XOCO_DIST_VERSION}")
set(FULL_VERSION "${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}")
message(STATUS "version is ${FULL_VERSION}")

set(PLUGIN_SUFFIX "${CMAKE_SYSTEM_NAME}-${CMAKE_SYSTEM_PROCESSOR}${CMAKE_SHARED_LIBRARY_SUFFIX}")

#######################################################################
#
# define cmake helper functions
#
#######################################################################

set_property(GLOBAL PROPERTY curr_generated_target_index "0")

function(generate_target_name TARGET_VAR)
    get_property(curr_index GLOBAL PROPERTY curr_generated_target_index)
    set(${TARGET_VAR} "xoco_generated_target_${curr_index}")
    math(EXPR next_index "${curr_index} + 1")
    set_property(GLOBAL PROPERTY curr_generated_target_index "${next_index}")
    return(PROPAGATE ${TARGET_VAR})
endfunction()

function(install_lyric_bootstrap BOOTSTRAP_DIR)
    message(STATUS "adding bootstrap from ${BOOTSTRAP_DIR}")

    file(GLOB_RECURSE MODULE_FILES RELATIVE "${BOOTSTRAP_DIR}" "${BOOTSTRAP_DIR}/*.lyo")

    foreach(MODULE_FILE ${MODULE_FILES})
        cmake_path(GET MODULE_FILE PARENT_PATH PARENT_DIR)
        set(DEST_DIR "${LYRIC_BOOTSTRAP_DIR_PREFIX}/${PARENT_DIR}")
        cmake_path(NORMAL_PATH DEST_DIR)

        install(FILES "${BOOTSTRAP_DIR}/${MODULE_FILE}" DESTINATION "${DEST_DIR}")
        message(STATUS "install ${LYRIC_BOOTSTRAP_DIR_PREFIX}/${MODULE_FILE}")

        string(REPLACE ".lyo" ".${PLUGIN_SUFFIX}" PLUGIN_FILE "${MODULE_FILE}")
        find_file(PLUGIN_EXISTS ${PLUGIN_FILE} PATHS ${BOOTSTRAP_DIR} NO_CACHE NO_DEFAULT_PATH)
        if (NOT ${PLUGIN_EXISTS} EQUAL "PLUGIN_EXISTS-NOTFOUND")
            generate_target_name(PLUGIN_TARGET)

            add_library(${PLUGIN_TARGET} MODULE IMPORTED)
            set_target_properties(${PLUGIN_TARGET} PROPERTIES IMPORTED_LOCATION "${BOOTSTRAP_DIR}/${PLUGIN_FILE}")

            install(IMPORTED_RUNTIME_ARTIFACTS ${PLUGIN_TARGET}
                RUNTIME_DEPENDENCY_SET all-deps
                LIBRARY DESTINATION ${DEST_DIR}
            )

            message(STATUS "install ${LYRIC_BOOTSTRAP_DIR_PREFIX}/${PLUGIN_FILE}")
        endif()
    endforeach()

endfunction()

function(install_zuri_package PACKAGES_DIR PACKAGE_ID)
    message(STATUS "adding ${PACKAGE_ID} from ${PACKAGES_DIR}")

    set(PACKAGE_PATH "${PACKAGES_DIR}/${PACKAGE_ID}")
    file(GLOB_RECURSE MODULE_FILES RELATIVE "${PACKAGE_PATH}" "${PACKAGE_PATH}/*.lyo")

    foreach(MODULE_FILE ${MODULE_FILES})
        cmake_path(GET MODULE_FILE PARENT_PATH PARENT_DIR)
        set(DEST_DIR "${ZURI_PACKAGES_DIR_PREFIX}/${PACKAGE_ID}/${PARENT_DIR}")
        cmake_path(NORMAL_PATH DEST_DIR)

        install(FILES "${PACKAGE_PATH}/${MODULE_FILE}" DESTINATION "${DEST_DIR}")
        message(STATUS "install ${ZURI_PACKAGES_DIR_PREFIX}/${PACKAGE_ID}/${MODULE_FILE}")

        string(REPLACE ".lyo" ".${PLUGIN_SUFFIX}" PLUGIN_FILE "${MODULE_FILE}")
        find_file(PLUGIN_EXISTS ${PLUGIN_FILE} PATHS ${PACKAGE_PATH} NO_CACHE NO_DEFAULT_PATH)
        if (NOT ${PLUGIN_EXISTS} EQUAL "PLUGIN_EXISTS-NOTFOUND")
            generate_target_name(PLUGIN_TARGET)

            add_library(${PLUGIN_TARGET} MODULE IMPORTED)
            set_target_properties(${PLUGIN_TARGET} PROPERTIES IMPORTED_LOCATION "${PACKAGE_PATH}/${PLUGIN_FILE}")

            install(IMPORTED_RUNTIME_ARTIFACTS ${PLUGIN_TARGET}
                RUNTIME_DEPENDENCY_SET all-deps
                LIBRARY DESTINATION ${DEST_DIR}
                )

            message(STATUS "install ${ZURI_PACKAGES_DIR_PREFIX}/${PACKAGE_ID}/${PLUGIN_FILE}")
        endif()
    endforeach()

endfunction()

#######################################################################
#
# install runtime artifacts
#
#######################################################################

# install programs
install(IMPORTED_RUNTIME_ARTIFACTS
    tempo::tempo-bytes2code
    tempo::tempo-generate-keypair
    lyric::lyric-dump-object
    zuri::zuri
    zuri::zuri-build
    chord::chord-agent
    chord::chord-local-machine
    RUNTIME_DEPENDENCY_SET all-deps
    )

# install lyric bootstrap
install_lyric_bootstrap(${LYRIC_RUNTIME_BOOTSTRAP_DIR})

# install zuri packages
install_zuri_package(${ZURI_INSTALL_PACKAGES_DIR} ${ZURI_STD_PACKAGE_ID})

# install library dependencies
install(RUNTIME_DEPENDENCY_SET all-deps
    DIRECTORIES ${CONAN_RUNTIME_LIB_DIRS}
    POST_EXCLUDE_REGEXES ".*/.conan2/p/b/[a-z0-9]+/b/.*"
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    )

# install system configuration
install(DIRECTORY "${ZURI_INSTALL_CONFIG_DIR}/"
    DESTINATION ${ZURI_CONFIG_DIR_PREFIX}
    USE_SOURCE_PERMISSIONS
    )

# install vendor configuration
#install(DIRECTORY ${ZURI_INSTALL_VENDOR_CONFIG_DIR}
#    DESTINATION ${ZURI_VENDOR_CONFIG_DIR_PREFIX}
#    )

# install documentation
#install(DIRECTORY ${ZURI_INSTALL_DOC_DIR}
#    DESTINATION ${ZURI_DOC_DIR_PREFIX}
#    )

#######################################################################
#
# configure packaging
#
#######################################################################

set(CPACK_PACKAGE_DIRECTORY "${CMAKE_BINARY_DIR}/dist")

set(CPACK_PRE_BUILD_SCRIPTS "${CMAKE_SOURCE_DIR}/cmake/fixup_rpaths.cmake")

set(CPACK_PACKAGE_NAME "xoco-dist")
set(CPACK_PACKAGE_VENDOR "Exocortic Systems")
set(CPACK_PACKAGE_VERSION_MAJOR ${MAJOR_VERSION})
set(CPACK_PACKAGE_VERSION_MINOR ${MINOR_VERSION})
set(CPACK_PACKAGE_VERSION_PATCH ${PATCH_VERSION})
set(CPACK_GENERATOR "TGZ")

include(CPack)
