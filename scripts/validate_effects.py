#!/usr/bin/env python3
"""Validate ordering of data/effects.json.

Rules:
1. All required fields must be non-empty (no null, empty strings, or empty lists).
2. Text formatting: no double spaces, leading/trailing whitespace, proper comma spacing.
3. No duplicate effect names within each mod (cross-mod duplicates allowed if descriptions differ).
4. Ordering: Minecraft first (alphabetical by effect), then mods (alphabetical by mod, then by effect).
5. Max level must be a Roman numeral from I to X.
6. Description: Formula ('^level', '× level'), time units, and ALL '+' symbols must be in <b> tags. Effects with maxLevel 'I' cannot contain 'higher level' or 'level'.
7. Tags: Exactly one of 'positive' or 'negative'. 'scaling' tag required for maxLevel > I, forbidden for maxLevel I.
8. Source: Potion/Arrow/Charm grouping (no Splash/Lingering variants).
9. Source: HTML tags (<i> only for mod names).
10. Source: Special terms (spell patterns, no ampersands except in names).

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


def validate_description_html_tags(effects):
    """Ensure formulas and time units are properly wrapped in <b> tags.

    Rules:
    - '^level' and '× level' must be inside <b> tags and either be at the end
      or followed by "second", "seconds", or "second(s)"
    - Every instance of "second", "seconds", or "second(s)" must be wrapped in <b> tags
    - Every instance of '+' must be wrapped in <b> tags (all plus symbols)
    - Effects with maxLevel 'I' cannot contain 'higher level' in description
    - Effects with maxLevel 'I' cannot contain 'level' in description (always level 1)
    - ONLY <b> tags allowed in descriptions (exception: "<i>To be added.</i>" and "<i>Unavailable.</i>")
    - Note: Duplicate effect names across mods are allowed if descriptions differ
    """
    # Terms that must be in bold
    time_terms = ["second", "seconds", "second(s)"]
    formula_terms = ["^level", "× level"]

    for eff in effects:
        desc = eff.get("description") or ""
        name = eff.get("effect") or "Unknown"
        max_level = eff.get("maxLevel") or ""

        # Check for non-<b> HTML tags in description, excluding allowed special cases
        desc_without_exceptions = desc
        if re.search(r"<(?!b>|/b>)[^>]+>", desc_without_exceptions):
            fail(
                f"Effect '{name}': Description should ONLY contain <b> tags (found other HTML tags). Exception: '<i>To be added.</i>' and '<i>Unavailable.</i>' are allowed."
            )

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

        # Check for '+' outside bold (ALL '+' symbols must be in bold)
        if "+" in outside:
            fail(f"Plus symbol '+' must be in <b> tags in effect '{name}'")

        # Check for 'higher level' in non-scaling effects
        if max_level == "I" and "higher level" in desc:
            fail(
                f"Effect '{name}' with maxLevel 'I' cannot contain 'higher level' in description (non-scaling effect)"
            )

        # Check for effect 'level' references in non-scaling effects
        # Look for patterns that suggest effect level: "× level", "^level", "level", but exclude "hunger level", "water level", etc.
        if max_level == "I":
            # Check for mathematical level references
            level_patterns = [
                r"\blevel\b(?!\s+(of|in|at|on|from|to|with))",  # "level" not followed by prepositions
                r"by\s+<b>level</b>",  # "by level"
                r"<b>level</b>",  # "level" in bold tags
            ]
            for pattern in level_patterns:
                if (
                    re.search(pattern, desc)
                    and "hunger level" not in desc
                    and "water level" not in desc
                ):
                    fail(
                        f"Effect '{name}' with maxLevel 'I' cannot contain effect 'level' references in description (always level 1)"
                    )

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
                    "× level)",
                    "× level second",
                    "× level seconds",
                    "× level second(s)",
                ]
                if not any(span.endswith(end) for end in valid_endings):
                    fail(
                        f"'× level' incorrectly positioned in bold span in effect '{name}' -> <b>{span}</b>"
                    )


def validate_source_potion_grouping(effects):
    """Validate Potion/Arrow/Charm grouping rules.

    Rules:
    - FORBIDDEN: "Potion/Arrow/Splash/Lingering" or "Potion/Splash/Lingering" (should be simplified)
    - Check for common mistakes in potion variant naming
    """
    for eff in effects:
        source = eff.get("source") or ""
        name = eff.get("effect") or "Unknown"

        # Check for forbidden Splash/Lingering in grouping patterns
        if "Potion/Arrow/Splash/Lingering" in source:
            fail(
                f"Effect '{name}': Use 'Potion/Arrow/Charm' or 'Potion/Arrow' instead of 'Potion/Arrow/Splash/Lingering'"
            )

        if "Potion/Splash/Lingering" in source:
            fail(
                f"Effect '{name}': Use 'Potion' or 'Potion/Arrow/Charm' instead of 'Potion/Splash/Lingering'"
            )

        # Check for other verbose potion naming
        if "/Splash/" in source or "/Lingering/" in source:
            fail(
                f"Effect '{name}': Don't name every potion variant - use default (Potion) instead of Splash/Lingering variants"
            )


def validate_source_html_tags(effects):
    """Validate HTML tag usage in source field.

    Rules:
    - <i> tags should ONLY be used for mod names
    - No <i> tags for mob names, item names, etc.
    - Check for common mistakes like italicizing mob/item names
    - ONLY <i> tags allowed in sources (no <b>, <u>, etc.)
    """
    for eff in effects:
        source = eff.get("source") or ""
        name = eff.get("effect") or "Unknown"

        # Check for non-<i> HTML tags in source
        if re.search(r"<(?!i>|/i>)[^>]+>", source):
            fail(
                f"Effect '{name}': Source should ONLY contain <i> tags (found other HTML tags like <b>, <u>, etc.)"
            )

        # Find all italic content
        italic_matches = re.findall(r"<i>(.*?)</i>", source)

        # Common non-mod terms that shouldn't be italicized
        forbidden_italic_terms = [
            "Tarantula Hawk",
            "Rocky Roller",
            "Enderiophage",
            "Frilled Shark",
            "Jerboa",
            "Nucleeper",
            "Brainiac",
            "Tremorzilla",
            "Gammaroach",
            "Warden",
            "Elder Guardian",
            "Wither",
            "Wither Skeleton",
            "Cave Spider",
            "Stray",
            "Husk",
            "Illusioner",
            "Shulker",
            # Add other common mob/item names that are often mistakenly italicized
        ]

        for italic_content in italic_matches:
            # Skip special cases
            if italic_content in ["To be added.", "Unavailable."]:
                continue

            # Check if it's a forbidden term
            if italic_content in forbidden_italic_terms:
                fail(
                    f"Effect '{name}': Mob/item name '<i>{italic_content}</i>' should not be italicized (only mod names use <i> tags)"
                )

            # Check for patterns that suggest it's not a mod name
            # Mod names typically contain "mod" or are proper capitalization without common words
            if any(
                word in italic_content.lower()
                for word in ["attacks", "landing", "projectile", "arrow"]
            ):
                fail(
                    f"Effect '{name}': '<i>{italic_content}</i>' appears to be a description, not a mod name (only mod names should use <i> tags)"
                )


def validate_source_special_terms(effects):
    """Validate special source terms and grouping rules.

    Rules:
    - Use "Delights" for multiple items from mods containing "delight"
    - Use "Unique Weapons" for Simple Swords weapons
    - Use "Affix Items" for Apotheosis affixes
    - Use spell patterns for Iron Spells'n'Spellbooks
    - Use "tools/weapons/armor sets from <i>ModName</i>" pattern
    """
    for eff in effects:
        source = eff.get("source") or ""
        name = eff.get("effect") or "Unknown"

        # Check for improper ampersand usage (should use "and" instead)
        if " & " in source or "&amp;" in source:
            # Allow if it's part of a mod name
            if not re.search(r"<i>[^<]*&[^<]*</i>", source):
                fail(
                    f"Effect '{name}': Use 'and' instead of '&' in source (unless it's part of a mod/item name)"
                )

        # Check for spell formatting from Iron Spells'n'Spellbooks
        if "spell" in source.lower() and "Iron Spells" in source:
            # Should be: "X spell from <i>Iron Spells'n'Spellbooks</i> mod" or "spells from <i>Iron Spells'n'Spellbooks</i> mod"
            # Allow for optional whitespace before </i>
            if not re.search(
                r"(spells?)\s+from\s+<i>Iron Spells'n'Spellbooks\s*</i>\s+mod", source
            ):
                fail(
                    f"Effect '{name}': Spell references should follow pattern 'X spell from <i>Iron Spells'n'Spellbooks</i> mod' or 'spells from <i>Iron Spells'n'Spellbooks</i> mod'"
                )


def validate_text_formatting(effects):
    """Validate general text formatting across all text fields.

    Rules:
    - No double spaces
    - No leading/trailing whitespace
    - Space after comma (not before)
    """
    fields_to_check = ["mod", "effect", "description", "source"]

    for eff in effects:
        name = eff.get("effect") or "Unknown"

        for field in fields_to_check:
            value = eff.get(field) or ""

            # Check for double spaces
            if "  " in value:
                fail(
                    f"Effect '{name}': Field '{field}' contains double spaces (use single spaces)"
                )

            # Check for leading/trailing whitespace
            if value != value.strip():
                fail(
                    f"Effect '{name}': Field '{field}' has leading or trailing whitespace"
                )

            # Check for comma without space after (except in HTML tags)
            # Remove HTML tags first to avoid false positives
            value_without_html = re.sub(r"<[^>]+>", "", value)
            if re.search(r",[^ ]", value_without_html):
                fail(
                    f"Effect '{name}': Field '{field}' - comma should be followed by a space"
                )

            # Check for space before comma
            if " ," in value:
                fail(f"Effect '{name}': Field '{field}' - remove space before comma")


def validate_no_empty_fields(effects):
    """Ensure all required fields are non-empty.

    Rules:
    - All fields must be present and non-empty
    """
    required_fields = [
        "mod",
        "id",
        "effect",
        "maxLevel",
        "type",
        "tags",
        "description",
        "source",
    ]

    for eff in effects:
        name = eff.get("effect") or "Unknown"

        for field in required_fields:
            if field not in eff:
                fail(f"Effect '{name}': Missing required field '{field}'")

            value = eff.get(field)

            # Check for empty strings
            if isinstance(value, str) and not value.strip():
                fail(f"Effect '{name}': Field '{field}' is empty")

            # Check for empty lists
            if isinstance(value, list) and len(value) == 0:
                fail(f"Effect '{name}': Field '{field}' is an empty list")

            # Check for None
            if value is None:
                fail(f"Effect '{name}': Field '{field}' is null")


def validate_max_level_format(effects):
    """Validate maxLevel field format.

    Rules:
    - Must be a Roman numeral from I to X
    """
    valid_roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

    for eff in effects:
        name = eff.get("effect") or "Unknown"
        max_level = eff.get("maxLevel")

        if max_level not in valid_roman_numerals:
            fail(
                f"Effect '{name}': maxLevel must be a Roman numeral from I to X, got '{max_level}'"
            )


def main():
    print(f"{PREFIX}: 🚀 Starting validation...")
    effects = load_effects()

    # General checks (most important first)

    # 1. No empty fields check
    print(f"{PREFIX}: 1/10 No empty fields check started...")
    validate_no_empty_fields(effects)
    print(f"{PREFIX}: ✅ No empty fields check passed.")

    # 2. Text formatting check (applies to multiple fields)
    print(f"{PREFIX}: 2/10 General text formatting check started...")
    validate_text_formatting(effects)
    print(f"{PREFIX}: ✅ General text formatting check passed.")

    # 3. Duplicate name check (within each mod)
    print(f"{PREFIX}: 3/10 Duplicate effect name check started...")
    mod_to_effect_names = {}
    for e in effects:
        mod = e.get("mod")
        name = e.get("effect")
        if mod not in mod_to_effect_names:
            mod_to_effect_names[mod] = set()
        if name in mod_to_effect_names[mod]:
            fail(f"Duplicate effect name detected within mod '{mod}': '{name}'")
        mod_to_effect_names[mod].add(name)
    print(f"{PREFIX}: ✅ Duplicate effect name check passed.")

    # 4. Ordering check
    print(f"{PREFIX}: 4/10 Effect ordering check started...")

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
    print(f"{PREFIX}: ✅ Effect ordering check passed.")

    # Column-specific checks (in column order: mod, effect, maxLevel, description, tags, source)

    # 5. Max level format check
    print(f"{PREFIX}: 5/10 Max level format check started...")
    validate_max_level_format(effects)
    print(f"{PREFIX}: ✅ Max level format check passed.")

    # 6. Description HTML tag usage check
    print(f"{PREFIX}: 6/10 Description HTML tag usage check started...")
    validate_description_html_tags(effects)
    print(f"{PREFIX}: ✅ Description HTML tag usage check passed.")

    # 7. Tags validation check
    print(f"{PREFIX}: 7/10 Tags validation check started...")
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

        # Check scaling tag requirements
        max_level = eff.get("maxLevel")
        if max_level == "I":
            # Effects with maxLevel "I" cannot have scaling tag
            if "scaling" in tags:
                fail(
                    f"Effect '{eff.get('effect')}' with maxLevel 'I' cannot have 'scaling' tag (non-scaling effect)"
                )
        else:
            # Effects with maxLevel > "I" must have scaling tag
            if "scaling" not in tags:
                fail(
                    f"Effect '{eff.get('effect')}' with maxLevel '{max_level}' must have 'scaling' tag"
                )
    print(f"{PREFIX}: ✅ Tags validation check passed.")

    # Source validation checks

    # 8. Source potion grouping check
    print(f"{PREFIX}: 8/10 Source potion grouping check started...")
    validate_source_potion_grouping(effects)
    print(f"{PREFIX}: ✅ Source potion grouping check passed.")

    # 9. Source HTML tag usage check
    print(f"{PREFIX}: 9/10 Source HTML tag usage check started...")
    validate_source_html_tags(effects)
    print(
        f"{PREFIX}: ✅ Source HTML tag usage check passed."
    )  # 10. Source special terms check
    print(f"{PREFIX}: 10/10 Source special terms check started...")
    validate_source_special_terms(effects)
    print(f"{PREFIX}: ✅ Source special terms check passed.")

    print(f"{PREFIX}: ✨ All 10/10 checks passed.")


if __name__ == "__main__":
    main()
