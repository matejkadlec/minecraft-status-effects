"""The effects database: schema, ordering and the writing rules from AGENTS.md."""

import json
import re
from collections import Counter

import pytest

from status_effects import config
from status_effects.data import ROMAN_NUMERALS, Dataset
from tests.effect_rules import record_problems

EFFECTS = json.loads(config.EFFECTS_FILE.read_text(encoding="utf-8"))["effects"]
MODS = json.loads(config.MODS_FILE.read_text(encoding="utf-8"))
KNOWN_MOD_NAMES = {mod["name"] for mod in MODS["mods"]} | set(MODS.get("referencedMods", []))
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REGISTRY_ID_RE = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")


def test_dataset_loads(dataset: Dataset):
    assert dataset.records
    assert all(dataset.counts[version] > 0 for version in config.VERSION_IDS)


@pytest.mark.parametrize("record", EFFECTS, ids=lambda r: r.get("id", "?"))
def test_writing_rules(record):
    assert record_problems(record, KNOWN_MOD_NAMES) == []


def test_ids_are_unique_slugs():
    ids = [record["id"] for record in EFFECTS]
    assert [i for i, n in Counter(ids).items() if n > 1] == []
    assert [i for i in ids if not ID_RE.match(i)] == []


def test_registry_ids_look_valid():
    bad = [r["id"] for r in EFFECTS if "registryId" in r and not REGISTRY_ID_RE.match(r["registryId"])]
    assert bad == []


def test_ordering():
    """Minecraft first, then mods alphabetically, effects alphabetically within a mod."""
    keys = [(r["mod"] != "Minecraft", r["mod"].lower(), r["effect"].lower()) for r in EFFECTS]
    first_wrong = next((i for i in range(1, len(keys)) if keys[i - 1] > keys[i]), None)
    assert first_wrong is None, f"out of order at {EFFECTS[first_wrong]['id']}"


def test_effect_names_unique_within_mod_and_version(dataset: Dataset):
    for version in config.VERSION_IDS:
        names = Counter((e.mod, e.effect.lower()) for e in dataset.effects(version))
        assert [key for key, count in names.items() if count > 1] == [], version


def test_changes_only_contain_differences():
    """A change must alter something compared to the previous version it cascades from."""
    for record in EFFECTS:
        effective = {**record, "unreliable": record.get("unreliable", False)}
        for version in config.VERSION_IDS:
            change = record.get("changes", {}).get(version)
            if change is None:
                continue
            assert change, f"{record['id']}: empty change for {version}"
            same = [k for k, v in change.items() if effective.get(k) == v]
            assert same == [], f"{record['id']}: change for {version} repeats the current value of {same}"
            effective.update(change)


def test_max_levels_are_roman(dataset: Dataset):
    for version in config.VERSION_IDS:
        assert {e.max_level for e in dataset.effects(version)} <= set(ROMAN_NUMERALS)


def test_every_mod_is_registered_and_used():
    registered = [mod["name"] for mod in MODS["mods"]]
    used = {record["mod"] for record in EFFECTS}
    assert sorted(used - set(registered)) == []
    assert sorted(set(registered) - used) == []
    assert len(registered) == len(set(registered))


def test_mods_are_sorted_and_linked():
    names = [mod["name"] for mod in MODS["mods"]]
    assert names[0] == "Minecraft"
    assert names[1:] == sorted(names[1:], key=str.lower)
    for mod in MODS["mods"]:
        assert set(mod) <= {"name", "url", "group"}, mod
        if "url" in mod:
            assert mod["url"].startswith("https://"), mod


def test_vanilla_effects_cover_every_version(dataset: Dataset):
    vanilla = {version: [e for e in dataset.effects(version) if e.is_vanilla] for version in config.VERSION_IDS}
    assert len(vanilla["1.20.x"]) >= 39
    assert all(len(effects) >= 40 for version, effects in vanilla.items() if version != "1.20.x")


def test_drafts_file():
    drafts = json.loads((config.DATA_DIR / "draft-effects.json").read_text(encoding="utf-8"))
    assert isinstance(drafts["drafts"], list)
    for draft in drafts["drafts"]:
        assert {"mod", "effect", "versions"} <= set(draft), draft
        assert set(draft["versions"]) <= set(config.VERSION_IDS), draft
