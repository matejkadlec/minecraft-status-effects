/*------------------------------*
 * Search & type filtering      *
 *------------------------------*/
(function (MCSE) {
  MCSE.searchInput = document.getElementById("search");
  MCSE.filterPositive = document.getElementById("filterPositive");
  MCSE.filterNegative = document.getElementById("filterNegative");
  MCSE.filterScaling = document.getElementById("filterScaling");
  MCSE.filterVanilla = document.getElementById("filterVanilla");
  MCSE.clearBtn = document.getElementById("search-clear");

  /*----------------------------*
   * Persist quick filter state *
   *----------------------------*/
  const FILTER_STORAGE_KEY = "mcse-filters";
  function loadStoredFilters() {
    try {
      const raw = localStorage.getItem(FILTER_STORAGE_KEY);
      if (!raw) return;
      const obj = JSON.parse(raw);
      [
        ["filterPositive", MCSE.filterPositive],
        ["filterNegative", MCSE.filterNegative],
        ["filterScaling", MCSE.filterScaling],
        ["filterVanilla", MCSE.filterVanilla],
      ].forEach(([key, el]) => {
        if (!el) return;
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
          el.checked = !!obj[key];
        }
      });
    } catch (e) {}
  }
  function saveFilters() {
    try {
      const payload = {
        filterPositive: !!MCSE.filterPositive?.checked,
        filterNegative: !!MCSE.filterNegative?.checked,
        filterScaling: !!MCSE.filterScaling?.checked,
        filterVanilla: !!MCSE.filterVanilla?.checked,
      };
      localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(payload));
    } catch (e) {}
  }
  loadStoredFilters();

  MCSE.getNoResultsRow = () => document.getElementById("no-results-row");

  MCSE.updateNoResults = function updateNoResults() {
    const row = MCSE.getNoResultsRow();
    if (!row) return;
    const anyVisible = MCSE.rows.some(
      (r) => r.id !== "no-results-row" && r.style.display !== "none"
    );
    row.style.display = anyVisible ? "none" : "";
  };

  MCSE.applyTypeFilters = function applyTypeFilters() {
    MCSE.withTransitionSuspended(() => {
      const showPos = MCSE.filterPositive.checked;
      const showNeg = MCSE.filterNegative.checked;
      const showScaling = MCSE.filterScaling.checked;
      const showVanilla = MCSE.filterVanilla
        ? MCSE.filterVanilla.checked
        : true;
      MCSE.rows.forEach((r) => {
        if (r.id === "no-results-row") return;
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
        const visibleByScaling = hasScaling ? showScaling : true;
        if (visibleByType && visibleByScaling) {
          if (r.matches("[data-hidden-search]")) return;
          r.style.display = "";
        } else {
          r.style.display = "none";
        }
      });
      MCSE.updateNoResults();
      MCSE.recomputeZebra();
    });
  };

  MCSE.applySearchFilter = function applySearchFilter() {
    MCSE.withTransitionSuspended(() => {
      const q = MCSE.searchInput.value.toLowerCase();
      MCSE.rows.forEach((r) => {
        if (r.id === "no-results-row") return;
        const text = r.innerText.toLowerCase();
        if (q && !text.includes(q)) {
          r.setAttribute("data-hidden-search", "1");
          r.style.display = "none";
        } else {
          r.removeAttribute("data-hidden-search");
        }
      });
      MCSE.applyTypeFilters();
      MCSE.updateNoResults();
      MCSE.recomputeZebra();
    });
  };

  if (MCSE.searchInput)
    MCSE.searchInput.addEventListener("input", MCSE.applySearchFilter);
  [
    MCSE.filterPositive,
    MCSE.filterNegative,
    MCSE.filterScaling,
    MCSE.filterVanilla,
  ].forEach(
    (cb) =>
      cb &&
      cb.addEventListener("change", () => {
        MCSE.applyTypeFilters();
        saveFilters();
      })
  );

  // Apply filters once after potential load from storage
  MCSE.applyTypeFilters();

  if (MCSE.clearBtn && MCSE.searchInput) {
    function syncClearVisibility() {
      MCSE.clearBtn.style.display =
        MCSE.searchInput.value.length > 0 ? "block" : "none";
    }
    MCSE.searchInput.addEventListener("input", syncClearVisibility);
    MCSE.clearBtn.addEventListener("click", () => {
      MCSE.searchInput.value = "";
      syncClearVisibility();
      MCSE.applySearchFilter();
      MCSE.searchInput.focus();
    });
    syncClearVisibility();
  }
})(window.MCSE);
