#!/usr/bin/env python3
"""Scrapes mcmod.cn list page for item detail links and write them to a mod-specific file.

Usage:
    python mcmod/scrape_effect_list.py https://www.mcmod.cn/item/list/3468-6.html

Behavior:
    1. Fetch the provided list URL.
    2. Extract mod name from navigation breadcrumb: div.common-nav > ul > 5th li > a > font > font.
       Remove [XXX] prefix if present. Example: "[ISS] Iron's Spells'n'Spellbooks" -> "Iron's Spells'n'Spellbooks".
    3. Within the HTML, only traverse <ul><li><a ...> and collect unique href values ending with /item/<integer>.html.
    4. Normalize each to absolute URL prefixed with https://www.mcmod.cn.
    5. Derive output filename with special sanitization rules:
       - Replace : and - with _
       - Delete ' and . and 's endings
       - Replace 'n' (quote n quote) with _n_
       - Lowercase everything
       Example: "Eidolon: Repraised" -> eidolon_repraised.txt
    6. Save one URL per line to mcmod/<mod_name>.txt.
"""
from __future__ import annotations

import re
import sys
import pathlib
from typing import Iterable

import requests
from bs4 import BeautifulSoup

BASE = "https://www.mcmod.cn"
HREF_RE = re.compile(r"^/item/(\d+)\.html$")
PREFIX_RE = re.compile(r"^\[[^\]]+\]\s*")  # matches [XXX] prefix


def extract_mod_name_from_nav(soup: BeautifulSoup) -> str:
    """Extract mod name from navigation breadcrumb (5th li > a).

    The text is in format: "中文名 (English Name)" or "[PREFIX] 中文名 (English Name)"
    We extract the English name from parentheses.
    If no parentheses, use the raw text.
    """
    nav_div = soup.find("div", class_="common-nav")
    if not nav_div:
        raise ValueError("Navigation div not found")

    ul = nav_div.find("ul")
    if not ul:
        raise ValueError("Navigation ul not found")

    lis = ul.find_all("li", recursive=False)
    if len(lis) < 5:
        raise ValueError(
            f"Not enough navigation items found (found {len(lis)}, need at least 5)"
        )

    fifth_li = lis[4]  # 5th li (0-indexed)
    a_tag = fifth_li.find("a")
    if not a_tag:
        raise ValueError("No anchor tag in 5th navigation item")

    text = a_tag.get_text(strip=True)
    if not text:
        raise ValueError("Mod name text is empty")

    # Try to extract English name from parentheses: "神化 (Apotheosis)" -> "Apotheosis"
    match = re.search(r"\(([^)]+)\)$", text)
    if match:
        mod_name = match.group(1).strip()
    else:
        # No parentheses, use raw text
        mod_name = text

    # Remove [XXX] prefix if present (e.g., "[ISS] Iron's Spells'n'Spellbooks")
    mod_name = PREFIX_RE.sub("", mod_name).strip()

    # Remove hyphen and everything to the right (e.g., "TO Magic 'n Extras - Iron's Spells Addon" -> "TO Magic 'n Extras")
    if " - " in mod_name:
        mod_name = mod_name.split(" - ")[0].strip()

    return mod_name


def sanitize_filename(mod_name: str) -> str:
    """Sanitize mod name for filename with specific rules."""
    # Replace : and - with _
    sanitized = mod_name.replace(":", "_").replace("-", "_")

    # Replace 'n' (quote n quote) with _n_
    sanitized = sanitized.replace("'n'", "_n_")

    # Remove possessive 's (apostrophe s at end of words)
    sanitized = re.sub(r"'s\b", "", sanitized)

    # Remove remaining apostrophes and dots
    sanitized = sanitized.replace("'", "").replace(".", "")

    # Convert to lowercase
    sanitized = sanitized.lower()

    # Replace special symbols with _
    sanitized = re.sub(r"[&]+", "_", sanitized)

    # Replace any remaining non-alphanumeric characters with _
    sanitized = re.sub(r"[^a-z0-9_]+", "_", sanitized)

    # Clean up multiple underscores and trim
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")

    return sanitized + ".txt"


def sanitize_mod_id(mod_name: str) -> str:
    """Sanitize mod name for use in effect IDs (uses hyphens instead of underscores)."""
    # Replace : and - with -
    sanitized = mod_name.replace(":", "-").replace("-", "-")

    # Replace 'n' (quote n quote) with -n-
    sanitized = sanitized.replace("'n'", "-n-")

    # Remove possessive 's (apostrophe s at end of words)
    sanitized = re.sub(r"'s\b", "", sanitized)

    # Remove remaining apostrophes and dots
    sanitized = sanitized.replace("'", "").replace(".", "")

    # Convert to lowercase
    sanitized = sanitized.lower()

    # Replace special symbols with -
    sanitized = re.sub(r"[&]+", "-", sanitized)

    # Replace any remaining non-alphanumeric characters with -
    sanitized = re.sub(r"[^a-z0-9-]+", "-", sanitized)

    # Clean up multiple hyphens and trim
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")

    return sanitized


def sanitize_effect_name(effect_name: str) -> str:
    """Sanitize effect name for use in IDs."""
    # Convert to lowercase
    sanitized = effect_name.lower()

    # Replace apostrophes with nothing
    sanitized = sanitized.replace("'", "")

    # Replace any non-alphanumeric characters with hyphens
    sanitized = re.sub(r"[^a-z0-9-]+", "-", sanitized)

    # Clean up multiple hyphens and trim
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")

    return sanitized


def generate_effect_id(mod_name: str, effect_name: str) -> str:
    """Generate a complete effect ID from mod name and effect name."""
    mod_id = sanitize_mod_id(mod_name)
    effect_id = sanitize_effect_name(effect_name)
    return f"{mod_id}-{effect_id}"


def collect_item_links(soup: BeautifulSoup) -> list[str]:
    links: set[str] = set()
    # Only traverse ul/li/a as specified
    for ul in soup.find_all("ul"):
        for li in ul.find_all("li", recursive=False):
            for a in li.find_all("a", href=True):
                href = a["href"]
                if HREF_RE.match(href):
                    links.add(BASE + href)
    return sorted(links, key=lambda u: int(re.search(r"(\d+)", u).group(1)))


def scrape(url: str) -> tuple[str, list[str]]:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract mod name from navigation breadcrumb
    mod_name = extract_mod_name_from_nav(soup)

    links = collect_item_links(soup)
    if not links:
        raise RuntimeError("No item links found on the page")
    return mod_name, links


def write_output(mod_name: str, links: Iterable[str]) -> pathlib.Path:
    folder = pathlib.Path("mcmod/effect_urls")
    folder.mkdir(exist_ok=True)
    filename = sanitize_filename(mod_name)
    path = folder / filename
    with path.open("w", encoding="utf-8") as f:
        for url in links:
            f.write(url + "\n")
    return path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python mcmod/scrape_effect_list.py <list_url>", file=sys.stderr)
        return 1
    url = argv[1].strip()
    try:
        mod_name, links = scrape(url)
    except Exception as e:  # noqa: BLE001 simple cli
        print(f"Error: {e}", file=sys.stderr)
        return 2
    out_path = write_output(mod_name, links)
    print(f"Mod: {mod_name}")
    print(f"Links: {len(links)}")
    print(f"Written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
