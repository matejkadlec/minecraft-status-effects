#!/usr/bin/env python3
"""
Populate index.html with effects data for SEO optimization.

This script injects effects from effects.json into index.html:
1. Full effects table pre-rendered in HTML (for search engines)
2. JSON-LD ItemList with all effects (for rich snippets)
3. All interactive JavaScript still works (progressive enhancement)

Usage:
    python scripts/populate_html.py

Output:
    Updates index.html with embedded effects data from effects.json
"""

import json
import re
from pathlib import Path


def load_effects():
    """Load effects from effects.json"""
    effects_path = Path(__file__).parent.parent / "data" / "effects.json"
    with open(effects_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["effects"]


def generate_table_rows(effects):
    """Generate HTML <tr> elements for all effects"""
    rows = []
    for effect in effects:
        # Generate tag spans
        tag_spans = " ".join(
            f'<span class="tag tag-{tag}">{tag}</span>' for tag in effect["tags"]
        )

        # Create table row
        row = f"""        <tr data-mod="{effect['mod']}" data-type="{effect['type']}" data-id="{effect['id']}">
          <td class="mod-cell">{effect['mod']}</td>
          <td class="effect-cell">{effect['effect']}</td>
          <td class="level-cell">{effect['maxLevel']}</td>
          <td class="description-cell">{effect['description']}</td>
          <td class="tags-cell">{tag_spans}</td>
          <td class="source-cell">{effect['source']}</td>
        </tr>"""
        rows.append(row)

    return "\n".join(rows)


def generate_item_list_jsonld(effects):
    """Generate JSON-LD ItemList structured data for all effects"""
    items = []
    for idx, effect in enumerate(effects, start=1):
        # Build keywords from effect name, mod, and tags
        keywords = [
            "minecraft",
            "status effect",
            "potion effect",
            effect["effect"].lower(),
            effect["mod"].lower(),
            effect["type"],
        ]
        if "scaling" in effect["tags"]:
            keywords.append("scaling effect")

        item = {
            "@type": "ListItem",
            "position": idx,
            "item": {
                "@type": "Thing",
                "name": f"{effect['effect']} ({effect['mod']})",
                "description": effect["description"],
                "keywords": ", ".join(keywords),
            },
        }
        items.append(item)

    jsonld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Minecraft Status Effects Database",
        "description": "Complete list of vanilla and modded Minecraft status effects with precise descriptions, formulas, and sources.",
        "numberOfItems": len(effects),
        "itemListElement": items,
    }

    # Format JSON with indentation
    return json.dumps(jsonld, indent=2, ensure_ascii=False)


def inject_seo_data(html_content, table_html, jsonld):
    """Inject table rows and JSON-LD into HTML content"""

    # 1. Inject table rows into <tbody>
    # Find the empty <tbody></tbody> and replace with populated one
    html_content = re.sub(
        r"<tbody[^>]*>\s*</tbody>",
        f"<tbody>\n{table_html}\n      </tbody>",
        html_content,
        flags=re.DOTALL,
    )

    # 2. Inject ItemList JSON-LD after the existing WebSite JSON-LD
    # Find the end of the first </script> tag after "Structured Data (JSON-LD)"
    jsonld_insertion = f"""    <script type="application/ld+json">
      {jsonld}
    </script>"""

    # Insert after the WebSite JSON-LD script tag
    pattern = r"(<!-- Structured Data \(JSON-LD\) -->.*?</script>)"
    replacement = r"\1\n" + jsonld_insertion
    html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

    return html_content


def main():
    """Main execution function"""
    print("🔍 Loading effects from effects.json...")
    effects = load_effects()
    print(f"✅ Loaded {len(effects)} effects")

    print("\n📝 Generating HTML table rows...")
    table_html = generate_table_rows(effects)
    print(f"✅ Generated {len(effects)} table rows")

    print("\n🏷️  Generating JSON-LD ItemList...")
    jsonld = generate_item_list_jsonld(effects)
    print(f"✅ Generated ItemList with {len(effects)} items")

    print("\n📄 Reading index.html template...")
    index_path = Path(__file__).parent.parent / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    print("💉 Injecting SEO data into HTML...")
    html_content = inject_seo_data(html_content, table_html, jsonld)

    print("💾 Writing updated index.html...")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ Successfully generated SEO-optimized index.html!")
    print(f"   - {len(effects)} effects in table")
    print(f"   - {len(effects)} items in JSON-LD")
    print(
        f"   - File size: {len(html_content):,} bytes ({len(html_content) / 1024:.1f} KB)"
    )


if __name__ == "__main__":
    main()
