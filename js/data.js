/*------------------------------*
 * Data loading & bootstrap     *
 *------------------------------*/
(function (MCSE) {
  MCSE.loadEffectsData = async function loadEffectsData() {
    const jsonUrl = `data/effects.json?v=${Date.now()}`;
    try {
      const res = await fetch(jsonUrl, { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return json.effects || json;
    } catch (err) {
      console.error("Failed to fetch data/effects.json", err);
      return [];
    }
  };

  (async function initAsync() {
    const fresh = await MCSE.loadEffectsData();
    if (MCSE.rows.length && fresh.length === MCSE.effects.length) return; // unchanged
    MCSE.effects = fresh;
    MCSE.renderTable(MCSE.effects);
    MCSE.applyTypeFilters();
    MCSE.updateNoResults();
  })();

  // Scroll state decoration for shadow under header etc.
  (function monitorScroll() {
    const scrollWrap = document.querySelector(".table-scroll");
    if (!scrollWrap) return;
    const handler = () => {
      if (scrollWrap.scrollTop > 0) scrollWrap.classList.add("scrolled");
      else scrollWrap.classList.remove("scrolled");
    };
    scrollWrap.addEventListener("scroll", handler, { passive: true });
    handler();
  })();
})(window.MCSE);
