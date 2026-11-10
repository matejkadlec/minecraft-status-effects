/*------------------------------------------------------------*
 * Sidebar: mod navigation (with collapsible groups) and the  *
 * collapse (desktop) / drawer (small screens) behaviour      *
 *------------------------------------------------------------*/
import { read, write } from "./storage.js";
import { prefersReducedMotion } from "./ui.js";

const root = document.documentElement;
const list = document.getElementById("mod-nav");
const sidebar = document.getElementById("sidebar");
const toggle = document.getElementById("sidebar-toggle");
const menuToggle = document.getElementById("menu-toggle");
const backdrop = document.getElementById("sidebar-backdrop");
const drawerQuery = window.matchMedia("(max-width: 899px)");
const openGroups = new Set();

function modLink(item, index) {
  const li = document.createElement("li");
  const link = document.createElement("a");
  link.href = `#${item.target}`;
  link.dataset.mod = item.mod;
  link.textContent = item.mod;
  if (index !== undefined) link.style.setProperty("--i", String(index));
  li.append(link);
  return li;
}

function setGroupExpanded(group, expanded) {
  group.classList.toggle("expanded", expanded);
  group.querySelector(".group-header").setAttribute("aria-expanded", String(expanded));
  group.querySelector(".group-children").inert = !expanded;
  if (expanded) openGroups.add(group.dataset.group);
  else openGroups.delete(group.dataset.group);
}

/** Keeps an expanded group in view inside the scrollable mod list. */
function keepInView(group) {
  const run = () => {
    const listRect = list.getBoundingClientRect();
    const rect = group.getBoundingClientRect();
    let delta = 0;
    if (rect.bottom > listRect.bottom) delta = rect.bottom - listRect.bottom + 4;
    if (rect.top - delta < listRect.top) delta = rect.top - listRect.top - 4;
    if (Math.abs(delta) > 1) list.scrollBy({ top: delta, behavior: prefersReducedMotion() ? "auto" : "smooth" });
  };
  const children = group.querySelector(".group-children");
  const onEnd = (event) => {
    if (event.target !== children) return;
    children.removeEventListener("transitionend", onEnd);
    run();
  };
  children.addEventListener("transitionend", onEnd);
  setTimeout(() => children.removeEventListener("transitionend", onEnd), 600);
}

/** Builds the list from the server's nav structure: mods first, then groups ("Other" last). */
export function renderNav(nav) {
  const fragment = document.createDocumentFragment();
  for (const item of nav) {
    if (!item.group) {
      fragment.append(modLink(item));
      continue;
    }
    const group = document.createElement("li");
    group.className = "mod-group";
    group.dataset.group = item.group;
    const header = document.createElement("button");
    header.type = "button";
    header.className = "group-header";
    header.innerHTML = '<span class="group-arrow" aria-hidden="true">▼</span><span class="group-name"></span>';
    header.querySelector(".group-name").textContent = item.group;
    const children = document.createElement("div");
    children.className = "group-children";
    const inner = document.createElement("ul");
    item.mods.forEach((mod, index) => inner.append(modLink(mod, index)));
    children.append(inner);
    group.append(header, children);
    fragment.append(group);
    setGroupExpanded(group, openGroups.has(item.group));
  }
  list.replaceChildren(fragment);
}

/**
 * Greys out mods without any effect in the filtered table and points each link at the
 * mod's first effect in the current order.
 */
export function updateNav(firstVisibleByMod) {
  list.querySelectorAll("a[data-mod]").forEach((link) => {
    const target = firstVisibleByMod.get(link.dataset.mod);
    if (target) {
      link.href = `#${target}`;
      link.removeAttribute("aria-disabled");
      link.removeAttribute("tabindex");
    } else {
      link.setAttribute("aria-disabled", "true");
      link.tabIndex = -1;
    }
  });
  list.querySelectorAll(".mod-group").forEach((group) => {
    const available = group.querySelector("a:not([aria-disabled])") !== null;
    group.classList.toggle("group-disabled", !available);
    const header = group.querySelector(".group-header");
    header.disabled = !available;
    if (!available && group.classList.contains("expanded")) setGroupExpanded(group, false);
  });
}

export function initNav({ onModClick }) {
  list.addEventListener("click", (event) => {
    const header = event.target.closest(".group-header");
    if (header) {
      const group = header.closest(".mod-group");
      if (group.classList.contains("group-disabled")) return;
      const expand = !group.classList.contains("expanded");
      setGroupExpanded(group, expand);
      if (expand) keepInView(group);
      return;
    }
    const link = event.target.closest("a[data-mod]");
    if (!link) return;
    event.preventDefault();
    if (link.getAttribute("aria-disabled") === "true") return;
    onModClick(link.dataset.mod);
    if (drawerQuery.matches) setDrawerOpen(false);
  });
}

/*-------------------------------------------*
 * Collapse (desktop) and drawer (mobile)    *
 *-------------------------------------------*/
function isCollapsed() {
  return root.classList.contains("sidebar-collapsed");
}

function syncToggleLabels() {
  if (drawerQuery.matches) {
    const open = root.classList.contains("sidebar-open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", "Close mods and filters");
    toggle.title = "Close (Esc)";
    menuToggle.setAttribute("aria-expanded", String(open));
    sidebar.inert = !open;
    return;
  }
  const collapsed = isCollapsed();
  const label = collapsed ? "Expand the sidebar" : "Collapse the sidebar";
  toggle.setAttribute("aria-expanded", String(!collapsed));
  toggle.setAttribute("aria-label", label);
  toggle.title = `${label} (Ctrl+B)`;
  sidebar.querySelector(".sidebar-inner").inert = collapsed;
  sidebar.inert = false;
}

function setCollapsed(collapsed) {
  root.classList.toggle("sidebar-collapsed", collapsed);
  write("sidebar", collapsed ? "collapsed" : "expanded");
  syncToggleLabels();
}

function setDrawerOpen(open) {
  if (open) {
    backdrop.hidden = false;
    sidebar.inert = false;
    // Next frame, so the slide-in and the backdrop fade actually transition.
    requestAnimationFrame(() => {
      root.classList.add("sidebar-open");
      syncToggleLabels();
    });
    toggle.focus({ preventScroll: true });
    return;
  }
  root.classList.remove("sidebar-open");
  window.setTimeout(() => {
    if (!root.classList.contains("sidebar-open")) backdrop.hidden = true;
  }, 300);
  if (sidebar.contains(document.activeElement)) menuToggle.focus({ preventScroll: true });
  syncToggleLabels();
}

export function toggleSidebar() {
  if (drawerQuery.matches) setDrawerOpen(!root.classList.contains("sidebar-open"));
  else setCollapsed(!isCollapsed());
}

export function initSidebar() {
  if (read("sidebar") === "collapsed") root.classList.add("sidebar-collapsed");
  toggle.addEventListener("click", toggleSidebar);
  menuToggle.addEventListener("click", () => setDrawerOpen(true));
  backdrop.addEventListener("click", () => setDrawerOpen(false));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && drawerQuery.matches && root.classList.contains("sidebar-open")) {
      setDrawerOpen(false);
    }
  });
  drawerQuery.addEventListener("change", () => {
    root.classList.remove("sidebar-open");
    backdrop.hidden = true;
    syncToggleLabels();
  });
  syncToggleLabels();
}
