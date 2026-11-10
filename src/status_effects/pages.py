"""Data shown on the pages: the effects payload for the frontend, the mod navigation and SEO texts."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime

from . import config
from .assets import format_text
from .data import Dataset, Effect

OTHER_GROUP = "Other"
# Mods with fewer effects than this (and no named group) go to the "Other" group.
OTHER_GROUP_MAX_EFFECTS = 2


def effect_payload(effect: Effect) -> dict:
    item = {
        "id": effect.id,
        "mod": effect.mod,
        "effect": effect.effect,
        "maxLevel": effect.max_level,
        "level": effect.level,
        "type": effect.type,
        "scaling": effect.scaling,
        "description": str(format_text(effect.description)),
        "source": str(format_text(effect.source)),
    }
    if effect.unreliable:
        item["unreliable"] = True
    if effect.since:
        item["since"] = effect.since
    return item


def build_nav(dataset: Dataset, version: str) -> list[dict]:
    """Mod navigation: ungrouped mods first (Minecraft on top), then named groups, "Other" last."""
    effects = dataset.effects(version)
    counts = Counter(effect.mod for effect in effects)
    first_id: dict[str, str] = {}
    for effect in effects:
        first_id.setdefault(effect.mod, effect.id)

    ungrouped: list[dict] = []
    groups: dict[str, list[dict]] = {}
    for mod in dataset.mod_names(version):
        item = {"mod": mod, "target": first_id[mod], "count": counts[mod]}
        group = dataset.mods[mod].group
        if group is None and mod != "Minecraft" and counts[mod] <= OTHER_GROUP_MAX_EFFECTS:
            group = OTHER_GROUP
        if group:
            groups.setdefault(group, []).append(item)
        else:
            ungrouped.append(item)

    names = sorted(groups, key=lambda name: (name == OTHER_GROUP, name.lower()))
    return ungrouped + [{"group": name, "mods": groups[name]} for name in names]


def payload(dataset: Dataset, version: str) -> dict:
    """Everything the frontend needs for one version."""
    return {
        "version": version,
        "fingerprint": dataset.fingerprint,
        "effects": [effect_payload(effect) for effect in dataset.effects(version)],
        "nav": build_nav(dataset, version),
        "mods": {name: {"url": info.url} for name in dataset.mod_names(version) if (info := dataset.mods[name]).url},
    }


def rounded_count(count: int) -> str:
    """350 -> '350+', 1234 -> '1,200+' (for marketing texts that shouldn't go stale on every edit)."""
    step = 50 if count < 1000 else 100
    return f"{count - count % step:,}+" if count >= step else str(count)


def page_texts(dataset: Dataset, version: str) -> dict:
    total = len({record.id for record in dataset.records})
    mods = len({record.mod for record in dataset.records} - {"Minecraft"})
    count = dataset.counts[version]
    game_version = next(v for v in config.VERSIONS if v.id == version)
    description = (
        f"Searchable database of {rounded_count(total)} vanilla and modded Minecraft status effects "
        f"from {rounded_count(mods)} mods, for every version from 1.20 to "
        f"{config.VERSIONS[-1].major}. Exact formulas, max levels and where to get each effect."
    )
    title = f"{config.SITE_NAME}: Vanilla and Modded Effects Database"
    if version != config.DEFAULT_VERSION:
        title = f"Minecraft {game_version.id} Status Effects: Vanilla and Modded Effects Database"
        description = (
            f"All {count} vanilla and modded Minecraft {game_version.id} status effects "
            f"({game_version.releases}): exact formulas, max levels and where to get each effect."
        )
    return {
        "title": title,
        "description": description,
        "total": total,
        "mods": mods,
        "count": count,
        "game_version": game_version,
    }


def json_ld(dataset: Dataset, version: str, texts: dict, canonical: str) -> list[dict]:
    site = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": config.SITE_NAME,
        "url": f"{config.SITE_URL}/",
        "inLanguage": "en",
        "creator": {"@type": "Person", "name": config.AUTHOR, "url": config.AUTHOR_URL},
    }
    dataset_ld = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"Minecraft {version} status effects"
        if version != config.DEFAULT_VERSION
        else "Minecraft status effects (vanilla and modded)",
        "description": texts["description"],
        "url": canonical,
        "keywords": [
            "Minecraft",
            "status effects",
            "potion effects",
            "mob effects",
            "modded Minecraft",
            f"Minecraft {version}",
        ],
        "license": f"{config.SITE_URL}/license/",
        "isAccessibleForFree": True,
        "creator": {"@type": "Person", "name": config.AUTHOR, "url": config.AUTHOR_URL},
        "dateModified": datetime.fromtimestamp(config.EFFECTS_FILE.stat().st_mtime, UTC).date().isoformat(),
        "variableMeasured": ["Mod", "Effect", "Max level", "Description", "Tags", "Source"],
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": media,
                "contentUrl": f"{config.SITE_URL}/api/export/{fmt}?version={version}",
            }
            for fmt, media in (("csv", "text/csv"), ("json", "application/json"))
        ],
    }
    return [site, dataset_ld]
