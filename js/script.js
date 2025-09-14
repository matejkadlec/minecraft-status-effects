// Build navigation from table rows
const navList = document.getElementById("mod-nav");
const rows = Array.from(document.querySelectorAll("#effects-table tbody tr"));
const seen = new Set();
rows.forEach((r) => {
  const mod = r.getAttribute("data-mod");
  if (!mod || seen.has(mod)) return;
  seen.add(mod);
  const li = document.createElement("li");
  li.innerHTML = `<a href="#${r.id}">${mod}</a>`;
  navList.appendChild(li);
});

const search = document.getElementById("search");
const filterPositive = document.getElementById("filterPositive");
const filterNegative = document.getElementById("filterNegative");
const filterScaling = document.getElementById("filterScaling");
const filterVanilla = document.getElementById("filterVanilla");
const clearBtn = document.getElementById("search-clear");
const noResultsRow = document.getElementById("no-results-row");

function updateNoResults() {
  if (!noResultsRow) return;
  // Count visible data rows (exclude the placeholder itself)
  const anyVisible = rows.some(
    (r) => r.id !== "no-results-row" && r.style.display !== "none"
  );
  if (!anyVisible) {
    noResultsRow.style.display = "";
  } else {
    noResultsRow.style.display = "none";
  }
}

function applyTypeFilters() {
  const showPos = filterPositive.checked;
  const showNeg = filterNegative.checked;
  const showScaling = filterScaling.checked;
  const showVanilla = filterVanilla ? filterVanilla.checked : true;
  rows.forEach((r) => {
    if (r.id === "no-results-row") return; // skip placeholder in filtering
    const type = r.getAttribute("data-type");
    const mod = r.getAttribute("data-mod");
    const isVanilla = mod === "Minecraft";
    const hasScaling = r.hasAttribute("data-scaling");
    if (!type) {
      r.style.display = "";
      return;
    }
    if (!showVanilla && isVanilla) {
      r.style.display = "none";
      return;
    }
    const visibleByType =
      (type === "positive" && showPos) || (type === "negative" && showNeg);
    const visibleByScaling = hasScaling ? showScaling : true; // if not scaling-tagged, ignore scaling filter
    if (visibleByType && visibleByScaling) {
      if (r.matches("[data-hidden-search]")) return;
      r.style.display = "";
    } else {
      r.style.display = "none";
    }
  });
  updateNoResults();
}

function applySearchFilter() {
  const q = search.value.toLowerCase();
  rows.forEach((r) => {
    if (r.id === "no-results-row") return; // skip placeholder
    const text = r.innerText.toLowerCase();
    if (q && !text.includes(q)) {
      r.setAttribute("data-hidden-search", "1");
      r.style.display = "none";
    } else {
      r.removeAttribute("data-hidden-search");
    }
  });
  applyTypeFilters();
  updateNoResults();
}

search.addEventListener("input", applySearchFilter);
[filterPositive, filterNegative, filterScaling, filterVanilla].forEach(
  (cb) => cb && cb.addEventListener("change", applyTypeFilters)
);
applyTypeFilters();

// Clear button behavior for search input
if (clearBtn && search) {
  function syncClearVisibility() {
    if (search.value.length > 0) {
      clearBtn.style.display = "block";
    } else {
      clearBtn.style.display = "none";
    }
  }
  search.addEventListener("input", syncClearVisibility);
  clearBtn.addEventListener("click", () => {
    search.value = "";
    syncClearVisibility();
    applySearchFilter();
    search.focus();
  });
  syncClearVisibility();
}

// Default is light theme (no class). Legacy stored 'light'/'dark' values handled below.
let suppressHashHighlight = false;

window.addEventListener("hashchange", () => {
  if (suppressHashHighlight) return; // skip during programmatic scroll
  rows.forEach((r) => r.classList.remove("highlight"));
  const id = location.hash.slice(1);
  if (!id) return;
  const target = document.getElementById(id);
  if (!target) return;
  target.classList.remove("highlight");
  void target.offsetWidth;
  target.classList.add("highlight");
});

// Intercept nav clicks for precise in-container scrolling (account sticky header)
navList.addEventListener("click", (e) => {
  const link = e.target.closest("a[href^='#']");
  if (!link) return;
  const hash = link.getAttribute("href");
  if (!hash) return;
  const id = hash.slice(1);
  const target = document.getElementById(id);
  if (!target) return;
  e.preventDefault();
  suppressHashHighlight = true;
  if (history.pushState) {
    history.pushState(null, "", hash);
  } else {
    location.hash = hash; // may fire hashchange but suppressed
  }
  function applyHighlight() {
    rows.forEach((r) => r.classList.remove("highlight"));
    target.classList.remove("highlight");
    void target.offsetWidth;
    target.classList.add("highlight");
  }
  const scrollWrap = document.querySelector(".table-scroll");
  if (scrollWrap) {
    const header = scrollWrap.querySelector("thead th");
    const headerHeight = header ? header.getBoundingClientRect().height : 0;
    // Use target offset relative to scroll container rather than DOMRect diff for precision
    const targetOffset = target.offsetTop; // distance from tbody start
    // Align so row is just under sticky header
    let desired = targetOffset - headerHeight;
    if (targetOffset === 0) desired = 0; // first row exact alignment
    // Clamp within scrollable range
    const maxScroll = scrollWrap.scrollHeight - scrollWrap.clientHeight;
    if (desired < 0) desired = 0;
    if (desired > maxScroll) desired = maxScroll;
    const start = performance.now();
    const duration = 600; // expected smooth scroll duration heuristic
    const delta = Math.abs(scrollWrap.scrollTop - desired);
    if (delta < 2) {
      // No real scrolling possible (already there or cannot move further)
      setTimeout(() => {
        applyHighlight();
        suppressHashHighlight = false;
      }, 70);
      return;
    }
    scrollWrap.scrollTo({ top: desired, behavior: "smooth" });
    let done = false;
    const check = () => {
      const diff = Math.abs(scrollWrap.scrollTop - desired);
      const elapsed = performance.now() - start;
      if (diff < 2 || elapsed > duration + 150) {
        if (!done) {
          done = true;
          setTimeout(() => {
            applyHighlight();
            suppressHashHighlight = false;
          }, 70); // slight delay to ensure visibility
        }
        return;
      }
      requestAnimationFrame(check);
    };
    requestAnimationFrame(check);
  } else {
    // Fallback to default behavior if wrapper missing
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    setTimeout(() => {
      applyHighlight();
      suppressHashHighlight = false;
    }, 650);
  }
});

// Remove highlight when clicking elsewhere (not on a nav link or highlighted row)
document.addEventListener("click", (e) => {
  const hashId = location.hash.slice(1);
  const targetRow = hashId ? document.getElementById(hashId) : null;
  // If click is inside nav links or inside the current highlighted row, ignore
  if (
    e.target.closest("#mod-nav") ||
    (targetRow && targetRow.contains(e.target))
  )
    return;
  // Otherwise clear highlight
  rows.forEach((r) => r.classList.remove("highlight"));
});

// Theme toggle logic
const root = document.documentElement;
const btnDark = document.getElementById("btn-dark");
const btnLight = document.getElementById("btn-light");
function applyTheme(theme) {
  if (theme === "dark") {
    root.classList.add("dark");
    btnDark.classList.add("active");
    btnLight.classList.remove("active");
  } else {
    root.classList.remove("dark");
    btnLight.classList.add("active");
    btnDark.classList.remove("active");
  }
  localStorage.setItem("mcse-theme", theme);
}
const storedTheme = localStorage.getItem("mcse-theme");
if (storedTheme === "dark") {
  applyTheme("dark");
} else {
  applyTheme("light");
}
btnLight?.addEventListener("click", () => applyTheme("light"));
btnDark?.addEventListener("click", () => applyTheme("dark"));

// Add after DOMContentLoaded or existing initialization
(function () {
  const scrollWrap = document.querySelector(".table-scroll");
  if (scrollWrap) {
    const handler = () => {
      if (scrollWrap.scrollTop > 0) scrollWrap.classList.add("scrolled");
      else scrollWrap.classList.remove("scrolled");
    };
    scrollWrap.addEventListener("scroll", handler, { passive: true });
    handler();
  }
})();
