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
    set(CMAKE_CUDA_ARCHITECTURES native)
endif()

project(CMakePro_CUDA_LifeGame_V2 LANGUAGES CXX C CUDA)

set(TARGET_NAME "CMakePro_CUDA_LifeGame_V2")

# ==========================================
# 2. 第三方库路径设置 (跨平台)
# ==========================================
if(WIN32)
    set(LIB_ROOT "D:/CPP_lib")
    set(OPENGL_ROOT "${LIB_ROOT}/OpenGL")
    set(SDL2_ROOT   "${LIB_ROOT}/SDL2/SDL2-devel-2.30.9-VC/SDL2-2.30.9")
    set(CUDAToolkit_ROOT "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8")
else()
    find_package(CUDAToolkit REQUIRED)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(GLFW3 REQUIRED glfw3)
    pkg_check_modules(GLEW REQUIRED glew)
    find_package(OpenGL REQUIRED)
    pkg_check_modules(SDL2 REQUIRED sdl2)
    pkg_check_modules(SDL2_IMAGE REQUIRED SDL2_image)
    pkg_check_modules(SDL2_MIXER REQUIRED SDL2_mixer)
endif()

# ==========================================
# 3. 收集源文件
# ==========================================
# ImGui & ImPlot (Docking 分支)
file(GLOB IMGUIDocking_SRCS
    "ImGui_docking/*.cpp"
    "ImPlot/*.cpp"
)

# CUDA 核函数文件
file(GLOB CUDA_USER_SOURCES "CUDA_Kernels/Cuda_Check.cu")
file(GLOB CUDA_USER_HEADERS "CUDA_Kernels/Cuda_Check.cuh")

# 项目主源文件
set(PROJECT_SRCS "Main_cpp/CMakePro_cuda.cpp")

# STB Image (仅头文件)
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

# ==========================================
# 5. 编译选项与标准设置
# ==========================================
set_target_properties(${TARGET_NAME} PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED ON
    CUDA_STANDARD 17
)

if(MSVC)
    set_target_properties(${TARGET_NAME} PROPERTIES
        MSVC_DEBUG_INFORMATION_FORMAT Embedded
    )
    target_compile_options(${TARGET_NAME} PRIVATE
        $<$<COMPILE_LANGUAGE:CXX>:/FS>
    )
    target_compile_options(${TARGET_NAME} PRIVATE
        $<$<COMPILE_LANGUAGE:CUDA>:
            --use_fast_math
            -Xcompiler=/wd4819
            -Xcompiler=/utf-8
            -Xcompiler=/Z7
        >
    )
else()
    target_compile_options(${TARGET_NAME} PRIVATE
        $<$<COMPILE_LANGUAGE:CUDA>:
            --use_fast_math
        >
        $<$<COMPILE_LANGUAGE:CXX>:
            -Wall -Wextra -Wno-unused-parameter
        >
    )
endif()

# ==========================================
# 6. 资源文件同步 (resources_gpu_v32)
# ==========================================
set(RESOURCE_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/resources_LifeGame_V2")
set(RESOURCE_DEST_DIR "${CMAKE_BINARY_DIR}/resources_LifeGame_V2")

file(GLOB_RECURSE RESOURCE_FILES "${RESOURCE_SRC_DIR}/*")

add_custom_target(copy_resources_LifeGame_V2
    COMMAND ${CMAKE_COMMAND} -E copy_directory_if_different ${RESOURCE_SRC_DIR} ${RESOURCE_DEST_DIR}
    DEPENDS ${RESOURCE_FILES}
    COMMENT "Syncing resource files..."
)
add_dependencies(${TARGET_NAME} copy_resources_LifeGame_V2)

# ==========================================
# 7. 配置头文件路径 (Include)
# ==========================================
target_include_directories(${TARGET_NAME} PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/Main_header"
    "${CMAKE_CURRENT_SOURCE_DIR}/ImGui_docking"
    "${CMAKE_CURRENT_SOURCE_DIR}/ImPlot"
    "${CMAKE_CURRENT_SOURCE_DIR}/stb_image"
    "${CMAKE_CURRENT_SOURCE_DIR}/CUDA_Kernels"
)

if(WIN32)
    target_include_directories(${TARGET_NAME} PRIVATE
        "${OPENGL_ROOT}/glm-master/glm-master"
        "${OPENGL_ROOT}/glew-2.1.0-win32/glew-2.1.0/include"
        "${OPENGL_ROOT}/glfw-3.4.bin.WIN64/glfw-3.4.bin.WIN64/include"
        "${SDL2_ROOT}/include"
        "${CUDAToolkit_ROOT}/include"
    )

    # ==========================================
    # 8. 配置库路径 (Link Directories) - Windows
    # ==========================================
    target_link_directories(${TARGET_NAME} PRIVATE
        "${OPENGL_ROOT}/glfw-3.4.bin.WIN64/glfw-3.4.bin.WIN64/lib-vc2022"
        "${OPENGL_ROOT}/glew-2.1.0-win32/glew-2.1.0/lib/Release/x64"
        "${SDL2_ROOT}/lib/x64"
        "${CUDAToolkit_ROOT}/lib/x64"
    )

    # ==========================================
    # 9. 链接库与定义 - Windows
    # ==========================================
    target_compile_definitions(${TARGET_NAME} PRIVATE GLEW_STATIC)
    target_link_libraries(${TARGET_NAME} PRIVATE
        glfw3.lib glew32s.lib opengl32.lib
        user32.lib gdi32.lib shell32.lib
        SDL2.lib SDL2_image.lib SDL2_mixer.lib
        cudart.lib cuda.lib
    )
else()
    # ==========================================
    # 8+9. Linux: use pkg-config and find_package results
    # ==========================================
    target_include_directories(${TARGET_NAME} PRIVATE
        ${GLFW3_INCLUDE_DIRS}
        ${GLEW_INCLUDE_DIRS}
        ${SDL2_INCLUDE_DIRS}
        ${SDL2_IMAGE_INCLUDE_DIRS}
        ${SDL2_MIXER_INCLUDE_DIRS}
        ${CUDAToolkit_INCLUDE_DIRS}
    )
    target_compile_definitions(${TARGET_NAME} PRIVATE GLEW_STATIC)
    target_link_libraries(${TARGET_NAME} PRIVATE
        ${GLFW3_LIBRARIES}
        ${GLEW_LIBRARIES}
        OpenGL::GL
        ${SDL2_LIBRARIES}
        ${SDL2_IMAGE_LIBRARIES}
        ${SDL2_MIXER_LIBRARIES}
        CUDA::cudart
        CUDA::cuda_driver
        dl pthread
    )
endif()

# ==========================================
# 10. IDE 视图美化 (可选)
# ==========================================
source_group("Source Files\\CUDA" FILES ${CUDA_USER_SOURCES} ${CUDA_USER_HEADERS})
source_group("Source Files\\ImGui" FILES ${IMGUIDocking_SRCS})