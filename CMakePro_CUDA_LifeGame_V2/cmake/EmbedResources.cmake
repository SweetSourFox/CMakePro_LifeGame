function(lifegame_embed_resources TARGET_NAME RESOURCE_DIR)
    file(GLOB_RECURSE _lifegame_resource_files RELATIVE "${RESOURCE_DIR}" "${RESOURCE_DIR}/*")
    set(_lifegame_rel_paths "")
    set(_lifegame_embed_objects "")
    set(_lifegame_embed_depends "")

    foreach(_rel ${_lifegame_resource_files})
        set(_abs "${RESOURCE_DIR}/${_rel}")
        if(IS_DIRECTORY "${_abs}")
            continue()
        endif()

        string(REPLACE "/" "_" _sym "${_rel}")
        string(REPLACE "." "_" _sym "${_sym}")
        string(REPLACE "-" "_" _sym "${_sym}")
        set(_obj "${CMAKE_CURRENT_BINARY_DIR}/embed/${_sym}.o")

        add_custom_command(
            OUTPUT "${_obj}"
            COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_BINARY_DIR}/embed"
            COMMAND ${CMAKE_COMMAND} -E chdir "${RESOURCE_DIR}"
                ${CMAKE_OBJCOPY}
                --input binary
                --output elf64-x86-64
                --binary-architecture i386:x86-64
                --rename-section .data=.rodata,alloc,load,readonly,data,contents
                "${_rel}"
                "${_obj}"
            DEPENDS "${_abs}"
            COMMENT "Embedding resource ${_rel}"
            VERBATIM
        )

        list(APPEND _lifegame_rel_paths "${_rel}")
        list(APPEND _lifegame_embed_objects "${_obj}")
        list(APPEND _lifegame_embed_depends "${_abs}")
    endforeach()

    list(JOIN _lifegame_rel_paths "\n" _lifegame_manifest_content)
    set(_lifegame_manifest "${CMAKE_CURRENT_BINARY_DIR}/embed/manifest.txt")
    file(WRITE "${_lifegame_manifest}" "${_lifegame_manifest_content}\n")

    set(_lifegame_registry_h "${CMAKE_CURRENT_BINARY_DIR}/embed/EmbeddedResources.h")
    set(_lifegame_registry_cpp "${CMAKE_CURRENT_BINARY_DIR}/embed/EmbeddedResources.cpp")

    add_custom_command(
        OUTPUT "${_lifegame_registry_h}" "${_lifegame_registry_cpp}"
        COMMAND ${Python3_EXECUTABLE}
            "${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_embed_registry.py"
            "${RESOURCE_DIR}"
            "${_lifegame_manifest}"
            "${_lifegame_registry_h}"
            "${_lifegame_registry_cpp}"
        DEPENDS
            "${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_embed_registry.py"
            "${_lifegame_manifest}"
            ${_lifegame_embed_depends}
        COMMENT "Generating embedded resource registry"
        VERBATIM
    )

    target_sources(${TARGET_NAME} PRIVATE
        "${_lifegame_registry_cpp}"
        ${_lifegame_embed_objects}
    )
    target_include_directories(${TARGET_NAME} PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/embed")
    target_compile_definitions(${TARGET_NAME} PRIVATE LIFEGAME_EMBEDDED_RESOURCES=1)
endfunction()
