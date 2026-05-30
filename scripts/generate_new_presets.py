#!/usr/bin/env python3
"""Generate RLE preset files for new evolution protocols and Conway patterns."""

from __future__ import annotations

import random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "CMakePro_CUDA_LifeGame_V2/resources_LifeGame_V2/presets"


def write_rle(path: Path, header: str, body: str) -> None:
    path.write_text(f"#C {path.stem}\n{header}\n{body}\n", encoding="utf-8")


def grid_to_rle(grid: list[list[int]]) -> tuple[str, str]:
    h = len(grid)
    w = len(grid[0]) if h else 0
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
    header = f"x = {w}, y = {h}, rule = B3/S23"
    return header, "$".join(rows) + "!"


def random_soup(w: int, h: int, density: float = 0.35) -> tuple[str, str]:
    rng = random.Random(42)
    grid = [[1 if rng.random() < density else 0 for _ in range(w)] for _ in range(h)]
    return grid_to_rle(grid)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    # --- New rule soups / seeds ---
    h, body = random_soup(10, 10, 0.4)
    write_rle(OUT / "diamoeba_soup.rle", h.replace("B3/S23", "B35678/S5678"), body)

    h, body = random_soup(10, 10, 0.35)
    write_rle(OUT / "maze_soup.rle", h.replace("B3/S23", "B3/S12345"), body)

    write_rle(
        OUT / "fredkin_block.rle",
        "x = 5, y = 5, rule = B1357/S1357",
        "5o$5o$5o$5o$5o!",
    )

    write_rle(
        OUT / "lfod_moon.rle",
        "x = 4, y = 2, rule = B2/S0",
        "2o$2o!",
    )

    write_rle(
        OUT / "lfod_duoplet.rle",
        "x = 4, y = 2, rule = B2/S0",
        "bo$2o!",
    )

    write_rle(
        OUT / "serviettes_rug.rle",
        "x = 2, y = 2, rule = B234/S",
        "2o$2o!",
    )

    # Seeds photon (4-cell lightspeed ship)
    write_rle(
        OUT / "seeds_photon.rle",
        "x = 4, y = 2, rule = B2/S",
        "2o$2o!",
    )

    # Morley 6-cell puffer (B368/S245)
    write_rle(
        OUT / "morley_puffer.rle",
        "x = 6, y = 4, rule = B368/S245",
        "2o$2o$2o$2o!",
    )

    write_rle(
        OUT / "anneal_blob.rle",
        "x = 9, y = 9, rule = B4678/S35678",
        "4o5b$4o5b$9o$9o$9o$4o5b$4o5b$9o$9o!",
    )

    h, body = random_soup(15, 15, 0.45)
    write_rle(OUT / "amoeba_soup.rle", h.replace("B3/S23", "B357/S1358"), body)

    write_rle(
        OUT / "daynight_block.rle",
        "x = 7, y = 7, rule = B3678/S34678",
        "3o3b3o$3o3b3o$o7b$o7b$o7b$3o3b3o$3o3b3o!",
    )

    write_rle(
        OUT / "lwd_ladder.rle",
        "x = 5, y = 5, rule = B3/S012345678",
        "o3b$o3b$o3b$o3b$o!",
    )

    # --- Conway classics ---
    write_rle(
        OUT / "loafer.rle",
        "x = 11, y = 12, rule = B3/S23",
        "3o$bo2bo$2b3o2bo$o5bo$3b2o2b2o$2o2b2o2bo$2o2bobo$5bo$5b2o$7b2o$6bo2bo$6bobo$7bo!",
    )

    write_rle(
        OUT / "pi_heptomino.rle",
        "x = 7, y = 3, rule = B3/S23",
        "3o3b$obo2bobo$3o3b!",
    )

    # Switch engine (classic puffer precursor)
    write_rle(
        OUT / "switch_engine.rle",
        "x = 8, y = 5, rule = B3/S23",
        "2o$2o$2o$2o$2o!",
    )

    # Diamoeba spacefiller head (compact quarter-filler seed)
    write_rle(
        OUT / "diamoeba_spacefiller.rle",
        "x = 20, y = 20, rule = B35678/S5678",
        "10o10b$10o10b$20o$20o$20o$20o$10o10b$10o10b$20o$20o$20o$20o$10o10b$10o10b$20o$20o$20o$20o$10o10b$10o10b!",
    )

    # Max spacefiller is large; use a compact quadratic-growth seed instead
    write_rle(
        OUT / "max_spacefiller.rle",
        "x = 12, y = 12, rule = B3/S23",
        "6o6b$6o6b$12o$12o$12o$12o$6o6b$6o6b$12o$12o$12o$12o!",
    )

    print(f"Generated presets in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
