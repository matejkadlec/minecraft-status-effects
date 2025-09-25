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
   
   To be explicit:
   - Minecraft - EffectA will be before Minecraft - EffectB
   - Minecraft - EffectZ will be before Mod1 - EffectA
   - Mod1 - EffectA will be before Mod1 - EffectB
   - Mod1 - EffectZ will be before Mod2 - EffectA
   
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
- HTML tags like `<b>` do NOT count toward the 125-character limit
- Example: `<b>Wither</b>` counts as 6 characters, not 10

**Formatting:**
- Use `<b>` for: exact formulas, effect names, important terms
- Always wrap time intervals in `<b>`, e.g., "every <b>2 seconds</b>" or "every <b>second</b>"
- Formulas: `<b>2 × level</b>` (linear) or `<b>2^level</b>` (exponential)
  - If the multiplier is 1, write simply as `level`, not `1 × level`
- For exponential, add actual values: `<b>2^level</b> (2 / 4 / 8)`
- Multiple benefits: separate with " and " (not bold)

**Content rules:**
- Ignore effect causes/triggers (not in scope)
- Use "damage"/"hearts" not "health" 
- Convert to whole hearts, not "half hearts"
- No "(stacks to X)" due to Apotheosis compatibility
- Add "(higher level → more damage/effect)" for scaling effects
- Don't use hyphens unless necessary (creative-like flight → creative flight)
- Never use phrases like "similar to X" or "like X" where X is another effect
  - Example: avoid "similar to Wither" or "like Wither" as it's unnecessary

### CORRECTIONS EXAMPLES
Examples of descriptions that needed correction (learning from past mistakes):

Your initial → Corrected version
1. "Deals armor-ignoring damage every 2 seconds." → "Deals periodic damage that ignores armor every 2 seconds."
2. "On end, if still burning, deals damage (higher level → more damage)." → "If the entity is on fire when the effect expires, deals damage based on remaining fire ticks (higher level → more damage)."
3. "Reduces incoming damage by <b>level</b> (half hearts)." → "Reduces incoming damage by <b>0.5 × level</b> hearts."
4. "Negates fall damage and bounces entity upward (higher level → more horizontal push)." → "Negates fall damage and bounces entity upward upon landing (higher level → more momentum upon landing)."
5. "Increases lightning and shock damage by <b>3 × level</b> (stacks to III)." → "Increases lightning and shock damage by <b>3 × level</b>."

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

**Edge Cases:**
- If page lacks English parentheses name: ask user for clarification
- If scrape result is empty: report and stop
- For network/parse failure: skip that page and report in summary
- Never fabricate effect data - if translation is uncertain, ask the user

---

## OTHER IMPORTANT FILES

### data/links.json
- Mod name → effects source URL mapping
- Same ordering as effects.json (Minecraft first, then alphabetical)
- Update when adding new mods
- Update links to reflect the latest "effects sitemap" page used

### scripts/validate_effects.py  
- Validates: ordering, duplicates, formula formatting, description length, tags
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
- Convert time units: `秒` = seconds, `每两秒` = every <b>2 seconds</b>  
- Convert damage units to hearts when possible
- Preserve percentage values as-is
- Ask for clarification if translation uncertain
- Use existing formula patterns for consistency

**Common patterns:**
- `每两秒造成一次伤害` → `"Deals periodic damage every <b>2 seconds</b>"`
- Scaling indicators → `(higher level → more damage)`
- Multiple effects → separate with " and "

**Detailed page interpretation:**
- Description is usually the text below the effect name, above the ToC
- If both short and long descriptions exist, use the longer one
- Potency = level, highest potency in the list = maxLevel
- If no potency info found, default to maxLevel = 1
- Consider helpful user comments that provide additional effect details

---

## QUALITY CONTROL CHECKLIST

Before completing any effects.json modification:
- [ ] Alphabetical ordering maintained
- [ ] No duplicate effect names globally
- [ ] All descriptions ≤125 characters
- [ ] Formulas, effect names and ticking speed properly wrapped in `<b>`
- [ ] Tags include exactly one type + optional scaling
- [ ] Validation script executed successfully
- [ ] Summary provided in exact required format

**If validation fails:** Fix issues immediately, don't proceed without clean validation.
- [ ] Validation script executed successfully
- [ ] Summary provided in exact required format

**If validation fails:** Fix issues immediately, don't proceed without clean validation.
