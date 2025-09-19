/*----------------------------------*
 * Core bootstrap & DOM references  *
 *----------------------------------*/
window.MCSE = window.MCSE || {};

const MCSE = window.MCSE;

MCSE.navList = document.getElementById("mod-nav");
MCSE.table = document.getElementById("effects-table");
MCSE.tbody = MCSE.table.querySelector("tbody");
MCSE.table.classList.add("zebra");

MCSE.effects = [];
MCSE.rows = [];
MCSE.loadStart = performance.now();

/** Recompute zebra striping for currently visible rows */
MCSE.recomputeZebra = function recomputeZebra() {
  let visibleIndex = 0;
  MCSE.rows.forEach((r) => {
    if (r.id === "no-results-row") return;
    if (r.style.display === "none") return;
    r.classList.remove("odd", "even");
    r.classList.add(visibleIndex % 2 === 0 ? "odd" : "even");
    visibleIndex++;
  });
};

/** Run a function with transitions temporarily disabled */
MCSE.withTransitionSuspended = function withTransitionSuspended(fn) {
  const container = MCSE.table;
  container.classList.add("suspend-transitions");
  try {
    fn();
  } finally {
    requestAnimationFrame(() =>
      container.classList.remove("suspend-transitions")
    );
  }
};
