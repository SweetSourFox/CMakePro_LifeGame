#!/usr/bin/env python3
"""Generate C++ registry for objcopy-embedded resource objects."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def symbol_for_rel_path(rel_path: str) -> str:
    return "_binary_" + rel_path.replace("/", "_").replace(".", "_").replace("-", "_")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("resource_root", type=Path)
    parser.add_argument("manifest", type=Path, help="Text file: one relative path per line")
    parser.add_argument("header_out", type=Path)
    parser.add_argument("source_out", type=Path)
    args = parser.parse_args()

    rel_paths = [
        line.strip()
        for line in args.manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    extern_lines = []
    table_lines = []

    for rel in rel_paths:
        sym = symbol_for_rel_path(rel)
        extern_lines.append(f"extern \"C\" const unsigned char {sym}_start[];")
        extern_lines.append(f"extern \"C\" const unsigned char {sym}_end[];")
        table_lines.append(
            f'    {{ "{rel}", {sym}_start, '
            f"(size_t)({sym}_end - {sym}_start) }},"
        )

    header = f"""#pragma once

#include <cstddef>

struct EmbeddedAsset {{
    const char* path;
    const unsigned char* data;
    std::size_t size;
}};

const EmbeddedAsset* FindEmbeddedAsset(const char* path);
bool HasEmbeddedAsset(const char* path);
std::size_t GetEmbeddedAssetCount();
"""

    source = f"""#include "EmbeddedResources.h"
#include <cstring>

{chr(10).join(extern_lines)}

static const EmbeddedAsset kEmbeddedAssets[] = {{
{chr(10).join(table_lines)}
}};

const EmbeddedAsset* FindEmbeddedAsset(const char* path) {{
    if (!path) return nullptr;
    for (const EmbeddedAsset& asset : kEmbeddedAssets) {{
        if (std::strcmp(asset.path, path) == 0) return &asset;
    }}
    return nullptr;
}}

bool HasEmbeddedAsset(const char* path) {{
    return FindEmbeddedAsset(path) != nullptr;
}}

std::size_t GetEmbeddedAssetCount() {{
    return sizeof(kEmbeddedAssets) / sizeof(kEmbeddedAssets[0]);
}}
"""

    args.header_out.parent.mkdir(parents=True, exist_ok=True)
    args.header_out.write_text(header, encoding="utf-8")
    args.source_out.write_text(source, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
