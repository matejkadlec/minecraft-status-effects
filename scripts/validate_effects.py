#!/usr/bin/env python3
"""Validate ordering of data/effects.json.

Rules:
1. All entries with mod == "Minecraft" appear first as a single contiguous section.
2. Inside the Minecraft section effects sorted alphabetically by `effect`.
3. Remaining entries grouped by `mod`, groups ordered alphabetically by mod.
4. Each group's effects sorted alphabetically by `effect`.
5. No duplicate effect names globally (effect name must be unique across all mods).
6. Formula formatting: '^level' and '× level' must be in <b> tags and properly positioned.
7. Time units: All "second", "seconds", "second(s)" must be in <b> tags.
8. Description length must be ≤125 chars (excluding HTML tags).

Exit code 0 if valid, else >0 with human-readable diagnostics to stderr.
"""
from __future__ import annotations
import json
import sys
import re
from pathlib import Path

PREFIX = "[Effects Validation]"

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


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text for length calculation."""
    return re.sub(r"<[^>]+>", "", text)


def validate_formula_and_time_wrapping(effects):
    """Ensure formulas and time units are properly wrapped in <b> tags.

    Rules:
    - '^level' and '× level' must be inside <b> tags and either be at the end
      or followed by "second", "seconds", or "second(s)"
    - Every instance of "second", "seconds", or "second(s)" must be wrapped in <b> tags
    """
    # Terms that must be in bold
    time_terms = ["second", "seconds", "second(s)"]
    formula_terms = ["^level", "× level"]

    for eff in effects:
        desc = eff.get("description") or ""
        name = eff.get("effect") or "Unknown"

        # Extract bold content and content outside bold
        bold_spans = re.findall(r"<b>(.*?)</b>", desc)
        outside = re.sub(r"<b>.*?</b>", "", desc)

        # Check for formula terms outside bold
        for term in formula_terms:
            if term in outside:
                fail(f"Formula '{term}' must be in <b> tags in effect '{name}'")

        # Check for time terms outside bold
        for term in time_terms:
            if term in outside:
                fail(f"Time unit '{term}' must be in <b> tags in effect '{name}'")

        # Check formula placement within bold spans
        for span in bold_spans:
            # For ^level
            if "^level" in span:
                valid_endings = [
                    "^level",
                    "^level second",
                    "^level seconds",
                    "^level second(s)",
                ]
                if not any(span.endswith(end) for end in valid_endings):
                    fail(
                        f"'^level' incorrectly positioned in bold span in effect '{name}' -> <b>{span}</b>"
                    )

            # For × level (when not in a span with ^level)
            if "× level" in span and "^level" not in span:
                valid_endings = [
                    "× level",
                    "× level second",
                    "× level seconds",
                    "× level second(s)",
                ]
                if not any(span.endswith(end) for end in valid_endings):
                    fail(
                        f"'× level' incorrectly positioned in bold span in effect '{name}' -> <b>{span}</b>"
                    )


def main():
    print(f"{PREFIX}: 🚀 Starting validation...")
    effects = load_effects()

    # Ordering validation section
    print(f"{PREFIX}: 1/5 Ordering checks started...")

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
    print(f"{PREFIX}: 2/5 Duplicate name check started...")
    # Check duplicate effect names globally
    seen_names = set()
    for e in effects:
        name = e.get("effect")
        if name in seen_names:
            fail(f"Duplicate effect name detected: '{name}'")
        seen_names.add(name)

    print(f"{PREFIX}: ✅ Effect duplicate name check passed.")

    # Formula and time wrapping validation section
    print(f"{PREFIX}: 3/5 Formula and time formatting check started...")
    validate_formula_and_time_wrapping(effects)
    print(f"{PREFIX}: ✅ Formula and time formatting check passed.")

    # Description length validation
    print(f"{PREFIX}: 4/5 Description length check started...")
    for eff in effects:
        desc = (eff.get("description") or "").strip()
        desc_without_html = strip_html_tags(desc)
        if len(desc_without_html) > 125:
            fail(
                f"Description too long (>125 chars) in effect '{eff.get('effect')}': {len(desc_without_html)} chars (without HTML tags)"
            )
    print(f"{PREFIX}: ✅ Description length check passed.")

    # Tags validation
    print(f"{PREFIX}: 5/5 Tags validation check started...")
    for eff in effects:
        tags = eff.get("tags", [])
        if not isinstance(tags, list):
            fail(f"Tags must be a list for effect '{eff.get('effect')}'")

        if "positive" not in tags and "negative" not in tags:
            fail(
                f"Effect '{eff.get('effect')}' must have either 'positive' or 'negative' tag"
            )

        if "positive" in tags and "negative" in tags:
            fail(
                f"Effect '{eff.get('effect')}' cannot have both 'positive' and 'negative' tags"
            )

        # Check if scaling tag is present when maxLevel > 1
        max_level = eff.get("maxLevel")
        if isinstance(max_level, str) and max_level not in ("I", "1", 1):
            if "scaling" not in tags:
                fail(
                    f"Effect '{eff.get('effect')}' with maxLevel '{max_level}' should have 'scaling' tag"
                )
        elif isinstance(max_level, int) and max_level > 1:
            if "scaling" not in tags:
                fail(
                    f"Effect '{eff.get('effect')}' with maxLevel {max_level} should have 'scaling' tag"
                )

    print(f"{PREFIX}: ✅ Tags validation check passed.")
    print(f"{PREFIX}: ✨ All 5/5 checks passed.")


if __name__ == "__main__":
    main()
