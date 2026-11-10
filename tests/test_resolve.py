"""Resolving records per version (changes cascade to later versions)."""

import pytest
from pydantic import ValidationError

from status_effects.assets import format_text
from status_effects.data import EffectRecord


def record(**overrides):
    data = {
        "id": "mod-effect",
        "mod": "Mod",
        "effect": "Effect",
        "versions": ["1.20.x", "1.21.x", "26.1.x"],
        "maxLevel": "II",
        "type": "positive",
        "description": "Old.",
        "source": "Potion",
        "changes": {"1.21.x": {"description": "New."}, "26.1.x": {"maxLevel": "III"}},
    }
    data.update(overrides)
    return EffectRecord.model_validate(data)


def test_changes_cascade():
    rec = record()
    assert rec.resolve("1.20.x").description == "Old."
    assert rec.resolve("1.21.x").description == "New."
    resolved = rec.resolve("26.1.x")
    assert (resolved.description, resolved.max_level, resolved.level) == ("New.", "III", 3)
    assert rec.resolve("26.2.x") is None


def test_since_only_shown_in_its_version():
    rec = record(since="1.20.5", changes={})
    assert rec.resolve("1.20.x").since == "1.20.5"
    assert rec.resolve("1.21.x").since is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"versions": []},
        {"versions": ["1.21.x", "1.20.x"]},
        {"versions": ["2.0.x"]},
        {"changes": {"1.20.x": {"description": "x"}}},
        {"changes": {"26.3.x": {"description": "x"}}},
        {"maxLevel": "XI"},
        {"type": "neutral"},
        {"since": "1.21.5"},
        {"unknownField": 1},
    ],
)
def test_invalid_records_are_rejected(overrides):
    with pytest.raises(ValidationError):
        record(**overrides)


def test_format_text_escapes_everything_but_inline_tags():
    html = str(format_text('<b>2^level</b> <script>x</script> <i>Mod</i> → "q" & <u>u</u>'))
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert '<b>2<sup class="lvl-sup">level</sup></b>' in html
    assert "<i>Mod</i>" in html and "&lt;u&gt;" in html
    assert '<span class="arrow" aria-hidden="true">→</span>' in html
    assert "&amp;" in html
