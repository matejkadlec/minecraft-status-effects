/*------------------------------*
 * Rendering & navigation build *
 *------------------------------*/
(function (MCSE) {
  MCSE.renderTable = function renderTable(data) {
    const tbody = MCSE.tbody;
    tbody.innerHTML = "";
    MCSE.rows = [];
    const placeholder = document.createElement("tr");
    placeholder.id = "no-results-row";
    placeholder.style.display = "none";
    placeholder.innerHTML = `<td colspan="5" class="no-results">No results found.</td>`;

    data.forEach((item) => {
      const tr = document.createElement("tr");
      tr.id = item.id;
      tr.setAttribute("data-mod", item.mod);
      if (item.type) tr.setAttribute("data-type", item.type);
      if (item.tags?.includes("scaling") || item.scaling)
        tr.setAttribute("data-scaling", "1");

      const tdMod = document.createElement("td");
      tdMod.textContent = item.mod;
      const tdEffect = document.createElement("td");
      tdEffect.textContent = item.effect;
      const tdMax = document.createElement("td");
      tdMax.textContent = item.maxLevel ?? "";
      const tdDesc = document.createElement("td");
      let rawDesc = item.descriptionHtml || item.description || "";
      // Replace ^level with exponent looking sup tag
      rawDesc = rawDesc.replace(/\^level/g, '<sup class="lvl-sup">level</sup>');
      // Normalize arrow glyphs to avoid row height expansion due to font metrics
      // Wrap any standalone right arrow U+2192 or the ascii sequence '->' in a span.arrow
      rawDesc = rawDesc
        .replace(/→/g, '<span class="arrow" aria-hidden="true">→</span>')
        .replace(
          /-&gt;|->/g,
          '<span class="arrow" aria-hidden="true">→</span>'
        );
      tdDesc.innerHTML = rawDesc;
      const tdTags = document.createElement("td");
      (item.tags || []).forEach((t) => {
        const span = document.createElement("span");
        span.className = `badge ${
          t === "positive"
            ? "pos"
            : t === "negative"
            ? "neg"
            : t === "utility"
            ? "util"
            : t
        }`;
        span.textContent = t.charAt(0).toUpperCase() + t.slice(1);
        tdTags.appendChild(span);
      });
      tr.append(tdMod, tdEffect, tdMax, tdDesc, tdTags);
      tbody.appendChild(tr);
      MCSE.rows.push(tr);
    });

    tbody.appendChild(placeholder);
    MCSE.recomputeZebra();
    MCSE.buildNav();
    // Minimum spinner visibility for perceived stability
    const MIN_MS = 500;
    const elapsed = performance.now() - (MCSE.loadStart || 0);
    const remaining = elapsed < MIN_MS ? MIN_MS - elapsed : 0;
    const finalize = () => {
      const navListEl = document.getElementById("mod-nav");
      const navLoader = document.getElementById("nav-loading");
      if (navListEl && navLoader) {
        navListEl.classList.remove("hidden");
        navLoader.remove();
      }
      const scroll = document.querySelector(".table-scroll.loading");
      if (scroll) {
        scroll.classList.remove("loading");
        const tbody = scroll.querySelector("table tbody");
        if (tbody) tbody.style.display = ""; // restore display
      }
    };
    if (remaining > 0) setTimeout(finalize, remaining);
    else finalize();
  };

  MCSE.buildNav = function buildNav() {
    const navList = MCSE.navList;
    navList.innerHTML = "";
    const seen = new Set();
    MCSE.rows.forEach((r) => {
      const mod = r.getAttribute("data-mod");
      if (!mod || seen.has(mod)) return;
      seen.add(mod);
      const li = document.createElement("li");
      li.innerHTML = `<a href="#${r.id}">${mod}</a>`;
      navList.appendChild(li);
    });
  };
})(window.MCSE);
