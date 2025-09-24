/*------------------------------*
 * Client-side pagination       *
 *------------------------------*/
(function (MCSE) {
  const STORAGE_KEY = "mcse-page-length";
  MCSE.pagination = {
    page: 1,
    perPage: 25, // Default to 25, will be overridden by localStorage or select
  };

  const infoEl = document.getElementById("table-info");
  const pagerEl = document.getElementById("pagination");
  const lengthSel = document.getElementById("page-length");

  // Initialize page length from localStorage or select element
  if (lengthSel) {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const storedValue = parseInt(stored, 10);
      if (!isNaN(storedValue) && [25, 50, 75, 100].includes(storedValue)) {
        MCSE.pagination.perPage = storedValue;
        lengthSel.value = String(storedValue);
      }
    }

    lengthSel.addEventListener("change", () => {
      const newValue = parseInt(lengthSel.value, 10);
      if (!isNaN(newValue)) {
        MCSE.pagination.perPage = newValue;
        localStorage.setItem(STORAGE_KEY, String(newValue));
        MCSE.pagination.page = 1;
        MCSE.updatePagination();
      }
    });
  }

  function storeBaseVisibility() {
    MCSE.rows.forEach((r) => {
      if (r.id === "no-results-row") return;
      r.dataset.baseDisplay = r.style.display || "";
    });
  }

  function restoreBaseVisibility() {
    MCSE.rows.forEach((r) => {
      if (r.id === "no-results-row") return;
      if (r.dataset.baseDisplay !== undefined) {
        r.style.display = r.dataset.baseDisplay;
      }
    });
  }

  function getBaseVisibleRows() {
    return MCSE.rows.filter(
      (r) => r.id !== "no-results-row" && r.dataset.baseDisplay !== "none"
    );
  }

  MCSE.updatePagination = function updatePagination() {
    if (!pagerEl) return;

    restoreBaseVisibility();
    const baseRows = getBaseVisibleRows();
    const total = baseRows.length;
    const per = MCSE.pagination.perPage;
    const totalPages = Math.max(1, Math.ceil(total / per));

    // Ensure current page is valid
    if (MCSE.pagination.page > totalPages) MCSE.pagination.page = totalPages;
    if (MCSE.pagination.page < 1) MCSE.pagination.page = 1;

    const current = MCSE.pagination.page;

    // Hide/show rows based on current page
    baseRows.forEach((r, idx) => {
      const pageIdx = Math.floor(idx / per) + 1;
      r.dataset.page = pageIdx;
      if (pageIdx === current) {
        r.style.display = r.dataset.baseDisplay || "";
      } else {
        r.style.display = "none";
      }
    });

    // Handle placeholder row
    const placeholder = document.getElementById("no-results-row");
    if (placeholder) placeholder.style.display = total === 0 ? "" : "none";

    MCSE.recomputeZebra();

    // Update info text
    const start = total === 0 ? 0 : (current - 1) * per + 1;
    const end = Math.min(current * per, total);
    if (infoEl) {
      infoEl.textContent = `Showing ${start} to ${end} of ${total} entries.`;
    }

    // Build pagination controls
    buildPagination(current, totalPages);
  };

  function buildPagination(current, totalPages) {
    // Clear pagination
    pagerEl.innerHTML = "";

    if (totalPages <= 1) {
      return; // No pagination needed
    }

    // Previous button
    const prevBtn = document.createElement("button");
    prevBtn.textContent = "◀";
    prevBtn.className = "arrow-btn";
    prevBtn.disabled = current === 1;
    prevBtn.addEventListener("click", () => {
      if (current > 1) {
        MCSE.pagination.page = current - 1;
        MCSE.updatePagination();
        scrollToTop();
      }
    });
    pagerEl.appendChild(prevBtn);

    // Calculate which pages to show
    const pagesToShow = calculatePageNumbers(current, totalPages);

    for (let i = 0; i < pagesToShow.length; i++) {
      const pageInfo = pagesToShow[i];

      if (pageInfo.type === "ellipsis") {
        const ellipsis = document.createElement("span");
        ellipsis.textContent = "...";
        ellipsis.className = "ellipsis";
        pagerEl.appendChild(ellipsis);
      } else {
        const pageBtn = document.createElement("button");
        pageBtn.textContent = pageInfo.page;
        pageBtn.className = "page-num";
        if (pageInfo.page === current) {
          pageBtn.classList.add("current");
          pageBtn.disabled = true;
        }
        pageBtn.addEventListener("click", () => {
          if (pageInfo.page !== current) {
            MCSE.pagination.page = pageInfo.page;
            MCSE.updatePagination();
            scrollToTop();
          }
        });
        pagerEl.appendChild(pageBtn);
      }
    }

    // Next button
    const nextBtn = document.createElement("button");
    nextBtn.textContent = "▶";
    nextBtn.className = "arrow-btn";
    nextBtn.disabled = current === totalPages;
    nextBtn.addEventListener("click", () => {
      if (current < totalPages) {
        MCSE.pagination.page = current + 1;
        MCSE.updatePagination();
        scrollToTop();
      }
    });
    pagerEl.appendChild(nextBtn);
  }

  function calculatePageNumbers(current, totalPages) {
    const pages = [];

    // If 5 or fewer pages, show them all
    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push({ type: "page", page: i });
      }
      return pages;
    }

    // Always show first page
    pages.push({ type: "page", page: 1 });

    // Logic based on current page position
    if (current <= 3) {
      // Current page is at the beginning: 1 2 3 4 ... last
      for (let i = 2; i <= 4; i++) {
        pages.push({ type: "page", page: i });
      }
      pages.push({ type: "ellipsis" });
      pages.push({ type: "page", page: totalPages });
    } else if (current >= totalPages - 2) {
      // Current page is at the end: 1 ... (last-3) (last-2) (last-1) last
      pages.push({ type: "ellipsis" });
      for (let i = totalPages - 3; i <= totalPages; i++) {
        pages.push({ type: "page", page: i });
      }
    } else {
      // Current page is in the middle: 1 ... (current-1) current (current+1) ... last
      pages.push({ type: "ellipsis" });
      pages.push({ type: "page", page: current - 1 });
      pages.push({ type: "page", page: current });
      pages.push({ type: "page", page: current + 1 });
      pages.push({ type: "ellipsis" });
      pages.push({ type: "page", page: totalPages });
    }

    return pages;
  }

  function scrollToTop() {
    const wrap = document.querySelector(".table-scroll");
    if (wrap) wrap.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Hook existing flows
  const originalApplyTypeFilters = MCSE.applyTypeFilters;
  MCSE.applyTypeFilters = function wrappedTypeFilters() {
    originalApplyTypeFilters();
    storeBaseVisibility();
    MCSE.pagination.page = 1;
    MCSE.updatePagination();
  };
  const originalApplySearchFilter = MCSE.applySearchFilter;
  MCSE.applySearchFilter = function wrappedSearch() {
    originalApplySearchFilter();
    storeBaseVisibility();
    MCSE.pagination.page = 1;
    MCSE.updatePagination();
  };
  const originalRenderTable = MCSE.renderTable;
  MCSE.renderTable = function wrappedRender(data) {
    originalRenderTable(data);
    storeBaseVisibility();
    MCSE.pagination.page = 1;
    MCSE.updatePagination();
  };
})(window.MCSE);
