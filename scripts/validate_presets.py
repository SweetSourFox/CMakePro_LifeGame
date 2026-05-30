#!/usr/bin/env python3
"""Validate all LifeGame preset RLE files against kLifePresets metadata."""

from __future__ import annotations

import re
from pathlib import Path

PRESET_DIR = Path(__file__).resolve().parents[1] / "CMakePro_CUDA_LifeGame_V2/resources_LifeGame_V2/presets"
COMMON_H = Path(__file__).resolve().parents[1] / "CMakePro_CUDA_LifeGame_V2/Main_header/Common.h"

SIM_W, SIM_H = 1920, 1080


def parse_presets_from_common_h() -> list[dict]:
    text = COMMON_H.read_text(encoding="utf-8")
    block = text.split("inline const LifePreset kLifePresets[] = {", 1)[1].split("};", 1)[0]
    entries = []
    pattern = re.compile(
        r'\{\s*"([^"]+)",\s*"([^"]+\.rle)"[^}]*?'
        r'(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*',
    )
    for m in pattern.finditer(block):
        entries.append({
            "name": m.group(1),
            "file": m.group(2),
            "cropX": int(m.group(3)),
            "cropY": int(m.group(4)),
            "cropW": int(m.group(5)),
            "cropH": int(m.group(6)),
        })
    return entries


def parse_rle_header(line: str) -> tuple[int, int, str | None]:
    compact = re.sub(r"\s+", "", line)
    xm = re.search(r"x=(\d+)", compact, re.I)
    ym = re.search(r"y=(\d+)", compact, re.I)
    rm = re.search(r"rule=([^,]+)", compact, re.I)
    if not xm or not ym:
        return 0, 0, None
    return int(xm.group(1)), int(ym.group(1)), rm.group(1) if rm else None


def decode_rle(content: str) -> tuple[int, int, str | None, list[list[int]], list[str]]:
    issues: list[str] = []
    lines = [ln.rstrip("\n") for ln in content.splitlines()]
    header_line = None
    body_parts: list[str] = []
    for ln in lines:
        if not ln or ln.startswith("#"):
            continue
        if header_line is None and re.search(r"x\s*=", ln, re.I) and re.search(r"y\s*=", ln, re.I):
            header_line = ln
            continue
        if header_line is not None:
            body_parts.append(ln)
    if not header_line:
        return 0, 0, None, [], ["no header"]

    w, h, rule = parse_rle_header(header_line)
    grid = [[0] * w for _ in range(h)]
    data = "".join(body_parts)

    x = y = 0
    run = 0
    overflow = 0
    for ch in data:
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
                    else:
                        overflow += 1
                    x += 1
            elif ch == "$":
                y += cnt
                x = 0

    live = sum(sum(row) for row in grid)
    if live == 0:
        issues.append("zero live cells")
    if overflow:
        issues.append(f"{overflow} live cells outside header bounds")

    parsed_rows = y + 1
    if parsed_rows > h:
        issues.append(f"data spans {parsed_rows} rows but header y={h}")

    return w, h, rule, grid, issues


def crop_grid(grid: list[list[int]], x0: int, y0: int, cw: int, ch: int) -> list[list[int]]:
    return [row[x0:x0 + cw] for row in grid[y0:y0 + ch]]


def deploy_sim(name: str, preset: dict, w: int, h: int, grid: list[list[int]]) -> list[str]:
    issues: list[str] = []
    pw, ph = w, h
    if preset["cropW"] > 0 and preset["cropH"] > 0:
        x0, y0, cw, ch = preset["cropX"], preset["cropY"], preset["cropW"], preset["cropH"]
        if x0 >= w or y0 >= h:
            issues.append(f"crop origin ({x0},{y0}) outside pattern {w}x{h}")
            return issues
        cw = min(cw, w - x0)
        ch = min(ch, h - y0)
        grid = crop_grid(grid, x0, y0, cw, ch)
        pw, ph = cw, ch

    ox = max(0, SIM_W // 2 - pw // 2)
    oy = max(0, SIM_H // 2 - ph // 2)
    if ox + pw > SIM_W:
        issues.append(f"truncated horizontally: need {ox + pw} > {SIM_W}")
    if oy + ph > SIM_H:
        issues.append(f"truncated vertically: need {oy + ph} > {SIM_H}")
    if ox + pw <= ox or oy + ph <= oy:
        issues.append("entirely out of bounds on 1920x1080")
    live = sum(sum(row) for row in grid)
    if live == 0:
        issues.append("zero live cells after crop")
    return issues


def main() -> int:
    presets = parse_presets_from_common_h()
    print(f"Checking {len(presets)} presets on default grid {SIM_W}x{SIM_H}\n")
    bad = []
    for p in presets:
        path = PRESET_DIR / p["file"]
        if not path.exists():
            bad.append((p["name"], ["missing file"]))
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        w, h, rule, grid, parse_issues = decode_rle(content)
        if w <= 0 or h <= 0:
            bad.append((p["name"], parse_issues or ["parse failed"]))
            continue
        deploy_issues = deploy_sim(p["name"], p, w, h, grid)
        all_issues = parse_issues + deploy_issues
        live = sum(sum(row) for row in grid)
        status = "OK" if not all_issues else "FAIL"
        print(f"[{status}] {p['name']:<18} {p['file']:<35} {w:>5}x{h:<5} live={live:>8}  {'; '.join(all_issues)}")
        if all_issues:
            bad.append((p["name"], all_issues))

    print(f"\nSummary: {len(bad)} problematic / {len(presets)} total")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
