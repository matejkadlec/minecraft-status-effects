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
    placeholder.innerHTML = `<td colspan="6" class="no-results">No results found.</td>`;

    data.forEach((item) => {
      const tr = document.createElement("tr");
      tr.id = item.id;
      tr.setAttribute("data-mod", item.mod);
      if (item.type) tr.setAttribute("data-type", item.type);
      if (item.tags?.includes("scaling")) tr.setAttribute("data-scaling", "1");

      const tdMod = document.createElement("td");
      tdMod.textContent = item.mod;
      const tdEffect = document.createElement("td");
      tdEffect.textContent = item.effect;
      const tdMax = document.createElement("td");
      tdMax.textContent = item.maxLevel ?? "";
      const tdDesc = document.createElement("td");
      let rawDesc = item.description || "";

      // Add unreliable warning emoji if the effect has unreliable tag
      if (item.tags?.includes("unreliable")) {
        rawDesc =
          '<span class="unreliable-warning" title="This effect might not work as described.">⚠️</span> ' +
          rawDesc;
      }

      // Replace ^level with exponent looking sup tag
      rawDesc = rawDesc.replace(/\^level/g, '<sup class="lvl-sup">level</sup>');
      // Normalize arrow glyphs to avoid row height expansion due to font metrics
      // Wrap any standalone right arrow U+2192 or the ascii sequence '->' in a span.arrow
      rawDesc = rawDesc
        .replace(/→/g, '<span class="arrow" aria-hidden="true">→</span>')
        .replace(
          /-&gt;(?![^<]*>)|->/g,
          '<span class="arrow" aria-hidden="true">→</span>'
        );
      tdDesc.innerHTML = rawDesc;
      const tdTags = document.createElement("td");
      (item.tags || []).forEach((t) => {
        // Skip unreliable tag as it's shown as emoji in description
        if (t === "unreliable") return;

        const span = document.createElement("span");
        span.className = `badge ${
          t === "positive" ? "pos" : t === "negative" ? "neg" : t
        }`;
        span.textContent = t.charAt(0).toUpperCase() + t.slice(1);
        tdTags.appendChild(span);
      });
      const tdSource = document.createElement("td");
      tdSource.innerHTML = item.source || "";
      tdSource.className = "source-column";
      tr.append(tdMod, tdEffect, tdMax, tdDesc, tdTags, tdSource);
      tbody.appendChild(tr);
      MCSE.rows.push(tr);
    });

    tbody.appendChild(placeholder);
    MCSE.recomputeZebra();
    MCSE.buildNav();

    // Initialize sorting if not already initialized
    if (typeof MCSE.initSorting === "function" && !MCSE.sortingInitialized) {
      MCSE.initSorting();
      MCSE.sortingInitialized = true;
    }

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

    // Get all unique mods from all rows (always show all mods)
    const allMods = [];
    const seenMods = new Set();

    MCSE.rows.forEach((r) => {
      if (r.id === "no-results-row") return;
      const mod = r.getAttribute("data-mod");
      if (!mod || seenMods.has(mod)) return;
      seenMods.add(mod);
      allMods.push({ mod, id: r.id });
    });

    // Get currently visible mods (considering filters and search)
    const visibleRows = MCSE.rows.filter((r) => {
      if (r.id === "no-results-row") return false;
      if (r.hasAttribute("data-hidden-search")) return false;
      return r.dataset.baseDisplay !== "none";
    });

    const availableMods = new Set();
    visibleRows.forEach((r) => {
      const mod = r.getAttribute("data-mod");
      if (mod) availableMods.add(mod);
    });

    // Helper function to determine mod order (Minecraft first, then alphabetical)
    const shouldComeBefore = (modA, modB) => {
      if (modA === "Minecraft" && modB !== "Minecraft") return true;
      if (modA !== "Minecraft" && modB === "Minecraft") return false;
      return modA < modB;
    };

    // Sort all mods
    allMods.sort((a, b) => (shouldComeBefore(a.mod, b.mod) ? -1 : 1));

    // Clear and rebuild navigation
    navList.innerHTML = "";

    allMods.forEach(({ mod, id }) => {
      const li = document.createElement("li");
      const isAvailable = availableMods.has(mod);

      // Find first visible effect for this mod to link to
      let targetId = id;
      if (isAvailable) {
        const firstVisibleEffect = visibleRows.find(
          (r) => r.getAttribute("data-mod") === mod
        );
        if (firstVisibleEffect) targetId = firstVisibleEffect.id;
      }

      li.innerHTML = `<a href="#${targetId}" data-mod="${mod}" data-available="${isAvailable}">${mod}</a>`;
      navList.appendChild(li);
    });
  };
})(window.MCSE);
