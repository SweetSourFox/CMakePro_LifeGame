# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview

This is a CUDA + OpenGL Game of Life simulator (`CMakePro_CUDA_LifeGame_V2`). It is a native C++/CUDA desktop application requiring an NVIDIA GPU at runtime.

### Build (Linux)

```bash
export PATH=/usr/local/cuda-12.8/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH
mkdir -p build && cd build
cmake .. -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DCMAKE_CUDA_ARCHITECTURES=89 -DCMAKE_BUILD_TYPE=Release
cmake --build . -j$(nproc)
```

The binary is produced at `build/CMakePro_CUDA_LifeGame_V2/CMakePro_CUDA_LifeGame_V2`.

### Key caveats

- **No GPU in Cloud Agent VMs**: The application requires a physical NVIDIA CUDA-capable GPU at runtime. Without one, the binary will print `[失败] 未找到 CUDA 设备或驱动程序异常！` and exit with code 255. Compilation still works because `nvcc` can cross-compile for a target architecture (set via `-DCMAKE_CUDA_ARCHITECTURES=89`).
- **Compiler**: Use GCC (`gcc`/`g++`), not the default Clang, because the system Clang links against GCC 14's libstdc++ which is not installed. Pass `-DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++` to cmake.
- **CUDA path**: CUDA 12.8 is installed at `/usr/local/cuda-12.8/`. You must add its `bin` to `PATH` and `lib64` to `LD_LIBRARY_PATH` before running cmake or the built binary.
- **Static analysis**: Run `cppcheck` for linting. Warnings from vendored ImGui/ImPlot libraries are expected and can be ignored.
- **Cross-platform portability**: The CMakeLists.txt uses `if(WIN32)` / `else()` to support both Windows (hardcoded paths) and Linux (`find_package`/`pkg-config`). Platform-specific APIs (`localtime_s` vs `localtime_r`, `strncpy_s` vs `strncpy`) are guarded with `#ifdef _WIN32` / `#ifdef _MSC_VER`.
