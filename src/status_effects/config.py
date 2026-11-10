"""Paths and site-wide settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(os.environ.get("STATUS_EFFECTS_ROOT", Path(__file__).resolve().parents[2]))
DATA_DIR = ROOT_DIR / "data"
PUBLIC_DIR = ROOT_DIR / "public"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

EFFECTS_FILE = DATA_DIR / "effects.json"
MODS_FILE = DATA_DIR / "mods.json"

SITE_URL = os.environ.get("SITE_URL", "https://minecraftstatuseffects.com").rstrip("/")
SITE_NAME = "Minecraft Status Effects"
AUTHOR = "Matěj Kadlec"
AUTHOR_URL = "https://matejkadlec.cz"
REPOSITORY_URL = "https://github.com/matejkadlec/status-effects"
CONTACT_URL = "https://discord.com/users/jimmorioriarty"


@dataclass(frozen=True)
class GameVersion:
    """A version bucket shown in the version dropdown."""

    id: str
    releases: str
    modded: str

    @property
    def major(self) -> str:
        """`1.21.x` -> `1.21` (used to match exact releases like `1.21.11`)."""
        return self.id.removesuffix(".x")

    def contains(self, release: str) -> bool:
        return release == self.major or release.startswith(self.major + ".")


VERSIONS: tuple[GameVersion, ...] = (
    GameVersion("1.20.x", "1.20 – 1.20.6", "1.20.1"),
    GameVersion("1.21.x", "1.21 – 1.21.11", "1.21.1"),
    GameVersion("26.1.x", "26.1 – 26.1.2", "26.1.2"),
    GameVersion("26.2.x", "26.2", "26.2"),
    GameVersion("26.3.x", "26.3", "26.3"),
)
VERSION_IDS: tuple[str, ...] = tuple(v.id for v in VERSIONS)
DEFAULT_VERSION = "1.20.x"

EXPORT_FORMATS = ("csv", "xlsx", "json")
THEMES = ("light", "dark")
