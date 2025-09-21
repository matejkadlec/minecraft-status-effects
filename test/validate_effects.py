#!/usr/bin/env python3
"""Validate ordering of data/effects.json.

Rules:
1. All entries with mod == "Minecraft" appear first as a single contiguous section.
2. Inside the Minecraft section effects sorted alphabetically by `effect`.
3. Remaining entries grouped by `mod`, groups ordered alphabetically by mod.
4. Each group's effects sorted alphabetically by `effect`.
5. No duplicate effect names globally (effect name must be unique across all mods).
Exit code 0 if valid, else >0 with human-readable diagnostics to stderr.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

PREFIX = "[Effects Validation]"
import re

EFFECTS_PATH = Path(__file__).resolve().parent.parent / "data" / "effects.json"


def load_effects():
    try:
        with EFFECTS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        fail(f"File not found: {EFFECTS_PATH}")
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON in {EFFECTS_PATH}: {e}")

    if "effects" not in data or not isinstance(data["effects"], list):
        fail("Missing 'effects' list in JSON root")
    return data["effects"]


def fail(msg: str, code: int = 1):
    print(f"{PREFIX} ❌ {msg}", file=sys.stderr)
    sys.exit(code)


def validate_formula_wrapping(effects):
    """Ensure '^level' and '× level' appear only inside <b>...</b> and terminate the bold span.

    Rules:
    - Any occurrence of '^level' must be inside a <b>...</b> whose content ends with '^level'.
    - Any occurrence of '× level' must be inside a <b>...</b> whose content ends with '× level'.
    - These substrings must not appear outside bold tags.
    """
    for eff in effects:
        desc = eff.get("description") or ""
        name = eff.get("effect")
        if "^level" not in desc and "× level" not in desc:
            continue
        bold_spans = re.findall(r"<b>(.*?)</b>", desc)
        outside = re.sub(r"<b>.*?</b>", "", desc)
        if "^level" in outside:
            fail(f"Formula '^level' outside <b> in effect '{name}'")
        if "× level" in outside:
            fail(f"Formula '× level' outside <b> in effect '{name}'")
        for span in bold_spans:
            if "^level" in span and not span.endswith("^level"):
                fail(
                    f"'^level' not at end of bold span in effect '{name}' -> <b>{span}</b>"
                )
            if (
                "× level" in span
                and not span.endswith("× level")
                and "^level" not in span
            ):
                fail(
                    f"'× level' not at end of bold span in effect '{name}' -> <b>{span}</b>"
                )


def main():
    print(f"{PREFIX}: 🚀 Starting validation...")
    effects = load_effects()

    # Ordering validation section
    print(f"{PREFIX}: 1/3 Ordering checks started...")

    if not effects:
        fail("No effects present (empty list)")

    # Collect indices of the Minecraft section
    minecraft_indices = [
        i for i, e in enumerate(effects) if e.get("mod") == "Minecraft"
    ]
    if not minecraft_indices:
        fail("Minecraft section missing (no entries with mod 'Minecraft')")

    # Must be contiguous starting at 0
    if minecraft_indices[0] != 0 or minecraft_indices != list(
        range(minecraft_indices[0], minecraft_indices[-1] + 1)
    ):
        fail("Minecraft section not first or not contiguous")

    # Check minecraft alphabetical order by effect
    mc_slice = effects[minecraft_indices[0] : minecraft_indices[-1] + 1]
    mc_effect_names = [e.get("effect") for e in mc_slice]
    if mc_effect_names != sorted(mc_effect_names, key=lambda s: s.lower()):
        # Find first out-of-order pair
        for a, b in zip(mc_effect_names, mc_effect_names[1:]):
            if a.lower() > b.lower():
                fail(
                    f"Minecraft ordering error: '{a}' should come after '{b}' (alphabetical)"
                )

    # Remaining effects
    tail = effects[minecraft_indices[-1] + 1 :]

    # Build mod -> list mapping preserving order
    mods_in_order = []
    mod_to_effects = {}
    for eff in tail:
        mod = eff.get("mod")
        if mod == "Minecraft":
            fail("Found a Minecraft effect after mod sections (section must be first)")
        if mod not in mod_to_effects:
            mods_in_order.append(mod)
            mod_to_effects[mod] = []
        mod_to_effects[mod].append(eff)

    # Check mods alphabetical
    if mods_in_order != sorted(mods_in_order, key=lambda s: s.lower()):
        for a, b in zip(mods_in_order, mods_in_order[1:]):
            if a.lower() > b.lower():
                fail(
                    f"Mod ordering error: '{a}' should come after '{b}' (alphabetical)"
                )

    # Check each mod internal order
    for mod, eff_list in mod_to_effects.items():
        names = [e.get("effect") for e in eff_list]
        if names != sorted(names, key=lambda s: s.lower()):
            for a, b in zip(names, names[1:]):
                if a.lower() > b.lower():
                    fail(
                        f"Effect ordering error in mod '{mod}': '{a}' should come after '{b}' (alphabetical)"
                    )
    print(f"{PREFIX}: ✅ Effect ordering checks passed.")

    # Duplication validation section
    print(f"{PREFIX}: 2/3 Duplicate name check started...")
    # Check duplicate effect names globally
    seen_names = set()
    for e in effects:
        name = e.get("effect")
        if name in seen_names:
            fail(f"Duplicate effect name detected: '{name}'")
        seen_names.add(name)

    print(f"{PREFIX}: ✅ Effect duplicate name check passed.")

    # Formula / bold formatting validation section
    print(f"{PREFIX}: 3/3 Formula formatting check started...")
    validate_formula_wrapping(effects)
    print(f"{PREFIX}: ✅ Formula formatting check passed.")
    print(f"{PREFIX}: ✨ All 3/3 checks passed.")


if __name__ == "__main__":
    main()
