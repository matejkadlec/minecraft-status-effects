# Minecraft Status Effects 🧪

![Minecraft 1.20](https://img.shields.io/badge/Minecraft-1.20/1.20.1-green)
![Stack HTML | CSS | JS](https://img.shields.io/badge/Stack-HTML/CSS/JS-red)
![Python | 3.12.3](https://img.shields.io/badge/Python-3.12.3-blue)
![Bottle | 0.13.4](https://img.shields.io/badge/Bottle-0.13.4-blueviolet)
![Docker](https://img.shields.io/badge/Docker-Supported-yellow)

Interactive list of vanilla and modded Minecraft status effects with proper descriptions.

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

## Data Integrity Test ✅

Four automated validations run against `data/effects.json`.

### 1. Ordering

Enforces deterministic ordering for readability and minimal diff noise.
- All `Minecraft` effects first (one contiguous block), alphabetically by effect name.
- Then each mod section ordered by mod name (A → Z).
- Inside every mod, effects ordered alphabetically by effect name.

### 2. Duplicate Effect Names

Effect names must be globally unique across ALL mods (not just within a mod). Adding an effect whose name already exists anywhere fails the check.

### 3. Formula Formatting

Any description containing scaling patterns must format them consistently:
- The substrings `^level` and `× level` (including the multiplication sign, not a plain 'x') must appear only inside a `<b>...</b>` span.
- The bold span must END with that substring (e.g. `<b>0.3^level</b>`, `<b>5 × level</b>`).
- These substrings must never appear outside bold formatting.

### 4. Description Length (max 120 chars)

This is primarily to keep descriptions on a single line on FHD full-screen browser window size (120 characters), but also ensures every description stays concise and easy to read.

### Run Locally

```bash
python test/validate_effects.py
```

GitHub Actions runs all four on every push / PR that touches `effects.json`.
