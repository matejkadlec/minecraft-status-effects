// Unit tests of the table logic (run with `node --test tests/js/`).
import assert from "node:assert/strict";
import { test } from "node:test";

import {
  DEFAULT_FILTERS,
  DEFAULT_SORT,
  filterEffects,
  htmlToText,
  infoText,
  nextSortState,
  normalizeFilters,
  pageItems,
  paginate,
  parseQuery,
  prepareEffects,
  sortEffects,
} from "../../public/js/logic.js";

const effects = prepareEffects([
  { id: "minecraft-poison", mod: "Minecraft", effect: "Poison", maxLevel: "II", level: 2, type: "negative", scaling: true,
    description: "Deals <b>1 damage</b> every <b>1.25 seconds</b>", source: "Potion of Poison, Cave Spider" },
  { id: "alexs-mobs-clinging", mod: "Alex's Mobs", effect: "Clinging", maxLevel: "I", level: 1, type: "positive", scaling: false,
    description: "Walk on ceilings", source: "Potion/Arrow/Charm of Clinging" },
  { id: "goety-acid-venom", mod: "Goety", effect: "Acid Venom", maxLevel: "II", level: 2, type: "negative", scaling: true,
    description: "Like <b>Poison</b> but affects undead &amp; more", source: "Servants from <i>Goety</i>" },
  { id: "aether-remedy", mod: "The Aether", effect: "Remedy", maxLevel: "I", level: 1, type: "positive", scaling: false,
    description: "Cures <b>Inebriation</b>", source: "White Apple" },
]);
const all = { ...DEFAULT_FILTERS, vanilla: true };
const ids = (list) => list.map((e) => e.id);

test("htmlToText strips tags and decodes entities", () => {
  assert.equal(htmlToText("a <b>b</b> &amp; &lt;c&gt; &#39;d&#39;"), "a b & <c> 'd'");
});

test("default filters hide vanilla effects", () => {
  assert.deepEqual(ids(filterEffects(effects)), ["alexs-mobs-clinging", "goety-acid-venom", "aether-remedy"]);
});

test("type and scaling filters", () => {
  assert.deepEqual(ids(filterEffects(effects, { filters: { ...all, negative: false } })), ["alexs-mobs-clinging", "aether-remedy"]);
  assert.deepEqual(ids(filterEffects(effects, { filters: { ...all, scaling: false } })), ["alexs-mobs-clinging", "aether-remedy"]);
});

test("search matches every word anywhere, quotes match a phrase", () => {
  assert.deepEqual(ids(filterEffects(effects, { query: "poison", filters: all })), ["minecraft-poison", "goety-acid-venom"]);
  assert.deepEqual(ids(filterEffects(effects, { query: "undead poison", filters: all })), ["goety-acid-venom"]);
  assert.deepEqual(ids(filterEffects(effects, { query: '"poison but"', filters: all })), ["goety-acid-venom"]);
  assert.deepEqual(ids(filterEffects(effects, { query: "SCALING negative", filters: all })), ["minecraft-poison", "goety-acid-venom"]);
  assert.deepEqual(ids(filterEffects(effects, { query: "  ", filters: all })).length, 4);
  assert.deepEqual(parseQuery(' a "b  c" '), ["a", "b c"]);
});

test("default sort puts Minecraft first, then mods and effects alphabetically", () => {
  const shuffled = [effects[3], effects[1], effects[2], effects[0]];
  assert.deepEqual(ids(sortEffects(shuffled, DEFAULT_SORT)), ["minecraft-poison", "alexs-mobs-clinging", "goety-acid-venom", "aether-remedy"]);
});

test("multi-column sort and stable ties", () => {
  const byLevel = sortEffects(effects, [["maxLevel", "desc"], ["effect", "asc"]]);
  assert.deepEqual(ids(byLevel), ["goety-acid-venom", "minecraft-poison", "alexs-mobs-clinging", "aether-remedy"]);
  const byTags = sortEffects(effects, [["tags", "asc"]]);
  assert.deepEqual(ids(byTags), ["alexs-mobs-clinging", "aether-remedy", "minecraft-poison", "goety-acid-venom"]);
});

test("clicking headers", () => {
  assert.deepEqual(nextSortState(DEFAULT_SORT, "mod"), [["mod", "desc"]]);
  assert.deepEqual(nextSortState(DEFAULT_SORT, "effect"), [["effect", "asc"]]);
  assert.deepEqual(nextSortState([["effect", "asc"]], "effect"), [["effect", "desc"]]);
  assert.deepEqual(nextSortState(DEFAULT_SORT, "source", true), [["mod", "asc"], ["effect", "asc"], ["source", "asc"]]);
  assert.deepEqual(nextSortState(DEFAULT_SORT, "effect", true), [["mod", "asc"], ["effect", "desc"]]);
});

test("pagination bounds", () => {
  assert.deepEqual(paginate(0, 3, 25), { page: 1, totalPages: 1, start: 0, end: 0 });
  assert.deepEqual(paginate(60, 3, 25), { page: 3, totalPages: 3, start: 50, end: 60 });
  assert.deepEqual(paginate(60, 9, 25), { page: 3, totalPages: 3, start: 50, end: 60 });
  assert.deepEqual(paginate(60, -2, 25).page, 1);
});

test("page buttons", () => {
  assert.deepEqual(pageItems(1, 5), [1, 2, 3, 4, 5]);
  assert.deepEqual(pageItems(1, 26), [1, 2, 3, 4, "…", 26]);
  assert.deepEqual(pageItems(13, 26), [1, "…", 12, 13, 14, "…", 26]);
  assert.deepEqual(pageItems(26, 26), [1, "…", 23, 24, 25, 26]);
  assert.deepEqual(pageItems(4, 9), [1, 2, 3, 4, 5, "…", 9]);
  assert.deepEqual(pageItems(5, 8), [1, "…", 4, 5, 6, 7, 8]);
  for (let total = 1; total <= 40; total += 1) {
    for (let page = 1; page <= total; page += 1) {
      const items = pageItems(page, total);
      assert.ok(items.includes(page) && items.includes(1) && items.includes(total), `${page}/${total}`);
      const numbers = items.filter((i) => i !== "…");
      assert.deepEqual(numbers, [...numbers].sort((a, b) => a - b), `${page}/${total}`);
      assert.ok(items.length <= 9, `${page}/${total}`);
    }
  }
});

test("info text", () => {
  assert.equal(infoText(0, 25, 208), "Showing 1 to 25 of 208 records");
  assert.equal(infoText(0, 0, 0), "Showing 0 to 0 of 0 records");
  assert.equal(infoText(0, 1, 1), "Showing 1 to 1 of 1 record");
});

test("filters saved by the old site are migrated", () => {
  assert.deepEqual(normalizeFilters({ filterVanilla: true, filterScaling: false }), { ...DEFAULT_FILTERS, vanilla: true, scaling: false });
  assert.deepEqual(normalizeFilters({ positive: false, bogus: 1 }), { ...DEFAULT_FILTERS, positive: false });
  assert.deepEqual(normalizeFilters("garbage"), DEFAULT_FILTERS);
});
