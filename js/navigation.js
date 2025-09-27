/*------------------------------*
 * Hash navigation & row focus *
 *------------------------------*/
(function (MCSE) {
  let suppressHashHighlight = false;

  window.addEventListener("hashchange", () => {
    if (suppressHashHighlight) return;
    MCSE.rows.forEach((r) => r.classList.remove("highlight"));
    const id = location.hash.slice(1);
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;
    target.classList.remove("highlight");
    void target.offsetWidth; // restart animation
    target.classList.add("highlight");
  });

  MCSE.navList.addEventListener("click", (e) => {
    const link = e.target.closest("a[href^='#']");
    if (!link) return;
    e.preventDefault();

    // Check if the mod is available (has visible effects)
    const isAvailable = link.getAttribute("data-available") === "true";
    if (!isAvailable) {
      return; // Do nothing if mod is not available
    }

    const targetMod = link.getAttribute("data-mod");
    if (!targetMod) return;

    // Find first visible effect for this mod (considering filters and search)
    const targetRow = MCSE.rows.find((r) => {
      if (r.id === "no-results-row") return false;
      if (r.getAttribute("data-mod") !== targetMod) return false;
      // Check if row is hidden by search filter
      if (r.hasAttribute("data-hidden-search")) return false;
      // Check if row is hidden by type filters
      return r.dataset.baseDisplay !== "none";
    });

    if (!targetRow) return;

    // Update hash in URL
    const hash = `#${targetRow.id}`;
    suppressHashHighlight = true;
    if (history.pushState) history.pushState(null, "", hash);
    else location.hash = hash;

    // Find which page contains this row
    if (MCSE.updatePagination && targetRow.dataset.page) {
      const targetPage = parseInt(targetRow.dataset.page, 10);
      if (targetPage && targetPage !== MCSE.pagination.page) {
        // Switch to the correct page first
        MCSE.pagination.page = targetPage;
        MCSE.updatePagination();
        // Small delay to ensure DOM updates
        setTimeout(() => scrollAndHighlight(targetRow), 50);
        return;
      }
    }

    // Row is on current page, scroll immediately
    scrollAndHighlight(targetRow);
  });

  function scrollAndHighlight(targetRow) {
    function applyHighlight() {
      MCSE.rows.forEach((r) => r.classList.remove("highlight"));
      targetRow.classList.remove("highlight");
      void targetRow.offsetWidth;
      targetRow.classList.add("highlight");
    }

    const scrollWrap = document.querySelector(".table-scroll");
    if (scrollWrap) {
      const header = scrollWrap.querySelector("thead th");
      const headerHeight = header ? header.getBoundingClientRect().height : 0;
      const targetOffset = targetRow.offsetTop;
      let desired = targetOffset - headerHeight;
      if (targetOffset === 0) desired = 0;
      const maxScroll = scrollWrap.scrollHeight - scrollWrap.clientHeight;
      if (desired < 0) desired = 0;
      if (desired > maxScroll) desired = maxScroll;

      const start = performance.now();
      const duration = 600;
      const delta = Math.abs(scrollWrap.scrollTop - desired);

      if (delta < 2) {
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
            }, 70);
          }
          return;
        }
        requestAnimationFrame(check);
      };
      requestAnimationFrame(check);
    } else {
      targetRow.scrollIntoView({ behavior: "smooth", block: "start" });
      setTimeout(() => {
        applyHighlight();
        suppressHashHighlight = false;
      }, 650);
    }
  }

  document.addEventListener("click", (e) => {
    const hashId = location.hash.slice(1);
    const targetRow = hashId ? document.getElementById(hashId) : null;
    if (
      e.target.closest("#mod-nav") ||
      (targetRow && targetRow.contains(e.target))
    )
      return;
    MCSE.rows.forEach((r) => r.classList.remove("highlight"));
  });
})(window.MCSE);

document.addEventListener("click", (e) => {
  const ref = e.target.closest(".fn-ref");
  if (!ref) return;
  const id = ref.getAttribute("data-target");
  if (!id) return;
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove("flash");
  void el.offsetWidth;
  el.classList.add("flash");
});
