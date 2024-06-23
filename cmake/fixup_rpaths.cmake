
set(BUILD_DIR "${CMAKE_CURRENT_LIST_DIR}/../")
cmake_path(NORMAL_PATH BUILD_DIR)
message(STATUS "build directory is ${BUILD_DIR}")

set(INSTALL_DIR ${CPACK_TEMPORARY_INSTALL_DIRECTORY})
message(STATUS "install directory is ${INSTALL_DIR}")

#
set(RESET_RPATHS "${BUILD_DIR}/tools/reset_rpaths")

# fix rpath for programs
file(GLOB_RECURSE PROGRAM_FILES "${INSTALL_DIR}/bin/*")
foreach(PROGRAM_FILE ${PROGRAM_FILES})
    message(STATUS "fixing rpath for program ${PROGRAM_FILE}")
    execute_process(COMMAND ${RESET_RPATHS} ${PROGRAM_FILE} "@executable_path/../lib"
        WORKING_DIRECTORY ${BUILD_DIR}
        COMMAND_ERROR_IS_FATAL ANY
        )
endforeach()

# fix rpath for libraries
file(GLOB LIBRARY_FILES "${INSTALL_DIR}/lib/*${CMAKE_SHARED_LIBRARY_SUFFIX}")
foreach(LIBRARY_FILE ${LIBRARY_FILES})
    message(STATUS "fixing rpath for library ${LIBRARY_FILE}")
    execute_process(COMMAND ${RESET_RPATHS} ${LIBRARY_FILE} "@loader_path"
        WORKING_DIRECTORY ${BUILD_DIR}
        COMMAND_ERROR_IS_FATAL ANY
        )
endforeach()

# fix rpath for bootstrap plugins
file(GLOB BOOTSTRAP_PLUGIN_FILES "${INSTALL_DIR}/${LYRIC_BOOTSTRAP_DIR_PREFIX}/*${CMAKE_SHARED_LIBRARY_SUFFIX}")
foreach(BOOTSTRAP_PLUGIN_FILE ${BOOTSTRAP_PLUGIN_FILES})
    message(STATUS "fixing rpath for bootstrap plugin ${BOOTSTRAP_PLUGIN_FILE}")
    execute_process(COMMAND ${RESET_RPATHS} ${BOOTSTRAP_PLUGIN_FILE} "@executable_path/../lib"
        WORKING_DIRECTORY ${BUILD_DIR}
        COMMAND_ERROR_IS_FATAL ANY
    )
endforeach()

# fix rpath for plugins
file(GLOB_RECURSE PLUGIN_FILES "${INSTALL_DIR}/${ZURI_PACKAGES_DIR_PREFIX}/*${CMAKE_SHARED_LIBRARY_SUFFIX}")
foreach(PLUGIN_FILE ${PLUGIN_FILES})
    message(STATUS "fixing rpath for plugin ${PLUGIN_FILE}")
    execute_process(COMMAND ${RESET_RPATHS} ${PLUGIN_FILE} "@executable_path/../lib"
        WORKING_DIRECTORY ${BUILD_DIR}
        COMMAND_ERROR_IS_FATAL ANY
        )
endforeach()
