#!/usr/bin/env python3
"""Scrapes mcmod.cn list page for item detail links and write them to a mod-specific file.

Usage:
    python scraping/mcmod_effect_list.py https://www.mcmod.cn/item/list/3468-6.html

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
    6. Save one URL per line to scraping/<mod_name>.txt.
"""
from __future__ import annotations

import re
import sys
from typing import Iterable

from common import fetch_page, sanitize_filename, write_output

BASE = "https://www.mcmod.cn"
HREF_RE = re.compile(r"^/item/(\d+)\.html$")
PREFIX_RE = re.compile(r"^\[[^\]]+\]\s*")  # matches [XXX] prefix


def extract_mod_name_from_nav(soup) -> str:
    """Extract mod name from navigation breadcrumb (5th li > a > font > font)."""
    nav_div = soup.find("div", class_="common-nav")
    if not nav_div:
        raise ValueError("Navigation div not found")

    ul = nav_div.find("ul")
    if not ul:
        raise ValueError("Navigation ul not found")

    lis = ul.find_all("li", recursive=False)
    if len(lis) < 5:
        raise ValueError("Not enough navigation items found")

    fifth_li = lis[4]  # 5th li (0-indexed)
    a_tag = fifth_li.find("a")
    if not a_tag:
        raise ValueError("No anchor tag in 5th navigation item")

    fonts = a_tag.find_all("font")
    if len(fonts) < 2:
        raise ValueError("Not enough font tags found")

    mod_name = fonts[-1].get_text(strip=True)  # last font tag
    if not mod_name:
        raise ValueError("Mod name is empty")

    # Remove [XXX] prefix if present
    mod_name = PREFIX_RE.sub("", mod_name).strip()
    return mod_name


def collect_item_links(soup) -> list[str]:
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
    soup = fetch_page(url)

    # Extract mod name from navigation breadcrumb
    mod_name = extract_mod_name_from_nav(soup)

    links = collect_item_links(soup)
    if not links:
        raise RuntimeError("No item links found on the page")
    return mod_name, links


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scraping/mcmod_effect_list.py <list_url>", file=sys.stderr)
        return 1
    url = argv[1].strip()
    try:
        mod_name, links = scrape(url)
    except Exception as e:  # noqa: BLE001 simple cli
        print(f"Error: {e}", file=sys.stderr)
        return 2
    filename = sanitize_filename(mod_name)
    out_path = write_output(filename, links)
    print(f"Mod: {mod_name}")
    print(f"Links: {len(links)}")
    print(f"Written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
