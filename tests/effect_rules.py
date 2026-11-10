"""Writing rules for effect records (description, source and text formatting).

Used by tests/test_data.py. It can also lint a single JSON file while adding effects:

    python tests/effect_rules.py data/effects.json
    python tests/effect_rules.py path/to/new-records.json

The file may be {"effects": [...]} or a plain list of records. Prints one line per
problem and exits with 1 if there are any.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

ROMAN_NUMERALS = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
TEXT_FIELDS = ("mod", "effect", "description", "source")
MAX_DESCRIPTION_LENGTH = 300

_TAG_RE = re.compile(r"<[^>]+>")
_BOLD_RE = re.compile(r"<b>(.*?)</b>")
_ITALIC_RE = re.compile(r"<i>(.*?)</i>")
_TIME_UNIT_RE = re.compile(r"\bseconds?\b|\bsecond\(s\)")
# "level" that refers to the effect level (allowed only when the effect can have level II+).
_LEVEL_WORD_RE = re.compile(
    r"(?<!hunger )(?<!food )(?<!water )(?<!light )(?<!experience )(?<!xp )(?<!sea )"
    r"(?<!enchantment )(?<!power )(?<!spell )(?<!mana )\blevels?\b(?!\s+(of|in|at|on|from|to|with)\b)"
)
_SPECIAL_SOURCES = ("<i>To be added.</i>", "<i>Unavailable.</i>")


def plain(text: str) -> str:
    return _TAG_RE.sub("", text)


def _balanced(text: str, tag: str) -> bool:
    depth = 0
    for match in re.finditer(rf"</?{tag}>", text):
        depth += -1 if match.group().startswith("</") else 1
        if depth not in (0, 1):
            return False
    return depth == 0


def text_problems(field: str, value: str) -> Iterator[str]:
    if "  " in value:
        yield f"{field}: double space"
    if value != value.strip():
        yield f"{field}: leading or trailing whitespace"
    text = plain(value)
    if re.search(r",(?=\S)", text):
        yield f"{field}: comma must be followed by a space"
    if " ," in text:
        yield f"{field}: space before a comma"


def description_problems(description: str, max_level: str) -> Iterator[str]:
    if re.search(r"<(?!/?b>)[^>]*>", description):
        yield "description: only <b> tags are allowed"
    if not _balanced(description, "b"):
        yield "description: unbalanced or nested <b> tags"
    if len(plain(description)) > MAX_DESCRIPTION_LENGTH:
        yield f"description: longer than {MAX_DESCRIPTION_LENGTH} characters"
    outside = _BOLD_RE.sub("", description)
    for term in ("^level", "× level"):
        if term in outside:
            yield f"description: formula '{term}' must be inside <b>"
    if _TIME_UNIT_RE.search(outside):
        yield "description: time units (second/seconds) must be inside <b>"
    if "+" in outside:
        yield "description: every '+' must be inside <b>"
    if re.search(r"(?<![\d.])1 × level", description):
        yield "description: write <b>level</b> instead of <b>1 × level</b>"
    if "->" in description or "-&gt;" in description:
        yield "description: use '→' instead of '->'"
    if " & " in plain(description):
        yield "description: use 'and' instead of '&'"
    for span in _BOLD_RE.findall(description):
        for term in ("^level", "× level"):
            if term not in span or (term == "× level" and "^level" in span):
                continue
            tail = span.split(term)[-1]
            if tail not in ("", ")") and not _TIME_UNIT_RE.fullmatch(tail.strip()):
                yield f"description: '{term}' must end its bold span or be followed by a time unit (<b>{span}</b>)"
    if max_level == "I":
        if "higher level" in description:
            yield "description: maxLevel I effects can't mention 'higher level'"
        elif _LEVEL_WORD_RE.search(plain(description)):
            yield "description: maxLevel I effects can't refer to the effect level"


def source_problems(source: str, mod_names: Iterable[str] = (), own_mod: str = "") -> Iterator[str]:
    if re.search(r"<(?!/?i>)[^>]*>", source):
        yield "source: only <i> tags are allowed"
    if not _balanced(source, "i"):
        yield "source: unbalanced or nested <i> tags"
    if "/Splash" in source or "/Lingering" in source or "Splash/" in source or "Lingering/" in source:
        yield "source: don't list Splash/Lingering variants (use Potion/Arrow/Charm of X)"
    if source in _SPECIAL_SOURCES:
        return
    known = set(mod_names)
    for italic in _ITALIC_RE.findall(source):
        if italic == own_mod:
            yield "source: don't italicize the effect's own mod (write 'from the mod' or just the item name)"
        elif known and italic not in known:
            yield f"source: <i>{italic}</i> is not a known mod name (only mod names are italic)"
    outside = _ITALIC_RE.sub("", source)
    if "&" in outside:
        yield "source: use 'and' instead of '&' (unless it's part of a name)"
    if "from the <i>" in source:
        yield "source: write 'from <i>Mod</i> mod' (without 'the') for other mods"
    for match in re.finditer(r"from <i>([^<]+)</i>(?! mod)", source):
        yield f"source: write 'from <i>{match.group(1)}</i> mod'"


def record_problems(record: dict, mod_names: Iterable[str] = ()) -> list[str]:
    """Problems of one record (base fields and every change)."""
    problems: list[str] = []
    for field in ("mod", "effect", "maxLevel", "type", "description", "source"):
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{field}: missing or empty")
    if problems:
        return problems
    if record["maxLevel"] not in ROMAN_NUMERALS:
        problems.append(f"maxLevel: must be a Roman numeral I-X, got {record['maxLevel']!r}")
    if record["type"] not in ("positive", "negative"):
        problems.append(f"type: must be 'positive' or 'negative', got {record['type']!r}")

    variants = [("", record)]
    merged = dict(record)
    for version, change in (record.get("changes") or {}).items():
        merged = {**merged, **change}
        variants.append((f"[{version}] ", merged))
    for prefix, variant in variants:
        for field in TEXT_FIELDS:
            problems += [prefix + p for p in text_problems(field, variant[field])]
        problems += [prefix + p for p in description_problems(variant["description"], variant["maxLevel"])]
        problems += [prefix + p for p in source_problems(variant["source"], mod_names, variant["mod"])]
    return list(dict.fromkeys(problems))


def lint_file(path: Path, mod_names: Iterable[str] = ()) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data.get("effects", data) if isinstance(data, dict) else data
    output = []
    for record in records:
        label = f"{record.get('mod', '?')} / {record.get('effect', '?')}"
        output += [f"{label}: {problem}" for problem in record_problems(record, mod_names)]
    return output


if __name__ == "__main__":
    mods_file = Path(__file__).resolve().parents[1] / "data" / "mods.json"
    names: list[str] = []
    if mods_file.exists():
        names = [m["name"] for m in json.loads(mods_file.read_text(encoding="utf-8"))["mods"]]
        names += json.loads(mods_file.read_text(encoding="utf-8")).get("referencedMods", [])
    found = []
    for arg in sys.argv[1:]:
        found += lint_file(Path(arg), names)
    print("\n".join(found) if found else "No problems found.")
    sys.exit(1 if found else 0)
