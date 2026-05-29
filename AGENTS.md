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

The binary is produced at `build/CMakePro_CUDA_LifeGame_V2/LifeGame_GPU` (standalone build, ~38 MB).

### GitHub Release (Linux + Windows)

Push a version tag to trigger `.github/workflows/release.yml`:

```bash
git tag v1.2.0
git push origin v1.2.0
```

The workflow builds standalone executables for both platforms and publishes a GitHub Release:

| Platform | Artifact |
|----------|----------|
| Linux x64 | `LifeGame_GPU_Linux_x64` |
| Windows x64 | `LifeGame_GPU_Windows_x64.exe` |

Both include embedded shaders, fonts, icons, and all preset RLE patterns. Runtime still requires an NVIDIA GPU with up-to-date drivers and a desktop environment (OpenGL + X11 on Linux).

### Standalone single-file build (Linux, default ON)

Use `-DLIFEGAME_STANDALONE=ON` (default) to produce a self-contained executable:

- All shaders, fonts, icons, and 17 preset RLE patterns are **embedded inside the binary**
- GLFW, GLEW, and CUDA runtime are **statically linked**
- No `resources_LifeGame_V2/` folder is required at runtime
- Binary size is ~38 MB (includes ~30 MB preset data)

```bash
cmake .. -DLIFEGAME_STANDALONE=ON -DCMAKE_BUILD_TYPE=Release ...
```

Runtime still requires OS-provided **NVIDIA GPU driver**, **OpenGL**, and **X11** — these cannot be bundled into a single file.

To build with external resource files instead: `-DLIFEGAME_STANDALONE=OFF`

### Key caveats

- **No GPU in Cloud Agent VMs**: The application requires a physical NVIDIA CUDA-capable GPU at runtime. Without one, the binary will print `[失败] 未找到 CUDA 设备或驱动程序异常！` and exit with code 255. Compilation still works because `nvcc` can cross-compile for a target architecture (set via `-DCMAKE_CUDA_ARCHITECTURES=89`).
- **Compiler**: Use GCC (`gcc`/`g++`), not the default Clang, because the system Clang links against GCC 14's libstdc++ which is not installed. Pass `-DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++` to cmake.
- **CUDA path**: CUDA 12.8 is installed at `/usr/local/cuda-12.8/`. You must add its `bin` to `PATH` and `lib64` to `LD_LIBRARY_PATH` before running cmake or the built binary.
- **Static analysis**: Run `cppcheck` for linting. Warnings from vendored ImGui/ImPlot libraries are expected and can be ignored.
- **Cross-platform portability**: The CMakeLists.txt uses `if(WIN32)` / `else()` to support both Windows (hardcoded paths) and Linux (`find_package`/`pkg-config`). Platform-specific APIs (`localtime_s` vs `localtime_r`, `strncpy_s` vs `strncpy`) are guarded with `#ifdef _WIN32` / `#ifdef _MSC_VER`.
