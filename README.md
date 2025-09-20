# Minecraft Status Effects 🧪

![Minecraft 1.20](https://img.shields.io/badge/Minecraft-1.20/1.20.1-green)
![Stack HTML | CSS | JS](https://img.shields.io/badge/Stack-HTML/CSS/JS-red)
![Python | 3.12.3](https://img.shields.io/badge/Python-3.12.3-blue)
![Bottle | 0.13.4](https://img.shields.io/badge/Bottle-0.13.4-blueviolet)
![Docker](https://img.shields.io/badge/Docker-Supported-yellow)

A comprehensive list of vanilla and modded Minecraft status effects with proper descriptions.<br>
Includes basic QoL functionality and features. Using python's framework Bottle for local development.

## Run Local Server 💻

### Option 1: Docker (Recommended)

1. Clone this repository

   - `git clone https://github.com/matejkadlec/minecraft-status-effects.git`

2. Build and run with Docker

   - `docker build -t minecraft-status-effects .`
   - `docker run -d -p 8000:8000 --name minecraft-status-effects minecraft-status-effects`

Open http://localhost:8000 in your browser.

### Option 2: Local Python Environment

1. Clone this repository

   - `git clone https://github.com/matejkadlec/minecraft-status-effects.git`

2. Create and activate venv, then install dependencies

   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - `pip install -r requirements.txt`

3. Start the dev server
   - `python run.py`

Open http://127.0.0.1:8000 in your browser.
