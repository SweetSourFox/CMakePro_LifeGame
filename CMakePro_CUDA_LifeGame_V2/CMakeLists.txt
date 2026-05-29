# ==========================================
# 1. 基础环境配置 (必须在 project 之前)
# ==========================================
cmake_minimum_required(VERSION 3.18)

if(POLICY CMP0141)
    cmake_policy(SET CMP0141 NEW)
endif()

if(MSVC)
    set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT Embedded)
    set(CMAKE_CUDA_COMPILE_OPTIONS_MSVC_PDB_OUTPUT_PATH "" CACHE STRING "" FORCE)
endif()

if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
    if(WIN32)
        set(CMAKE_CUDA_ARCHITECTURES 89)
    else()
        set(CMAKE_CUDA_ARCHITECTURES native)
    endif()
endif()

project(CMakePro_CUDA_LifeGame_V2 LANGUAGES CXX C CUDA)

set(TARGET_NAME "CMakePro_CUDA_LifeGame_V2")

option(LIFEGAME_STANDALONE "Build a self-contained executable with embedded resources" ON)
option(LIFEGAME_USE_LEGACY_WIN_LIBS "Use legacy D:/CPP_lib paths on Windows (local dev only)" OFF)

find_package(CUDAToolkit REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
if(NOT WIN32)
    find_package(OpenGL REQUIRED)
endif()

# ==========================================
# 2. 第三方库 (GLFW / GLEW)
# ==========================================
if(LIFEGAME_STANDALONE)
    include(FetchContent)
    set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
    set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    set(GLFW_INSTALL OFF CACHE BOOL "" FORCE)
    set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
    FetchContent_Declare(glfw
        GIT_REPOSITORY https://github.com/glfw/glfw.git
        GIT_TAG 3.3.10
    )
    FetchContent_MakeAvailable(glfw)

    FetchContent_Declare(glew
        GIT_REPOSITORY https://github.com/Perlmint/glew-cmake.git
        GIT_TAG glew-cmake-2.2.0
    )
    set(ONLY_LIBS ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(glew)
elseif(WIN32 AND LIFEGAME_USE_LEGACY_WIN_LIBS)
    set(LIB_ROOT "D:/CPP_lib")
    set(OPENGL_ROOT "${LIB_ROOT}/OpenGL")
    set(SDL2_ROOT   "${LIB_ROOT}/SDL2/SDL2-devel-2.30.9-VC/SDL2-2.30.9")
    set(CUDAToolkit_ROOT "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8")
else()
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(GLFW3 REQUIRED glfw3)
    pkg_check_modules(GLEW REQUIRED glew)
    find_package(OpenGL REQUIRED)
endif()

# ==========================================
# 3. 收集源文件
# ==========================================
file(GLOB IMGUIDocking_SRCS
    "ImGui_docking/*.cpp"
    "ImPlot/*.cpp"
)
file(GLOB CUDA_USER_SOURCES "CUDA_Kernels/Cuda_Check.cu")
file(GLOB CUDA_USER_HEADERS "CUDA_Kernels/Cuda_Check.cuh")
set(PROJECT_SRCS "Main_cpp/CMakePro_cuda.cpp")
set(STB_SRCS "stb_image/stb_image_write.h")

# ==========================================
# 4. 创建可执行文件
# ==========================================
add_executable(${TARGET_NAME}
    ${IMGUIDocking_SRCS}
    ${STB_SRCS}
    ${PROJECT_SRCS}
    ${CUDA_USER_SOURCES}
    ${CUDA_USER_HEADERS}
    "Main_header/Common.h"
)

set_target_properties(${TARGET_NAME} PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED ON
    CUDA_STANDARD 17
    OUTPUT_NAME "LifeGame_GPU"
)

if(MSVC)
    set_target_properties(${TARGET_NAME} PROPERTIES
        MSVC_DEBUG_INFORMATION_FORMAT Embedded
    )
    target_compile_options(${TARGET_NAME} PRIVATE
        $<$<COMPILE_LANGUAGE:CXX>:/FS /utf-8>
        $<$<COMPILE_LANGUAGE:CUDA>:--use_fast_math -Xcompiler=/wd4819 -Xcompiler=/utf-8 -Xcompiler=/Z7>
    )
else()
    target_compile_options(${TARGET_NAME} PRIVATE
        $<$<COMPILE_LANGUAGE:CUDA>:--use_fast_math>
        $<$<COMPILE_LANGUAGE:CXX>:-Wall -Wextra -Wno-unused-parameter>
    )
endif()

# ==========================================
# 5. 资源文件 (嵌入或复制)
# ==========================================
set(RESOURCE_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/resources_LifeGame_V2")

if(LIFEGAME_STANDALONE)
    include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/EmbedResources.cmake")
    lifegame_embed_resources(${TARGET_NAME} "${RESOURCE_SRC_DIR}")
else()
    set(RESOURCE_DEST_DIR "${CMAKE_BINARY_DIR}/resources_LifeGame_V2")
    file(GLOB_RECURSE RESOURCE_FILES "${RESOURCE_SRC_DIR}/*")
    add_custom_target(copy_resources_LifeGame_V2
        COMMAND ${CMAKE_COMMAND} -E copy_directory_if_different ${RESOURCE_SRC_DIR} ${RESOURCE_DEST_DIR}
        DEPENDS ${RESOURCE_FILES}
        COMMENT "Syncing resource files..."
    )
    add_dependencies(${TARGET_NAME} copy_resources_LifeGame_V2)
endif()

# ==========================================
# 6. Include 路径
# ==========================================
target_include_directories(${TARGET_NAME} PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/Main_header"
    "${CMAKE_CURRENT_SOURCE_DIR}/ImGui_docking"
    "${CMAKE_CURRENT_SOURCE_DIR}/ImPlot"
    "${CMAKE_CURRENT_SOURCE_DIR}/stb_image"
    "${CMAKE_CURRENT_SOURCE_DIR}/CUDA_Kernels"
)

# ==========================================
# 7. 链接库
# ==========================================
target_compile_definitions(${TARGET_NAME} PRIVATE GLEW_STATIC)

if(WIN32)
    if(LIFEGAME_USE_LEGACY_WIN_LIBS)
        target_include_directories(${TARGET_NAME} PRIVATE
            "${OPENGL_ROOT}/glew-2.1.0-win32/glew-2.1.0/include"
            "${OPENGL_ROOT}/glfw-3.4.bin.WIN64/glfw-3.4.bin.WIN64/include"
            "${SDL2_ROOT}/include"
            "${CUDAToolkit_ROOT}/include"
        )
        target_link_directories(${TARGET_NAME} PRIVATE
            "${OPENGL_ROOT}/glfw-3.4.bin.WIN64/glfw-3.4.bin.WIN64/lib-vc2022"
            "${OPENGL_ROOT}/glew-2.1.0-win32/glew-2.1.0/lib/Release/x64"
            "${SDL2_ROOT}/lib/x64"
            "${CUDAToolkit_ROOT}/lib/x64"
        )
        target_link_libraries(${TARGET_NAME} PRIVATE
            glfw3.lib glew32s.lib opengl32.lib
            user32.lib gdi32.lib shell32.lib
            cudart.lib
        )
    else()
        target_link_libraries(${TARGET_NAME} PRIVATE
            glfw
            libglew_static
            opengl32.lib
            user32.lib gdi32.lib shell32.lib
            CUDA::cudart_static
        )
    endif()
else()
    if(LIFEGAME_STANDALONE)
        target_link_libraries(${TARGET_NAME} PRIVATE
            glfw
            libglew_static
            OpenGL::GL
            CUDA::cudart_static
            dl pthread rt m X11
        )
        target_link_options(${TARGET_NAME} PRIVATE
            -static-libstdc++
            -static-libgcc
        )
    else()
        target_include_directories(${TARGET_NAME} PRIVATE
            ${GLFW3_INCLUDE_DIRS}
            ${GLEW_INCLUDE_DIRS}
        )
        target_link_libraries(${TARGET_NAME} PRIVATE
            ${GLFW3_LIBRARIES}
            ${GLEW_LIBRARIES}
            OpenGL::GL
            CUDA::cudart
            dl pthread
        )
    endif()
endif()

source_group("Source Files\\CUDA" FILES ${CUDA_USER_SOURCES} ${CUDA_USER_HEADERS})
source_group("Source Files\\ImGui" FILES ${IMGUIDocking_SRCS})
