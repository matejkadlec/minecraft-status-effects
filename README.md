# Minecraft Status Effects 🧪

![Minecraft 1.20](https://img.shields.io/badge/Minecraft-1.20/1.20.1-green)
![Stack HTML | CSS | JS](https://img.shields.io/badge/Stack-HTML/CSS/JS-red)
![Python | 3.12.3](https://img.shields.io/badge/Python-3.12.3-blue)
![Bottle | 0.13.4](https://img.shields.io/badge/Bottle-0.13.4-blueviolet)
![Docker](https://img.shields.io/badge/Docker-Supported-yellow)

Interactive website for browsing vanilla and modded Minecraft status effects with detailed descriptions, multi-column sorting, filtering, and pagination.

## ✨ Features

- 📊 **Multi-column Sorting**: Sort by any column (Shift+click for multi-column)
- 📱 **Horizontal Scrolling**: Wide tables scroll smoothly on narrow screens  
- 🔍 **Advanced Filtering**: Filter by type, mod, scaling effects
- 📖 **Pagination**: Customizable page sizes (25/50/75/100 rows)
- 🌓 **Theme Switching**: Light and dark modes
- 🎯 **Quick Navigation**: Jump to specific mods/effects
- 🔎 **Real-time Search**: Search effects and mods instantly
- 📥 **Data Export**: CSV, Excel, JSON with theme-aware styling

## Run Local Server 💻

### Option 1: Docker (Recommended)

1. Clone this repository

   ```bash
   git clone https://github.com/matejkadlec/minecraft-status-effects.git
   ```

2. Build and run with Docker

   ```bash
   docker build -t minecraft-status-effects . && docker run -d -p 8000:8000 --name minecraft-status-effects minecraft-status-effects
   ```

Open http://localhost:8000 in your browser.

### Option 2: Local Python Environment

1. Clone this repository

   ```bash
   git clone https://github.com/matejkadlec/minecraft-status-effects.git`
   ```

2. Create and activate venv, then install dependencies

   ```bash
   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
   ```

3. Start the server

   ```bash
   `python run.py`
   ```

Open http://localhost:8000 in your browser.

## Automated Effect Ingestion (mcmod.cn) ⬇️

Trigger automated scraping in two ways:

### Single URL Method
Issue a prompt containing `add` + one or more `mcmod.cn` list URLs (e.g. `Add https://www.mcmod.cn/item/list/3468-6.html`).

### Batch Processing Method
Use `add {number} mods` (1-10) to process multiple mods from the queue in `data/effect-list-urls.json`. The system:
- Processes URLs with `"status": "TODO"` or `"WIP"` from top to bottom
- Only scrapes mcmod.cn URLs
- Updates status to `"DONE"` after successful ingestion
- Stops after processing {number} mods or exhausting the queue
- Provides detailed summary grouped by mod

Flow summary:
1. Scrapes list page(s) with `python mcmod/scrape_effect_list.py <url>` producing `mcmod/<mod>.txt` of item detail URLs.
2. Scrapes each individual effect page with `python mcmod/scrape_effect.py <effect_url>` to extract detailed information.
3. Fetch each effect page, extract English name (in parentheses), potency (max level), description (compressed), formulas, type and tags.
4. Build `id` (`mod-name-effect-name` lowercase, hyphen separated) and enforce description length ≤200 chars.
5. Insert (or update) effects in `data/effects.json` maintaining ordering rules and uniqueness.
6. Run `python scripts/validate_effects.py` once; if errors, attempt up to 2 auto-fix iterations.
7. Output Added / Updated / Skipped summary (for changed effects only).

Edge handling:
- Duplicate effect name across mods → skip.
- Missing English name → manual intervention required.
- Network/parse failure for a page → skipped with reason.
- Max level absent → defaults to I (no scaling tag).

This logic is documented in more detail in `AGENTS.md`.

## Data Integrity Test ✅

Ten automated validations run against `data/effects.json` to ensure data quality and consistency.

**General Checks:**
1. **No Empty Fields** - All required fields must be present and non-empty
2. **Text Formatting** - Proper spacing, no trailing/leading whitespace, correct comma placement
3. **Duplicate Effects** - Effect names must be globally unique across all mods
4. **Effects Ordering** - Minecraft effects first (alphabetical), then mods (alphabetical by mod, then by effect)

**Column-Specific Checks:**
5. **Max Level Format** - Must be valid Roman numerals (I-X)
6. **Description HTML Tags** - Formulas and time units must be wrapped in `<b>` tags
7. **Tags Validation** - Exactly one type tag (positive/negative), scaling tag when maxLevel > I
8. **Source Potion Grouping** - Simplified format (`Potion/Arrow/Charm of X`)
9. **Source HTML Tags** - `<i>` for mod names, no other tags are allowed
10. **Source Special Terms** - Ensures proper source text formatting

If ordering issues occur, re-normalize with:

```bash
python scripts/sort_effects.py --check    # Verify
python scripts/sort_effects.py            # Rewrite in-place
python scripts/validate_effects.py        # Final confirmation
```

### Run Locally

```bash
python scripts/validate_effects.py
```

- Or, to run all available tests:

```bash
./run_tests.sh
```

- You will most likely need to run `chmod +x run_tests.sh` first.

GitHub Actions runs the integration test on every push / PR that touches `effects.json`.


## Table Export 📤

Export effects data in multiple formats with theme-aware styling. Supports exporting complete dataset or filtered results based on current table state.

**Available Formats:**
- **CSV** - Plain text format for spreadsheets and data analysis
- **Excel (XLSX)** - Styled format with theme colors, borders, and formatting
- **JSON** - Structured data format preserving all original information

**Export Process:**
1. "Export as..." dropdown located next to search bar
2. "Ignore filters" checkbox controls whether current filters apply
3. Format selection triggers immediate download with timestamp filename

**Export Features:**
- 📊 **Theme-aware Excel styling** - Blue headers (light mode), gold headers (dark mode)
- 🔍 **Filter integration** - Respects current search, type, and mod filters
- ⚡ **Pre-generated files** - Instant downloads for complete dataset
- 🎯 **Dynamic generation** - On-demand creation for filtered results

Exported files contain: Mod, Effect Name, Level, Description, Tags, and Source. All formats strip HTML from descriptions and source except Excel which preserves formatting structure.