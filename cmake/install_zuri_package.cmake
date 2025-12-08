
include(generate_target_name)

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
