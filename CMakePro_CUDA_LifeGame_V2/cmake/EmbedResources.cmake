function(lifegame_embed_resources TARGET_NAME RESOURCE_DIR)
    if(NOT Python3_EXECUTABLE)
        find_package(Python3 REQUIRED COMPONENTS Interpreter)
    endif()

    if(NOT CMAKE_OBJCOPY)
        if(WIN32)
            find_program(_lifegame_gnu_objcopy
                NAMES objcopy
                PATHS
                    "$ENV{RUNNER_TEMP}/setup-msys2/mingw64/bin"
                    "C:/Program Files/Git/usr/bin"
                    "C:/msys64/mingw64/bin"
            )
            if(_lifegame_gnu_objcopy)
                set(CMAKE_OBJCOPY "${_lifegame_gnu_objcopy}")
            else()
                message(FATAL_ERROR
                    "GNU objcopy is required to embed resources on Windows. "
                    "Install mingw-w64-x86_64-binutils (msys2) or Git for Windows usr/bin/objcopy.")
            endif()
        else()
            find_program(CMAKE_OBJCOPY NAMES objcopy REQUIRED)
        endif()
    endif()

    if(WIN32 AND CMAKE_OBJCOPY MATCHES "llvm-objcopy")
        message(FATAL_ERROR
            "llvm-objcopy cannot produce MSVC-linkable PE objects for embedded resources. "
            "Use GNU objcopy from msys2 or Git for Windows.")
    endif()

    if(WIN32)
        set(_lifegame_obj_ext "obj")
        set(_lifegame_objcopy_format "pe-x86-64")
        set(_lifegame_objcopy_arch "i386")
    else()
        set(_lifegame_obj_ext "o")
        set(_lifegame_objcopy_format "elf64-x86-64")
        set(_lifegame_objcopy_arch "i386:x86-64")
    endif()

    set(_lifegame_objcopy_input_flag "--input")
    set(_lifegame_objcopy_output_flag "--output")
    set(_lifegame_objcopy_arch_flag "--binary-architecture=${_lifegame_objcopy_arch}")

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
        set(_obj "${CMAKE_CURRENT_BINARY_DIR}/embed/${_sym}.${_lifegame_obj_ext}")

        add_custom_command(
            OUTPUT "${_obj}"
            COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_BINARY_DIR}/embed"
            COMMAND ${CMAKE_COMMAND} -E chdir "${RESOURCE_DIR}"
                ${CMAKE_OBJCOPY}
                ${_lifegame_objcopy_input_flag} binary
                ${_lifegame_objcopy_output_flag} ${_lifegame_objcopy_format}
                ${_lifegame_objcopy_arch_flag}
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
