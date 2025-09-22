# Copilot Instructions

## General

- You are in WSL 2.3.26.0 Linux subsystem (Ubuntu 24.04.1), with access to all files in this project.
- If you are going to work with cmd, start with simple `source venv/bin/activate` to activate the Python venv.
- No need to put `home/matej/projects/minecraft-status-effects/` before paths, you are already (and always) in the project root.
- Do not run Python files like this `/home/matej/projects/minecraft-status-effects/venv/bin/python`, always use `python` or `python3` after activating the venv.
- Note that you are not able to delete files (LLMs are not allowed to do that on their own), only edit existing ones or create new ones.
  - So if there is a file/folder that is not needed anymore, tell me to delete it, do not mislead me by saying "I deleted ...".
- Prompts are **always** above any rules and instructions, so if there is a conflict, follow the prompt.
  - If you are unsure about something, ask me in chat, do not make assumptions.
- You can and you should update this file as we progress, for you to better undestand it and read from it faster.
  - You don't need to tell me about small changes, but if you make significant changes, inform me.
  - If it's extremely significant, prompt me for permission first.

## About me
- Years of coding experience: **4+**.
- Primary: Python (backend) — prefer Django for web apps.
- Secondary: SQL (mainly PostgreSQL), JavaScript, HTML/CSS.
- Other skills: ETL, web scraping, Linux (WSL).
- Roles I do/did in the past: backend/SW engineer, ETL developer, web developer, QA engineer.
- Tools: Git, GitHub, VS Code, JIRA, Confluence, Copilot.
- Coding preferences:
  - Always use case that the language/framework is intended for (snake_case for Python, camelCase for JavaScript, ...).
  - Do not declare variables that are used only once, unless it improves readability.
  - Use list/dict/set comprehensions where appropriate.
  - Avoid unnecessary complexity; prefer simple and clear solutions.
    - This doesn't mean you should create a new function for everything, too many functions is not good either, find some middleground.
- Interaction rules:
  - IMPORTANT: Use lists for steps and short examples; important for me, I read from lists much better and faster than from paragraphs.
    - So instead of "You should do A, then B, and finally C.", write:
      1. Do A.
      2. Do B.
      3. Finally, do C.
  - Explain terms that I might not know (e.g., "idempotent", "decorator", "closure", ...).
    - When explaining, use simple language, as if you were explaining to a beginner.
    - Use comparisons and analogies whenever possible to make it easier to understand.
  - Use warm, conversational English with contractions.
  - Assume sensible defaults (don’t ask unnecessary confirmation)
  - Avoid face emojis, use symbols like ✅/❌/⚠️/ℹ️.
- When recommending stacks/tools, list tradeoffs (pros, cons, cost, privacy).

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
│   └── workflows/
│       ├── validate-effects.yml
│       └── deploy.yml
│   └── copilot-instructions.md
├── .gitignore
├── Dockerfile
├── LICENSE.md
├── README.md
├── css/
│   ├── legal.css
│   ├── navigation.css
│   ├── note.css
│   ├── styles.css
│   ├── table.css
│   └── theme.css
├── data/
│   ├── effects.json
│   └── links.json
├── img/
│   ├── icon.ico
│   ├── loading-dark.gif
│   ├── loading-light.gif
│   └── logo.png
├── index.html
├── js/
│   ├── core.js
│   ├── data.js
│   ├── filters.js
│   ├── navigation.js
│   ├── render.js
│   └── theme.js
├── license/
│   └── index.html
├── privacy-policy/
│   └── index.html
├── requirements.txt
├── run.py
├── test/
│   └── validate_effects.py
├── logs/
│   └── .gitkeep

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
- Order of the effects is important:
  - Minecraft effects always first, alphabetically by effect's name.
  - Then modded effects alphabetically by mod name, then effect's name.
- To be explicit:
  - Minecraft - EffectA will be before Minecraft - EffectB.
  - Minecraft - EffectZ will be before Mod1 - EffectA.
  - Mod1 - EffectA will be before Mod1 - EffectB.
  - Mod1 - EffectZ will be before Mod2 - EffectA.
- Do not add effects or mods already present; effect names must be globally unique across all mods.
  - If I send you an effect which is already present, do not add it and inform me.
  - But you can change its description, maxLevel, type, tags, if the newly provided info is better/more accurate.
    - In that case also inform me, and send me the OLD and the NEW value of the field (no need for reason).
- If I prompt you to add effect which's mod is already present, put it under the existing mod, in the exact spot so the order described above is preserved.
- Each effect has: `mod`, `id` ("mod-name-effect-name"), `effect` (effect's name), `maxLevel`, `type` (positive/negative), `tags` (always one of the types, optionally scaling), `description`.
- Descriptions use `<b>` tag to wrap exact formulas (almost always containing word "level"), important terms, or another effect name.
- Don't change the structure unless prompted to do so.
- If you change existing effect name or description without me asking for it, inform me about it in chat, and provide a reason why you changed it.
- At the end of each of your responses, when you modify this file, add a short summary (as a list, not a paragraph) of what you've changed, in this exact format:
  - **Added**: List of effect name(s) with mod name(s) in parentheses
  - **Updated**: List of effect name(s) with mod name(s) in parentheses + sublist of changed field(s) (OLD:, NEW:; again, list, not paragraph)
  - **Skipped**: List of effect name(s) with mod name(s) in parentheses

Example of summary (please keep it as a list > list > list, not paragraph(s)):
- **Added**: 
  - EffectA (Mod1)
  - EffectB (Mod2)
- **Updated**:
  - EffectC (Mod3)
    - Description (OLD: "Old description", NEW: "New description")
- **Skipped**:
  - EffectD (Mod4)

⚠️ Whenever you modify this file, run `python test/validate_effects.py` to check everything is correct. ⚠️
- This should run once per prompt, not once per change.

### Description rules
- Description is (almost) always the text in the middle of the page, right below the effect name and above the ToC.
  - i.e. "Irradiated is a status effect that prevents the affected entity from naturally regenerating while holding radioactive items. Irradiated I simply prevents regeneration, but Irradiated II and beyond slowly damages the affected entity."
- Sometimes a short descrtion is given in a box right below the effect name, and a longer one below it. Use the longer one.
- You are going to shorten this to the shortest string possible while keeping the meaning.
- If the effect can have level, also add "(higher level → more damage)".
  - i.e. "Prevents natural regeneration. Level II+ additionally deals periodic damage (higher level → more damage)."
- If there is an exact formula, use it in the description, wrapped in `<b>`.
  - i.e. "Prevents natural regeneration. Level II+ deals <b>0.5 × level</b> damage per second."
- If there is another effect mentioned, also wrap it in `<b>`.
- Note this specific effect can be caused by more things while in a modpack, that's why we skip "while holding radioactive items".
  - But generally, always ignore the cause of the effect, it's not in the project scope.
- If I send you a page with a single effect, that page can have these keywords:
  - "Cause" (of the effect), ignore that, it's not needed.
  - "Potency" = level, highest potency in the list = maxLevel.
  - "Length" = how long the effect lasts, ignore that, it's not needed.
- Sometimes it's just the description, in that case, potency is always I.
- Scaling of the effect is generally either linear or exponential.
  - Linear is always in the form of `2 × level`.
    - If the multiplier is 1, write is simply as `level`, not `1 × level`.
  - Exponential is always in the form of `2^level`.
    - Since exponential is generally harder to understand, we put the exact number in brackets after it.
    - Those numbers are not wrapped in `<b>`, only the formula is.
- If effect grants multiple things, separate them by " and ", which wont be wrapped in `<b>`.

✅ Examples covering most cases (directly from effects.json):
- "Grants fire immunity."
- "Damages over time leaving entity alive at half a heart (higher level → faster ticks)."
- "Increases movement speed by <b>10% × level</b>."
- "<b>+50% jump height × level</b> and reduces <b>fall damage by level hearts</b>."
- "<b>-10% attack speed × level</b> and sets <b>mining speed to 0.3^level</b> (0.3 / 0.09 / 0.027)."
- "Combines <b>Water Breathing</b>, <b>Night Vision</b> and <b>Haste</b> effects."
- "<b>+3 armor</b> and <b>+1 armor toughness × level</b>. Also gains <b>Regeneration</b> equal to level."

### Tags rules
- Each effect must have exactly one of these tags: "positive" or "negative".
- It's up to you to decide if the effect is positive or negative, based on the description.
- If the effect can have level >=2 (some cause has Potency II+), add the "scaling" tag as well.
- Different lengths of the effect at the same level are not considered as scaling, only the power of the effect is.

## validate_effects.py
- Python script that validates `effects.json` for:
  1. Correct ordering
  2. Duplicate effect names
  3. Correct formula formatting in descriptions
  4. Description length ≤ 120 characters
- Run this script whenever you modify `effects.json` to ensure data integrity.
- If we add new rules to the Python file, we also need to update these files:
  - .github/copilot-instructions.md (this file)
  - .github/workflows/validate-effects.yml
  - ./README.md
Optionally:
  - ./requirements.txt (if new dependencies are added)
  - .github/workflows/deploy.yml (if name/workflow changes)

## README.md

- Keep this file updated, but also simple, note that this is a private repo, not a public one.
- Do NOT change the order of sections if I manually change them after you do changes to the file.
- Do NOT put the info about what you've changed in the README.md, it's not a changelog.
- Only put there the actual changes (if they are significant enough), as if the new changes were always there.

## requirements.txt & .gitignore

- Keep these files updated as you add/remove dependencies or files to be ignored.
