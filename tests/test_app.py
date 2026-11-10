"""Pages, routing, caching and security of the web app."""

import json
import re
import xml.etree.ElementTree as ET

import pytest

from status_effects import config


def app_data(html: str) -> dict:
    match = re.search(r'<script id="app-data" type="application/json">(.*?)</script>', html, re.S)
    assert match
    return json.loads(match.group(1))


def test_index_renders_the_default_version(client, dataset):
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    effects = dataset.effects(config.DEFAULT_VERSION)
    assert html.count("<tr id=") == len(effects)
    assert f'<link rel="canonical" href="{config.SITE_URL}/" />' in html
    data = app_data(html)
    assert data["version"] == config.DEFAULT_VERSION
    assert [e["id"] for e in data["effects"]] == [e.id for e in effects]
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        json.loads(block)
    assert response.headers["content-security-policy"].startswith("default-src 'self'")
    assert response.headers["cache-control"] == "no-cache"


@pytest.mark.parametrize("version", config.VERSION_IDS)
def test_index_for_each_version(client, dataset, version):
    response = client.get("/", params={"version": version})
    assert response.status_code == 200
    data = app_data(response.text)
    assert data["version"] == version
    assert len(data["effects"]) == len(dataset.effects(version))
    assert all(item.get("mod") or item.get("group") for item in data["nav"])
    if version != config.DEFAULT_VERSION:
        assert f"?version={version}" in response.text
        assert version in response.text.split("<title>")[1].split("</title>")[0]


def test_unknown_version_redirects_home(client):
    response = client.get("/?version=9.99.x", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"


def test_api_effects_and_etag(client):
    response = client.get("/api/effects", params={"version": "1.21.x"})
    assert response.status_code == 200
    etag = response.headers["etag"]
    assert response.json()["version"] == "1.21.x"
    again = client.get("/api/effects", params={"version": "1.21.x"}, headers={"If-None-Match": etag})
    assert again.status_code == 304
    assert client.get("/api/effects", params={"version": "x"}).status_code == 400


def test_payload_html_is_escaped(client):
    data = client.get("/api/effects").json()
    for effect in data["effects"]:
        for field in ("description", "source"):
            tags = set(re.findall(r"</?([a-z]+)", effect[field]))
            assert tags <= {"b", "i", "sup", "span"}, (effect["id"], tags)


@pytest.mark.parametrize("path", ["/license/", "/privacy-policy/"])
def test_legal_pages(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert "<h1>" in response.text
    assert client.get(path.rstrip("/"), follow_redirects=False).status_code == 301


def test_index_html_redirects(client):
    response = client.get("/index.html?version=1.21.x", follow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == "/?version=1.21.x"


def test_robots_and_sitemap(client):
    robots = client.get("/robots.txt").text
    assert f"Sitemap: {config.SITE_URL}/sitemap.xml" in robots
    sitemap = client.get("/sitemap.xml")
    assert sitemap.headers["content-type"].startswith("application/xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text for loc in ET.fromstring(sitemap.content).findall("s:url/s:loc", namespace)]
    assert f"{config.SITE_URL}/" in urls
    assert f"{config.SITE_URL}/license/" in urls
    for version in config.VERSION_IDS:
        if version != config.DEFAULT_VERSION:
            assert f"{config.SITE_URL}/?version={version}" in urls


@pytest.mark.parametrize(
    "path",
    [
        "/data/effects.json",
        "/pyproject.toml",
        "/src/status_effects/app.py",
        "/AGENTS.md",
        "/run.sh",
        "/.git/config",
        "/css/../../pyproject.toml",
        "/does-not-exist",
    ],
)
def test_private_files_are_not_served(client, path):
    response = client.get(path)
    assert response.status_code == 404


def test_not_found_page_is_html(client):
    response = client.get("/nothing-here")
    assert response.status_code == 404
    assert "Page not found" in response.text


def test_versioned_assets_are_cached_long(client):
    html = client.get("/").text
    css = re.search(r'href="(/css/table\.css\?v=[0-9a-f]+)"', html).group(1)
    response = client.get(css)
    assert response.status_code == 200
    assert "immutable" in response.headers["cache-control"]
    assert client.get("/css/table.css").headers["cache-control"] == "no-cache"


def test_assets_referenced_by_pages_exist(client):
    html = client.get("/").text + client.get("/license/").text
    for path in set(re.findall(r'(?:href|src)="(/(?:css|js|img|fonts)/[^"?]+)', html)):
        assert client.get(path).status_code == 200, path
    assert client.get("/favicon.ico").status_code == 200


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert set(body["effects"]) == set(config.VERSION_IDS)
