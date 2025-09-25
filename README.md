# Minecraft Status Effects 🧪

![Minecraft 1.20](https://img.shields.io/badge/Minecraft-1.20/1.20.1-green)
![Stack HTML | CSS | JS](https://img.shields.io/badge/Stack-HTML/CSS/JS-red)
![Python | 3.12.3](https://img.shields.io/badge/Python-3.12.3-blue)
![Bottle | 0.13.4](https://img.shields.io/badge/Bottle-0.13.4-blueviolet)
![Docker](https://img.shields.io/badge/Docker-Supported-yellow)

Browse interactive list of vanilla and modded Minecraft status effects with proper descriptions.

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

You can trigger an automated scrape + insert flow by issuing a prompt that contains the word `add` and at least one `mcmod.cn` list URL (e.g. `Add https://www.mcmod.cn/item/list/3468-6.html`).

Flow summary:
1. Scrapes list page(s) with `python scrape/mcmod.py <url>` producing `scrape/<mod>.txt` of item detail URLs.
2. Fetch each effect page, extract English name (in parentheses), potency (max level), description (compressed), formulas, type and tags.
3. Build `id` (`mod-name-effect-name` lowercase, hyphen separated) and enforce description length ≤125 chars.
4. Insert (or update) effects in `data/effects.json` maintaining ordering rules and uniqueness.
5. Run `python scripts/validate_effects.py` once; if errors, attempt up to 2 auto-fix iterations.
6. Output Added / Updated / Skipped summary (for changed effects only).

Edge handling:
- Duplicate effect name across mods → skip.
- Missing English name → manual intervention required.
- Network/parse failure for a page → skipped with reason.
- Max level absent → defaults to I (no scaling tag).

This logic is documented in more detail in `.github/copilot-instructions.md`.

## Data Integrity Test ✅

Five automated validations run against `data/effects.json`.

### 1. Effects Order

Enforces deterministic ordering for readability and minimal diff noise.
- All `Minecraft` effects first (one contiguous block), alphabetically by effect name.
- Then each mod section ordered by mod name (A → Z).
- Inside every mod, effects ordered alphabetically by effect name.

### 2. Duplicate Effects

Effect names must be globally unique across ALL mods (not just within a mod). Adding an effect whose name already exists anywhere fails the check.

### 3. Formula Formatting

Any description containing scaling patterns must format them consistently:
- The substrings `^level` and `× level` (including the multiplication sign, not a plain 'x') must appear only inside a `<b>...</b>` span.
- The bold span must END with that substring (e.g. `<b>0.3^level</b>`, `<b>5 × level</b>`).
- These substrings must never appear outside bold formatting.
- Time units like "second", "seconds", and "second(s)" must always be wrapped in `<b>` tags.

### 4. Description Length

This is primarily to keep descriptions on a single line on FHD full-screen browser window size (125 characters), but also ensures every description stays concise and easy to read.

### 5. Tags Validation

Ensures proper tag structure for every effect:
- Each effect must have exactly one of either "positive" or "negative" tag (not both, not neither)
- The "scaling" tag must be present when maxLevel > 1 (i.e., effects that can have multiple levels)
- Tags must be properly formatted as an array of strings

### Run Locally

```bash
python scripts/validate_effects.py
```

- Or, to run all available tests:

```bash
./run_tests.sh
```

- You might need to run `chmod +x run_tests.sh` first.

GitHub Actions runs the integration test on every push / PR that touches `effects.json`.

## Additional Python scripts 🐍

### Fix effects.js order

If an ordering slip occurs during manual edits you can re-normalize ordering:

```bash
python scripts/sort_effects.py --check    # Verify
python scripts/sort_effects.py            # Rewrite in-place
python scripts/validate_effects.py        # Final confirmation
```
