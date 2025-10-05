# AGENT INSTRUCTIONS

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
- Before running commands, use `source venv/bin/activate` to activate venv
- To run local server for testing: `python run.py 8001` (port 8000 is reserved)
- Terminals always open in project root - no need for full paths
- Use `rm` to delete obsolete files
- Stop local server after testing to free the port
- **Development workflow**: JS/CSS/HTML changes are visible immediately on browser refresh (Ctrl+F5) - no server restart needed

### 6. COMPONENT INTEGRATION - CRITICAL FOR UI CHANGES
- **Test cross-component compatibility**: When modifying navigation, filters, search, or pagination, verify all components work together seamlessly
- **Example lesson**: Navigation links initially failed when target effects were on different table pages - always test pagination integration
- **Update interconnected systems**: Changes to filtering must update navigation availability, pagination must rebuild nav links, search must work with both

### 7. ASSET PRELOADING - PREVENT THEME FLASHING  
- **Preload theme-specific assets**: All images/gifs must be properly preloaded to prevent light→dark mode flashing on page load
- **CSS-based theme switching**: Use CSS show/hide patterns (like loading spinners) rather than JavaScript asset swapping when possible
- **Test theme consistency**: Always verify assets load correctly in both light and dark modes without visual flashing

### 8. DUAL-THEME VISUAL DESIGN
- **Test both themes**: Ensure new UI elements look good in both light and dark modes
- **Avoid theme blending**: Don't use the same CSS variable for both themes if it causes elements to blend into backgrounds
- **Theme-specific values**: Use different colors/opacities per theme when needed for proper contrast and visibility

---

## PROJECT OVERVIEW

**What this is:** Minecraft status effects website - vanilla + modded effects database with interactive features

**Current Features:**
- 📊 **Multi-column sorting** (single/multi-column with Shift+click)
- 📱 **Horizontal scrolling** for smaller screens
- 🔍 **Advanced filtering** (type, mod, scaling effects)
- 📖 **Pagination** with customizable page sizes
- 🌓 **Theme switching** (light/dark modes)
- 🎯 **Navigation** (jump to specific mods/effects)
- 🔍 **Real-time search** (anything in the table)
- 📥 **Data export** (CSV, Excel, JSON with theme-aware styling)

**Tech stack:** HTML, CSS, JavaScript (vanilla), Python 3.12 (Bottle framework), Docker (production only)

**Key files:**
- `index.html` - main page with effects table
- `data/effects.json` - effects database (CRITICAL FILE)
- `data/links.json` - mod links/sources
- `scripts/validate_effects.py` - validation script (RUN AFTER CHANGES)
- `TODO.md` - feature requests and development roadmap (JIRA-style tickets)
- `.github/workflows/` - CI/CD workflows

**Legal pages:** `license/index.html`, `privacy-policy/index.html` (separate, no JS)

---

## PROJECT STRUCTURE
- IMPORTANT: Keep the structure updated with each new/deleted/moved file/folder.

```
minecraft-status-effects/
├── .github/
│   └── workflows/
│       ├── deploy.yml
│       └── validate-effects.yml
├── css/ (stylesheets)
├── data/
│   ├── draft-effects.json  
│   ├── effects.json ⚠️ CRITICAL
│   └── links.json
├── export/ (theme-aware export functionality)
│   ├── export_handler.py
│   ├── export_formatter.py
│   ├── generate_static.py
│   └── files/ (pre-generated export files)
├── img/ (icons, logos, loading gifs)
├── js/ (modular JavaScript files)
├── license/ & privacy-policy/ (legal pages)
├── mcmod/ (mcmod.cn scraping scripts)
│   ├── scrape_effect (scrapes individual effect page)
│   ├── scrape_effect_list (scrapes effects list page)
│   └── effect_urls/ (generated .txt files with URLs)
├── scripts/
│   ├── sort_effects.py
│   └── validate_effects.py ⚠️ CRITICAL
├── index.html (main page)
├── run.py (Python server)
├── sitemap.xml ⚠️ KEEP UPDATED
├── robots.txt (SEO)
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
   - If duplicate found, SKIP and report in summary, with the exception for Apotheosis mod, in that case, remove the Apotheosis record and put the effect under the new mod group
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
  "description": "As short as possible but also clear description ≤200 chars (for complex effects find some middleground between length and readibility).",
  "source": "Source of any kind, i.e. potion, being hit by some mob, wearing some armor set. Supports HTML tags like <b>, <i>, <u>, <br>."
}
```

### GENERAL RULES
- Never update existing maxLevel to lower value, different mods makes the maxLevel different for an effect, and we care about the highest level possible in survival, so if somehow we got i.e. "EffectX" maxLevel is "V", it will stay "V", even if some page says max is IV.
  - I.e. our "Strength" effect maxLevel is "III", even though vanilla MC wiki says "II"
  - That's because some mod can increase the vanilla effects maxLevel, and we cary about the modded version, not vanilla.
- Do not use "&" symbol, unless it's literally in some mod/effect/item name. Other than that, always use "and".

### DESCRIPTION RULES - FOLLOW EXACTLY

**Formatting:**
- Supports HTML bold tags `<b>` (`<i>`, `<u>` and `<br>` are supported as well, but currently unused)
- Use `<b>` for effect names, all kind of formulas and time intervals; do not use HTML tags for anything else
- Always wrap time intervals in `<b>`, e.g., "every <b>2 seconds</b>" or "every <b>second</b>"
- Formulas: `<b>2 × level</b>` (linear) or `<b>2^level</b>` (exponential)
  - If the multiplier is 1, write simply as `level`, not `1 × level`
- For exponential, add actual values: `<b>2^level</b> (2 / 4 / 8)`
- Multiple benefits: separate with " and " (not bold)
- Avoid using "You" or other pronouns; "Causes you to move faster" -> "Causes [entity, player, mob] to move faster"
  - Use entity if both player and mobs can be affected, use player if only players can be affected, and use mob if only mobs can be affected

**Content rules:**
- Use "damage"/"hearts" not "health" 
- Convert to whole hearts, not "half hearts"
- No "(stacks to X)" due to Apotheosis compatibility
- Add "(higher level → more damage/effect)" for scaling effects, but ONLY if we don't have exact formula/numbers, in that case, use the formula and don't add "(higher level → more damage/effect)".
- Don't use hyphens unless necessary (creative-like flight → creative flight)
- Avoid using phrases like "similar to X" or "like X" where X is another effect
  - Example: avoid "similar to Wither" or "like Wither" as it's unnecessary
  - Exceptions for special cases exists, i.e. if the effect is changing the color of your hearts, or i.e. is cancelled by touching water (like fire), using comparison is valid

### CORRECTIONS EXAMPLES
Examples of descriptions that needed correction (learning from past mistakes):

Your initial → Corrected version
1. "Deals armor-ignoring damage every 2 seconds." → "Deals periodic damage that ignores armor every <b>2 seconds</b>."
2. "On end, if still burning, deals damage (higher level → more damage)." → "If the entity is on fire when the effect expires, deals damage based on remaining fire ticks (higher level → more damage)."
3. "Reduces incoming damage by <b>level</b> (half hearts)." → "Reduces incoming damage by <b>0.5 × level</b>."
4. "Negates fall damage and bounces entity upward (higher level → more horizontal push)." → "Negates fall damage and bounces entity upward upon landing (higher level → more momentum upon landing)."
5. "Increases lightning and shock damage by <b>3 × level</b> (stacks to III)." → "Increases lightning and shock damage by <b>3 × level</b>."

### TAGS RULES
- **Required:** exactly one of `"positive"` or `"negative"`
- **Optional:** 
  - `"scaling"` if maxLevel ≥ 2
  - `"unreliable"` if description lacks crucial, effect description source is not trustwourthy, effect is buggy, etc.
    - This can be determined from description itself, or i.e. user comments which we are scraping from mcmod
- Decision based on overall effect benefit/harm

### SOURCE RULES
- Might be called "Cause" on some sites, we use "Source"
- Supports HTML italic tags `<i>` (`<b>`, `<u>` and `<br>` are supported as well, but currently unused)
- Sources must be divided by comma, short, and readable. 
- Use `<i>` for mod names; do not use HTML tags for anything else
- Use "<i>To be added.</i>" if I didn't provide you source of the source yet, and "<i>Unavailable.<i> if you can't find it where it should be.

**Saving space is crucial:**
- Group everything you can, while maintaning readability.
- If there are more items names ending with same string, i.e. "of Strength", use "Item1/Item2/Item3 of Strength".
- If there are more items names starting with same string, i.e. "Blessed, use "Blessed Item1/Item2/Item3".
- If source of some effect is Potion of X and Arrow of X, add "Charm" to it, and group it: "Potion/Arrow/Charm of X".
- If the effect can be obtained via two or more different Potions/Arrow/Charms, it will look like this: "Potion/Arrow/Charm of X/Y/Z".
  - With the exceptions of powerful Potions that give multiple effects, i.e. Potion of Divinite from Dungeons and Combat mod, these don't have charm variants
- Don't name every item type for effect, just use the default variant; "Potion/Splash/Lingering of Strength" → "Potion of Strength".
  - This mostly applies to Potions and Arrows, but can apply to anything
- If the effect can be obtained via two or more items from any mod which name contains string "delight", do not list any of them and use "Delights" instead
- If the effect can be obtained via two or more unique weapons from Simple Swords mod, do not list any of them and use "Unique Weapons" instead
- If the effect can be obtained via Apothesis affix, use "Affix Items"
- If the effect can be obtained via Apotheosis jewel/gem, use it without the "Cracked/Chipped/Flawed/Flawless/Perfect" prefix, just use the name of the jewel/gem.
- If the effect can be obtained via single magic mod spell, use "{spell_name} spell from <i>{magic mod name}</i> mod"
- If the effect can be obtained via two or more magic mod spells, use "spells from <i>{magic mod name}</i> mod"
  - Optionally, if the spells have common prefix, add it: "Poison spells from <i>{magic mod name}</i> mod"
- If the effect can be obtained via two or more tools/weapons/armor sets from a single mod, do not list any of them and use "tools/weapons/armor sets from <i>{mod_name}</i>" instead
- DO NOT add "from <i>{mod name}</it> mod" to the sources if whatever is before the "from" is from the same mod that the effect is, only use "from <i>{mod name}</it> mod" for cross references/integrations between mods. If the item/entity is from the same mod as the effect, just name it, don't add the "from mod" part.
  - With the exceptions of Spells, Rituals, and similar unique mechanics. Unique item or entity is not a mechanics.

**Examples of various long, well written sources:**
1. Potion/Arrow/Charm/Bamboo Spikes of Slowness, Potion/Arrow of the Turtle Master/Gigant, Alchemy Flask/Vial, Delights, Affix Items, Withering Dross, Rotten Hammer, Stray's arrow, Earthquake spell from <i>Iron Spells'n'Spellbooks</i> mod, Suspicious Stew
2. Potion/Arrow/Charm of Haste, Potion/Arrow of Divinite, Affix Items, Unique Weapons, Delights, Mask of Rage, Blessed items from <i>Dungeons and Combat</i> mod, Beacon, Suspicious Stew
3. Potion/Arrow/Charm of Night Vision, Alchemy Flask/Vial, Delights, Luminous Jelly, Glittering Grenadine, Neptunium armor set (only while in water), Forlorn Harbinger armor set's ability, Suspicious Stew

### AUTOMATED MCMOD.CN WORKFLOW

**Trigger:** User says "add" + mcmod.cn URL

**Process:**
1. Activate venv `source venv/bin/activate`
2. Run `python mcmod/effects_lists/scrape_effect_list.py <url>` to extract individual effect URLs → saves to `mcmod/effect_urls/<mod_name>.txt`
3. Run `python mcmod/effects/scrape_effect.py <effect_url>` for each URL to extract:
   - English name from text inside parenthesis in <a> of 5th <li> of <ul> inside <div class="common-nav">
   - Effect description from item-text section
   - Command information and mod namespace
   - Table data for level information
   - User comments for additional context
   - Determine maxLevel from potency indicators (I/II/III/IV/V) or table data
   - Determine effect type (positive/negative) from classification or description analysis
4. Process extracted data:
   - Create compressed description following DESCRIPTION RULES
   - Create formatted source following SOURCE RULES
   - Set type (positive/negative) and tags
   - Build ID: `mod-name-effect-name` (lowercase, hyphens)
5. Check for duplicates (skip if effect name exists)
6. Insert maintaining alphabetical order
7. Run validator once at end
8. Provide exact summary format

**Quality checks before summary:**
- Ordering preserved
- No duplicate effect names  
- Descriptions formatted correctly and ≤200 chars
- Tags include type + optional scaling
- Summary uses exact format

**Edge Cases:**
- If page lacks English parentheses name: ask user for clarification
- If scraping result is empty: report and stop
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
- **CRITICAL:** Run after every effects.json change
- **10 validation checks in order:**

**General Checks (by importance):**
  1. **No empty fields check**
     - Ensures all required fields are present and non-empty
     - Required fields: `mod`, `id`, `effect`, `maxLevel`, `type`, `tags`, `description`, `source`
     - Checks for: missing fields, empty strings, empty lists, null values
     - Function: `validate_no_empty_fields()`
  
  2. **General text formatting check**
     - Applies to: `mod`, `effect`, `description`, `source` fields
     - Rules enforced:
       - No double spaces (e.g., "foo  bar" is invalid)
       - No leading/trailing whitespace
       - Space required after comma, not before (e.g., "a, b" not "a,b" or "a , b")
     - HTML tags are excluded from comma spacing checks to avoid false positives
     - Function: `validate_text_formatting()`
  
  3. **Duplicate effect name check**
     - Effect names must be globally unique across all mods
     - Prevents conflicts in table rendering and navigation
     - Inline check in `main()`
  
  4. **Effect ordering check**
     - Minecraft effects first (sorted alphabetically by effect name)
     - Then mod effects (sorted alphabetically by mod name, then by effect name within each mod)
     - Ensures consistent table presentation
     - Inline check in `main()`

**Column-Specific Checks (in table column order):**
  5. **Max level format check**
     - Must be a Roman numeral from I to X (case-sensitive)
     - Valid values: I, II, III, IV, V, VI, VII, VIII, IX, X
     - No Arabic numerals (1, 2, 3) or other formats accepted
     - Function: `validate_max_level_format()`
  
  6. **Description HTML tag usage check**
     - Formulas must be wrapped in `<b>` tags:
       - `^level` (exponential scaling)
       - `× level` (linear scaling)
     - Time units must be wrapped in `<b>` tags:
       - "second", "seconds", "second(s)"
     - Formula positioning rules:
       - Must be at end of bold span OR followed by time unit
       - Valid: `<b>2 × level</b>`, `<b>1</b> every <b>2 seconds</b>`
       - Invalid: `<b>2 × level damage</b>` (formula not at end)
     - Function: `validate_description_html_tags()`
  
  7. **Tags validation check**
     - Must contain exactly one type tag: `"positive"` OR `"negative"` (not both)
     - Must contain `"scaling"` tag if maxLevel > I
     - Tags field must be a list (array)
     - Inline check in `main()`
  
  8. **Source potion grouping check**
     - Use simplified format: `Potion/Arrow/Charm of X`
     - Forbidden: `Potion/Arrow/Splash/Lingering` (too verbose)
     - Forbidden: `Potion/Splash/Lingering` (redundant variants)
     - Forbidden: `/Splash/` or `/Lingering/` anywhere in source
     - Modded potions without Charm variants are allowed (e.g., `Potion/Arrow of Tenacity`)
     - Function: `validate_source_potion_grouping()`
  
  9. **Source HTML tag usage check**
     - Only `<i>` tags allowed, and ONLY for mod names
     - Forbidden italic uses:
       - Mob names (e.g., Tarantula Hawk, Warden, Elder Guardian)
       - Item names, weapon names, armor names
       - Descriptions or attack types
     - Special cases allowed: `<i>To be added.</i>`, `<i>Unavailable.</i>`
     - Maintains list of known mob names to catch common mistakes
     - Function: `validate_source_html_tags()`
  
  10. **Source special terms check**
      - Spell pattern validation:
        - Must follow: `X spell from <i>Iron Spells'n'Spellbooks</i> mod`
        - Or: `spells from <i>Iron Spells'n'Spellbooks</i> mod`
        - Allows optional whitespace before closing `</i>` tag
      - Ampersand usage:
        - Use "and" instead of "&" or "&amp;"
        - Exception: When part of mod/item name (inside `<i>` tags)
      - Function: `validate_source_special_terms()`

**Check Execution Order:**
- General checks run first (most fundamental → most specific)
- Column-specific checks follow table column order: mod → effect → maxLevel → description → tags → source
- Within source checks: grouping rules → HTML tags → special terms (general → specific)

**If adding new validation rules, also update:**
- This instruction file (AGENTS.md)
- .github/workflows/validate-effects.yml
- README.md

### sitemap.xml - SEO MAINTENANCE
- **ALWAYS update lastmod date** when making changes that affect the main page
- Update to current date format: `YYYY-MM-DD`
- Update when:
  - Adding new pages to the website
  - Making major content changes to existing pages
  - Updating effects.json with substantial additions
- Current structure includes: main page, license, privacy-policy
- If adding new routes/pages, add them to sitemap with appropriate priority:
  - Main page: priority="1.0", changefreq="daily"
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

## AUTOMATED DOCUMENTATION UPDATE WORKFLOW

**Trigger:** User prompt contains `"update arm"` (case insensitive, can be part of larger request)

**Process:**
1. Review entire codebase for changes since last documentation update
2. Update AGENTS.md:
   - Verify and update PROJECT OVERVIEW (features, tech stack, key files)
   - Update PROJECT STRUCTURE if files/folders added or removed
   - Add/update any important workflows or instructions discovered
   - Remove redundant or outdated information
   - Improve clarity and organization for AI agents
3. Update README.md:
   - Keep human-friendly, collaborator-focused style
   - Update feature lists to match current implementation
   - Verify installation/setup instructions are current
   - Maintain short, to-the-point descriptive style
   - Update dependencies and version badges if needed
4. Provide summary of changes made to both files

**Note:** This workflow ensures documentation stays synchronized with codebase evolution.

---

## AUTOMATED CLEANUP WORKFLOW

**Trigger:** User prompt contains `"do cleanup"` (case insensitive, can be part of larger request)

**Process:**
1. **CSS Cleanup:**
   - Remove redundant/overwritten styles (keep only the final/effective style)
   - Remove unnecessary comments (keep only structural/functional comments)
   - Identify and remove unused CSS classes
   
2. **JavaScript Cleanup:**
   - Remove unused functions, variables, and constants
   - Remove redundant comments (keep only functional documentation)
   - Check for dead code and unused imports
   
3. **Python Cleanup:**
   - Remove unused functions and imports
   - Clean up redundant comments
   - Verify all dependencies in requirements.txt are used
   
4. **Configuration Files:**
   - Check .yml workflow files for legacy/unused steps
   - Review run_tests.sh for outdated logic
   - Verify .gitignore covers all necessary patterns
   
5. **Optimization (optional):**
   - Identify poorly structured code
   - Suggest or implement performance improvements
   - Consolidate duplicate logic

6. Provide summary of all cleanup actions taken

**Note:** This workflow maintains code quality and removes technical debt. DO NOT modify .md, .html, .json, or .txt files during cleanup.

---

## QUALITY CONTROL CHECKLIST

Before completing any effects.json modification:
- [ ] Alphabetical ordering maintained
- [ ] No duplicate effect names globally
- [ ] All descriptions ≤200 characters
- [ ] Formulas, effect names and ticking speed properly wrapped in `<b>`
- [ ] Tags include exactly one type + optional scaling
- [ ] Validation script executed successfully
- [ ] Summary provided in exact required format

**If validation fails:** Fix issues immediately, don't proceed without clean validation.

