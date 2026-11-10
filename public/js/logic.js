/*------------------------------------------------------------*
 * Pure table logic: search, filters, sorting and pagination. *
 * No DOM access, so it can be unit tested with Node.         *
 *------------------------------------------------------------*/
export const COLUMNS = ["mod", "effect", "maxLevel", "description", "tags", "source"];
export const DEFAULT_SORT = Object.freeze([
  ["mod", "asc"],
  ["effect", "asc"],
]);
export const DEFAULT_FILTERS = Object.freeze({ vanilla: false, scaling: true, positive: true, negative: true });
export const PAGE_LENGTHS = [25, 50, 75, 100];

const ENTITIES = { "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&#x27;": "'" };

/** Plain text of an HTML snippet produced by the server (only simple inline tags and entities). */
export function htmlToText(html) {
  return String(html)
    .replace(/<[^>]*>/g, "")
    .replace(/&(?:amp|lt|gt|quot|#39|#x27);/g, (entity) => ENTITIES[entity])
    .replace(/\s+/g, " ")
    .trim();
}

/** Adds the derived fields used for searching and sorting. */
export function prepareEffects(effects) {
  return effects.map((effect, index) => {
    const descriptionText = htmlToText(effect.description);
    const sourceText = htmlToText(effect.source);
    const tags = effect.scaling ? `${effect.type} scaling` : effect.type;
    return {
      ...effect,
      index,
      descriptionText,
      sourceText,
      tags,
      haystack: [effect.mod, effect.effect, effect.maxLevel, descriptionText, tags, sourceText, effect.since ?? ""]
        .join(" \u0000 ")
        .toLowerCase(),
    };
  });
}

/**
 * Turns the search box value into a matcher.
 * Words are matched independently (all must occur); "quoted text" must occur as a phrase.
 */
export function parseQuery(query) {
  const value = String(query ?? "").trim().toLowerCase();
  if (!value) return [];
  const terms = [];
  const pattern = /"([^"]+)"|(\S+)/g;
  let match;
  while ((match = pattern.exec(value)) !== null) {
    const term = (match[1] ?? match[2]).replace(/\s+/g, " ").replace(/^"|"$/g, "").trim();
    if (term) terms.push(term);
  }
  return terms;
}

export function matchesQuery(effect, terms) {
  return terms.every((term) => effect.haystack.includes(term));
}

export function filterEffects(effects, { query = "", filters = DEFAULT_FILTERS } = {}) {
  const terms = parseQuery(query);
  return effects.filter((effect) => {
    if (!filters.vanilla && effect.mod === "Minecraft") return false;
    if (effect.type === "positive" ? !filters.positive : !filters.negative) return false;
    if (effect.scaling && !filters.scaling) return false;
    return terms.length === 0 || matchesQuery(effect, terms);
  });
}

function compareText(a, b) {
  return a < b ? -1 : a > b ? 1 : 0;
}

const SORT_KEYS = {
  mod: (effect) => (effect.mod === "Minecraft" ? "\u0000" : effect.mod.toLowerCase()),
  effect: (effect) => effect.effect.toLowerCase(),
  maxLevel: (effect) => effect.level,
  description: (effect) => effect.descriptionText.toLowerCase(),
  tags: (effect) => (effect.type === "positive" ? 0 : 1),
  source: (effect) => effect.sourceText.toLowerCase(),
};

/** Stable multi-column sort; ties keep the server's default order. */
export function sortEffects(effects, sortState = DEFAULT_SORT) {
  const keys = sortState.filter(([column]) => column in SORT_KEYS);
  return [...effects].sort((a, b) => {
    for (const [column, direction] of keys) {
      const key = SORT_KEYS[column];
      const result = compareText(key(a), key(b));
      if (result !== 0) return direction === "desc" ? -result : result;
    }
    return a.index - b.index;
  });
}

/**
 * New sort state after clicking a column header.
 * Click: sort by that column only (toggles the direction if it's already the primary column).
 * Shift+click: add the column as the next sort key, or toggle its direction if it's already sorted.
 */
export function nextSortState(sortState, column, additive = false) {
  const current = sortState.find(([col]) => col === column);
  if (additive) {
    if (!current) return [...sortState.map((entry) => [...entry]), [column, "asc"]];
    return sortState.map(([col, dir]) => [col, col === column ? (dir === "asc" ? "desc" : "asc") : dir]);
  }
  if (sortState.length > 0 && sortState[0][0] === column) {
    return [[column, sortState[0][1] === "asc" ? "desc" : "asc"]];
  }
  return [[column, "asc"]];
}

export function paginate(total, page, perPage) {
  const totalPages = Math.max(1, Math.ceil(total / perPage));
  const current = Math.min(Math.max(1, Math.trunc(page) || 1), totalPages);
  const start = total === 0 ? 0 : (current - 1) * perPage;
  const end = Math.min(start + perPage, total);
  return { page: current, totalPages, start, end };
}

/**
 * Page buttons to show: always the first and the last page, a window around the current page
 * and "…" for gaps (a gap of a single page shows that page instead).
 */
export function pageItems(current, totalPages) {
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1);
  let from = Math.max(2, current - 1);
  let to = Math.min(totalPages - 1, current + 1);
  if (current <= 3) {
    from = 2;
    to = 4;
  } else if (current >= totalPages - 2) {
    from = totalPages - 3;
    to = totalPages - 1;
  }
  const items = [1];
  if (from > 3) items.push("…");
  else if (from === 3) items.push(2);
  for (let page = from; page <= to; page += 1) items.push(page);
  if (to < totalPages - 2) items.push("…");
  else if (to === totalPages - 2) items.push(totalPages - 1);
  items.push(totalPages);
  return items;
}

/** "Showing 1 to 25 of 208 records" */
export function infoText(start, end, total) {
  if (total === 0) return "Showing 0 to 0 of 0 records";
  return `Showing ${start + 1} to ${end} of ${total} ${total === 1 ? "record" : "records"}`;
}

/** Reads the filters saved by this or the previous version of the site. */
export function normalizeFilters(saved) {
  const filters = { ...DEFAULT_FILTERS };
  if (!saved || typeof saved !== "object") return filters;
  const legacy = { filterVanilla: "vanilla", filterScaling: "scaling", filterPositive: "positive", filterNegative: "negative" };
  for (const [key, value] of Object.entries(saved)) {
    const name = legacy[key] ?? key;
    if (name in filters && typeof value === "boolean") filters[name] = value;
  }
  return filters;
}
