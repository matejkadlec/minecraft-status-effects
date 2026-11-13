# Agent Information

Minecraft Status Effects (project name `status-effects`): an interactive database of vanilla
and modded Minecraft status effects (mob effects) per Minecraft version, live at
https://effects.matejkadlec.cz. A FastAPI app renders the page and serves a small JSON
API and the exports; the frontend is plain HTML, CSS and vanilla JavaScript (ES modules)
without a build step.

`CLAUDE.md` is a symlink to this file.

## Structure

```
data/effects.json        The database (schema version 2), see "Data" below
data/mods.json           Mod registry: display name, link, navigation group; referencedMods
data/draft-effects.json  Effects that exist but couldn't be verified yet (not shown on the site)
src/status_effects/
  config.py              Paths, site URL, the version buckets (VERSIONS, DEFAULT_VERSION)
  data.py                Loading and validating the data, resolving a record for a version
  pages.py               Payload for the frontend, mod navigation groups, SEO texts, JSON-LD
  export.py              CSV / XLSX (theme-colored) / JSON exports
  assets.py              Cache-busting asset URLs, safe HTML of descriptions and sources
  app.py                 Routes, security and cache headers, static files from public/
  __main__.py            `python -m status_effects` (uvicorn)
  templates/             index.html, the legal pages (license, privacy) and 404 (Jinja2)
public/                  Everything served as static files (and nothing else is)
  css/                   theme.css (variables), base, sidebar, toolbar, table, dialog, legal, fonts
  js/                    app.js (entry), logic.js (pure table logic), table.js, nav.js, ui.js, storage.js
  img/, fonts/           WebP images, OG image, self-hosted Montserrat (OFL.txt)
tests/                   pytest (data rules, pages, API, exports), js/ (node --test)
tests/effect_rules.py    The writing rules for records; also a CLI linter
run.sh                   Runs everything without activating the venv (see "Running")
Dockerfile, compose.yml  Production image and stack (see "Deployment")
requirements.lock        Exact, hashed dependencies of the production image
deploy/                  Server provisioning and the forced deploy command
```

## Running

- `./run.sh` – dev server with auto-reload on port 8000, bound to 0.0.0.0 (reachable from
  Windows when running in WSL). Creates `venv/` and installs the project on first run and
  whenever `pyproject.toml` changes. Any `python -m status_effects` option works
  (`./run.sh --port 8080`).
- `./run.sh test` – pytest, then the JavaScript tests if Node.js is installed.
- `./run.sh lint` – ruff and the effect linter on `data/effects.json`.
- `./run.sh prod` – no reload, 2 workers, `--proxy-headers`, binds 127.0.0.1 (put it behind
  a reverse proxy that terminates TLS).
- Data, templates, CSS and JS changes show up on a browser refresh; data files are reloaded
  automatically when their mtime changes.
- Python 3.12+, dependencies in `pyproject.toml` (FastAPI, uvicorn, Jinja2, openpyxl; dev:
  pytest, httpx, ruff).
- `docker compose up --build --wait web` builds and starts the production image alone (no
  port is published; add `-p`/`ports` yourself to open it in a browser).

## Versions

- The version dropdown lists buckets: `1.20.x`, `1.21.x`, `26.1.x`, `26.2.x`, `26.3.x`
  (`config.VERSIONS`). The default is `1.20.x` (`config.DEFAULT_VERSION`).
- Modded 1.20.x means the 1.20.1 build of a mod (Forge), 1.21.x means 1.21.1 (NeoForge) when
  it exists, 26.x the latest build for that drop.
- Adding a version: add it to `config.VERSIONS` (in order), add the version to the records
  that exist there, and add `changes` where an effect behaves differently. The dropdown,
  sitemap, canonical URLs, API and tests pick it up automatically.
- The selected version is in the URL (`?version=1.21.x`, omitted for the default) and in
  localStorage; the server renders the requested version, the frontend fetches others from
  `/api/effects?version=...`.

## Data

### Record schema (`data/effects.json` → `effects[]`)

```json
{
  "id": "alexs-caves-irradiated",
  "mod": "Alex's Caves",
  "effect": "Irradiated",
  "registryId": "alexscaves:irradiated",
  "versions": ["1.20.x"],
  "since": "1.20.5",
  "maxLevel": "V",
  "type": "negative",
  "unreliable": true,
  "description": "Prevents all healing. <b>Level II+</b> additionally deals <b>1 damage</b> every ...",
  "source": "Nuclear Furnace/Bomb explosions, holding radioactive items, eating Radgill",
  "changes": { "1.21.x": { "description": "...", "maxLevel": "III" } }
}
```

- `id`: `<mod slug>-<effect slug>` (lowercase, hyphens, no apostrophes, `&` → `and`). It is
  the row's HTML id and URL hash (`/#alexs-caves-irradiated`), so keep it stable.
- `registryId`: the game's id (`namespace:path`); `effect`: the name from the mod's `en_us.json`.
- `versions`: every bucket where the effect exists, in bucket order.
- `since` (optional): first exact release when it's later than the bucket's first release
  (e.g. vanilla Oozing exists in 1.20.x only from 1.20.5). Shown as a badge in that bucket.
- `maxLevel`: Roman numeral `I`–`X`, the highest level obtainable in survival (with mods).
  Never lower an existing value; cap at `X`.
- `type`: `positive` or `negative`. The `scaling` tag is derived (maxLevel > I).
- `unreliable` (only `true`): buggy effect or unconfirmed behaviour; shown as ⚠️.
- `changes` (optional): fields that differ from a later bucket on (`effect`, `maxLevel`,
  `type`, `unreliable`, `description`, `source`). A change applies to its bucket and every
  later one until changed again; it must actually change something.
- Base fields describe the first version in `versions`.

### File rules (enforced by tests)

- Order: Minecraft first (by effect name), then mods alphabetically, effects alphabetically
  within a mod (case-insensitive). Ids are unique; effect names are unique within a mod and
  version (use a suffix like "Rampage (Light)" for same-named variants).
- Every `mod` is in `data/mods.json` and every registered mod is used. `mods.json` is sorted
  the same way; `group` puts a mod into a collapsible navigation group (mods without a group
  and with fewer than 3 effects in a version go to "Other"). `referencedMods` lists other mod
  names that may appear in italics in sources.

### Description rules

- Only `<b>`: for effect names, every number/formula that comes from the effect, and time
  intervals ("every <b>2 seconds</b>", "every <b>second</b>"); "second(s)" is always bold.
- Formulas: `<b>2 × level</b>`, `<b>level</b>` (not `1 × level`), `<b>9 + (3 × level)</b>`,
  `<b>level + 2</b>`, exponential `<b>2^level</b> (2 / 4 / 8)` with the values. A formula ends
  its bold span or is followed by the time unit. Every `+` is inside `<b>` ("<b>Level II+</b>").
- maxLevel I effects never mention the effect level or "higher level".
- Third person ("the entity", "the player", "mobs"), no "you". Damage in game points
  ("<b>1 damage</b>" = half a heart), healing and health in whole hearts.
- Without an exact formula a scaling effect gets "(higher level → stronger effect)"; with a
  formula it doesn't. Use "→", never "->". No "(stacks to X)", no "&", no unnecessary hyphens,
  avoid "similar to X". Short (aim for ≤ 200 characters, hard limit 300), precise.

### Source rules

- Only `<i>`, and only for other mods' names: "Blessed items from <i>Dungeons and Combat</i> mod".
  Same-mod things are named directly ("Frilled Shark attacks", "spells from the mod",
  "Angel Wings spell from the mod", "rituals from the mod").
- Potions: "Potion/Arrow/Charm of X" for brewable potions, "Potion/Arrow/Charm/Bamboo Spikes
  of X" for brewable harmful ones, "Potion/Arrow of X" for loot-only potions; never list
  Splash/Lingering. Group shared parts ("Item1/Item2 of Strength").
- Shorthands: "Delights" (≥ 2 foods from Delight mods), "Affix Items" (Apotheosis affixes),
  "Unique Weapons" (Simply Swords), "armor sets from <i>Mod</i> mod".
- Unknown: `<i>To be added.</i>`; not obtainable in survival: `<i>Unavailable.</i>`.

### Researching effects

- Existence per version: read the released jars. Modrinth API
  (`https://api.modrinth.com/v2/project/<slug>/version`) gives the files per game version;
  the jar's `assets/<ns>/lang/en_us.json` lists `effect.<ns>.<id>` names (some mods use other
  keys, e.g. Alex's Mobs `alexsmobs.potion.*`, so check the registry class too). Ranged HTTP
  requests can read single entries without downloading the whole jar. Vanilla: the client jar
  from Mojang's version manifest.
- Behaviour: the mod's source code (effect classes, `applyEffectTick`, attribute modifiers,
  event handlers using `hasEffect`); 20 ticks = 1 second, level = amplifier + 1. Without public
  source: decompile (Vineflower), the mod's wiki, or mcmod.cn. Vanilla: minecraft.wiki
  (`?action=raw`, the History sections).
- Unverifiable effects go to `data/draft-effects.json`. Purely internal effects (hidden
  cooldown markers) are left out.
- After editing: `python tests/effect_rules.py data/effects.json` (or `./run.sh lint`), then
  `./run.sh test`.

## Frontend

- The server renders every row of the selected version (for crawlers and no-JS visitors) and
  embeds the same data as JSON (`#app-data`); `app.js` takes over and renders only the
  current page. Description/source HTML in the payload is already escaped by
  `assets.format_text` (only `<b>`, `<i>`, the level exponent and arrow spans remain).
- `logic.js` has no DOM access (search, filters, sorting, pagination) and is tested with Node.
- State: version and search in the URL (`?version=…&search=…`, hash = effect id); version,
  search, quick filters, rows per page, sidebar state, theme and "Ignore filters" in
  localStorage under `se-*` keys (listed on the privacy page; update it when adding a key).
- Search: every word must match (mod, effect, max, description, tags, source); "quotes" match a
  phrase. Sorting: click a header, Shift+click adds a column. `/` focuses the search, Ctrl+B
  (⌘B) collapses the sidebar (a drawer below 900px). Exports post the ids of the filtered,
  sorted table (or GET the whole version with "Ignore filters").
- Table columns use `table-layout: fixed` with widths that depend only on the available width
  (container queries on `.content`), so filtering and paging never shift the columns. Below
  760px of content width the rows become cards.
- Themes: light (blue) and dark (gold); colors only through the variables in `theme.css`.
  Test UI changes in both themes, in table and card layout. Respect `prefers-reduced-motion`.
- CSP allows only same-origin resources; the inline script in `_head.html` is allowed by its
  hash, which `app.py` computes from the templates at startup – keep it a plain `<script>`.
- CSS section comments:

  ```css
  /*----------------*
   * Section header *
   *----------------*/
  ```

## SEO

- The public address is `config.SITE_URL` (default `https://effects.matejkadlec.cz`, overridable
  with the `SITE_URL` environment variable); canonical URLs, the sitemap, `robots.txt`, Open
  Graph tags, JSON-LD and the export metadata are built from it.
- Canonical URL per version (`/` for the default, `/?version=…` otherwise), title and meta
  description per version, Open Graph/Twitter tags with `img/og-image.jpg` (1200×630),
  JSON-LD `WebSite` + `Dataset` (with CSV/JSON download links). `sitemap.xml` and
  `robots.txt` are generated by `app.py`.
- Assets in templates go through `asset()` (adds `?v=<content hash>`, cached for a year), so a
  changed file automatically gets a new URL; files referenced without it (from CSS, the font
  preload) revalidate with ETag. Images are WebP, the OG image is a JPEG.

## Conventions

- Keep the look and behaviour of the site; refactor without visible side effects unless asked.
- No change-log comments in code ("Changed…", "Added…"); comments explain the code.
- Don't use "&" in prose (write "and") unless it's part of a name.
- README: short, current state only. Update this file when the structure or workflows change.

## Deployment

Production is https://effects.matejkadlec.cz on `matejkadlec-cz1`, a FORPSI server shared with
other sites. This project is one tenant there: change only what is listed below and ask the
owner before anything host-wide (packages, SSH daemon, firewall, other accounts).

- **Tenant**: the locked account `se-deploy` (no sudo, no extra groups) with its own rootless
  Docker daemon (a user service kept running across reboots by lingering),
  `/srv/status-effects/` (repository mirror, releases, state) and `/etc/status-effects/`.
  `deploy/provision-server.sh` creates all of it and can be run again.
- **Stack** (`compose.yml`): `web` is the image from `Dockerfile` (base image pinned by digest,
  dependencies from `requirements.lock`, unprivileged user, read-only, no access log, no
  published port); `cloudflared` (profile `tunnel`) is the connector of the Cloudflare Tunnel
  `status-effects-production`, whose public hostname `effects.matejkadlec.cz` points to
  `http://web:8000`. Containers restart on their own (`restart: unless-stopped`).
- **Secret**: only the tunnel token, in `/etc/status-effects/cloudflared-token` (owner
  `se-deploy`, mode 0600), mounted as a Compose secret. It never goes into git, GitHub, the
  image or a chat. The connector is started once that file exists. Cloudflare (tunnel, DNS) is
  managed by the owner in the dashboard.
- **Deploy**: a push to `master` runs `tests.yml`; when it passes, `deploy.yml` connects with
  the SSH key of the GitHub environment `production` (secret `DEPLOY_SSH_PRIVATE_KEY`, variables
  `DEPLOY_SSH_HOST`, `DEPLOY_SSH_PORT`, `DEPLOY_SSH_USER`, `DEPLOY_SSH_HOST_KEY`; the
  environment only admits `master`). On the server that key can only run the root-owned
  `/usr/local/libexec/status-effects-deploy` (a copy of `deploy/status-effects-deploy`) with
  `deploy <commit>` or `status`. The command fetches the commit from GitHub itself, requires it
  to be on `master`, builds the image, replaces the containers (a few seconds without the
  site) and goes back to the previous release when the new one doesn't become healthy.
- **By hand**: "Run workflow" on the Deploy workflow redeploys `master`. On the host:
  `sudo -u se-deploy /usr/local/libexec/status-effects-deploy status`, or
  `... deploy <commit> [<branch>]` to roll back or to deploy a pushed branch.
- **Changing the deploy command or the key** is deliberately not automated: copy `deploy/` to
  the host and run `sudo ./provision-server.sh ./status-effects-deploy ./deploy-key.pub`.
- **Dependencies**: after changing the dependencies in `pyproject.toml` (or to pick up
  updates) regenerate the lock and commit it:
  `uv pip compile pyproject.toml --generate-hashes --python-version 3.12 --python-platform x86_64-manylinux_2_28 --no-header -o requirements.lock`.
  Update the base image and `cloudflared` by changing the tag and the digest together.
