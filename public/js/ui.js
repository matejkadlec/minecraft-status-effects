/*-------------------------------------------*
 * Small UI pieces: theme toggle and dialogs *
 *-------------------------------------------*/
import { read, write } from "./storage.js";

const root = document.documentElement;
const THEME_COLORS = { light: "#2366b8", dark: "#1b1d1f" };

export function debounce(fn, wait) {
  let timer = 0;
  const debounced = (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
  debounced.flush = (...args) => {
    clearTimeout(timer);
    fn(...args);
  };
  return debounced;
}

export function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/*--------------*
 * Theme toggle *
 *--------------*/
export function currentTheme() {
  return root.classList.contains("dark") ? "dark" : "light";
}

function applyTheme(theme, persist) {
  root.classList.toggle("dark", theme === "dark");
  document.querySelectorAll(".theme-button").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.id === `theme-${theme}`));
  });
  document.querySelectorAll('meta[name="theme-color"]').forEach((meta) => {
    meta.setAttribute("content", THEME_COLORS[theme]);
    meta.removeAttribute("media");
  });
  if (persist) write("theme", theme);
}

export function initTheme() {
  const stored = read("theme");
  // The inline script in <head> already applied the stored (or system) theme; only sync the buttons here.
  applyTheme(stored === "dark" || stored === "light" ? stored : currentTheme(), false);
  document.getElementById("theme-light")?.addEventListener("click", () => applyTheme("light", true));
  document.getElementById("theme-dark")?.addEventListener("click", () => applyTheme("dark", true));
}

/*--------------------------------------*
 * Help dialogs (native <dialog>)       *
 *--------------------------------------*/
export function initDialogs() {
  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-dialog]");
    if (!trigger) return;
    const dialog = document.getElementById(trigger.dataset.dialog);
    if (!dialog || typeof dialog.showModal !== "function") return;
    event.preventDefault();
    event.stopPropagation();
    dialog.showModal();
    root.classList.add("dialog-open");
  });

  document.querySelectorAll("dialog.dialog").forEach((dialog) => {
    // A click on the backdrop lands on the <dialog> element itself, outside its card.
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener("close", () => root.classList.remove("dialog-open"));
  });
}
