#!/usr/bin/env python3
"""Common utilities for web scraping scripts."""
from __future__ import annotations

import pathlib
import re
import time
from typing import Iterable

import requests
from bs4 import BeautifulSoup


def fetch_page(url_or_path: str, timeout: int = 15) -> BeautifulSoup:
    """Fetch a webpage and return BeautifulSoup object. Accepts URL or local file path."""
    import os

    # Check if it's a local file
    if os.path.exists(url_or_path):
        with open(url_or_path, "r", encoding="utf-8") as f:
            return BeautifulSoup(f.read(), "html.parser")

    # Otherwise treat as URL
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    # Add a small delay to be polite
    time.sleep(0.5)

    session = requests.Session()
    session.headers.update(headers)

    resp = session.get(url_or_path, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return BeautifulSoup(resp.text, "html.parser")


def clean_text(text: str | None) -> str:
    """Clean up text by removing extra whitespace and newlines."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def sanitize_filename(name: str) -> str:
    """Sanitize name for filename with specific rules."""
    # Replace : and - with _
    sanitized = name.replace(":", "_").replace("-", "_")

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


def write_output(filename: str, links: Iterable[str]) -> pathlib.Path:
    """Write links to a file in the scraping folder."""
    folder = pathlib.Path("scraping")
    folder.mkdir(exist_ok=True)
    path = folder / filename
    with path.open("w", encoding="utf-8") as f:
        for url in links:
            f.write(url + "\n")
    return path
