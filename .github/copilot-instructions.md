# Copilot Instructions

## ⚠️ CRITICAL RULES - NEVER IGNORE THESE ⚠️

### 1. PROMPT PRIORITY
- **User prompts ALWAYS override these instructions**
- If unsure about anything, ASK in chat - do NOT make assumptions
- Follow the user's exact requirements, even if they contradict these rules

### 2. EFFECTS.JSON VALIDATION - MANDATORY
- **ALWAYS run `python scripts/validate_effects.py` after modifying `data/effects.json`**
- This is NON-NEGOTIABLE - run it exactly ONCE per user request
- If validation fails, fix the issues before proceeding

### 3. SUMMARY FORMAT - EXACT REQUIREMENT
When modifying `data/effects.json`, provide this summary at the end of your response:
```
- **Added**: 
  - Effect Name (Mod Name)
- **Updated**:
  - Effect Name (Mod Name)
    - Field (OLD: "old value", NEW: "new value")
- **Skipped**:
  - Effect Name (Mod Name)
```

### 4. NO CHANGE COMMENTS
- NEVER add comments like "Changed...", "Added...", "Removed..." to code files
- Only add production-quality comments that help understand the code

### 5. ENVIRONMENT SETUP
- Working directory: `/home/matej/projects/minecraft-status-effects/` (project root)
- Python: Use `python` or `python3` after `source venv/bin/activate`
- Never use full paths like `/home/matej/projects/minecraft-status-effects/venv/bin/python`
- Cannot delete files - tell user to delete instead

---

## PROJECT OVERVIEW

**What this is:** Minecraft status effects website - vanilla + modded effects database

**Tech stack:** HTML, CSS, JavaScript, Python (Bottle framework), Docker (production only)

**Key files:**
- `index.html` - main page with effects table
- `data/effects.json` - effects database (CRITICAL FILE)
- `data/links.json` - mod links/sources
- `scripts/validate_effects.py` - validation script (RUN AFTER CHANGES)
- `.github/workflows/` - CI/CD workflows

**Legal pages:** `license/index.html`, `privacy-policy/index.html` (separate, no JS)

---

## PROJECT STRUCTURE

```
minecraft-status-effects/
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│       ├── deploy.yml
│       └── validate-effects.yml
├── css/ (stylesheets)
├── data/
│   ├── effects.json ⚠️ CRITICAL
│   └── links.json
├── img/ (icons, logos, loading gifs)
├── js/ (modular JavaScript files)
├── license/ & privacy-policy/ (legal pages)
├── logs/ (runtime logs)
├── scrape/ (mcmod.cn scraping tools)
├── scripts/
│   ├── sort_effects.py
│   └── validate_effects.py ⚠️ CRITICAL
├── index.html (main page)
├── run.py (Python server)
├── sitemap.xml ⚠️ KEEP UPDATED
├── robots.txt (SEO)
├── humans.txt (developer info)
└── [config files]
```

**Update this section when adding/removing files or folders.**

---

## EFFECTS.JSON - THE CORE DATABASE

### ABSOLUTE REQUIREMENTS

1. **ORDERING RULES** (strictly enforced):
   - Minecraft effects first (alphabetical by effect name)
   - Then mods alphabetically by mod name
   - Within each mod, effects alphabetical by effect name
   
2. **GLOBAL UNIQUENESS**: Effect names must be unique across ALL mods
   - If duplicate found, SKIP and report in summary
   - Can update existing effects with better data

3. **MANDATORY VALIDATION**: Run `python scripts/validate_effects.py` after ANY change

### EFFECT STRUCTURE
```json
{
  "mod": "Mod Name",
  "id": "mod-name-effect-name",
  "effect": "Effect Name", 
  "maxLevel": 1,
  "type": "positive",
  "tags": ["positive"],
  "description": "Short description ≤125 chars"
}
```

### DESCRIPTION RULES - FOLLOW EXACTLY

**Length:** ≤ 125 characters (enforced by validator)

**Formatting:**
- Use `<b>` for: exact formulas, effect names, important terms
- Formulas: `<b>2 × level</b>` (linear) or `<b>2^level</b>` (exponential)
- For exponential, add actual values: `<b>2^level</b> (2 / 4 / 8)`
- Multiple benefits: separate with " and " (not bold)

**Content rules:**
- Ignore effect causes/triggers (not in scope)
- Use "damage"/"hearts" not "health" 
- Convert to whole hearts, not "half hearts"
- No "(stacks to X)" due to Apotheosis compatibility
- Add "(higher level → more damage/effect)" for scaling effects

**Examples from actual data:**
- `"Grants fire immunity."`
- `"Increases movement speed by <b>10% × level</b>."`
- `"<b>+50% jump height × level</b> and reduces <b>fall damage by level hearts</b>."`
- `"Combines <b>Water Breathing</b>, <b>Night Vision</b> and <b>Haste</b> effects."`

### TAGS SYSTEM
- **Required:** exactly one of `"positive"` or `"negative"`
- **Optional:** `"scaling"` if maxLevel ≥ 2
- Decision based on overall effect benefit/harm

### AUTOMATED MCMOD.CN WORKFLOW

**Trigger:** User says "add" + mcmod.cn URL

**Process:**
1. Extract mcmod.cn list URLs
2. Run `python scrape/mcmod.py <url>` for each
3. Process each effect detail page:
   - Extract English name from parentheses: `中文名 (English Name)`
   - Determine maxLevel from potency indicators (I/II/III)
   - Create compressed description following rules above
   - Set type (positive/negative) and tags
   - Build ID: `mod-name-effect-name` (lowercase, hyphens)
4. Check for duplicates (skip if effect name exists)
5. Insert maintaining alphabetical order
6. Run validator once at end
7. Provide exact summary format

**Quality checks before summary:**
- Ordering preserved
- No duplicate effect names  
- Descriptions formatted correctly and ≤125 chars
- Tags include type + optional scaling
- Summary uses exact format

---

## OTHER IMPORTANT FILES

### data/links.json
- Mod name → effects source URL mapping
- Same ordering as effects.json (Minecraft first, then alphabetical)
- Update when adding new mods

### scripts/validate_effects.py  
- Validates: ordering, duplicates, formula formatting, description length
- **CRITICAL:** Run after every effects.json change
- If adding new validation rules, also update:
  - This instruction file
  - .github/workflows/validate-effects.yml
  - README.md

### sitemap.xml - SEO MAINTENANCE
- **ALWAYS update lastmod date** when making significant content changes
- Update to current date format: `YYYY-MM-DD` (e.g., `2025-09-25`)
- Update when:
  - Adding new pages to the website
  - Making major content changes to existing pages
  - Updating effects.json with substantial additions
- Current structure includes: main page, license, privacy-policy
- If adding new routes/pages, add them to sitemap with appropriate priority:
  - Main page: priority="1.0", changefreq="weekly"
  - Legal pages: priority="0.3", changefreq="yearly"
  - Other content pages: priority="0.7", changefreq="monthly"

### CSS Comments Format
```css
/*----------------*
 * Section header *
 *----------------*/
```
- Dash count matches text length exactly
- Use `/* Subsection */` for smaller headers

### Forbidden Files
- Server returns 403 for: `.py`, `.md`, `Dockerfile`, etc.
- Defined in `run.py`

---

## FILE UPDATE GUIDELINES

### README.md
- Keep simple (private repo)
- Don't reorder sections after manual changes
- No changelog info - just current state
- Only document significant changes

### requirements.txt & .gitignore  
- Keep updated when adding/removing dependencies or ignored files

### This instructions file
- Update as project evolves for better AI understanding
- Inform user of significant changes
- Ask permission for major restructuring

---

## MCMOD.CN TRANSLATION GUIDELINES

**When processing Chinese mcmod.cn pages:**

- Extract precise English translations
- Convert time units: `秒` = seconds, `每两秒` = every 2 seconds  
- Convert damage units to hearts when possible
- Preserve percentage values as-is
- Ask for clarification if translation uncertain
- Use existing formula patterns for consistency

**Common patterns:**
- `每两秒造成一次伤害` → `"Deals periodic damage every 2 seconds"`
- Scaling indicators → `(higher level → more damage)`
- Multiple effects → separate with " and "

---

## QUALITY CONTROL CHECKLIST

Before completing any effects.json modification:
- [ ] Alphabetical ordering maintained
- [ ] No duplicate effect names globally
- [ ] All descriptions ≤125 characters
- [ ] Formulas and effect names properly wrapped in `<b>`
- [ ] Tags include exactly one type + optional scaling
- [ ] Validation script executed successfully
- [ ] Summary provided in exact required format

**If validation fails:** Fix issues immediately, don't proceed without clean validation.

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

- Update this section when adding new files or folders.
- Files and folders ignored by git (in .gitignore) shouldn't be there.

minecraft-status-effects/
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│       ├── deploy.yml
│       └── validate-effects.yml
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
│   ├── logo-dark.png
│   └── logo-light.png
├── js/
│   ├── core.js
│   ├── data.js
│   ├── filters.js
│   ├── navigation.js
│   ├── pagination.js
│   ├── render.js
│   └── theme.js
├── license/
│   └── index.html
├── logs/
├── privacy-policy/
│   └── index.html
├── scrape/
│   ├── mcmod.py
│   └── <mod>.txt
├── scripts/
│   ├── sort_effects.py
│   └── validate_effects.py
├── .gitignore
├── Dockerfile
├── LICENSE.md
├── README.md
├── index.html
├── requirements.txt
├── run_tests.sh
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


## data/effects.json

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
At the end of each of your responses, when you modify this file, add a short summary (as a list, not a paragraph) of what you've changed, in this exact format:
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

⚠️ Whenever you modify this file, run `python scripts/validate_effects.py` to check everything is correct. ⚠️
- This should run once per prompt, not once per change.
- You can use "pylanceRunCodeSnippet" command in VS Code to run it quickly.

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
  - "Note" = additional note about the effect; can sometimes include an useful info
- If you can find a description but can't find anything about potency, it generally means that the potency is 1
- Sometimes the page can have helpful comments from people that tell us more about the effect (i.e. damage type, damage scaling, ...)
  - Those comments usually acts like an addiction to the description and are mostly trustworthy.
- Scaling of the effect is generally either linear or exponential.
  - Linear is always in the form of `2 × level`.
    - If the multiplier is 1, write is simply as `level`, not `1 × level`.
  - Exponential is always in the form of `2^level`.
    - Since exponential is generally harder to understand, we put the exact number in brackets after it.
    - Those numbers are not wrapped in `<b>`, only the formula is.
- If effect grants multiple things, separate them by " and ", which wont be wrapped in `<b>`.
- Don't use hyphens unless you feel it's necessary (creative-like flight → creative flight).
- Don't use (stacks to X), due to Apotheosis affixes, most effects from other mods can stack up to higher levels than they are initially meant to.
- Use "damage" or "hearts" as a units of measurement, rather than "health", unless it's something like "half max health".
- If you are going to use term "heart(s)", always convert final formula to whole hearts, do not use "half hearts" or "half a heart"
- There is a specific Chinese website https://www.mcmod.cn, which contains info about modded effects that can't be found elsewhere on the whole internet.
  - If I send you a link to a status effects on that website, give me the most precise English translation of all fields
  - If you aren't sure about something regarding the translation, ask me in chat.

### Examples covering most cases (directly from effects.json):
- "Grants fire immunity."
- "Damages over time leaving entity alive at half a heart (higher level → faster ticks)."
- "Increases movement speed by <b>10% × level</b>."
- "<b>+50% jump height × level</b> and reduces <b>fall damage by level hearts</b>."
- "<b>-10% attack speed × level</b> and sets <b>mining speed to 0.3^level</b> (0.3 / 0.09 / 0.027)."
- "Combines <b>Water Breathing</b>, <b>Night Vision</b> and <b>Haste</b> effects."
- "<b>+3 armor</b> and <b>+1 armor toughness × level</b>. Also gains <b>Regeneration</b> equal to level."

### Corrections (examples of the descripnstions you created and how I modified them; learn from this):
Your initial version → My corrected version
1. "Deals armor-ignoring damage every 2 seconds." → "Deals periodic damage that ignores armor every 2 seconds."
2. "On end, if still burning, deals damage (higher level → more damage)." → "If the entity is on fire when the effect expires, deals damage based on remaining fire ticks (higher level → more damage).
3. "Reduces incoming damage by <b>level</b> (half hearts)." → "Reduces incoming damage by <b>0.5 × level</b> hearts."
4. "Negates fall damage and bounces entity upward (higher level → more horizontal push)." → "Negates fall damage and bounces entity upward upon landing (higher level → more momentum upon landing)."
5. "Increases lightning and shock damage by <b>3 × level</b> (stacks to III)." -> "Increases lightning and shock damage by <b>3 × level</b>."

### Tags rules
- Each effect must have exactly one of these tags: "positive" or "negative".
- It's up to you to decide if the effect is positive or negative, based on the description.
- If the effect can have level >=2 (some cause has Potency II+), add the "scaling" tag as well.
- Different lengths of the effect at the same level are not considered as scaling, only the power of the effect is.

### Automated "Add <mcmod.cn URL>" Flow

Trigger conditions (case-insensitive):
1. User prompt contains the word "add" (variants like `Add`, `add:`, `add effects`, `Add:` are all valid) AND
2. At least one URL substring containing `mcmod.cn`.

Supported prompt examples:
1. `Add https://www.mcmod.cn/item/list/3468-6.html`
2. `add effects https://www.mcmod.cn/item/list/1708-6.html`
3. `Add: https://www.mcmod.cn/item/list/1254-6.html more text` (ignore extra text)
4. `Please add https://www.mcmod.cn/item/list/9999-6.html`.

Steps you must perform when triggered (no need to ask for confirmation):
1. Extract all unique mcmod.cn list URLs from the prompt.
2. For each list URL run: `python scrape/mcmod.py <url>`.
  - This creates (or overwrites) `scrape/<sanitized_mod_name>.txt` with absolute item detail URLs.
3. Read each generated `.txt` file line by line (deduplicate again just in case).
4. For every effect detail page URL:
  1. Fetch the page HTML.
  2. Extract effect English name (inside parentheses after Chinese name, e.g. `火焰引爆 (Flaming Detonation)` → `Flaming Detonation`).
  3. Determine mod name: reuse the mod name already derived from the list page (do NOT attempt to guess a different mod per item).
  4. Determine max level (potency):
    - Look for patterns like `I / II / III` or Chinese numerals + level indicators; if none found, use `I`.
    - If the page text explicitly lists higher tiers (e.g., "在 III 级或更高等级时"), highest mentioned tier = maxLevel.
  5. Extract description text (longer explanatory paragraph under the effect heading) and compress per existing Description rules.
  6. Identify formulas: percent or numeric scaling referencing level. Wrap formulas or effect names in `<b>` per existing rules.
  7. Decide `type`: positive vs negative.
  8. Set tags:
    - Always include the type tag.
    - Add `scaling` if maxLevel ≥ II.
  9. Build `id` as: `<mod-name-lower-no-apostrophes-hyphenated>-<effect-name-lower-hyphenated>` using same rules already used in file (hyphen separators, no apostrophes).
  10. Enforce description length ≤ 125 chars (truncate intelligently only if absolutely necessary; prefer tightening wording first).
5. Before inserting, check if an effect with the same `effect` name already exists globally:
  - If exists under same mod: treat as potential update (only update fields with better info; record in summary under Updated).
  - If exists under different mod: SKIP (name must be globally unique) and record under Skipped.
6. Insert new effects preserving ordering rules:
  - Ensure the mod section exists (mod ordering alphabetical after Minecraft block).
  - Place effect in alphabetical order within its mod by `effect` name.
7. After all insertions/updates, run `python scripts/validate_effects.py` exactly once.
8. Provide the standard summary block (Added / Updated / Skipped) exactly in the required nested list format.
9. If validation fails:
  - Attempt up to 2 fix iterations.
  - If still failing, report failing rule(s) and stop further modifications.

Edge cases & clarifications:
1. Duplicate URLs in list output: ignore duplicates silently.
2. Empty scrape result: report and stop (no changes).
3. Network/parse failure for a single effect page: skip that page, record under Skipped with reason in parentheses.
4. If a page lacks English parentheses name: ask user for clarification before adding.
5. Prefer consistency with previous formulas (e.g., use `<b>+20% movement speed × level</b>` style).
6. Convert “每两秒造成一次伤害” to “Deals periodic damage every 2 seconds” and similar patterns; keep phrasing concise.
7. Chinese `%` values retain percent sign; convert fractions if obvious (e.g., 0.5 hearts, 2 秒 = 2 seconds).
8. If damage or scaling is level-dependent but no numeric formula is given, append `(higher level → more damage)` if and only if the effect actually scales in intensity, not just duration.

Quality checklist before final summary:
1. Ordering still valid.
2. No duplicate `effect` names.
3. All new descriptions obey formatting (bold only for formulas/effect names/important terms) and length limit.
4. Tags include exactly one of `positive`/`negative` plus optional `scaling`.
5. Summary conforms EXACT list formatting.

Do NOT modify unrelated effects or reorder unaffected entries.

If multiple list URLs are provided, batch all changes and run validator only once at the end.

If the user sends an "Add" prompt with invalid mcmod.cn URL, ask for a valid mcmod.cn URL.

If the user sends an "Add" prompt for completely different website/source, it's a different scenario; in that case don't ask for a valid mcmod.cn URL.

Never fabricate effect data; if unsure about translation or potency, ask the user.

## data/links.json

- JSON file with list of mod names and URLs of their status effects lists.
  - Link can be to mod's wiki, mcmod.cn, GitHub, CurseForge, Modrinth, and so on.
  - We will call those pages "effects sitemap"
- If we add new mod, add it with it's effects sitemap to this file.
  - Keep the same ordering rules as for the effects.json (Minecraft first; then alphabetically by mod name).
- Update links in this file to the latest "effects sitemap" page that you updated effects based on.

## scripts/validate_effects.py
- Python script that validates `effects.json` for:
  1. Correct ordering
  2. Duplicate effect names
  3. Correct formula formatting in descriptions
  4. Description length ≤ 125 characters
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
