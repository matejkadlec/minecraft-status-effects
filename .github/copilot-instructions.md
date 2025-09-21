# Copilot Instructions

## General

- You are in WSL 2.3.26.0 Linux subsystem (Ubuntu 24.04.1), with access to all files in this project.
- If you are going to work with cmd, start with simple `activate` to activate the Python venv.
- No need to put `home/matej/projects/minecraft-status-effects/` before paths, you are already (and always) in the project root.
- Note that you are not able to delete files (LLMs are not allowed to do that on their own), only edit existing ones or create new ones.
  - So if there is a file/folder that is not needed anymore, tell me to delete it, do not mislead me by saying "I deleted ...".

## About this project

- Website listing Minecraft status effects from vanilla and mods.
- Single functional page `./index.html` with navigation, effects table, and everything else.
- Additional pages for legal reasons; `./license/index.html` and `./privacy-policy/index.html`.
- Having simple features: searching, filtering by tags. Sorting to be added.
- Data stored in `effects.json`, loaded by `data.js` and rendered by `run.py`.
- Whatever JS functionality/CSS group is big enough to be put into separate file, is in separate file.
- Legal pages have their own HTML, CSS, no JS.

## Used technologies

- HTML, CSS, JS and Python (Bottle framework).
- Production also uses Docker, but we don't use it during development.

## Project structure

Update this section when adding new files or folders.

minecraft-status-effects/
├── .github/
│ └── copilot-instructions.md
├── .gitignore
├── Dockerfile
├── LICENSE.md
├── README.md
├── css/
│ ├── legal.css
│ ├── navigation.css
│ ├── note.css
│ ├── styles.css
│ ├── table.css
│ └── theme.css
├── data/
│ ├── effects.json
│ └── links.json
├── img/
│ ├── icon.ico
│ ├── loading-dark.gif
│ ├── loading-light.gif
│ └── logo.png
├── index.html
├── js/
│ ├── core.js
│ ├── data.js
│ ├── filters.js
│ ├── navigation.js
│ ├── render.js
│ └── theme.js
├── license/
│ └── index.html
├── privacy-policy/
│ └── index.html
├── requirements.txt
└── run.py

## Forbidden files/extensions

- As we don't want to show everything in this project, we return a 403 error for certain files or file extensions.
- These files and extensions are listed (and handled) in `run.py`.
- i.e., `.py`, `.md`, `Dockerfile`, and so on.

## Commenting

- Do not comment on what you've changed in the files, never.
  - I don't want to see comments like "Changed ... to ...", "Added ...", "Removed ...", and so on.
  - If I do see them, I will ask you to remove them and make this rule more dummy-proof.
- Only add production-like comments that help understand the code. Do not comment on trivial things.
- You can use any of the current comments as a reference.
- For CSS section headers, use this format:
  ```css
  /*----------------*
   * Section header *
   *----------------*/
  ```
  - The number of `-` must match the length of the section header text.
  - " Section header " = 16 characters, so there are 16 `-` on both edges.
  - `*` must be aligned with the text, directly under eachother, from both sides.
  - `/` is only used at the start and end of the whole comment block.
  - You can also use CSS one-liners, like `/* Subsection header */` for subsections.
- Other than that, use simple `//` for JS and `#` for Python.
- Note that I prefer one-liner comments, but multi-liners are allowed when necessary.
- Do not create insanely long and complex Python docstrings, keep them simple and to the point.
  - Again, ideally one-liners, but multi-liners are allowed when necessary.

## links.json

- JSON file with list of mod names and URLs of their status effects lists.
  - Link can be to mod's wiki, GitHub, CurseForge, Modrinth, and so on.
  - There is a specific Chinese website https://www.mcmod.cn, which contains info about modded effects that can't be found elsewhere on the whole internet.
- Ignore for now, since it's too long to be put on the main page.
- Will be most likely used in future on a different (new) page.

## effects.json

- JSON file with list of effects; main data source.
- Order is very important:
  - Minecraft effects always first, alphabetically by effect name.
  - Then modded effects alphabetically by mod name, then effect name.
- To be explicit:
  - Minecraft - EffectA will be before Minecraft - EffectB.
  - Minecraft - EffectZ will be before Mod1 - EffectA.
  - Mod1 - EffectA will be before Mod1 - EffectB.
  - Mod1 - EffectZ will be before Mod2 - EffectA.
- Do not add effects or mods already present, we don't want duplicates, nor mods or effects.
- If I prompt you to add effect which's mod is already present, put it under the existing mod, in the exact spot so the order described above is preserved.
- Each effect has: name, mod, maxLevel, type (positive/negative), tags (always the type, optionally scaling), description.
- Descriptions use `<b>` tag to wrap exact formulas (almost always containing word "level"), important terms, or another effect name.
- Don't change the structure unless prompted to do so.

## README.md

- Keep it updated, but simple, note that this is a private repo, not a public one.
- Do NOT put the info about what you've changed in the README.md, this is not a changelog.
- Only put there the actual changes (if they are significant enough).

## requirements.txt & .gitignore

- Keep these files updated as you add/remove dependencies or files to be ignored.
