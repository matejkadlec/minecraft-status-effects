"""Cache-busting URLs for files in public/ and the HTML formatting of effect text."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from markupsafe import Markup, escape

from . import config

_hash_cache: dict[Path, tuple[float, str]] = {}


def asset_url(path: str) -> str:
    """`css/site.css` -> `/css/site.css?v=<content hash>` (served with a long cache lifetime)."""
    file = config.PUBLIC_DIR / path
    mtime = file.stat().st_mtime
    cached = _hash_cache.get(file)
    if cached is None or cached[0] != mtime:
        digest = hashlib.sha256(file.read_bytes()).hexdigest()[:10]
        cached = (mtime, digest)
        _hash_cache[file] = cached
    return f"/{path}?v={cached[1]}"


_ALLOWED_TAGS = re.compile(r"&lt;(/?)(b|i)&gt;")
_GROUPED_EXPONENT = re.compile(r"\^\(([^()<>]{1,40})\)")
_ARROW = Markup('<span class="arrow" aria-hidden="true">→</span>')
_EXPONENT = Markup('<sup class="lvl-sup">level</sup>')


def format_text(value: str) -> Markup:
    """Escape a description/source value, keeping only <b> and <i>.

    Also renders `^level` and `^(level − 1)` as exponents and wraps arrows so they don't change the
    line height.
    """
    html = str(escape(value))
    html = _ALLOWED_TAGS.sub(r"<\1\2>", html)
    html = _GROUPED_EXPONENT.sub(r'<sup class="lvl-sup">\1</sup>', html)
    html = html.replace("^level", str(_EXPONENT)).replace("→", str(_ARROW))
    return Markup(html)
