#!/usr/bin/env python3
"""Utility to re-sort data/effects.json deterministically.

Usage:
  python scripts/sort_effects.py [--check]

--check : exit 0 if already sorted, else 1 and print a diff-like summary.

This script enforces the same ordering rules as validate_effects.py but will
rewrite the file in-place (unless --check).
"""
from __future__ import annotations
import json, sys, argparse
from pathlib import Path

EFFECTS_PATH = Path(__file__).resolve().parent.parent / "data" / "effects.json"


def load():
    with EFFECTS_PATH.open("r", encoding="utf-8") as f:
        root = json.load(f)
    return root


def save(root):
    EFFECTS_PATH.write_text(
        json.dumps(root, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def sort_effects(effects):
    mc = [e for e in effects if e["mod"] == "Minecraft"]
    others = [e for e in effects if e["mod"] != "Minecraft"]
    mc_sorted = sorted(mc, key=lambda e: e["effect"].lower())
    # group others by mod
    mod_map = {}
    for e in others:
        mod_map.setdefault(e["mod"], []).append(e)
    mods_sorted = sorted(mod_map.keys(), key=lambda s: s.lower())
    ordered = mc_sorted
    for mod in mods_sorted:
        ordered.extend(sorted(mod_map[mod], key=lambda e: e["effect"].lower()))
    return ordered


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check", action="store_true", help="Only check ordering, do not rewrite file"
    )
    args = ap.parse_args()

    root = load()
    effects = root["effects"]
    sorted_effects = sort_effects(effects)
    if [e["id"] for e in effects] == [e["id"] for e in sorted_effects]:
        print("[sort_effects] Already sorted.")
        return 0
    if args.check:
        print("[sort_effects] NOT sorted. First differing position:")
        for i, (a, b) in enumerate(zip(effects, sorted_effects)):
            if a["id"] != b["id"]:
                print(f"  index {i}: current={a['id']} expected={b['id']}")
                break
        return 1
    root["effects"] = sorted_effects
    save(root)
    print("[sort_effects] Rewrote effects.json with deterministic ordering.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
