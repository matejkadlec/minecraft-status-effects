"""Loading the effects database and resolving it for a Minecraft version."""

from __future__ import annotations

import hashlib
import json
import re
import threading
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from . import config

ROMAN_NUMERALS = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
EffectType = Literal["positive", "negative"]
_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    """Plain text of a description/source value (they only contain simple inline tags)."""
    return _TAG_RE.sub("", text)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, frozen=True)


class EffectChange(_Strict):
    """Fields that differ from a version bucket onwards."""

    effect: str | None = None
    max_level: str | None = Field(default=None, alias="maxLevel")
    type: EffectType | None = None
    unreliable: bool | None = None
    description: str | None = None
    source: str | None = None

    @field_validator("max_level")
    @classmethod
    def _roman(cls, value: str | None) -> str | None:
        if value is not None and value not in ROMAN_NUMERALS:
            raise ValueError(f"maxLevel must be a Roman numeral I-X, got {value!r}")
        return value


class EffectRecord(_Strict):
    """One effect as stored in data/effects.json."""

    id: str
    mod: str
    effect: str
    # The game's id of the effect (`namespace:path`), useful when updating the data from a mod's files.
    registry_id: str | None = Field(default=None, alias="registryId")
    versions: tuple[str, ...]
    since: str | None = None
    max_level: str = Field(alias="maxLevel")
    type: EffectType
    unreliable: bool = False
    description: str
    source: str
    changes: dict[str, EffectChange] = Field(default_factory=dict)

    @field_validator("max_level")
    @classmethod
    def _roman(cls, value: str) -> str:
        if value not in ROMAN_NUMERALS:
            raise ValueError(f"maxLevel must be a Roman numeral I-X, got {value!r}")
        return value

    @model_validator(mode="after")
    def _check_versions(self) -> EffectRecord:
        if not self.versions:
            raise ValueError(f"{self.id}: versions must not be empty")
        unknown = [v for v in self.versions if v not in config.VERSION_IDS]
        if unknown:
            raise ValueError(f"{self.id}: unknown versions {unknown}")
        order = [config.VERSION_IDS.index(v) for v in self.versions]
        if order != sorted(set(order)):
            raise ValueError(f"{self.id}: versions must be unique and in order {config.VERSION_IDS}")
        for version in self.changes:
            if version not in self.versions:
                raise ValueError(f"{self.id}: change for {version} which is not in versions")
            if version == self.versions[0]:
                raise ValueError(f"{self.id}: a change for the first version belongs in the base fields")
        if self.since is not None:
            first = next(v for v in config.VERSIONS if v.id == self.versions[0])
            if not first.contains(self.since):
                raise ValueError(f"{self.id}: since {self.since} is not a {first.id} release")
        return self

    def resolve(self, version: str) -> Effect | None:
        """The effect as it is in `version`, or None if it doesn't exist there."""
        if version not in self.versions:
            return None
        fields = {
            "effect": self.effect,
            "max_level": self.max_level,
            "type": self.type,
            "unreliable": self.unreliable,
            "description": self.description,
            "source": self.source,
        }
        upto = config.VERSION_IDS.index(version)
        for change_version, change in sorted(self.changes.items(), key=lambda item: config.VERSION_IDS.index(item[0])):
            if config.VERSION_IDS.index(change_version) > upto:
                break
            fields.update(change.model_dump(exclude_none=True))
        since = self.since if self.since and version == self.versions[0] else None
        return Effect(id=self.id, mod=self.mod, version=version, since=since, **fields)


class ModInfo(_Strict):
    name: str
    url: str | None = None
    group: str | None = None


@dataclass(frozen=True)
class Effect:
    """An effect resolved for one version bucket."""

    id: str
    mod: str
    version: str
    effect: str
    max_level: str
    type: EffectType
    unreliable: bool
    description: str
    source: str
    since: str | None = None

    @property
    def level(self) -> int:
        return ROMAN_NUMERALS.index(self.max_level) + 1

    @property
    def scaling(self) -> bool:
        return self.level > 1

    @property
    def tags(self) -> list[str]:
        return [self.type, "scaling"] if self.scaling else [self.type]

    @property
    def is_vanilla(self) -> bool:
        return self.mod == "Minecraft"

    def sort_key(self) -> tuple:
        return (not self.is_vanilla, self.mod.lower(), self.effect.lower())

    def public(self) -> dict:
        """JSON shape used by the frontend and the JSON export."""
        data = {
            "id": self.id,
            "mod": self.mod,
            "effect": self.effect,
            "maxLevel": self.max_level,
            "type": self.type,
            "tags": self.tags,
            "description": self.description,
            "source": self.source,
        }
        if self.unreliable:
            data["unreliable"] = True
        if self.since:
            data["since"] = self.since
        return data


class Dataset:
    """The whole database: all effect records and the mod registry."""

    def __init__(self, records: list[EffectRecord], mods: list[ModInfo], fingerprint: str):
        self.records = records
        self.mods = {mod.name: mod for mod in mods}
        self.fingerprint = fingerprint
        self._by_version: dict[str, list[Effect]] = {}

    @classmethod
    def load(cls, effects_file: Path = config.EFFECTS_FILE, mods_file: Path = config.MODS_FILE) -> Dataset:
        effects_raw = effects_file.read_bytes()
        mods_raw = mods_file.read_bytes()
        effects_json = json.loads(effects_raw)
        mods_json = json.loads(mods_raw)
        records = [EffectRecord.model_validate(item) for item in effects_json["effects"]]
        mods = [ModInfo.model_validate(item) for item in mods_json["mods"]]
        fingerprint = hashlib.sha256(effects_raw + b"\0" + mods_raw).hexdigest()[:16]
        dataset = cls(records, mods, fingerprint)
        dataset.check_integrity()
        return dataset

    def check_integrity(self) -> None:
        ids = [record.id for record in self.records]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate effect ids: {duplicates}")
        unknown = sorted({record.mod for record in self.records} - set(self.mods))
        if unknown:
            raise ValueError(f"mods missing in mods.json: {unknown}")

    def effects(self, version: str) -> list[Effect]:
        """All effects of a version bucket in the default order (Minecraft first, then by mod and effect)."""
        if version not in self._by_version:
            resolved = [e for e in (record.resolve(version) for record in self.records) if e]
            self._by_version[version] = sorted(resolved, key=Effect.sort_key)
        return self._by_version[version]

    def effects_by_id(self, version: str) -> dict[str, Effect]:
        return {effect.id: effect for effect in self.effects(version)}

    @cached_property
    def counts(self) -> dict[str, int]:
        return {version: len(self.effects(version)) for version in config.VERSION_IDS}

    def mod_names(self, version: str) -> list[str]:
        seen: dict[str, None] = {}
        for effect in self.effects(version):
            seen.setdefault(effect.mod, None)
        return list(seen)

    def mods_payload(self, version: str) -> list[dict]:
        """Mods present in a version with their nav group and link, in default order."""
        payload = []
        for name in self.mod_names(version):
            info = self.mods[name]
            item = {"name": name}
            if info.group:
                item["group"] = info.group
            if info.url:
                item["url"] = info.url
            payload.append(item)
        return payload


_lock = threading.Lock()
_cache: tuple[tuple[float, float], Dataset] | None = None


def get_dataset() -> Dataset:
    """The current dataset; reloaded automatically when a data file changes."""
    global _cache
    stamp = (config.EFFECTS_FILE.stat().st_mtime, config.MODS_FILE.stat().st_mtime)
    with _lock:
        if _cache is None or _cache[0] != stamp:
            _cache = (stamp, Dataset.load())
        return _cache[1]
