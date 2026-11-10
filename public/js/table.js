/*----------------------------------------------------------*
 * Effects table: rows of the current page, sort indicators, *
 * scrolling to a row and the highlight after a jump         *
 *----------------------------------------------------------*/
import { DEFAULT_SORT } from "./logic.js";
import { prefersReducedMotion } from "./ui.js";

const tbody = document.getElementById("effects-body");
const scroller = document.getElementById("table-scroll");
const table = document.getElementById("effects");
const rowCache = new Map();

const template = document.createElement("template");
template.innerHTML =
  '<tr><td class="cell-mod"></td><td class="cell-effect"></td>' +
  '<td class="cell-max"></td><td class="cell-desc"></td>' +
  '<td class="cell-tags"></td><td class="cell-source"></td></tr>';

function badge(className, text) {
  const span = document.createElement("span");
  span.className = `badge ${className}`;
  span.textContent = text;
  return span;
}

function createRow(effect) {
  const row = template.content.firstElementChild.cloneNode(true);
  const [mod, name, max, description, tags, source] = row.children;
  row.id = effect.id;
  mod.textContent = effect.mod;
  name.textContent = effect.effect;
  if (effect.since) {
    const since = document.createElement("span");
    since.className = "since";
    since.title = `Added in Minecraft ${effect.since}`;
    since.textContent = `${effect.since}+`;
    name.append(" ", since);
  }
  max.textContent = effect.maxLevel;
  // Description and source are HTML escaped by the server; only <b>, <i> and formatting spans remain.
  description.innerHTML = effect.description;
  if (effect.unreliable) {
    const warning = document.createElement("span");
    warning.className = "unreliable";
    warning.setAttribute("role", "img");
    warning.setAttribute("aria-label", "Unreliable");
    warning.title = "This effect might not work as described.";
    warning.textContent = "⚠️";
    description.prepend(warning, " ");
  }
  tags.append(badge(effect.type === "positive" ? "pos" : "neg", effect.type));
  if (effect.scaling) tags.append(badge("scaling", "scaling"));
  source.innerHTML = effect.source;
  return row;
}

/** Forget the rows built for the previous version. */
export function resetRows() {
  rowCache.clear();
}

export function renderRows(effects, emptyMessage = "No results found.") {
  const fragment = document.createDocumentFragment();
  for (const effect of effects) {
    let row = rowCache.get(effect.id);
    if (!row) {
      row = createRow(effect);
      rowCache.set(effect.id, row);
    }
    row.classList.remove("flash");
    fragment.append(row);
  }
  if (effects.length === 0) {
    const row = document.createElement("tr");
    row.className = "no-results";
    const cell = document.createElement("td");
    cell.colSpan = 6;
    cell.textContent = emptyMessage;
    row.append(cell);
    fragment.append(row);
  }
  tbody.replaceChildren(fragment);
}

function isDefaultSort(sortState) {
  return JSON.stringify(sortState) === JSON.stringify(DEFAULT_SORT);
}

export function updateSortIndicators(sortState) {
  table.querySelectorAll("thead th").forEach((th) => {
    const index = sortState.findIndex(([column]) => column === th.dataset.column);
    const button = th.querySelector(".sort-button");
    th.querySelector(".sort-priority")?.remove();
    if (index === -1) {
      th.removeAttribute("aria-sort");
      return;
    }
    th.setAttribute("aria-sort", sortState[index][1] === "asc" ? "ascending" : "descending");
    if (sortState.length > 1 && !isDefaultSort(sortState)) {
      const priority = document.createElement("span");
      priority.className = "sort-priority";
      priority.textContent = String(index + 1);
      priority.title = `Sort priority ${index + 1}`;
      button.querySelector(".sort-arrows").before(priority);
    }
  });
}

export function setCaption(text) {
  const caption = table.querySelector("caption");
  if (caption) caption.textContent = text;
}

export function setLoading(loading) {
  scroller.classList.toggle("is-loading", loading);
  scroller.setAttribute("aria-busy", String(loading));
}

export function scrollToTop(smooth = false) {
  scroller.scrollTo({ top: 0, left: 0, behavior: smooth && !prefersReducedMotion() ? "smooth" : "auto" });
}

function headerHeight() {
  const head = table.tHead;
  return head && getComputedStyle(head).display !== "none" ? head.getBoundingClientRect().height : 0;
}

let flashTimer = 0;

function flash(row) {
  clearTimeout(flashTimer);
  tbody.querySelectorAll("tr.flash").forEach((other) => other.classList.remove("flash"));
  // Restart the animation even if the same row is highlighted twice in a row.
  void row.offsetWidth;
  row.classList.add("flash");
  flashTimer = setTimeout(() => row.classList.remove("flash"), 1500);
}

/** Smoothly scrolls the table so the row sits right below the sticky header, then highlights it. */
export function revealRow(id) {
  const row = document.getElementById(id);
  if (!row || !tbody.contains(row)) return;
  const offset = row.getBoundingClientRect().top - scroller.getBoundingClientRect().top - headerHeight();
  const target = Math.max(0, Math.min(scroller.scrollTop + offset, scroller.scrollHeight - scroller.clientHeight));
  if (Math.abs(target - scroller.scrollTop) < 2 || prefersReducedMotion()) {
    scroller.scrollTo({ top: target, left: 0 });
    flash(row);
    return;
  }
  let done = false;
  const finish = () => {
    if (done) return;
    done = true;
    scroller.removeEventListener("scrollend", finish);
    flash(row);
  };
  scroller.addEventListener("scrollend", finish, { once: true });
  // Fallback for browsers without the scrollend event (and if the scroll gets interrupted).
  setTimeout(finish, 700);
  scroller.scrollTo({ top: target, left: 0, behavior: "smooth" });
}
