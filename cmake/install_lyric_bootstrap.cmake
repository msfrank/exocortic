
include(generate_target_name)

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
