"""CSV, XLSX and JSON exports."""

import csv
import io
import json

import pytest
from openpyxl import load_workbook

from status_effects import config, export
from status_effects.data import Effect


def test_csv_export_of_a_version(client, dataset):
    response = client.get("/api/export/csv", params={"version": "1.21.x"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert 'filename="status-effects-1.21.x-' in response.headers["content-disposition"]
    assert response.content.startswith(b"\xef\xbb\xbf")
    rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
    assert rows[0] == list(export.COLUMNS)
    assert len(rows) - 1 == len(dataset.effects("1.21.x"))
    assert all("<b>" not in cell and "<i>" not in cell for row in rows for cell in row)


def test_json_export(client, dataset):
    response = client.get("/api/export/json")
    payload = json.loads(response.content)
    assert payload["version"] == config.DEFAULT_VERSION
    assert len(payload["effects"]) == len(dataset.effects(config.DEFAULT_VERSION))
    assert {"id", "mod", "effect", "maxLevel", "type", "tags", "description", "source"} <= set(payload["effects"][0])


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_xlsx_export_is_styled(client, theme):
    response = client.get("/api/export/xlsx", params={"theme": theme})
    assert response.status_code == 200
    sheet = load_workbook(io.BytesIO(response.content), rich_text=True).active
    assert [cell.value for cell in sheet[1]] == [name.upper() for name in export.COLUMNS]
    header_color = export.THEME_COLORS[theme]["header_bg"]
    assert sheet["A1"].fill.start_color.rgb.endswith(header_color)
    rich = [row[3].value for row in sheet.iter_rows(min_row=2) if not isinstance(row[3].value, str)]
    assert rich, "descriptions with <b> should be rich text"
    assert any(block.font.b for value in rich for block in value if hasattr(block, "font"))


def test_post_export_keeps_the_order_of_the_table(client, dataset):
    effects = dataset.effects(config.DEFAULT_VERSION)
    ids = [effects[5].id, effects[2].id, effects[5].id, effects[9].id]
    response = client.post("/api/export/json", json={"version": config.DEFAULT_VERSION, "ids": ids})
    assert response.status_code == 200
    assert [e["id"] for e in response.json()["effects"]] == [effects[5].id, effects[2].id, effects[9].id]


@pytest.mark.parametrize(
    "body",
    [
        {"version": "1.20.x", "ids": ["no-such-effect"]},
        {"version": "0.0.x", "ids": []},
        {"version": "1.20.x", "theme": "purple", "ids": []},
        {"ids": []},
    ],
)
def test_post_export_rejects_bad_input(client, body):
    assert client.post("/api/export/csv", json=body).status_code in (400, 422)


def test_unknown_format(client):
    assert client.get("/api/export/pdf").status_code == 422


def test_rich_text_conversion():
    colors = export.THEME_COLORS["light"]
    value = export._rich_text("Deals <b>2 damage</b> from <i>Mod</i> & more", colors)
    text = "".join(block.text if hasattr(block, "text") else block for block in value)
    assert text == "Deals 2 damage from Mod & more"


def test_empty_export_has_only_the_header():
    content, name = export.build("csv", [], "1.20.x")
    assert content.decode("utf-8-sig").strip() == ",".join(export.COLUMNS)
    assert name.endswith(".csv")


def test_tags_include_unreliable():
    effect = Effect(
        id="x",
        mod="M",
        version="1.20.x",
        effect="E",
        max_level="II",
        type="negative",
        unreliable=True,
        description="d",
        source="s",
    )
    assert export.export_tags(effect) == ["negative", "scaling", "unreliable"]
