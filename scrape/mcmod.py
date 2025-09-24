#!/usr/bin/env python3
"""Scrapes mcmod.cn list page for item detail links and write them to a mod-specific file.

Usage:
    python scrape/mcmod.py https://www.mcmod.cn/item/list/3468-6.html

Behavior:
    1. Fetch the provided list URL.
    2. Parse <meta name="description">, extract the first bracketed English mod name inside parentheses.
       Example meta content: "新生魔艺 (Ars Nouveau)模组的BUFF/DEBUFF列表..." -> "Ars Nouveau".
    3. Within the HTML, only traverse <ul><li><a ...> and collect unique href values ending with /item/<integer>.html.
    4. Normalize each to absolute URL prefixed with https://www.mcmod.cn.
    5. Derive output filename: lowercase, spaces & non-alphanumeric (except apostrophe) replaced by underscores.
       Apostrophes removed, multiple underscores collapsed. Example: "Eidolon: Repraised" -> eidolon_repraised.txt
    6. Save one URL per line to scrape/<mod_name>.txt.
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
META_DESC_RE = re.compile(r"\(([^()]+)\)")  # text inside first parentheses
SANITIZE_RE = re.compile(r"[^a-z0-9]+")


def extract_mod_name(meta_description: str) -> str:
    """Extract mod name from meta description (English text inside parentheses)."""
    match = META_DESC_RE.search(meta_description)
    if not match:
        raise ValueError("Could not locate mod name in meta description")
    name = match.group(1).strip()
    return name


def sanitize_filename(mod_name: str) -> str:
    # Remove apostrophes entirely
    mod_name = mod_name.replace("'", "")
    lowered = mod_name.lower()
    # Replace sequences of non-alphanumerics with underscore
    slug = SANITIZE_RE.sub("_", lowered).strip("_")
    # Collapse multiple underscores
    slug = re.sub(r"_+", "_", slug)
    return slug + ".txt"


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

    # Meta description
    meta = soup.find("meta", attrs={"name": "description"})
    if not meta or not meta.get("content"):
        raise RuntimeError("Meta description tag not found")
    mod_name = extract_mod_name(meta["content"])

    links = collect_item_links(soup)
    if not links:
        raise RuntimeError("No item links found on the page")
    return mod_name, links


def write_output(mod_name: str, links: Iterable[str]) -> pathlib.Path:
    folder = pathlib.Path("scrape")
    folder.mkdir(exist_ok=True)
    filename = sanitize_filename(mod_name)
    path = folder / filename
    with path.open("w", encoding="utf-8") as f:
        for url in links:
            f.write(url + "\n")
    return path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scrape/mcmod.py <list_url>", file=sys.stderr)
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
