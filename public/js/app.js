/*------------------------------------------------------------*
 * Entry point: state (URL + localStorage), data per version, *
 * rendering and all the controls around the effects table   *
 *------------------------------------------------------------*/
import {
  DEFAULT_SORT,
  PAGE_LENGTHS,
  filterEffects,
  infoText,
  nextSortState,
  normalizeFilters,
  pageItems,
  paginate,
  prepareEffects,
  sortEffects,
} from "./logic.js";
import { initNav, initSidebar, renderNav, toggleSidebar, updateNav } from "./nav.js";
import { read, readJSON, write, writeJSON } from "./storage.js";
import {
  renderRows,
  resetRows,
  revealRow,
  scrollToTop,
  setCaption,
  setLoading,
  updateSortIndicators,
} from "./table.js";
import { currentTheme, debounce, initDialogs, initTheme } from "./ui.js";

const root = document.documentElement;
const $ = (id) => document.getElementById(id);
const elements = {
  search: $("search"),
  searchClear: $("search-clear"),
  version: $("version"),
  cardSort: $("card-sort"),
  pageLength: $("page-length"),
  pagination: $("pagination"),
  info: $("table-info"),
  ignoreFilters: $("ignore-filters"),
  exportFormat: $("export-format"),
  homeLink: $("home-link"),
  thead: document.querySelector("#effects thead"),
  canonical: document.querySelector('link[rel="canonical"]'),
  filters: {
    vanilla: $("filter-vanilla"),
    scaling: $("filter-scaling"),
    positive: $("filter-positive"),
    negative: $("filter-negative"),
  },
};

const VERSIONS = [...elements.version.options].map((option) => option.value);
const DEFAULT_VERSION = elements.version.dataset.default || VERSIONS[0];
const SITE_ORIGIN = elements.canonical ? new URL(elements.canonical.href).origin : location.origin;
const CARD_SORTS = {
  mod: DEFAULT_SORT,
  effect: [["effect", "asc"], ["mod", "asc"]],
  maxLevel: [["maxLevel", "desc"], ["mod", "asc"], ["effect", "asc"]],
  tags: [["tags", "asc"], ["mod", "asc"], ["effect", "asc"]],
};

const cache = new Map();
let current = null;
let view = [];
let loadController = null;
let serverVersion = DEFAULT_VERSION;

const state = {
  version: DEFAULT_VERSION,
  search: "",
  filters: normalizeFilters(null),
  sort: DEFAULT_SORT.map((entry) => [...entry]),
  page: 1,
  perPage: 25,
};

/*-----------------*
 * Data per version *
 *-----------------*/
function prepare(payload) {
  return { ...payload, effects: prepareEffects(payload.effects) };
}

async function fetchVersion(version) {
  loadController?.abort();
  loadController = new AbortController();
  const response = await fetch(`/api/effects?version=${encodeURIComponent(version)}`, {
    signal: loadController.signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return prepare(await response.json());
}

/*-----------*
 * Rendering *
 *-----------*/
function compute() {
  const filtered = filterEffects(current.effects, { query: state.search, filters: state.filters });
  view = sortEffects(filtered, state.sort);
}

function firstVisibleByMod() {
  const first = new Map();
  for (const effect of view) if (!first.has(effect.mod)) first.set(effect.mod, effect.id);
  return first;
}

function pageButton(label, page, { current: isCurrent = false, arrow = false, disabled = false, title } = {}) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = arrow ? "page-arrow" : "page-num";
  button.textContent = label;
  button.dataset.page = String(page);
  if (title) button.setAttribute("aria-label", title);
  if (isCurrent) button.setAttribute("aria-current", "page");
  button.disabled = disabled;
  return button;
}

function renderPagination(page, totalPages) {
  const nodes = [];
  if (totalPages > 1) {
    nodes.push(pageButton("◀", page - 1, { arrow: true, disabled: page === 1, title: "Previous page" }));
    for (const item of pageItems(page, totalPages)) {
      if (item === "…") {
        const gap = document.createElement("span");
        gap.className = "ellipsis";
        gap.textContent = "…";
        nodes.push(gap);
      } else {
        nodes.push(pageButton(String(item), item, { current: item === page, title: `Page ${item}` }));
      }
    }
    nodes.push(pageButton("▶", page + 1, { arrow: true, disabled: page === totalPages, title: "Next page" }));
  }
  elements.pagination.replaceChildren(...nodes);
}

function syncCardSort() {
  const key = Object.entries(CARD_SORTS).find(
    ([, sort]) => JSON.stringify(sort) === JSON.stringify(state.sort),
  )?.[0];
  if (key) elements.cardSort.value = key;
}

function render() {
  const { page, totalPages, start, end } = paginate(view.length, state.page, state.perPage);
  state.page = page;
  const empty = current.effects.length === 0
    ? `There are no effects for Minecraft ${state.version} yet.`
    : "No results found.";
  renderRows(view.slice(start, end), empty);
  elements.info.textContent = infoText(start, end, view.length);
  renderPagination(page, totalPages);
  updateSortIndicators(state.sort);
  updateNav(firstVisibleByMod());
  syncCardSort();
}

function syncUrl({ hash = "" } = {}) {
  const url = new URL(location.href);
  url.searchParams.delete("version");
  url.searchParams.delete("search");
  if (state.version !== DEFAULT_VERSION) url.searchParams.set("version", state.version);
  const query = state.search.trim();
  if (query) url.searchParams.set("search", query);
  url.hash = hash;
  const next = `${url.pathname}${url.search}${url.hash}`;
  if (next !== `${location.pathname}${location.search}${location.hash}`) history.replaceState(null, "", next);
}

/** Recomputes the table after a change of the search, filters, sorting or page length. */
function update({ resetPage = true } = {}) {
  if (!current) return;
  if (resetPage) state.page = 1;
  compute();
  render();
  scrollToTop(false);
  syncUrl();
}

function goToPage(page) {
  state.page = page;
  render();
  scrollToTop(true);
}

function jumpToIndex(index) {
  const effect = view[index];
  if (!effect) return;
  const page = Math.floor(index / state.perPage) + 1;
  if (page !== state.page) {
    state.page = page;
    render();
    scrollToTop(false);
  }
  syncUrl({ hash: effect.id });
  requestAnimationFrame(() => revealRow(effect.id));
}

function jumpToMod(mod) {
  jumpToIndex(view.findIndex((effect) => effect.mod === mod));
}

function jumpToHash() {
  const id = decodeURIComponent(location.hash.slice(1));
  if (!id) return;
  const index = view.findIndex((effect) => effect.id === id);
  if (index !== -1) jumpToIndex(index);
}

/*--------------------------------*
 * Version switching              *
 *--------------------------------*/
function versionTitle(version) {
  return version === DEFAULT_VERSION
    ? "Minecraft Status Effects: Vanilla and Modded Effects Database"
    : `Minecraft ${version} Status Effects: Vanilla and Modded Effects Database`;
}

function showVersion(data) {
  current = data;
  resetRows();
  renderNav(data.nav);
  document.title = versionTitle(data.version);
  setCaption(`Minecraft ${data.version} status effects`);
  if (elements.canonical) {
    const query = data.version === DEFAULT_VERSION ? "" : `?version=${encodeURIComponent(data.version)}`;
    elements.canonical.href = `${SITE_ORIGIN}/${query}`;
  }
}

async function setVersion(version) {
  state.version = version;
  elements.version.value = version;
  write("version", version);
  if (!cache.has(version)) {
    scrollToTop(false);
    setLoading(true);
    try {
      cache.set(version, await fetchVersion(version));
    } catch (error) {
      if (error.name === "AbortError") return;
      console.error("Couldn't load the effects for", version, error);
      setLoading(false);
      // Stay on (or fall back to) a version that is loaded, so the table keeps working.
      const fallback = current ?? cache.get(serverVersion);
      state.version = fallback.version;
      elements.version.value = fallback.version;
      write("version", fallback.version);
      if (current !== fallback) {
        showVersion(fallback);
        update();
      }
      window.alert(`Couldn't load the effects for Minecraft ${version}. Please check your connection and try again.`);
      return;
    }
  }
  if (state.version !== version) return;
  setLoading(false);
  showVersion(cache.get(version));
  update();
}

/*----------*
 * Controls *
 *----------*/
const saveSearch = debounce(() => write("search", state.search.trim()), 400);
const searchChanged = debounce(() => {
  update();
  saveSearch();
}, 120);

function setSearch(value, { immediate = false } = {}) {
  state.search = value;
  elements.search.value = value;
  elements.searchClear.hidden = value.length === 0;
  if (immediate) searchChanged.flush();
  else searchChanged();
}

function initControls() {
  elements.search.addEventListener("input", () => setSearch(elements.search.value));
  elements.search.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && elements.search.value) {
      event.preventDefault();
      setSearch("", { immediate: true });
    }
  });
  elements.searchClear.addEventListener("click", () => {
    setSearch("", { immediate: true });
    elements.search.focus();
  });

  for (const [name, input] of Object.entries(elements.filters)) {
    input.addEventListener("change", () => {
      state.filters = { ...state.filters, [name]: input.checked };
      writeJSON("filters", state.filters);
      update();
    });
  }

  elements.version.addEventListener("change", () => setVersion(elements.version.value));

  elements.pageLength.addEventListener("change", () => {
    state.perPage = Number(elements.pageLength.value);
    write("page-length", state.perPage);
    update();
  });

  elements.pagination.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-page]");
    if (!button || button.disabled || button.getAttribute("aria-current")) return;
    goToPage(Number(button.dataset.page));
  });

  elements.thead.addEventListener("click", (event) => {
    const button = event.target.closest(".sort-button");
    if (!button) return;
    state.sort = nextSortState(state.sort, button.closest("th").dataset.column, event.shiftKey);
    update();
  });

  elements.cardSort.addEventListener("change", () => {
    state.sort = CARD_SORTS[elements.cardSort.value].map((entry) => [...entry]);
    update();
  });

  elements.ignoreFilters.addEventListener("change", () => {
    writeJSON("ignore-filters", elements.ignoreFilters.checked);
  });
  elements.exportFormat.addEventListener("change", () => exportTable(elements.exportFormat.value));

  elements.homeLink.addEventListener("click", (event) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.button !== 0) return;
    event.preventDefault();
    state.sort = DEFAULT_SORT.map((entry) => [...entry]);
    setSearch("", { immediate: true });
    write("search", "");
  });

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && !event.altKey && !event.shiftKey && event.key.toLowerCase() === "b") {
      event.preventDefault();
      toggleSidebar();
      return;
    }
    const typing = event.target.closest?.("input, textarea, select, [contenteditable='true']");
    if (event.key === "/" && !typing && !event.ctrlKey && !event.metaKey && !event.altKey) {
      event.preventDefault();
      elements.search.focus();
      elements.search.select();
    }
  });

  window.addEventListener("hashchange", jumpToHash);
}

/*--------*
 * Export *
 *--------*/
function filenameFrom(disposition) {
  const match = /filename="?([^";]+)"?/i.exec(disposition ?? "");
  return match ? match[1] : null;
}

async function exportTable(format) {
  if (!format || !current) return;
  const select = elements.exportFormat;
  const ignoreFilters = elements.ignoreFilters.checked;
  if (!ignoreFilters && view.length === 0) {
    select.value = "";
    window.alert("There are no effects to export with the current search and filters.");
    return;
  }
  select.disabled = true;
  try {
    const theme = currentTheme();
    const response = ignoreFilters
      ? await fetch(`/api/export/${format}?${new URLSearchParams({ version: state.version, theme })}`)
      : await fetch(`/api/export/${format}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ version: state.version, theme, ids: view.map((effect) => effect.id) }),
        });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filenameFrom(response.headers.get("Content-Disposition")) ?? `status-effects.${format}`;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  } catch (error) {
    console.error("Export failed", error);
    window.alert("The export failed. Please try again.");
  } finally {
    select.value = "";
    select.disabled = false;
  }
}

/*----------------*
 * Initialisation *
 *----------------*/
function readInitialState(serverVersion) {
  const params = new URLSearchParams(location.search);
  const urlVersion = params.get("version");
  const storedVersion = read("version");
  if (VERSIONS.includes(urlVersion)) state.version = urlVersion;
  else if (params.has("version")) state.version = serverVersion;
  else state.version = VERSIONS.includes(storedVersion) ? storedVersion : serverVersion;

  state.search = (params.has("search") ? params.get("search") : read("search")) ?? "";
  state.search = state.search.slice(0, 100);
  state.filters = normalizeFilters(readJSON("filters", null));
  const perPage = Number(read("page-length"));
  state.perPage = PAGE_LENGTHS.includes(perPage) ? perPage : PAGE_LENGTHS[0];

  elements.search.value = state.search;
  elements.searchClear.hidden = state.search.length === 0;
  elements.version.value = state.version;
  elements.pageLength.value = String(state.perPage);
  elements.ignoreFilters.checked = readJSON("ignore-filters", false) === true;
  for (const [name, input] of Object.entries(elements.filters)) input.checked = state.filters[name];
}

async function init() {
  initTheme();
  initDialogs();
  initSidebar();
  initNav({ onModClick: jumpToMod });

  let payload;
  try {
    payload = JSON.parse(document.getElementById("app-data").textContent);
  } catch (error) {
    console.error("Missing effects data; the static table stays as rendered by the server.", error);
    root.classList.add("app-ready");
    return;
  }
  serverVersion = payload.version;
  cache.set(payload.version, prepare(payload));
  readInitialState(payload.version);
  initControls();

  if (state.version === payload.version) {
    showVersion(cache.get(payload.version));
    compute();
    render();
    syncUrl({ hash: location.hash.slice(1) });
    root.classList.add("app-ready");
    jumpToHash();
  } else {
    // The server rendered another version (e.g. the default): keep its rows hidden while loading.
    await setVersion(state.version);
    root.classList.add("app-ready");
    jumpToHash();
  }
}

init();
