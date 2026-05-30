#!/usr/bin/env python3
"""Regenerate preset RLE files with header/body dimensions that match exactly."""

from __future__ import annotations

from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_presets import decode_rle

ROOT = Path(__file__).resolve().parents[1] / "CMakePro_CUDA_LifeGame_V2" / "resources_LifeGame_V2" / "presets"


def encode_rle(grid: list[list[int]], rule: str, comment: str) -> str:
    h = len(grid)
    w = len(grid[0]) if h else 0
    lines: list[str] = []
    for y, row in enumerate(grid):
        parts: list[str] = []
        x = 0
        while x < w:
            if row[x]:
                run = 0
                while x < w and row[x]:
                    run += 1
                    x += 1
                parts.append(f"{run}o" if run > 1 else "o")
            else:
                run = 0
                while x < w and not row[x]:
                    run += 1
                    x += 1
                parts.append(f"{run}b")
        line = "".join(parts)
        if y + 1 < h:
            line += "$"
        lines.append(line)
    body = "".join(lines) + "!"
    return f"#C {comment}\nx = {w}, y = {h}, rule = {rule}\n{body}\n"


def grid_from_rows(rows: list[str]) -> list[list[int]]:
    w = max(len(r) for r in rows)
    out: list[list[int]] = []
    for row in rows:
        line = row.ljust(w, ".")
        out.append([1 if c in "O1" else 0 for c in line])
    return out


PRESETS: dict[str, tuple[str, list[list[int]]]] = {
    "toad.rle": (
        "B3/S23",
        grid_from_rows([
            "..OOO.",
            "..OOO.",
            "......",
            "......",
        ]),
    ),
    "beacon.rle": (
        "B3/S23",
        grid_from_rows([
            "OO..",
            "OO..",
            "..OO",
            "..OO",
        ]),
    ),
    "pulsar.rle": (
        "B3/S23",
        None,  # use CANONICAL_RLE
    ),
    "loafer.rle": (
        "B3/S23",
        None,
    ),
    "pi_heptomino.rle": (
        "B3/S23",
        grid_from_rows([
            ".OO.",
            "O.O.O",
            ".OO.",
        ]),
    ),
    "morley_glider.rle": (
        "B368/S245",
        None,
    ),
    "glider_synth.rle": (
        "B3/S23",
        grid_from_rows([
            "..O........",
            ".O.........",
            "OO.........",
            "...........",
            "......O....",
            "....OOO....",
            "...O.......",
            "...OO......",
            "...O.......",
            "....OOO....",
            "......O....",
        ]),
    ),
    "daynight_seed.rle": (
        "B3678/S34678",
        grid_from_rows([
            "..OO.....",
            "..OO.....",
            "O........",
            "..OO.....",
            "..OO.....",
            "O........",
            "..OO.....",
        ]),
    ),
    "daynight_block.rle": (
        "B3678/S34678",
        grid_from_rows([
            "..OO.....",
            "..OO.....",
            "O........",
            "..OO.....",
            "..OO.....",
            "O........",
            "..OO.....",
        ]),
    ),
}


EXPECTED_LIVE: dict[str, int] = {
    "pulsar.rle": 48,
    "loafer.rle": 21,
    "pi_heptomino.rle": 7,
    "morley_glider.rle": 6,
    "toad.rle": 6,
    "beacon.rle": 8,
}

CANONICAL_RLE: dict[str, str] = {
    "pulsar.rle": """#C Pulsar (period-3 oscillator)
x = 13, y = 13, rule = B3/S23
2b3o3b3o2$o4bobo4bo$o4bobo4bo$o4bobo4bo$2b3o3b3o2$2b3o3b3o$o4bobo4bo$o4bobo4bo$o4bobo4bo$2b3o3b3o2!
""",
    "loafer.rle": """#C Loafer (c/7 orthogonal spaceship)
x = 9, y = 9, rule = B3/S23
bo$b2o$3bo$3o$o$6bo$5bobo$3ob2o2bo$2o4b2o!
""",
    "morley_glider.rle": """#C Morley glider (B368/S245)
x = 5, y = 4, rule = B368/S245
bo2bo$o4b$o4b$bo2bo!
""",
}


def main() -> None:
    for name, (rule, grid) in PRESETS.items():
        if grid is None:
            if name not in CANONICAL_RLE:
                raise SystemExit(f"Missing CANONICAL_RLE for {name}")
            content = CANONICAL_RLE[name]
            (ROOT / name).write_text(content, encoding="utf-8")
            w, h, _, g, _ = decode_rle(content)
            live = sum(sum(row) for row in g)
        else:
            live = sum(sum(row) for row in grid)
            if name in EXPECTED_LIVE and live != EXPECTED_LIVE[name]:
                raise SystemExit(f"{name}: expected {EXPECTED_LIVE[name]} live cells, got {live}")
            comment = name.replace(".rle", "").replace("_", " ").title()
            content = encode_rle(grid, rule, comment)
            (ROOT / name).write_text(content, encoding="utf-8")
            w, h = len(grid[0]), len(grid)
        if name in EXPECTED_LIVE and live != EXPECTED_LIVE[name]:
            raise SystemExit(f"{name}: expected {EXPECTED_LIVE[name]} live cells, got {live}")
        print(f"Wrote {name} ({w}x{h}, live={live})")


if __name__ == "__main__":
    main()
