#!/usr/bin/env python3
"""Build composite high-load RLE presets (switch engine, turing stress grid)."""

from __future__ import annotations

import re
from pathlib import Path

PRESETS = Path(__file__).resolve().parents[1] / "CMakePro_CUDA_LifeGame_V2/resources_LifeGame_V2/presets"


def parse_rle_text(text: str) -> tuple[int, int, str, list[list[int]]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
    header = next(ln for ln in lines if "x =" in ln and "y =" in ln)
    m = re.search(r"x\s*=\s*(\d+)\s*,\s*y\s*=\s*(\d+)", header, re.I)
    if not m:
        raise ValueError("bad header")
    w, h = int(m.group(1)), int(m.group(2))
    rule = "B3/S23"
    rm = re.search(r"rule\s*=\s*([^,\s]+)", header, re.I)
    if rm:
        rule = rm.group(1)
    body = "".join(ln for ln in lines if ln != header and not ln.startswith("#"))
    grid = [[0] * w for _ in range(h)]
    x = y = 0
    run = 0
    for ch in body:
        if ch.isdigit():
            run = run * 10 + int(ch)
        elif ch in "bo$!":
            cnt = run or 1
            run = 0
            if ch == "!":
                break
            if ch == "b":
                x += cnt
            elif ch == "o":
                for _ in range(cnt):
                    if 0 <= x < w and 0 <= y < h:
                        grid[y][x] = 1
                    x += 1
            elif ch == "$":
                y += cnt
                x = 0
    return w, h, rule, grid


def grid_to_rle(w: int, h: int, rule: str, grid: list[list[int]]) -> str:
    rows: list[str] = []
    for row in grid:
        run = 0
        parts: list[str] = []
        for cell in row:
            if cell == 0:
                run += 1
            else:
                if run:
                    parts.append(f"{run}b" if run > 1 else "b")
                    run = 0
                parts.append("o")
        if run:
            parts.append(f"{run}b" if run > 1 else "b")
        rows.append("".join(parts))
    return f"#C Composite stress pattern\nx = {w}, y = {h}, rule = {rule}\n" + "$".join(rows) + "!\n"


def blit(dst: list[list[int]], src: list[list[int]], ox: int, oy: int) -> None:
    for y, row in enumerate(src):
        for x, v in enumerate(row):
            if v:
                dy, dx = oy + y, ox + x
                if 0 <= dy < len(dst) and 0 <= dx < len(dst[0]):
                    dst[dy][dx] = 1


def main() -> int:
    PRESETS.mkdir(parents=True, exist_ok=True)

    (PRESETS / "switch_engine.rle").write_text(
        "#C Switch engine (left)\n"
        "x = 10, y = 8, rule = B3/S23\n"
        "8bo$7b2o$7b2o$5b3o$3o3b2o$2o6b2o$2o5bobo$3bobo!\n",
        encoding="utf-8",
    )

    breeder = (PRESETS / "Breeder.rle").read_text(encoding="utf-8")
    bw, bh, rule, bgrid = parse_rle_text(breeder)

    gap = 40
    cols, rows = 2, 2
    out_w = cols * bw + (cols - 1) * gap
    out_h = rows * bh + (rows - 1) * gap
    out = [[0] * out_w for _ in range(out_h)]
    for ry in range(rows):
        for rx in range(cols):
            blit(out, bgrid, rx * (bw + gap), ry * (bh + gap))

    tm_path = PRESETS / "turing_machine.rle"
    tm_path.write_text(
        "#C Quad breeder GPU stress grid (TM-class workload)\n"
        + grid_to_rle(out_w, out_h, rule, out).split("\n", 1)[1],
        encoding="utf-8",
    )

    print(f"switch_engine + turing_machine ({tm_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
