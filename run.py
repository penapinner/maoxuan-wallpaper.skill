#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
毛选壁纸 — One-click random wallpaper.

Picks a random Mao Zedong quote, generates a calligraphic wallpaper,
and optionally sets it as the desktop background.

Usage:
    python run.py                        # Save to current dir
    python run.py --output ~/Desktop/   # Save to specific dir
    python run.py --set-wallpaper        # Generate + set as wallpaper
    python run.py 52                     # Use quote #52 specifically
"""

import json, os, random, subprocess, sys, argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
QUOTES_PATH = SCRIPT_DIR / "quotes.json"
GEN_SCRIPT = SCRIPT_DIR / "gen_wallpaper.py"


def load_quotes():
    with open(QUOTES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="毛选壁纸 — 一键随机语录桌面壁纸")
    parser.add_argument("index", nargs="?", type=int, default=None,
                        help="指定语录编号 (1-100)，不指定则随机")
    parser.add_argument("--output", "-o", default="mao_quote_wallpaper.png",
                        help="输出路径 (default: mao_quote_wallpaper.png)")
    parser.add_argument("--set-wallpaper", "-w", action="store_true",
                        help="生成后设为桌面壁纸")
    parser.add_argument("--list", "-l", action="store_true",
                        help="列出所有语录")
    args = parser.parse_args()

    quotes = load_quotes()

    if args.list:
        for i, q in enumerate(quotes, 1):
            print(f"{i:3d}. {q['quote']}")
            print(f"      {q['volume']} · {q['article']} ({q['date']})")
            print()
        return

    # Pick quote
    if args.index is not None:
        if args.index < 1 or args.index > len(quotes):
            print(f"Error: index must be 1-{len(quotes)}")
            sys.exit(1)
        q = quotes[args.index - 1]
    else:
        q = random.choice(quotes)

    print(f"[Quote #{quotes.index(q) + 1}] {q['quote']}")
    print(f"   {q['volume']} · {q['article']}")

    # Build command
    cmd = [
        sys.executable, str(GEN_SCRIPT),
        "--quote", q["quote"],
        "--volume", q["volume"],
        "--article", q["article"],
        "--date", q["date"],
        "--vertical-year", q["year"],
        "--note", q["note"],
        "--output", args.output,
    ]
    if args.set_wallpaper:
        cmd.append("--set-wallpaper")

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
