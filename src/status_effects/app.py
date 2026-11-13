"""FastAPI application: pages, JSON API, exports and static files."""

from __future__ import annotations

import base64
import hashlib
import re
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.gzip import GZipMiddleware

from . import __version__, config, export, pages
from .assets import asset_url, format_text
from .data import get_dataset

app = FastAPI(
    title=config.SITE_NAME,
    version=__version__,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.add_middleware(GZipMiddleware, minimum_size=1024)

templates = Jinja2Templates(directory=config.TEMPLATES_DIR)
templates.env.globals.update(asset=asset_url, config=config, year=lambda: datetime.now(UTC).year)
templates.env.filters["rich"] = format_text
templates.env.trim_blocks = True
templates.env.lstrip_blocks = True

VersionParam = Annotated[str | None, Query(max_length=16)]
FormatParam = Literal["csv", "xlsx", "json"]
ThemeParam = Literal["light", "dark"]


def _inline_script_hashes() -> list[str]:
    """CSP hashes of the inline <script> blocks in the templates (theme bootstrap)."""
    hashes = []
    for template in config.TEMPLATES_DIR.glob("*.html"):
        for body in re.findall(r"<script>(.*?)</script>", template.read_text(encoding="utf-8"), re.S):
            digest = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
            hashes.append(f"'sha256-{digest}'")
    return sorted(set(hashes))


CONTENT_SECURITY_POLICY = "; ".join(
    [
        "default-src 'self'",
        f"script-src 'self' {' '.join(_inline_script_hashes())}",
        "style-src 'self'",
        "img-src 'self' data:",
        "font-src 'self'",
        "connect-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
    ]
)
SECURITY_HEADERS = {
    "Content-Security-Policy": CONTENT_SECURITY_POLICY,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}
STATIC_PREFIXES = ("/css/", "/js/", "/img/", "/fonts/", "/favicon")


@app.middleware("http")
async def headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    if "cache-control" not in response.headers:
        static = request.url.path.startswith(STATIC_PREFIXES)
        if static and "v" in request.query_params and response.status_code == 200:
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        else:
            response.headers["Cache-Control"] = "no-cache"
    return response


def _resolve_version(version: str | None) -> str:
    if version is None:
        return config.DEFAULT_VERSION
    if version not in config.VERSION_IDS:
        raise HTTPException(400, f"Unknown version {version!r}. Use one of: {', '.join(config.VERSION_IDS)}")
    return version


def _canonical(version: str) -> str:
    if version == config.DEFAULT_VERSION:
        return f"{config.SITE_URL}/"
    return f"{config.SITE_URL}/?version={version}"


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def index(request: Request, version: str | None = None):
    if version is not None and version not in config.VERSION_IDS:
        return RedirectResponse("/", status_code=302)
    selected = version or config.DEFAULT_VERSION
    dataset = get_dataset()
    texts = pages.page_texts(dataset, selected)
    canonical = _canonical(selected)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "version": selected,
            "versions": config.VERSIONS,
            "counts": dataset.counts,
            "effects": dataset.effects(selected),
            "nav": pages.build_nav(dataset, selected),
            "payload": pages.payload(dataset, selected),
            "texts": texts,
            "canonical": canonical,
            "json_ld": pages.json_ld(dataset, selected, texts, canonical),
        },
    )


@app.get("/index.html", include_in_schema=False)
def index_html(request: Request):
    query = f"?{request.url.query}" if request.url.query else ""
    return RedirectResponse(f"/{query}", status_code=301)


def _etag_matches(if_none_match: str | None, etag: str) -> bool:
    """Weak comparison of If-None-Match: a proxy that compresses the body sends the ETag back as `W/"..."`."""
    if not if_none_match:
        return False
    candidates = {value.strip().removeprefix("W/") for value in if_none_match.split(",")}
    return "*" in candidates or etag in candidates


@app.api_route("/api/effects", methods=["GET", "HEAD"])
def api_effects(request: Request, version: VersionParam = None):
    selected = _resolve_version(version)
    dataset = get_dataset()
    etag = f'"{dataset.fingerprint}-{selected}"'
    if _etag_matches(request.headers.get("if-none-match"), etag):
        return Response(status_code=304, headers={"ETag": etag})
    return JSONResponse(pages.payload(dataset, selected), headers={"ETag": etag})


class ExportRequest(BaseModel):
    version: str = Field(max_length=16)
    theme: ThemeParam = "light"
    ids: list[Annotated[str, Field(max_length=200)]] = Field(max_length=10000)


def _export_response(fmt: str, version: str, theme: str, ids: list[str] | None) -> Response:
    selected = _resolve_version(version)
    dataset = get_dataset()
    if ids is None:
        effects = dataset.effects(selected)
    else:
        by_id = dataset.effects_by_id(selected)
        unknown = [effect_id for effect_id in ids if effect_id not in by_id]
        if unknown:
            raise HTTPException(422, f"Unknown effect ids for {selected}: {', '.join(unknown[:10])}")
        effects = [by_id[effect_id] for effect_id in dict.fromkeys(ids)]
    content, name = export.build(fmt, effects, selected, theme)
    return Response(
        content,
        media_type=export.MEDIA_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@app.get("/api/export/{fmt}")
def export_all(fmt: FormatParam, version: VersionParam = None, theme: ThemeParam = "light"):
    """All effects of a version."""
    return _export_response(fmt, version or config.DEFAULT_VERSION, theme, None)


@app.post("/api/export/{fmt}")
def export_selection(fmt: FormatParam, body: Annotated[ExportRequest, Body()]):
    """The given effects (the filtered table) in the given order."""
    return _export_response(fmt, body.version, body.theme, body.ids)


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok", "version": __version__, "effects": get_dataset().counts}


@app.api_route("/license/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def license_page(request: Request):
    return templates.TemplateResponse(request, "license.html", {"canonical": f"{config.SITE_URL}/license/"})


@app.api_route("/privacy-policy/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def privacy_page(request: Request):
    return templates.TemplateResponse(request, "privacy.html", {"canonical": f"{config.SITE_URL}/privacy-policy/"})


@app.get("/license", include_in_schema=False)
@app.get("/license/index.html", include_in_schema=False)
def license_redirect():
    return RedirectResponse("/license/", status_code=301)


@app.get("/privacy-policy", include_in_schema=False)
@app.get("/privacy-policy/index.html", include_in_schema=False)
def privacy_redirect():
    return RedirectResponse("/privacy-policy/", status_code=301)


@app.api_route("/robots.txt", methods=["GET", "HEAD"], response_class=PlainTextResponse)
def robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {config.SITE_URL}/sitemap.xml\n"


@app.api_route("/sitemap.xml", methods=["GET", "HEAD"])
def sitemap():
    data_date = datetime.fromtimestamp(
        max(config.EFFECTS_FILE.stat().st_mtime, config.MODS_FILE.stat().st_mtime), UTC
    ).date()
    legal_date = datetime.fromtimestamp(
        max((config.TEMPLATES_DIR / name).stat().st_mtime for name in ("license.html", "privacy.html")), UTC
    ).date()
    urls = [
        (_canonical(v.id), data_date, "weekly", "1.0" if v.id == config.DEFAULT_VERSION else "0.8")
        for v in config.VERSIONS
    ]
    urls += [
        (f"{config.SITE_URL}/license/", legal_date, "yearly", "0.3"),
        (f"{config.SITE_URL}/privacy-policy/", legal_date, "yearly", "0.3"),
    ]
    entries = "".join(
        f"  <url>\n    <loc>{loc.replace('&', '&amp;')}</loc>\n    <lastmod>{date.isoformat()}</lastmod>\n"
        f"    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n  </url>\n"
        for loc, date, freq, priority in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}</urlset>\n"
    )
    return Response(xml, media_type="application/xml")


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404 and not request.url.path.startswith("/api/"):
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)


app.mount("/", StaticFiles(directory=config.PUBLIC_DIR, html=False), name="static")
